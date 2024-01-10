from typing import (
    Any,
    Awaitable,
    Callable
)

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.infrastructure.database.repository.uow import UnitOfWorkRepositoryImpl


class UoWRepositoryMiddlewareImpl(BaseMiddleware):
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
        
        async with self.uow.transaction():
            try:
                await handler(event, data)
            except Exception as e:
                await self.uow.rollback()
                raise e
            else:
                await self.uow.commit()
