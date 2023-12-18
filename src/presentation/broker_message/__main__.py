import asyncio
import sys
from logging import basicConfig, INFO

from faststream import FastStream
from faststream.nats import NatsBroker

from src.application.config import ConfigFactory
from src.presentation.broker_message.di import close_connect, setup_context
from src.presentation.broker_message.handlers.routing import route


async def main():
    config = ConfigFactory()
    
    broker = NatsBroker(config.config.nats.url)
    broker.include_router(route)
    c = config.config
    
    app = FastStream(broker)
    app.on_startup(setup_context)
    app.on_shutdown(close_connect)
    app.context.set_global('config', config)
    
    await app.run()


if __name__ == '__main__':
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    basicConfig(level=INFO)
    asyncio.run(main())
