from abc import abstractmethod
from typing import Protocol

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


class AbstractHomeWorkDAO(Protocol):
    @abstractmethod
    async def create(self, model: CreateHomeWorkDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def read_all_by_telegram_user_id(
        self, model: TelegramUserIdDTO
    ) -> HomeWorkEntities:
        raise NotImplementedError

    @abstractmethod
    async def read_all_by_telegram_user_id_and_status_type(
        self, model: TelegramUserIdAndStatusTypeDTO
    ) -> HomeWorkEntities:
        raise NotImplementedError

    @abstractmethod
    async def update_type(self, model: UpdatingTypeByIdDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_type_and_comment(
        self, model: UpdatingTypeAndCommentByIdDTO
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def read_from_letters_range(
        self, model: HomeWorkPaginationDTO
    ) -> UserHomeWorkEntities:
        raise NotImplementedError

    @abstractmethod
    async def read_from_numbers_range(
        self, model: HomeWorkPaginationDTO
    ) -> UserHomeWorkEntities:
        raise NotImplementedError

    @abstractmethod
    async def read_from_offset(
        self, model: HomeWorkPaginationDTO
    ) -> UserHomeWorkEntities:
        raise NotImplementedError

    @abstractmethod
    async def read_homework_by_db_id_and_user_info(
        self, model: HomeWorkIdDTO
    ) -> HomeWorkAndUserInfoEntity:
        raise NotImplementedError

    @abstractmethod
    async def update_evaluation(
        self, model: UpdatingEvaluationByIdDTO
    ) -> None:
        raise NotImplementedError
