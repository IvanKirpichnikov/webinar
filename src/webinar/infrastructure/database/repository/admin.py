from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.application.schemas.dto.admin import CreateAdminDTO
from webinar.application.schemas.dto.common import (
    DirectionsTrainingDTO,
    ResultExistsDTO,
    TelegramUserIdDTO,
)
from webinar.application.schemas.entities.admin import (
    AdminDataInfoEntity,
    AdminEntities,
    AdminEntity,
)
from webinar.infrastructure.database.dao.admin import AdminDAOImpl
from webinar.infrastructure.database.repository.base import BaseRepository


class AdminRepositoryImpl(BaseRepository):
    connect: AsyncConnection[DictRow]

    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect

    async def create(self, model: CreateAdminDTO) -> None:
        dao = AdminDAOImpl(self.connect)
        await dao.create(model)

    async def exists(self, model: TelegramUserIdDTO) -> ResultExistsDTO:
        dao = AdminDAOImpl(self.connect)
        return await dao.exists(model)

    async def read_random(self) -> AdminEntity:
        dao = AdminDAOImpl(self.connect)
        return await dao.read_random()

    async def read_data_by_telegram_user_id(
        self, model: TelegramUserIdDTO
    ) -> AdminDataInfoEntity:
        dao = AdminDAOImpl(self.connect)
        return await dao.read_data_by_telegram_user_id(model)

    async def read_all_by_direction_training(
        self, model: DirectionsTrainingDTO
    ) -> AdminEntities:
        dao = AdminDAOImpl(self.connect)
        return await dao.read_all_by_direction_training(model)

    async def read_by_telegram_user_id(
        self, model: TelegramUserIdDTO
    ) -> AdminDataInfoEntity:
        dao = AdminDAOImpl(self.connect)
        return await dao.read_data_by_telegram_user_id(model)
