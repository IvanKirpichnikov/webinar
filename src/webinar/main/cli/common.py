from dishka import AsyncContainer, make_async_container
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

from webinar.config import ConfigFactory
from webinar.main.di.providers.config import ConfigProvider
from webinar.main.di.providers.gateway import GatewayProvider
from webinar.main.di.providers.interactions import InteractionsProvider
from webinar.main.di.providers.other import OtherProvider
from webinar.main.di.providers.use_case import UseCaseProvider


async def setup() -> tuple[
    AsyncConnectionPool[AsyncConnection[DictRow]], ConfigFactory, AsyncContainer
]:
    config_factory = ConfigFactory()
    config = config_factory.config
    
    psql_pool = AsyncConnectionPool(
        config.psql.url,
        open=True,
        connection_class=AsyncConnection[DictRow],
    )
    container = make_async_container(
        ConfigProvider(),
        GatewayProvider(),
        InteractionsProvider(),
        OtherProvider(),
        UseCaseProvider(),
    )
    return psql_pool, config_factory, container
