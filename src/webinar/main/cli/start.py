import logging

from anyio import create_task_group

from webinar.main.cli.common import setup
from webinar.presentation.broker_message.__main__ import (
    broker_message as broker_message_presentation
)
from webinar.presentation.tgbot.__main__ import tgbot as tgbot_presentation


logger = logging.getLogger(__name__)


async def tgbot() -> None:
    data = await setup()
    logger.warning('Start telegram bot')
    try:
        await tgbot_presentation(*data)
    finally:
        logger.warning('Stop telegram bot')
        await data[2].close()
        await data[0].close()


async def broker_message() -> None:
    data = await setup()
    logger.warning('Start broker message')
    try:
        await broker_message_presentation(*data[:2])
    finally:
        logger.warning('Stop broker message')
        await data[2].close()
        await data[0].close()


async def application() -> None:
    data = await setup()
    logger.warning('Start telegram bot')
    logger.warning('Start broker message')
    try:
        async with create_task_group() as tg:
            tg.start_soon(tgbot_presentation, *data)
            tg.start_soon(broker_message_presentation, *data[:2])
    finally:
        logger.warning('Stop telegram bot')
        logger.warning('Stop broker message')
        await data[2].close()
        await data[0].close()
