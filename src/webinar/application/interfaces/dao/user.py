from abc import abstractmethod
from typing import Protocol

from webinar.application.schemas.dto.common import (
    DirectionsTrainingDTO,
    ResultExistsDTO,
    TelegramUserIdDTO,
)
from webinar.application.schemas.dto.user import CreateUserDTO
from webinar.application.schemas.entities.user import UserEntities


class AbstractUserDAO(Protocol):
    @abstractmethod
    async def create(self, model: CreateUserDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, model: TelegramUserIdDTO) -> ResultExistsDTO:
        raise NotImplementedError

    @abstractmethod
    async def read_all_by_direction_training(
        self, model: DirectionsTrainingDTO
    ) -> UserEntities:
        raise NotImplementedError
