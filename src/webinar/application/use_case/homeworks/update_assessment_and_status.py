from abc import abstractmethod
from typing import Protocol

from webinar.application.dto.homework import UpdateHomeworkEvolutionAndStatusDTO
from webinar.application.interfaces.gateways.homework import HomeWorkGateway
from webinar.application.interfaces.uow import DBUoW
from webinar.application.use_case.base import UseCase


class UpdateHomeworkEvolutionAndStatus(
    UseCase[UpdateHomeworkEvolutionAndStatusDTO, None], Protocol
):
    @abstractmethod
    async def __call__(self, data: UpdateHomeworkEvolutionAndStatusDTO) -> None:
        raise NotImplementedError


class UpdateHomeworkEvolutionAndStatusImpl(UpdateHomeworkEvolutionAndStatus):
    def __init__(self, gateway: HomeWorkGateway, uow: DBUoW) -> None:
        self._uow = uow
        self._gateway = gateway
    
    async def __call__(self, data: UpdateHomeworkEvolutionAndStatusDTO) -> None:
        async with self._uow.transaction():
            await self._gateway.update_evolution_and_status(data)
