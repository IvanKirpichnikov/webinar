from typing import (
    Any,
    Awaitable,
    Callable,
)

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject
from psycopg import AsyncConnection
from psycopg.rows import dict_row, DictRow

from webinar.infrastructure.database.repository.admin import AdminRepositoryImpl
from webinar.infrastructure.database.repository.homework import HomeWorkRepositoryImpl
from webinar.infrastructure.database.repository.stats import StatsRepositoryImpl
from webinar.infrastructure.database.repository.uow import UnitOfWorkRepositoryImpl
from webinar.infrastructure.database.repository.user import UserRepositoryImpl
from webinar.infrastructure.database.repository.webinar import WebinarRepositoryImpl


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
    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.uow = UnitOfWorkRepositoryImpl(connect)
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if get_flag(data, "repo_uow") is None:
            return await handler(event, data)
        
        async with data['pool'].connection() as conn:
            conn.row_factory = dict_row
            setup_repository(data, conn)
            try:
                await handler(event, data)
            except Exception as e:
                await self.uow.rollback()
                raise e
            else:
                await self.uow.commit()
