import logging

from anyio import create_task_group

from webinar.presentation.broker_message.__main__ import (
    broker_message as broker_message_presentation,
)
from webinar.presentation.cli.common import setup
from webinar.presentation.tgbot.__main__ import tgbot as tgbot_presentation


async def tgbot() -> None:
    config_factory, psql_connect = await setup()
    logging.basicConfig(level=logging.INFO)
    try:
        await tgbot_presentation(psql_connect, config_factory)
    finally:
        await psql_connect.close()


async def broker_message() -> None:
    config_factory, psql_connect = await setup()
    logging.basicConfig(level=logging.INFO)
    try:
        await broker_message_presentation(psql_connect, config_factory)
    finally:
        await psql_connect.close()


async def application() -> None:
    config_factory, psql_connect = await setup()
    logging.basicConfig(level=logging.INFO)
    try:
        async with create_task_group() as tg:
            tg.start_soon(tgbot_presentation, psql_connect, config_factory)
            tg.start_soon(
                broker_message_presentation, psql_connect, config_factory
            )
    finally:
        await psql_connect.close()
