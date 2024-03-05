from datetime import datetime

from adaptix import as_is_loader, Retort
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.domain.models.stats import Stats
from webinar.infrastructure.postgres.gateways.homework import PostgresHomeWorkGateway
from webinar.infrastructure.postgres.gateways.user import PostgresUserGateway
from webinar.infrastructure.postgres.repository.base import BaseRepository


class StatsRepositoryImpl(BaseRepository):
    connect: AsyncConnection[DictRow]

    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect
        self.retort = Retort(
            recipe=[
                as_is_loader(datetime)
            ]
        )

    async def read(self) -> Stats:
        user_dao = PostgresUserGateway(self.connect)
        homework_dao = PostgresHomeWorkGateway(self.connect)
        raw_data = dict(
            users=await user_dao.read_stats(),
            homework=await homework_dao.read_stats(),
        )
        return self.retort.load(raw_data, Stats)
