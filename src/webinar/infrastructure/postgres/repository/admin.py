from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.application.exceptions import NotFoundAdmin
from webinar.application.dto.admin import CreateAdminDTO, GetAdminFromDirectionTraining
from webinar.application.dto.common import (
    DirectionsTrainingDTO,
    ResultExistsDTO,
    TgChatIdDTO,
    TgUserIdDTO,
)
from webinar.domain.models.admin import (
    AdminDataInfo,
    Admins,
    Admin,
)
from webinar.domain.types import TgChatId
from webinar.infrastructure.postgres.gateways.admin import PostgresAdminGateway
from webinar.infrastructure.postgres.repository.base import BaseRepository


class AdminRepositoryImpl(BaseRepository):
    connect: AsyncConnection[DictRow]

    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect

    async def create(self, model: CreateAdminDTO) -> None:
        dao = PostgresAdminGateway(self.connect)
        await dao.create(model)

    async def exists(self, model: TgUserIdDTO) -> ResultExistsDTO:
        dao = PostgresAdminGateway(self.connect)
        return await dao.exists(model)
    
    async def get_admin_by_letters_range_from_user_or_random(
        self,
        model: GetAdminFromDirectionTraining
    ) -> TgChatIdDTO:
        dao = PostgresAdminGateway(self.connect)
        try:
            return await dao.get_admin_by_letters_range_from_user(model)
        except NotFoundAdmin:
            data = await dao.read_random_by_direction_training(
                DirectionsTrainingDTO(
                    [model.direction_training]
                )
            )
            return TgChatIdDTO(
                TgChatId(
                    data.telegram_chat_id
                )
            )
    
    async def read_random(self) -> Admin:
        dao = PostgresAdminGateway(self.connect)
        return await dao.read_random()

    async def read_data_by_telegram_user_id(
        self, model: TgUserIdDTO
    ) -> AdminDataInfo:
        dao = PostgresAdminGateway(self.connect)
        return await dao.read_data_by_telegram_user_id(model)

    async def read_all_by_direction_training(
        self, model: DirectionsTrainingDTO
    ) -> Admins:
        dao = PostgresAdminGateway(self.connect)
        return await dao.read_all_by_direction_training(model)

    async def read_by_telegram_user_id(
        self, model: TgUserIdDTO
    ) -> AdminDataInfo:
        dao = PostgresAdminGateway(self.connect)
        return await dao.read_data_by_telegram_user_id(model)
