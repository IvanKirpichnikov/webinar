from psycopg import AsyncConnection
from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

from webinar.application.config import ConfigFactory


async def setup() -> tuple[AsyncConnectionPool[AsyncConnection[DictRow]], ConfigFactory]:
    config_factory = ConfigFactory()
    config = config_factory.config
    
    psql_pool = AsyncConnectionPool(
        config.psql.url,
        open=True,
    )
    return psql_pool, config_factory
