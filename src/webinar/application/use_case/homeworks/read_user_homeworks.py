from abc import abstractmethod
from typing import Protocol

from webinar.application.dto.common import TgUserIdDTO
from webinar.application.interfaces.gateways.homework import HomeWorkGateway
from webinar.application.use_case.base import UseCase
from webinar.domain.models.homework import HomeWorks


class ReadUserHomeWorks(UseCase[TgUserIdDTO, HomeWorks], Protocol):
    @abstractmethod
    async def __call__(self, data: TgUserIdDTO) -> HomeWorks:
        raise NotImplementedError


class ReadUserHomeworkError(Exception):
    pass


class ReadUserHomeWorksImpl(ReadUserHomeWorks):
    _homework_gateway: HomeWorkGateway
    
    def __init__(self, homework_gateway: HomeWorkGateway) -> None:
        self._homework_gateway = homework_gateway
    
    async def __call__(self, data: TgUserIdDTO) -> HomeWorks:
        result = await self._homework_gateway.read_all_by_telegram_user_id(data)
        if result is None:
            raise ReadUserHomeworkError
        return result
