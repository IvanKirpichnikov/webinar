from faststream import FastStream
from faststream.nats import NatsBroker
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.application.config import ConfigFactory
from webinar.presentation.broker_message.di import close_connect, setup_context
from webinar.presentation.broker_message.handlers.main import route


async def broker_message(
    connect: AsyncConnection[DictRow], config_factory: ConfigFactory
) -> None:
    config = ConfigFactory().config

    broker = NatsBroker(config.nats.url)
    broker.include_router(route)
    app = FastStream(broker)
    app.on_startup(setup_context)
    app.on_shutdown(close_connect)
    app.context.set_global("config", config_factory)
    app.context.set_global("connect", connect)

    return await app.run()
