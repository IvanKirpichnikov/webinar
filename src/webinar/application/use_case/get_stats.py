from datetime import datetime
from logging import getLogger
from typing import Protocol

from adaptix import as_is_loader, Retort

from webinar.application.interfaces.gateways.homework import HomeWorkGateway
from webinar.application.interfaces.gateways.user import UserGateway
from webinar.application.use_case.base import UseCase
from webinar.domain.models.stats import Stats


class GetStats(
    UseCase[None, Stats], Protocol
):
    async def __call__(self, data: None = None) -> Stats:
        raise NotImplementedError


class GetStatsImpl(GetStats):
    logger = getLogger(__name__)
    retort = Retort(
        recipe=[
            as_is_loader(datetime)
        ]
    )
    
    def __init__(
        self,
        user_gateway: UserGateway,
        homework_gateway: HomeWorkGateway,
    ):
        self._user_gateway = user_gateway
        self._homework_gateway = homework_gateway
    
    async def __call__(self, data: None = None) -> Stats:
        self.logger.info('Get stats')
        raw_data = dict(
            users=await self._user_gateway.read_stats(),
            homework=await self._homework_gateway.read_stats(),
        )
        return self.retort.load(raw_data, Stats)
