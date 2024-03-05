import logging

from anyio import create_task_group

from webinar.presentation.broker_message.__main__ import (
    broker_message as broker_message_presentation
)
from webinar.main.cli.common import setup
from webinar.presentation.tgbot.__main__ import tgbot as tgbot_presentation


async def tgbot() -> None:
    data = await setup()
    logging.basicConfig(level=logging.INFO)
    try:
        await tgbot_presentation(*data)
    finally:
        await data[0].close()


async def broker_message() -> None:
    data = await setup()
    logging.basicConfig(level=logging.INFO)
    try:
        await broker_message_presentation(*data)
    finally:
        await data[0].close()


async def application() -> None:
    data = await setup()
    logging.basicConfig(level=logging.INFO)
    try:
        async with create_task_group() as tg:
            tg.start_soon(tgbot_presentation, *data)
            tg.start_soon(broker_message_presentation, *data)
    finally:
        await data[0].close()
