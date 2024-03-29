from abc import abstractmethod
from logging import getLogger
from typing import Protocol

from webinar.application.dto.webinar import CreateWebinarDTO
from webinar.application.exceptions import DuplicateWebinar
from webinar.application.interfaces.gateways.webinar import WebinarGateway
from webinar.application.interfaces.uow import DBUoW
from webinar.application.use_case.base import UseCase


class CreateWebinar(UseCase[CreateWebinarDTO, None], Protocol):
    @abstractmethod
    async def __call__(self, data: CreateWebinarDTO) -> None:
        raise NotImplementedError


class CreateWebinarImpl(CreateWebinar):
    logger = getLogger(__name__)
    
    def __init__(self, gateway: WebinarGateway, uow: DBUoW) -> None:
        self._uow = uow
        self._gateway = gateway
    
    async def __call__(self, data: CreateWebinarDTO) -> None:
        async with self._uow.transaction():
            result = await self._gateway.create(data)
        if result:
            self.logger.info(
                'Create webinar. %r'
                % data
            )
            return None
        self.logger.warning(
            'Not create webinar. %r'
            % data
        )
        raise DuplicateWebinar(data)
