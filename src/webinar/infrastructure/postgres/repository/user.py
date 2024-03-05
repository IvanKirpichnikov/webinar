from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.application.dto.common import (
    DirectionsTrainingDTO,
    DirectionTrainingDTO,
    ResultExistsDTO,
    TgUserIdDTO,
)
from webinar.application.dto.user import (
    AddUserDTO,
    UpdateUserDataGoogleSheetsDto,
)
from webinar.domain.models.user import (
    Users,
    User
)
from webinar.infrastructure.postgres.gateways.user import PostgresUserGateway
from webinar.infrastructure.postgres.repository.base import BaseRepository


class UserRepositoryImpl(BaseRepository):
    connect: AsyncConnection[DictRow]
    
    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect
    
    async def create(self, model: AddUserDTO) -> None:
        dao = PostgresUserGateway(self.connect)
        await dao.create(model)
    
    async def exists(self, model: TgUserIdDTO) -> ResultExistsDTO:
        dao = PostgresUserGateway(self.connect)
        return await dao.exists(model)
    
    async def read_by_telegram_user_id(
        self, model: TgUserIdDTO
    ) -> User:
        dao = PostgresUserGateway(self.connect)
        return await dao.read_by_telegram_user_id(model)
    
    async def read_all_by_direction_training(
        self, model: DirectionsTrainingDTO
    ) -> Users:
        dao = PostgresUserGateway(self.connect)
        return await dao.read_all_by_direction_training(model)
    
    async def read_user_and_he_homeworks(
        self, model: DirectionTrainingDTO
    ) -> list[UpdateUserDataGoogleSheetsDto]:
        dao = PostgresUserGateway(self.connect)
        return await dao.read_user_and_he_homeworks(model)
