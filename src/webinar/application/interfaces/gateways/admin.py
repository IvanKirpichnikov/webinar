from abc import abstractmethod
from typing import Protocol

from webinar.application.dto.admin import CreateAdminDTO, ReadAdminByLettersRangeData
from webinar.application.dto.common import (
    DirectionsTrainingDTO,
    ResultExistsDTO,
    TgChatIdDTO,
    TgUserIdDTO,
)
from webinar.domain.models.admin import (Admin, AdminDataInfo, Admins)


class AdminGateway(Protocol):
    @abstractmethod
    async def create(self, model: CreateAdminDTO) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    async def exists(self, model: TgUserIdDTO) -> ResultExistsDTO:
        raise NotImplementedError
    
    @abstractmethod
    async def read_by_telegram_user_id(
        self, model: TgUserIdDTO
    ) -> Admin:
        raise NotImplementedError
    
    @abstractmethod
    async def read_all_by_direction_training(
        self, model: DirectionsTrainingDTO
    ) -> Admins | None:
        raise NotImplementedError
    
    @abstractmethod
    async def read_data_by_telegram_user_id(
        self, model: TgUserIdDTO
    ) -> AdminDataInfo:
        raise NotImplementedError
    
    @abstractmethod
    async def read_random_by_direction_training(
        self, model: DirectionsTrainingDTO
    ) -> TgChatIdDTO | None:
        raise NotImplementedError
    
    @abstractmethod
    async def read_by_letters_range(
        self,
        model: ReadAdminByLettersRangeData
    ) -> TgChatIdDTO | None:
        raise NotImplementedError
