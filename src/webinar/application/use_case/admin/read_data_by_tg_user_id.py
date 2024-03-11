from abc import abstractmethod
from typing import Protocol

from webinar.application.dto.common import TgUserIdDTO
from webinar.application.interfaces.gateways.admin import AdminGateway
from webinar.application.use_case.base import UseCase
from webinar.domain.models.admin import AdminDataInfo


class ReadAdminDataByTgUserId(UseCase[TgUserIdDTO, AdminDataInfo], Protocol):
    @abstractmethod
    async def __call__(self, data: TgUserIdDTO) -> AdminDataInfo:
        raise NotImplementedError


class ReadAdminDataByTgUserIdImpl(ReadAdminDataByTgUserId):
    def __init__(self, gateway: AdminGateway) -> None:
        self._gateway = gateway
    
    async def __call__(self, data: TgUserIdDTO) -> AdminDataInfo:
        result = await self._gateway.read_data_by_telegram_user_id(self._gateway)
        return result
