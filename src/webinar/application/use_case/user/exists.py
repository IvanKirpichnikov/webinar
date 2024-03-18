from logging import getLogger

from webinar.application.dto.common import ResultExistsDTO, TgUserIdDTO
from webinar.application.interfaces.gateways.user import UserGateway
from webinar.application.use_case.base import UseCase


class UserIsExists(UseCase[TgUserIdDTO, ResultExistsDTO]):
    async def __call__(self, data: TgUserIdDTO) -> ResultExistsDTO:
        raise NotImplementedError


class UserIsExistsImpl(UserIsExists):
    logger = getLogger(__name__)
    
    def __init__(self, gateway: UserGateway) -> None:
        self._gateway = gateway
    
    async def __call__(self, data: TgUserIdDTO) -> ResultExistsDTO:
        result = await self._gateway.exists(data)
        self.logger.info(
            'User tg_id=%r exists=%r'
            % (data.telegram_user_id, result.result)
        )
        return result
