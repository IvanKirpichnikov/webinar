from typing import AsyncIterator

from dishka import provide, Provider, Scope
from psycopg import AsyncConnection
from psycopg.rows import dict_row, DictRow
from psycopg_pool import AsyncConnectionPool

from webinar.application.interfaces.gateways.admin import AdminGateway
from webinar.application.interfaces.gateways.homework import HomeWorkGateway
from webinar.application.interfaces.gateways.user import UserGateway
from webinar.application.interfaces.gateways.webinar import WebinarGateway
from webinar.application.interfaces.uow import DBUoW
from webinar.config import Config
from webinar.infrastructure.postgres.gateways.admin import PostgresAdminGateway
from webinar.infrastructure.postgres.gateways.homework import PostgresHomeWorkGateway
from webinar.infrastructure.postgres.gateways.user import PostgresUserGateway
from webinar.infrastructure.postgres.gateways.webinar import PostgresWebinarGateway
from webinar.infrastructure.postgres.uow import PostgresUoWImpl


class GatewayProvider(Provider):
    scope = Scope.REQUEST
    
    @provide(scope=Scope.APP)
    async def psql_pool(
        self, config: Config
    ) -> AsyncIterator[AsyncConnectionPool[AsyncConnection[DictRow]]]:
        conn = AsyncConnectionPool(
            conninfo=config.psql.url,
            max_size=1000,
            connection_class=AsyncConnection[DictRow]
        )
        await conn.wait()
        yield conn
        await conn.close()
    
    @provide
    async def connect(
        self, pool: AsyncConnectionPool[AsyncConnection[DictRow]]
    ) -> AsyncIterator[AsyncConnection[DictRow]]:
        async with pool.connection() as conn:
            conn.row_factory = dict_row
            yield conn
    
    db_uow = provide(
        PostgresUoWImpl,
        provides=DBUoW
    )
    
    user = provide(
        source=PostgresUserGateway,
        provides=UserGateway,
    )
    admin = provide(
        source=PostgresAdminGateway,
        provides=AdminGateway,
    )
    homework = provide(
        source=PostgresHomeWorkGateway,
        provides=HomeWorkGateway,
    )
    webinar = provide(
        source=PostgresWebinarGateway,
        provides=WebinarGateway,
    )
