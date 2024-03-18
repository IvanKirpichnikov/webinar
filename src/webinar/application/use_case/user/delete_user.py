from logging import getLogger

from webinar.application.dto.common import EmailDTO
from webinar.application.exceptions import NotFoundUser
from webinar.application.interfaces.gateways.user import UserGateway
from webinar.application.interfaces.uow import DBUoW
from webinar.application.use_case.base import UseCase
from webinar.domain.types import TgUserId


class DeleteUserByEmail(UseCase[EmailDTO, TgUserId | None]):
    async def __call__(self, data: EmailDTO) -> TgUserId | None:
        raise NotImplementedError


class DeleteUserByEmailImpl(DeleteUserByEmail):
    logger = getLogger(__name__)
    
    def __init__(self, uow: DBUoW, gateway: UserGateway) -> None:
        self._uow = uow
        self._gateway = gateway
    
    async def __call__(self, data: EmailDTO) -> TgUserId | None:
        async with self._uow.transaction():
            user_exists = await self._gateway.exists_by_email(data)
            if not user_exists.result:
                raise NotFoundUser(data)
            result = await self._gateway.delete_by_email(data)
        if result is None:
            self.logger.info('Not found user for delete by email=%r' % data.email)
            return None
        self.logger.info('Delete user(tg_user_id=%r) by email=%r' % (result, data.email))
        return result
        
