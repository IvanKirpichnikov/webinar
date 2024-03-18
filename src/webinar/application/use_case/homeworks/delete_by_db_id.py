from logging import getLogger

from webinar.application.dto.common import DbIdDTO
from webinar.application.interfaces.gateways.homework import HomeWorkGateway
from webinar.application.interfaces.uow import DBUoW
from webinar.application.use_case.base import UseCase


class DeleteHomeworkByDbId(UseCase[DbIdDTO, None]):
    async def __call__(self, data: DbIdDTO) -> None:
        raise NotImplementedError


class DeleteHomeworkByDbIdImpl(DeleteHomeworkByDbId):
    logger = getLogger(__name__)
    
    def __init__(self, uow: DBUoW, gateway: HomeWorkGateway) -> None:
        self._uow = uow
        self._gateway = gateway
    
    async def __call__(self, data: DbIdDTO) -> None:
        async with self._uow.transaction():
            await self._gateway.delete_by_db_id(data)
        self.logger.info('Delete homework by db_id=%r', data.db_id)
