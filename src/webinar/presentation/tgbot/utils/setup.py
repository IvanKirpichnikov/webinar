from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from faststream.nats import NatsBroker
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.application.config import ConfigFactory
from webinar.infrastructure.adapters.cache import CacheStore
from webinar.infrastructure.database.repository.admin import (
    AdminRepositoryImpl,
)
from webinar.infrastructure.database.repository.homework import (
    HomeWorkRepositoryImpl,
)
from webinar.infrastructure.database.repository.stats import (
    StatsRepositoryImpl,
)
from webinar.infrastructure.database.repository.user import UserRepositoryImpl
from webinar.infrastructure.database.repository.webinar import (
    WebinarRepositoryImpl,
)
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.middlewaring.is_super_admin import (
    IsSuperAdminMiddlewareImpl,
)
from webinar.presentation.tgbot.middlewaring.uow import (
    UoWRepositoryMiddlewareImpl,
)


def setup_repository(
    disp: Dispatcher, connect: AsyncConnection[DictRow]
) -> None:
    repos = [
        ("user", UserRepositoryImpl),
        ("webinar", WebinarRepositoryImpl),
        ("homework", HomeWorkRepositoryImpl),
        ("admin", AdminRepositoryImpl),
        ("stats", StatsRepositoryImpl),
    ]
    for raw_key, repo in repos:
        key = raw_key + "_repository"
        disp[key] = repo(connect)


def setup_factory(disp: Dispatcher, config: ConfigFactory) -> None:
    disp["keyboard"] = KeyboardFactory()
    disp["config"] = config


async def setup_adapters(disp: Dispatcher, cache: CacheStore) -> None:
    disp["cache"] = cache


def setup_middleware(
    disp: Dispatcher, connect: AsyncConnection[DictRow]
) -> None:
    uow_middleware = UoWRepositoryMiddlewareImpl(connect)
    is_admin_middleware = IsSuperAdminMiddlewareImpl()
    disp.update.middleware(is_admin_middleware)
    disp.message.middleware(uow_middleware)
    disp.callback_query.middleware(uow_middleware)
    disp.callback_query.middleware(CallbackAnswerMiddleware())


def setup_connections(
    disp: Dispatcher, psql_connect: AsyncConnection[DictRow]
) -> None:
    disp["psql_connect"] = psql_connect


async def setup_faststream(disp: Dispatcher, broker: NatsBroker) -> None:
    await broker.connect()
    disp["broker"] = broker


async def setup_app(
    disp: Dispatcher,
    cache: CacheStore,
    config_: ConfigFactory,
    psql_connect: AsyncConnection[DictRow],
    broker: NatsBroker,
) -> None:
    setup_factory(disp, config_)
    await setup_faststream(disp, broker)
    setup_repository(disp, psql_connect)
    setup_connections(disp, psql_connect)
    setup_middleware(disp, psql_connect)
    await setup_adapters(disp, cache)
