from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from faststream.nats import NatsBroker
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

from webinar.application.config import ConfigFactory
from webinar.infrastructure.adapters.cache import CacheStore
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.middlewaring.is_super_admin import IsSuperAdminMiddlewareImpl
from webinar.presentation.tgbot.middlewaring.uow import RepositoryMiddlewareImpl


def setup_factory(disp: Dispatcher, config: ConfigFactory) -> None:
    disp["keyboard"] = KeyboardFactory()
    disp["config"] = config


async def setup_adapters(disp: Dispatcher, cache: CacheStore) -> None:
    disp["cache"] = cache


def setup_middleware(
    disp: Dispatcher, connect: AsyncConnection[DictRow]
) -> None:
    uow_middleware = RepositoryMiddlewareImpl(connect)
    is_admin_middleware = IsSuperAdminMiddlewareImpl()
    disp.update.middleware(is_admin_middleware)
    disp.message.middleware(uow_middleware)
    disp.callback_query.middleware(uow_middleware)
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
) -> None:
    setup_factory(disp, config_)
    await setup_faststream(disp, broker)
    setup_connections(disp, pool)
    setup_middleware(disp, psql_connect)
    await setup_adapters(disp, cache)
