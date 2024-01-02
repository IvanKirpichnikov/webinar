from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.infrastructure.database.dao.admin import AdminOtherCreateImpl
from webinar.infrastructure.database.dao.homework import (
    HomeWorkOtherCreateImpl,
)
from webinar.infrastructure.database.repository.uow import (
    UnitOfWorkRepositoryImpl,
)
from webinar.infrastructure.database.dao.user import UserOtherCreateImpl
from webinar.infrastructure.database.dao.webinar import WebinarOtherCreateImpl


async def create_other_database(connect: AsyncConnection[DictRow]) -> None:
    uow = UnitOfWorkRepositoryImpl(connect)
    other_create = [
        UserOtherCreateImpl(connect),
        WebinarOtherCreateImpl(connect),
        HomeWorkOtherCreateImpl(connect),
        AdminOtherCreateImpl(connect),
    ]
    try:
        for _ in other_create:
            await _.create_table()
            await _.create_index()
    except Exception as e:
        await uow.rollback()
        raise e
    else:
        await uow.commit()
