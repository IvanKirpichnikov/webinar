from psycopg import AsyncConnection

from src.application.interfaces.uow import AbstractUnitOfWork


class UnitOfWorkRepository(AbstractUnitOfWork):
    connect: AsyncConnection

    def __init__(self, connect: AsyncConnection) -> None:
        super().__init__()
        self.connect = connect
    
    async def commit(self) -> None:
        await self.connect.commit()
    
    async def rollback(self) -> None:
        await self.connect.rollback()
