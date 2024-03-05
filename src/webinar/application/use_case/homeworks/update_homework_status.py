from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from webinar.application.interfaces.gateways.homework import HomeWorkGateway
from webinar.application.interfaces.uow import DBUoW
from webinar.application.use_case.base import UseCase
from webinar.domain.enums.homework import HomeWorkStatusType
from webinar.domain.types import DataBaseId


@dataclass(frozen=True, slots=True)
class UpdateHomeWorkStatusDTO:
    db_id: DataBaseId
    status_type: HomeWorkStatusType


class UpdateHomeWorkStatus(UseCase[UpdateHomeWorkStatusDTO, None], Protocol):
    @abstractmethod
    async def __call__(self, data: UpdateHomeWorkStatusDTO) -> None:
        raise NotImplementedError


class UpdateHomeWorkStatusImpl(UpdateHomeWorkStatus):
    _db_uow: DBUoW
    _homework_gateway: HomeWorkGateway
    
    def __init__(
        self,
        db_uow: DBUoW,
        homework_gateway: HomeWorkGateway,
    ) -> None:
        self._db_uow = db_uow
        self._homework_gateway = homework_gateway
    
    async def __call__(self, data: UpdateHomeWorkStatusDTO) -> None:
        async with self._db_uow.transaction():
            await self._homework_gateway.update_status(data)
