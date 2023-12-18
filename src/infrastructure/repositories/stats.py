from typing import cast, Final, Mapping

from adaptix import name_mapping, Retort
from psycopg import AsyncConnection

from src.application.interfaces.repository.stats import AbstractStats
from src.application.schemas.dto.stats import (
    CountHomeWorkDTO,
    CountStatsDTO,
    HomeWorkStatsDTO,
    HomeWorkTypeStatsDTO,
    StatsDTO
)
from src.infrastructure.repositories.base import BaseRepository


HOMEWORK_DTO_KEY: Final = {
    '1': 'first',
    '2': 'second',
    '3': 'third',
    '4': 'fourth',
    '5': 'fifth',
    '6': 'sixth'
}


class StatsRepositoryImpl(AbstractStats, BaseRepository):
    connect: AsyncConnection
    
    def __init__(self, connect: AsyncConnection) -> None:
        self.connect = connect
        self.retort = Retort(
            recipe=[
                name_mapping(CountStatsDTO, extra_in='homework'),
                name_mapping(
                    CountHomeWorkDTO,
                    map=dict(
                        smm='count_homework_smm',
                        copyrighting='count_homework_copyrighting'
                    )
                )
            ]
        )
    
    async def get_count_users(self) -> CountStatsDTO:
        sql = '''
            WITH users_data AS (
                SELECT COUNT(id) AS users,
                       COUNT(id) FILTER(WHERE direction='SMM') AS users_smm,
                       COUNT(id) FILTER(WHERE direction='Копирайтинг') AS users_copyrighting
                  FROM users
            ), homeworks_data AS(
                SELECT COUNT(h.id) FILTER(WHERE u.direction='SMM') AS homework_smm,
                       COUNT(h.id) FILTER(WHERE u.direction='Копирайтинг') AS homework_copyrighting
                  FROM homeworks AS h
                       JOIN users AS u
                       ON u.id = h.user_id
            )
            SELECT *
              FROM users_data, homeworks_data
        '''
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql)
            raw_data = cast(
                Mapping[str, int],
                await cursor.fetchone()
            )
        return self.retort.load(raw_data, CountStatsDTO)
    
    async def get_homework_stats(self) -> HomeWorkStatsDTO:
        sql_smm = '''
            SELECT number,
                   COUNT(h.number) AS count
              FROM homeworks AS h
                   JOIN users AS u
                   ON u.id = h.user_id
             WHERE direction = 'SMM'
            GROUP BY h.number
            HAVING number IN (1, 2, 3, 4, 5, 6)
        '''
        sql_copyrighting = '''
            SELECT number,
                   COUNT(h.number) AS count
              FROM homeworks AS h
                   JOIN users AS u
                     ON u.id = h.user_id
             WHERE direction = 'Копирайтинг'
            GROUP BY h.number
            HAVING number IN (1, 2, 3, 4, 5, 6)
        '''
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql_smm)
            raw_data_1 = await cursor.fetchall()
            await cursor.execute(sql_copyrighting)
            raw_data_2 = await cursor.fetchall()
            return HomeWorkStatsDTO(
                smm=HomeWorkTypeStatsDTO(  # type: ignore
                    **{
                        HOMEWORK_DTO_KEY.get(f'{data.get("number")}'): data.get('count')
                        for data in raw_data_1
                    }
                ),
                copyrighting=HomeWorkTypeStatsDTO(  # type: ignore
                    **{
                        HOMEWORK_DTO_KEY.get(f'{data.get("number")}'): data.get('count')
                        for data in raw_data_2
                    }
                )
            )
    
    async def stats(self) -> StatsDTO:
        count = await self.get_count_users()
        homework = await self.get_homework_stats()
        return StatsDTO(
            count=count,
            homework=homework
        )
