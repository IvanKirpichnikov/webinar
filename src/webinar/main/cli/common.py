from psycopg import AsyncConnection
from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

from webinar.config import ConfigFactory


async def setup() -> tuple[AsyncConnectionPool[AsyncConnection[DictRow]], ConfigFactory]:
    config_factory = ConfigFactory()
    config = config_factory.config
    
    psql_pool = AsyncConnectionPool(
        config.psql.url,
        open=True,
        connection_class=AsyncConnection[DictRow],
    )
    return psql_pool, config_factory
