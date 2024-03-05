from psycopg import AsyncConnection
from psycopg.rows import DictRow


class PostgresGateway:
    connect: AsyncConnection[DictRow]
    
    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect


class BaseOtherCreate(PostgresGateway):
    async def create_table(self) -> None:
        raise NotImplementedError
    
    async def create_index(self) -> None:
        raise NotImplementedError
