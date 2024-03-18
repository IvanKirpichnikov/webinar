from webinar.application.dto.common import ResultExistsDTO, TgUserIdDTO
from webinar.application.interfaces.gateways.admin import AdminGateway
from webinar.application.use_case.base import UseCase


class UserIsAdmin(UseCase[TgUserIdDTO, ResultExistsDTO]):
    async def __call__(self, data: TgUserIdDTO) -> ResultExistsDTO:
        raise NotImplementedError


class UserIsAdminImpl(UserIsAdmin):
    def __init__(self, gateway: AdminGateway) -> None:
        self._gateway = gateway
    
    async def __call__(self, data: TgUserIdDTO) -> ResultExistsDTO:
        result = await self._gateway.exists(data)
        return result
