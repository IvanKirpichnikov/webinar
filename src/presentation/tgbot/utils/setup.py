from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from faststream.nats import NatsBroker
from psycopg import AsyncConnection

from src.application.config import _Config, ConfigFactory
from src.infrastructure.cache import CacheAdapter
from src.infrastructure.google_sheets.adapter import google_sheets_adapter
from src.infrastructure.repositories.admin import AdminRepositoryImpl
from src.infrastructure.repositories.homework import HomeWorkRepositoryImpl
from src.infrastructure.repositories.stats import StatsRepositoryImpl
from src.infrastructure.repositories.user import UserRepository
from src.infrastructure.repositories.webinar import WebinarRepository
from src.presentation.tgbot.keyboard import KeyboardFactory
from src.presentation.tgbot.middlewaring.is_super_admin import IsSuperAdminMiddlewareImpl
from src.presentation.tgbot.middlewaring.uow import UoWRepositoryMiddlewareImpl


def setup_repository(disp: Dispatcher, connect: AsyncConnection) -> None:
    repos = [
        ('user', UserRepository),
        ('webinar', WebinarRepository),
        ('homework', HomeWorkRepositoryImpl),
        ('admin', AdminRepositoryImpl),
        ('stats', StatsRepositoryImpl)
    ]
    for raw_key, repo in repos:
        key = raw_key + '_repository'
        disp[key] = repo(connect)


def setup_factory(
    disp: Dispatcher,
    config: ConfigFactory
) -> None:
    disp['keyboard'] = KeyboardFactory()
    disp['config'] = config


async def setup_adapters(
    disp: Dispatcher,
    cache: CacheAdapter
) -> None:
    disp['cache'] = cache
    config: _Config = disp['config'].config


def setup_middleware(
    disp: Dispatcher,
    connect: AsyncConnection
) -> None:
    uow_middleware = UoWRepositoryMiddlewareImpl(connect)
    is_admin_middleware = IsSuperAdminMiddlewareImpl()
    disp.update.middleware(is_admin_middleware)
    disp.message.middleware(uow_middleware)
    disp.callback_query.middleware(uow_middleware)
    disp.callback_query.middleware(CallbackAnswerMiddleware())


def setup_connections(
    disp: Dispatcher,
    psql_connect: AsyncConnection
) -> None:
    disp['psql_connect'] = psql_connect


async def setup_faststream(
    disp: Dispatcher,
    broker: NatsBroker
) -> None:
    await broker.connect()
    disp['broker'] = broker


async def setup_app(
    disp: Dispatcher,
    cache: CacheAdapter,
    config_: ConfigFactory,
    psql_connect: AsyncConnection,
    broker: NatsBroker
) -> None:
    setup_factory(disp, config_)
    await setup_faststream(disp, broker)
    setup_repository(disp, psql_connect)
    setup_connections(disp, psql_connect)
    setup_middleware(disp, psql_connect)
    await setup_adapters(disp, cache)
