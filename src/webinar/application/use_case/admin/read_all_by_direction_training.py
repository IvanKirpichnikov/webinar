from typing import Protocol

from webinar.application.dto.common import DirectionsTrainingDTO
from webinar.application.interfaces.gateways.admin import AdminGateway
from webinar.application.use_case.base import UseCase
from webinar.domain.models.admin import Admins


class NotFoundAdminsToTrainingDirection(Exception):
    pass


class ReadAllAdminByDirectionTraining(
    UseCase[DirectionsTrainingDTO, Admins], Protocol
):
    async def __call__(self, data: DirectionsTrainingDTO) -> Admins:
        raise NotImplementedError


class ReadAllAdminByDirectionTrainingImpl(ReadAllAdminByDirectionTraining):
    def __init__(self, gateway: AdminGateway) -> None:
        self._gateway = gateway
    
    async def __call__(self, data: DirectionsTrainingDTO) -> Admins:
        result = await self._gateway.read_all_by_direction_training(data)
        if result is None:
            raise NotFoundAdminsToTrainingDirection(data)
        return result
