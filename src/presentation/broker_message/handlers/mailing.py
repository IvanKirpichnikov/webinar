from asyncio import sleep
from typing import cast
from uuid import uuid4

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from faststream import Context, Path
from faststream.nats import JStream, NatsRouter
from faststream.nats.annotations import NatsBroker as NatsBrokerAnn, NatsMessage
from nats.js.api import DeliverPolicy

from src.application.schemas.enums import DirectionEnum
from src.infrastructure.repositories.user import UserRepository
from src.presentation.broker_message.decoder import decoder


route = NatsRouter()
stream = JStream('webinar_stream')


@route.subscriber('start-mailing', decoder=decoder)
async def start_mailing(
    msg: dict[str, int | list[str]],
    broker: NatsBrokerAnn,
    user_repository: UserRepository = Context()
) -> None:
    admin_chat_id = msg.get('admin_chat_id')
    mailing_msg_id = msg.get('mailing_msg_id')
    direction_type = cast(
        list[DirectionEnum] | None,
        msg.get('direction_type')
    )
    
    if admin_chat_id is None:
        raise ValueError('admin_chat_id is None')
    if mailing_msg_id is None:
        raise ValueError('mailing_msg_id is None')
    if direction_type is None:
        raise ValueError('direction_type is None')
    
    async for user in user_repository.get_all_from_direction_type(direction_type):
        user_chat_id = user.chat_id
        await broker.publish(
            message='',
            subject=f'mailing.from.{admin_chat_id}.to.{user_chat_id}.{mailing_msg_id}',
            headers={'Nats-Msg-Id': str(uuid4())}
        )


@route.subscriber(
    subject='mailing.from.{admin_chat_id}.to.{user_chat_id}.{mailing_msg_id}',
    stream=stream,
    no_ack=True,
    deliver_policy=DeliverPolicy.NEW
)
async def mailing_handler(
    _: str,
    msg: NatsMessage,
    bot: Bot = Context(),
    admin_chat_id: int = Path(),
    user_chat_id: int = Path(),
    mailing_msg_id: int = Path()
) -> None:
    try:
        await bot.copy_message(
            from_chat_id=admin_chat_id,
            chat_id=user_chat_id,
            message_id=mailing_msg_id
        )
    except TelegramRetryAfter as exception:
        await sleep(exception.retry_after)
        await msg.nack()
    except TelegramBadRequest as exception:
        pass
    await msg.ack()
    await sleep(0.08)
