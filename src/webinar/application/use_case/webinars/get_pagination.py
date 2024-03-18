from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from webinar.application.interfaces.gateways.webinar import WebinarGateway
from webinar.application.use_case.base import UseCase
from webinar.domain.models.webinar import Webinars


class NotFoundWebinars(Exception):
    pass


@dataclass(frozen=True, slots=True)
class GetPaginationWebinarsData:
    limit: int
    offset: int


class GetPaginationWebinars(UseCase[GetPaginationWebinarsData, Webinars], Protocol):
    @abstractmethod
    async def __call__(
        self, data: GetPaginationWebinarsData
    ) -> Webinars:
        raise NotImplementedError


class GetPaginationWebinarsImpl(GetPaginationWebinars):
    _webinar_gateway: WebinarGateway
    
    def __init__(
        self,
        webinar_gateway: WebinarGateway
    ) -> None:
        self._webinar_gateway = webinar_gateway
    
    async def __call__(
        self, data: GetPaginationWebinarsData
    ) -> Webinars:
        result = await self._webinar_gateway.pagination(data)
        if result is None:
            raise NotFoundWebinars
        
        if result.count > 0 and not result.webinars:
            raise NotFoundWebinars
        return result
