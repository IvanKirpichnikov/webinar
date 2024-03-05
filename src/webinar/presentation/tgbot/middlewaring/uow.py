from typing import (
    Any,
    Awaitable,
    Callable,
)

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from psycopg import AsyncConnection
from psycopg.rows import dict_row, DictRow
from psycopg_pool import AsyncConnectionPool

from webinar.infrastructure.postgres.repository.admin import AdminRepositoryImpl
from webinar.infrastructure.postgres.repository.homework import HomeWorkRepositoryImpl
from webinar.infrastructure.postgres.repository.stats import StatsRepositoryImpl
from webinar.infrastructure.postgres.uow import PostgresUoWImpl
from webinar.infrastructure.postgres.repository.user import UserRepositoryImpl
from webinar.infrastructure.postgres.repository.webinar import WebinarRepositoryImpl


def setup_repository(
    data, connect: AsyncConnection[DictRow]
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
        data[key] = repo(connect)


class RepositoryMiddlewareImpl(BaseMiddleware):
    def __init__(self, pool: AsyncConnectionPool[AsyncConnection[DictRow]]) -> None:
        self.pool = pool
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with self.pool.connection() as conn:
            async with PostgresUoWImpl(conn).transaction():
                conn.row_factory = dict_row
                setup_repository(data, conn)
                await handler(event, data)
