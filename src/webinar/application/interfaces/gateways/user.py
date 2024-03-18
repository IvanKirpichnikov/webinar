from abc import abstractmethod
from typing import Mapping, Protocol, TYPE_CHECKING

from webinar.application.dto.common import (
    DirectionsTrainingDTO,
    DirectionTrainingDTO, EmailDTO, ResultExistsDTO,
    TgUserIdDTO,
)
from webinar.application.dto.user import UpdateUserDataGoogleSheetsDto
from webinar.domain.models.user import User, Users
from webinar.domain.types import TgUserId


if TYPE_CHECKING:
    from webinar.application.use_case.user.add_user import AddUserDTO


class UserGateway(Protocol):
    @abstractmethod
    async def delete_by_email(self, model: EmailDTO) -> TgUserId | None:
        raise NotImplementedError
    
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
    async def exists_by_email(self, model: EmailDTO) -> ResultExistsDTO:
        raise NotImplementedError
    
    @abstractmethod
    async def read_user_and_he_homeworks(
        self, model: DirectionTrainingDTO
    ) -> list[UpdateUserDataGoogleSheetsDto]:
        raise NotImplementedError
    
    @abstractmethod
    async def read_stats(self) -> Mapping[str, int]:
        raise NotImplementedError
    
    @abstractmethod
    async def read_all_by_direction_training(
        self, model: DirectionsTrainingDTO
    ) -> Users:
        raise NotImplementedError
