from psycopg import AsyncConnection
from psycopg.rows import (
    dict_row,
    DictRow
)

from webinar.application.config import ConfigFactory


async def setup() -> tuple[AsyncConnection[DictRow], ConfigFactory]:
    config_factory = ConfigFactory()
    config = config_factory.config
    
    psql_connect = await AsyncConnection.connect(
        config.psql.url,
        row_factory=dict_row
    )
    return psql_connect, config_factory
