from logging import getLogger

from aiogram import (
    Bot,
    Dispatcher,
)
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import (
    MemoryStorage,
    SimpleEventIsolation,
)
from dishka import AsyncContainer
from faststream.nats import NatsBroker
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

from webinar.config import ConfigFactory
from webinar.infrastructure.adapters.cache import CacheStore
from webinar.presentation.tgbot.handling.main import route
from webinar.presentation.tgbot.utils.setup import setup_app


async def tgbot(
    psql_pool: AsyncConnectionPool[AsyncConnection[DictRow]],
    config_factory: ConfigFactory,
    container: AsyncContainer,
) -> None:
    config = config_factory.config
    cache = CacheStore()
    
    bot = Bot(
        config.bot.token,
        parse_mode=ParseMode.HTML
    )
    disp = Dispatcher(
        storage=MemoryStorage(),
        events_isolation=SimpleEventIsolation()
    )
    disp.include_router(route)
    await setup_app(
        disp,
        cache,
        config_factory,
        psql_pool,
        NatsBroker(config.nats.url, logger=getLogger('webinar.presentation.broker_message.__main__')),
        container
    )
    
    return await disp.start_polling(bot)
