from abc import abstractmethod
from typing import Protocol

from webinar.application.dto.common import TgUserIdDTO
from webinar.application.interfaces.gateways.user import UserGateway
from webinar.application.use_case.base import UseCase
from webinar.domain.models.user import User


class NotFoundUser(Exception):
    pass


class ReadUserData(UseCase[TgUserIdDTO, User], Protocol):
    @abstractmethod
    async def __call__(self, data: TgUserIdDTO) -> User:
        raise NotImplementedError


class ReadUserDataImpl(ReadUserData):
    _user_gateway: UserGateway
    
    def __init__(
        self,
        user_gateway: UserGateway
    ) -> None:
        self._user_gateway = user_gateway
    
    async def __call__(self, data: TgUserIdDTO) -> User:
        result = await self._user_gateway.read_by_tg_user_id(data)
        if result is None:
            raise NotFoundUser(data)
        return result
