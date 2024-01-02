from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from faststream.nats import NatsBroker
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.application.config import ConfigFactory
from webinar.infrastructure.adapters.cache import CacheStore
from webinar.presentation.tgbot.handling.main import route
from webinar.presentation.tgbot.utils.create import create_other_database
from webinar.presentation.tgbot.utils.setup import setup_app


async def tgbot(
    psql_connect: AsyncConnection[DictRow], config_factory: ConfigFactory
) -> None:
    config = config_factory.config
    cache = CacheStore()

    bot = Bot(token=config.bot.token, parse_mode=ParseMode.HTML)
    disp = Dispatcher(
        storage=MemoryStorage(), events_isolation=SimpleEventIsolation()
    )
    await setup_app(
        disp, cache, config_factory, psql_connect, NatsBroker(config.nats.url)
    )
    await create_other_database(psql_connect)
    disp.include_router(route)
    return await disp.start_polling(bot)
