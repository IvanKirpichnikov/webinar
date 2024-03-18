from contextlib import asynccontextmanager
from logging import getLogger
from typing import (
    AsyncIterator
)

from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.application.interfaces.uow import DBUoW


class PostgresUoWImpl(DBUoW):
    logger = getLogger(__name__)
    connect: AsyncConnection[DictRow]
    
    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        super().__init__()
        self.connect = connect
    
    async def commit(self) -> None:
        self.logger.debug('Callable commit')
        await self.connect.commit()
    
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:  # type: ignore
        self.logger.debug('Open transaction')
        async with self.connect.transaction():
            yield None
    
    async def rollback(self) -> None:
        self.logger.debug('Callable rollback')
        await self.connect.rollback()
