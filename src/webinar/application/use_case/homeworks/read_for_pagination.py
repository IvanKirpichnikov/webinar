from abc import abstractmethod
from typing import Protocol

from webinar.application.dto.homework import HomeWorkPaginationDTO
from webinar.application.interfaces.gateways.homework import HomeWorkGateway
from webinar.application.use_case.base import UseCase
from webinar.domain.models.homework import UserHomeWorks


class NoFoundHomeworksForPagination(Exception):
    pass


class ReadUserHomeworksForPagination(
    UseCase[HomeWorkPaginationDTO, UserHomeWorks], Protocol
):
    @abstractmethod
    async def __call__(self, data: HomeWorkPaginationDTO) -> UserHomeWorks:
        raise NotImplementedError


class ReadUserHomeworksForPaginationImpl(ReadUserHomeworksForPagination):
    def __init__(self, gateway: HomeWorkGateway) -> None:
        self._gateway = gateway
    
    async def __call__(self, data: HomeWorkPaginationDTO) -> UserHomeWorks:
        if data.letters_range:
            result = await self._gateway.read_from_letters_range(data)
        elif data.numbers_range:
            result = await self._gateway.read_from_numbers_range(data)
        else:
            raise ValueError(data)
        if result is None:
            raise NoFoundHomeworksForPagination(data)
        return result
