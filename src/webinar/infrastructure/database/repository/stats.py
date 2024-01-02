from datetime import datetime

from adaptix import as_is_loader, name_mapping, Retort
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.application.schemas.entities.stats import StatsEntity
from webinar.application.schemas.entities.user import UserStatsEntity
from webinar.infrastructure.database.dao.homework import HomeWorkDAOImpl
from webinar.infrastructure.database.dao.user import UserDAOImpl
from webinar.infrastructure.database.repository.base import BaseRepository


class StatsRepositoryImpl(BaseRepository):
    connect: AsyncConnection[DictRow]

    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect
        self.retort = Retort(
            recipe=[
                as_is_loader(datetime),
                name_mapping(UserStatsEntity, extra_in="homework"),
            ]
        )

    async def read(self) -> StatsEntity:
        user_dao = UserDAOImpl(self.connect)
        homework_dao = HomeWorkDAOImpl(self.connect)
        raw_data = dict(
            users=await user_dao.read_stats(),
            homework=await homework_dao.read_stats(),
        )
        return self.retort.load(raw_data, StatsEntity)
