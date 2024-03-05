from abc import abstractmethod
from typing import Protocol

from webinar.application.dto.common import DirectionsTrainingDTO, TgChatIdDTO
from webinar.application.interactions.base import Interactor
from webinar.application.interfaces.gateways.admin import AdminGateway


class ReadRandomAdmin(
    Interactor[DirectionsTrainingDTO, TgChatIdDTO | None],
    Protocol
):
    @abstractmethod
    async def __call__(
        self, data: DirectionsTrainingDTO
    ) -> TgChatIdDTO | None:
        raise NotImplementedError


class ReadRandomAdminImpl(ReadRandomAdmin):
    _admin_gateway: AdminGateway
    
    def __init__(
        self,
        admin_gateway: AdminGateway
    ) -> None:
        self._admin_gateway = admin_gateway
    
    async def __call__(
        self, data: DirectionsTrainingDTO
    ) -> TgChatIdDTO | None:
        result = await self._admin_gateway.read_random_by_direction_training(data)
        return result
