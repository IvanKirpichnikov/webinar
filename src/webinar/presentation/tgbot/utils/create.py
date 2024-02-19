from psycopg import AsyncConnection
from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

from webinar.infrastructure.database.dao.admin import AdminOtherCreateImpl
from webinar.infrastructure.database.dao.homework import HomeWorkOtherCreateImpl
from webinar.infrastructure.database.dao.user import UserOtherCreateImpl
from webinar.infrastructure.database.dao.webinar import WebinarOtherCreateImpl
from webinar.infrastructure.database.repository.uow import UnitOfWorkRepositoryImpl


async def create_other_database(pool: AsyncConnectionPool[AsyncConnection[DictRow]]) -> None:
    async with pool.connection() as connect:
        uow = UnitOfWorkRepositoryImpl(connect)
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
