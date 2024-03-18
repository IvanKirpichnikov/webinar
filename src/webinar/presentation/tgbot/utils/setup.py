from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from dishka import AsyncContainer
from faststream.nats import NatsBroker
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

from webinar.config import ConfigFactory
from webinar.infrastructure.adapters.cache import CacheStore
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.middlewaring.container import ContainerMiddleware
from webinar.presentation.tgbot.middlewaring.is_super_admin import IsSuperAdminMiddlewareImpl


def setup_factory(disp: Dispatcher, config: ConfigFactory) -> None:
    disp["keyboard"] = KeyboardFactory()
    disp["config"] = config


async def setup_adapters(disp: Dispatcher, cache: CacheStore) -> None:
    disp["cache"] = cache


def setup_middleware(
    disp: Dispatcher,
    pool: AsyncConnectionPool[AsyncConnection[DictRow]],
    container: AsyncContainer
) -> None:
    is_admin_middleware = IsSuperAdminMiddlewareImpl()
    container_middleware = ContainerMiddleware(container)
    
    disp.update.outer_middleware(container_middleware)
    disp.update.middleware(is_admin_middleware)
    
    disp.error.outer_middleware(container_middleware)
    disp.error.middleware(is_admin_middleware)
    
    disp.callback_query.middleware(CallbackAnswerMiddleware())


def setup_connections(
    disp: Dispatcher, pool: AsyncConnectionPool[AsyncConnection[DictRow]]
) -> None:
    disp["psql_pool"] = pool


async def setup_faststream(disp: Dispatcher, broker: NatsBroker) -> None:
    await broker.connect()
    disp["broker"] = broker


async def setup_app(
    disp: Dispatcher,
    cache: CacheStore,
    config_: ConfigFactory,
    pool: AsyncConnectionPool[AsyncConnection[DictRow]],
    broker: NatsBroker,
    container: AsyncContainer,
) -> None:
    setup_factory(disp, config_)
    await setup_faststream(disp, broker)
    setup_connections(disp, pool)
    setup_middleware(disp, pool, container)
    await setup_adapters(disp, cache)
