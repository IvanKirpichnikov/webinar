from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject
from psycopg import AsyncConnection

from src.infrastructure.repositories.uow import UnitOfWorkRepository


class UoWRepositoryMiddlewareImpl(BaseMiddleware):
    def __init__(self, connect: AsyncConnection) -> None:
        self.uow = UnitOfWorkRepository(connect)
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        flag = get_flag(data, 'repo_uow')
        if flag is None:
            return await handler(event, data)
        try:
            await handler(event, data)
        except Exception as e:
            await self.uow.rollback()
            raise e
        else:
            await self.uow.commit()
