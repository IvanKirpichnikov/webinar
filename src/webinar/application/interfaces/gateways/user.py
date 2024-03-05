from abc import abstractmethod
from typing import Protocol, TYPE_CHECKING

from webinar.application.dto.common import (
    DirectionsTrainingDTO,
    ResultExistsDTO,
    TgUserIdDTO,
)
from webinar.domain.models.user import User, Users


if TYPE_CHECKING:
    from webinar.application.use_case.user.add_user import AddUserDTO


class UserGateway(Protocol):
    @abstractmethod
    async def read_by_tg_user_id(
        self, model: TgUserIdDTO
    ) -> User | None:
        raise NotImplementedError
    
    @abstractmethod
    async def create(self, model: 'AddUserDTO') -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def exists(self, model: TgUserIdDTO) -> ResultExistsDTO:
        raise NotImplementedError
    
    @abstractmethod
    async def read_all_by_direction_training(
        self, model: DirectionsTrainingDTO
    ) -> Users:
        raise NotImplementedError
