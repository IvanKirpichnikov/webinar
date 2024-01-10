from contextlib import asynccontextmanager
from typing import (
    AsyncIterator
)

from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.application.interfaces.uow import AbstractUnitOfWork


class UnitOfWorkRepositoryImpl(AbstractUnitOfWork):
    connect: AsyncConnection[DictRow]
    
    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        super().__init__()
        self.connect = connect
    
    async def commit(self) -> None:
        await self.connect.commit()
    
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        with self.connect.transaction():
            yield None
    
    async def rollback(self) -> None:
        await self.connect.rollback()
