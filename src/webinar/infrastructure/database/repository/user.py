from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.application.schemas.dto.common import (
    DirectionsTrainingDTO,
    DirectionTrainingDTO,
    ResultExistsDTO,
    TelegramUserIdDTO,
)
from webinar.application.schemas.dto.user import (
    CreateUserDTO,
    UpdateUserDataGoogleSheetsDto,
)
from webinar.application.schemas.entities.user import (
    UserEntities,
    UserEntity
)
from webinar.infrastructure.database.dao.user import UserDAOImpl
from webinar.infrastructure.database.repository.base import BaseRepository


class UserRepositoryImpl(BaseRepository):
    connect: AsyncConnection[DictRow]
    
    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect
    
    async def create(self, model: CreateUserDTO) -> None:
        dao = UserDAOImpl(self.connect)
        await dao.create(model)
    
    async def exists(self, model: TelegramUserIdDTO) -> ResultExistsDTO:
        dao = UserDAOImpl(self.connect)
        return await dao.exists(model)
    
    async def read_by_telegram_user_id(
        self, model: TelegramUserIdDTO
    ) -> UserEntity:
        dao = UserDAOImpl(self.connect)
        return await dao.read_by_telegram_user_id(model)
    
    async def read_all_by_direction_training(
        self, model: DirectionsTrainingDTO
    ) -> UserEntities:
        dao = UserDAOImpl(self.connect)
        return await dao.read_all_by_direction_training(model)
    
    async def read_user_and_he_homeworks(
        self, model: DirectionTrainingDTO
    ) -> list[UpdateUserDataGoogleSheetsDto]:
        dao = UserDAOImpl(self.connect)
        return await dao.read_user_and_he_homeworks(model)
