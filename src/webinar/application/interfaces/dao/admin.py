from abc import abstractmethod
from typing import Protocol

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


class AbstractAdminDAO(Protocol):
    @abstractmethod
    async def create(self, model: CreateAdminDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, model: TelegramUserIdDTO) -> ResultExistsDTO:
        raise NotImplementedError

    @abstractmethod
    async def read_by_telegram_user_id(
        self, model: TelegramUserIdDTO
    ) -> AdminEntity:
        raise NotImplementedError

    @abstractmethod
    async def read_all_by_direction_training(
        self, model: DirectionsTrainingDTO
    ) -> AdminEntities:
        raise NotImplementedError

    @abstractmethod
    async def read_data_by_telegram_user_id(
        self, model: TelegramUserIdDTO
    ) -> AdminDataInfoEntity:
        raise NotImplementedError

    @abstractmethod
    async def read_random_by_direction_training(self, model: DirectionsTrainingDTO) -> AdminEntity:
        raise NotImplementedError
