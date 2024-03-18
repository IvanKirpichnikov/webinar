from logging import getLogger
from typing import Protocol

from webinar.application.dto.admin import CreateAdminDTO
from webinar.application.exceptions import AdminCreated
from webinar.application.interfaces.gateways.admin import AdminGateway
from webinar.application.interfaces.uow import DBUoW
from webinar.application.use_case.base import UseCase


class CreateAdmin(UseCase[CreateAdminDTO, None], Protocol):
    async def __call__(self, data: CreateAdminDTO) -> None:
        raise NotImplementedError


class CreateAdminImpl(CreateAdmin):
    logger = getLogger(__name__)
    
    def __init__(self, gateway: AdminGateway, uow: DBUoW) -> None:
        self._uow = uow
        self._gateway = gateway
    
    async def __call__(self, data: CreateAdminDTO) -> None:
        async with self._uow.transaction():
            result = await self._gateway.create(data)
        if result:
            self.logger.info(
                'Created admin. %r' % data
            )
            return None
        self.logger.warning(
            'Not created admin. %r' % data
        )
        raise AdminCreated(data)
