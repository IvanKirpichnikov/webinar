from aiogram import Bot
from faststream import FastStream
from faststream.nats import NatsBroker
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

from webinar.application.config import ConfigFactory
from webinar.presentation.broker_message.di import (
    close_connect,
    setup_context
)
from webinar.presentation.broker_message.handlers.main import route


async def broker_message(
    pool: AsyncConnectionPool[AsyncConnection[DictRow]],
    config_factory: ConfigFactory
) -> None:
    config = ConfigFactory().config
    
    broker = NatsBroker(config.nats.url, connect_timeout=100)
    broker.include_router(route)
    
    app = FastStream(broker)
    bot = Bot(config.bot.token)
    app.context.set_global('bot', bot)
    app.context.set_global("config", config_factory)
    app.context.set_global("pool", pool)
    app.on_startup(setup_context)
    app.on_shutdown(close_connect)
    
    try:
        await app.run()
    finally:
        await bot.session.close()
        

