from psycopg import AsyncConnection
from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

from webinar.infrastructure.postgres.dao.admin import AdminOtherCreateImpl
from webinar.infrastructure.postgres.dao.homework import HomeWorkOtherCreateImpl
from webinar.infrastructure.postgres.dao.user import UserOtherCreateImpl
from webinar.infrastructure.postgres.dao.webinar import WebinarOtherCreateImpl
from webinar.infrastructure.postgres.uow import PostgresUoWImpl


async def create_other_database(pool: AsyncConnectionPool[AsyncConnection[DictRow]]) -> None:
    async with pool.connection() as connect:
        uow = PostgresUoWImpl(connect)
        other_create = [
            UserOtherCreateImpl(connect),
            WebinarOtherCreateImpl(connect),
            HomeWorkOtherCreateImpl(connect),
            AdminOtherCreateImpl(connect),
        ]
        try:
            for obj in other_create:
                await obj.create_table()
                await obj.create_index()
        except Exception as e:
            await uow.rollback()
            raise e
        else:
            await uow.commit()
