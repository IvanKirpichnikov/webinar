from asyncio import sleep
from contextlib import suppress
from typing import Any
from uuid import uuid4

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramRetryAfter,
)
from faststream import (
    Context,
    Path,
)
from faststream.nats import (
    NatsRouter
)
from faststream.nats.annotations import (
    NatsBroker as NatsBrokerAnn,
    NatsMessage,
)
from psycopg import AsyncConnection
from psycopg.rows import dict_row, DictRow
from psycopg_pool import AsyncConnectionPool

from webinar.application.exceptions import NotFoundUsers
from webinar.application.schemas.dto.common import DirectionsTrainingDTO
from webinar.application.schemas.enums.direction_type import DirectionTrainingType
from webinar.infrastructure.database.repository.user import UserRepositoryImpl
from webinar.presentation.broker_message.decoder import decoder


route = NatsRouter()


@route.subscriber("start-mailing", decoder=decoder)
async def start_mailing(
    msg: dict[str, Any],
    broker: NatsBrokerAnn,
    pool: AsyncConnectionPool[AsyncConnection[DictRow]] = Context(),
) -> None:
    admin_chat_id = msg["admin_chat_id"]
    mailing_msg_id = msg["mailing_msg_id"]
    direction_training = DirectionTrainingType(msg["direction_training"])
    direction_trainings = [direction_training]
    
    if direction_training == DirectionTrainingType.ALl:
        direction_trainings = [
            DirectionTrainingType.SMM,
            DirectionTrainingType.COPYRIGHTING,
        ]
    try:
        async with pool.connection() as connect:
            connect.row_factory = dict_row
            user_entities = await UserRepositoryImpl(connect).read_all_by_direction_training(
                DirectionsTrainingDTO(direction_trainings)
            )
    except NotFoundUsers:
        return None
    
    for user in user_entities.users:
        await broker.publish(
            message="",
            subject=f"mailing.from.{admin_chat_id}.to.{user.telegram_chat_id}.msg_id.{mailing_msg_id}",
            headers={"Nats-Msg-Id": str(uuid4())},
        )


@route.subscriber(
    subject="mailing.from.{admin_chat_id}.to.{telegram_chat_id}.msg_id.{mailing_msg_id}"
)
async def mailing_handler(
    _: str,
    msg: NatsMessage,
    bot: Bot = Context(),
    admin_chat_id: int = Path(),
    telegram_chat_id: int = Path(),
    mailing_msg_id: int = Path(),
) -> None:
    task = bot.copy_message(
        from_chat_id=admin_chat_id,
        chat_id=telegram_chat_id,
        message_id=mailing_msg_id
    )
    with suppress(TelegramBadRequest):
        try:
            await task
        except TelegramRetryAfter as exception:
            retry_after = exception.retry_after
            await sleep(retry_after)
            await task
    await sleep(0.08)
