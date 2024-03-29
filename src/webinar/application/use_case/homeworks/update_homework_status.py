from abc import abstractmethod
from logging import getLogger
from typing import Protocol

from webinar.application.dto.homework import UpdateHomeWorkStatusDTO
from webinar.application.interfaces.gateways.homework import HomeWorkGateway
from webinar.application.interfaces.uow import DBUoW
from webinar.application.use_case.base import UseCase


class UpdateHomeWorkStatus(UseCase[UpdateHomeWorkStatusDTO, None], Protocol):
    @abstractmethod
    async def __call__(self, data: UpdateHomeWorkStatusDTO) -> None:
        raise NotImplementedError


class UpdateHomeWorkStatusImpl(UpdateHomeWorkStatus):
    logger = getLogger(__name__)
    
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
        self.logger.info(
            'Update homework db_id=%r status=%r'
            % (data.db_id, data.status_type)
        )
