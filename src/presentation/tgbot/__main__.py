import asyncio
import sys
from logging import basicConfig, INFO

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from faststream.nats import NatsBroker
from psycopg import AsyncConnection
from psycopg.rows import dict_row

from src.application.config import ConfigFactory
from src.infrastructure.cache import CacheAdapter
from src.infrastructure.google_sheets.adapter import google_sheets_adapter
from src.presentation.tgbot.handling import routing
from src.presentation.tgbot.utils.create import create_other_database
from src.presentation.tgbot.utils.setup import setup_app


# TODO: изменить copywriting на copyrighting
async def main() -> None:
    cache = CacheAdapter()
    config_ = ConfigFactory()
    config = config_.config
    
    psql_connect = await AsyncConnection.connect(
        config.psql.url,
        row_factory=dict_row
    )
    bot = Bot(
        token=config.bot.token,
        parse_mode=ParseMode.HTML
    )
    disp = Dispatcher(
        storage=MemoryStorage(),
        events_isolation=SimpleEventIsolation()
    )
    await setup_app(disp, cache, config_, psql_connect, NatsBroker(config.nats.url))
    await create_other_database(psql_connect)
    disp.include_router(routing.route)
    
    try:
        await asyncio.gather(disp.start_polling(bot))
    finally:
        await psql_connect.close()


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

basicConfig(level=INFO)
asyncio.run(main())
