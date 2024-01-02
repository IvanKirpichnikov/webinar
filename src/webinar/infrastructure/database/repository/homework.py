from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.application.schemas.dto.common import TelegramUserIdDTO
from webinar.application.schemas.dto.homework import (
    CreateHomeWorkDTO,
    HomeWorkIdDTO,
    HomeWorkPaginationDTO,
    TelegramUserIdAndStatusTypeDTO,
    UpdatingEvaluationByIdDTO,
    UpdatingTypeAndCommentByIdDTO,
    UpdatingTypeByIdDTO,
)
from webinar.application.schemas.entities.homework import (
    HomeWorkAndUserInfoEntity,
    HomeWorkEntities,
    UserHomeWorkEntities,
)
from webinar.infrastructure.database.dao.homework import HomeWorkDAOImpl
from webinar.infrastructure.database.repository.base import BaseRepository


class HomeWorkRepositoryImpl(BaseRepository):
    connect: AsyncConnection[DictRow]

    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect

    def dao(self) -> HomeWorkDAOImpl:
        return HomeWorkDAOImpl(self.connect)

    async def create(self, model: CreateHomeWorkDTO) -> None:
        dao = self.dao()
        await dao.create(model)

    async def read_all_by_telegram_user_id(
        self, model: TelegramUserIdDTO
    ) -> HomeWorkEntities:
        dao = self.dao()
        return await dao.read_all_by_telegram_user_id(model)

    async def read_all_by_telegram_user_id_and_status_type(
        self, model: TelegramUserIdAndStatusTypeDTO
    ) -> HomeWorkEntities:
        dao = self.dao()
        return await dao.read_all_by_telegram_user_id_and_status_type(model)

    async def update_type(self, model: UpdatingTypeByIdDTO) -> None:
        dao = self.dao()
        return await dao.update_type(model)

    async def update_type_and_comment(
        self, model: UpdatingTypeAndCommentByIdDTO
    ) -> None:
        dao = self.dao()
        return await dao.update_type_and_comment(model)

    async def update_evaluation(
        self, model: UpdatingEvaluationByIdDTO
    ) -> None:
        dao = self.dao()
        return await dao.update_evaluation(model)

    async def read_homework_by_db_id_and_user_info(
        self, model: HomeWorkIdDTO
    ) -> HomeWorkAndUserInfoEntity:
        dao = self.dao()
        return await dao.read_homework_by_db_id_and_user_info(model)

    async def read_pagination(
        self, model: HomeWorkPaginationDTO
    ) -> UserHomeWorkEntities:
        dao = self.dao()
        method = dao.read_from_offset
        if model.letters_range:
            method = dao.read_from_letters_range
        elif model.numbers_range:
            method = dao.read_from_numbers_range
        return await method(model)
