from psycopg import AsyncConnection

from src.infrastructure.repositories.admin import AdminOtherCreateImpl
from src.infrastructure.repositories.homework import HomeWorkOtherCreateImpl
from src.infrastructure.repositories.uow import UnitOfWorkRepository
from src.infrastructure.repositories.user import UserOtherCreate
from src.infrastructure.repositories.webinar import WebinarOtherCreate


async def create_other_database(connect: AsyncConnection) -> None:
    uow = UnitOfWorkRepository(connect)
    other_create = [
        UserOtherCreate(connect),
        WebinarOtherCreate(connect),
        HomeWorkOtherCreateImpl(connect),
        AdminOtherCreateImpl(connect)
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
