from dataclasses import asdict, astuple
from datetime import datetime
from typing import Any, cast, Final, Mapping

from adaptix import as_is_loader, name_mapping, Retort

from webinar.application.dto.common import TgUserIdDTO
from webinar.application.dto.homework import (
    HomeWorkIdDTO,
    HomeWorkPaginationDTO,
    TgUserIdAndStatusTypeDTO,
    UpdateHomeworkEvolutionAndStatusDTO, UpdatingTypeAndCommentByIdDTO,
)
from webinar.application.interfaces.gateways.homework import HomeWorkGateway
from webinar.application.use_case.homeworks.add_user_homework import AddUserHomeWorkDTO
from webinar.application.use_case.homeworks.update_homework_status import UpdateHomeWorkStatusDTO
from webinar.domain.enums.direction_type import DirectionTrainingType
from webinar.domain.models.homework import (
    HomeWorkAndUserInfoEntity,
    HomeWorks,
    HomeWorkStatsEntities,
    UserHomeWorks,
)
from webinar.infrastructure.postgres.gateways.base import BaseOtherCreate, PostgresGateway


HOMEWORK_DTO_KEY: Final = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth",
    6: "sixth",
    7: "seventh",
}


def parse_data(raw_data: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        HOMEWORK_DTO_KEY[data["number"]]: data["count"] for data in raw_data
    }


class HomeWorkOtherCreateImpl(BaseOtherCreate):
    async def create_table(self) -> None:
        sql = """
            CREATE TABLE IF NOT EXISTS homeworks(
                db_id                   SERIAL     PRIMARY KEY, -- уникальный айди
                db_user_id              BIGINT     REFERENCES users(db_id) ON DELETE CASCADE,
                date_time_registration  TIMESTAMP  NOT NULL,    -- дата добавления
                status_type             TEXT       NOT NULL,    -- тип состояния
                number                  SMALLINT   NOT NULL,    -- номер домашнего задания
                url                     TEXT       NOT NULL,    -- ссылка на него
                comments                TEXT,                   -- комментарии
                evaluation              TEXT                    -- Оценка
            );
        """
        await self.connect.execute(sql)
    
    async def create_index(self) -> None:
        sqls = [
            (
                "CREATE UNIQUE INDEX "
                "IF NOT EXISTS unique_homeworks_for_user "
                "ON homeworks(db_user_id, number);"
            ),
            (
                "CREATE INDEX IF NOT EXISTS "
                "homeworks_user_id "
                "ON homeworks(db_user_id)"
            ),
        ]
        for sql in sqls:
            await self.connect.execute(sql)


class PostgresHomeWorkGateway(PostgresGateway, HomeWorkGateway):
    retort = Retort(
        recipe=[
            as_is_loader(datetime),
            name_mapping(
                HomeWorkStatsEntities,
                map=dict(
                    smm="count_homework_smm",
                    copyrighting="count_homework_copyrighting",
                ),
            ),
        ]
    )
    
    async def add_user_homework(self, model: AddUserHomeWorkDTO) -> None:
        sql = """
            INSERT INTO
                homeworks(
                    db_user_id,
                    date_time_registration,
                    status_type,
                    number,
                    url,
                    comments,
                    evaluation
                )
            SELECT
                db_id,
                %(date_time_registration)s,
                %(status_type)s,
                %(number)s,
                %(url)s,
                %(comments)s,
                %(evaluation)s
            FROM
                users
            WHERE
                telegram_user_id = %(telegram_user_id)s;
        """
        await self.connect.execute(sql, asdict(model))
    
    async def read_all_by_telegram_user_id(
        self, model: TgUserIdDTO
    ) -> HomeWorks | None:
        sql = """
            SELECT
                h.db_id,
                h.db_user_id,
                h.date_time_registration,
                h.status_type,
                h.number,
                h.url,
                h.comments,
                h.evaluation
            FROM
                homeworks AS h
                JOIN
                    users AS u
                    ON u.db_id = h.db_user_id
            WHERE
                u.telegram_user_id = %s
            ORDER BY
                h.number;
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, astuple(model))
            raw_data = await cursor.fetchall()
        if not raw_data:
            return None
        return self.retort.load(dict(homeworks=raw_data), HomeWorks)
    
    async def read_all_by_telegram_user_id_and_status_type(
        self, model: TgUserIdAndStatusTypeDTO
    ) -> HomeWorks:
        sql = """
            SELECT
                h.db_id,
                h.db_user_id,
                h.date_time_registration,
                h.status_type,
                h.number,
                h.url,
                h.comments,
                h.evaluation
            FROM
                homeworks h
                JOIN
                    users u
                    ON u.id = h.user_id
            WHERE
                u.telegram_user_id = %(telegram_user_id)s
                AND h.status_type = %(status_type)s
            ORDER BY
                h.number;
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
            raw_data = cast(list[dict[str, Any]], await cursor.fetchall())
        return self.retort.load(dict(homeworks=raw_data), HomeWorks)
    
    async def update_status(self, model: UpdateHomeWorkStatusDTO) -> None:
        sql = """
            UPDATE
                homeworks
            SET
                status_type = %(status_type)s
            WHERE
                db_id = %(db_id)s;
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
    
    async def update_type_and_comment(
        self, model: UpdatingTypeAndCommentByIdDTO
    ) -> None:
        sql = """
            UPDATE
                homeworks
            SET
                status_type = %(status_type)s,
                comments = %(comments)s
            WHERE
                db_id = %(db_id)s;
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
    
    async def update_evolution_and_status(
        self, model: UpdateHomeworkEvolutionAndStatusDTO
    ) -> None:
        sql = """
           UPDATE
               homeworks
           SET
               status_type = %(status_type)s,
               evaluation = %(evaluation)s,
               comments = null
           WHERE
               db_id = %(db_id)s;
       """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
    
    async def read_from_letters_range(
        self, model: HomeWorkPaginationDTO
    ) -> UserHomeWorks | None:
        sql = """
            SELECT
                h.db_id,
                h.number,
                h.date_time_registration,
                h.evaluation,
                u.surname,
                u.name,
                u.patronymic
            FROM
                homeworks AS h
                JOIN
                    users AS u
                    ON u.db_id = h.db_user_id
            WHERE
                h.status_type = 'under_inspection'
                AND u.direction_training = ANY(%(direction_training)s)
                AND %(letters_range)s LIKE '%%' || LOWER(SUBSTRING(u.surname, 1, 1)) || '%%'
            ORDER BY
                h.date_time_registration LIMIT %(limit)s OFFSET %(offset)s
    """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
            raw_data = cast(list[dict[str, Any]], await cursor.fetchall())
        if not raw_data:
            return None
        return self.retort.load(dict(homeworks=raw_data), UserHomeWorks)
    
    async def read_from_numbers_range(
        self, model: HomeWorkPaginationDTO
    ) -> UserHomeWorks | None:
        sql = """
            WITH raw_homeworks AS (
                SELECT
                    h.db_id,
                    h.number,
                    h.date_time_registration,
                    h.evaluation,
                    u.surname,
                    u.name,
                    u.patronymic
                FROM
                    homeworks AS h
                    JOIN
                        users AS u
                        ON u.db_id = h.db_user_id
                WHERE
                    h.status_type = 'under_inspection'
                    AND u.direction_training = ANY(%(direction_training)s)
                ORDER BY
                    h.date_time_registration
                OFFSET (
                    SELECT
                        ((ROW_NUMBER() OVER()) - 1) * %(count_homeworks)s
                    FROM
                        admins AS a
                        JOIN
                            users AS u
                            ON a.db_user_id = u.db_id
                    WHERE
                        u.telegram_user_id = %(telegram_user_id)s
                )
            )
            SELECT *
            FROM
                raw_homeworks
            LIMIT %(limit)s OFFSET %(offset)s
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
            raw_data = cast(list[dict[str, Any]], await cursor.fetchall())
        if not raw_data:
            return None
        return self.retort.load(dict(homeworks=raw_data), UserHomeWorks)
    
    async def read_from_offset(
        self, model: HomeWorkPaginationDTO
    ) -> UserHomeWorks | None:
        sql = """
            SELECT
                h.db_id,
                h.number,
                h.date_time_registration,
                h.evaluation,
                u.surname,
                u.name,
                u.patronymic
            FROM
                homeworks AS h
                JOIN
                    users AS u
                    ON u.db_id = h.db_user_id
            WHERE
                h.status_type = 'under_inspection'
                AND u.direction_training = ANY(%(direction_training)s)
            ORDER BY
                h.date_time_registration
            LIMIT %(offset)s OFFSET %(offset)s
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
            raw_data = cast(list[Mapping[str, Any]], await cursor.fetchall())
        if not raw_data:
            return None
        return self.retort.load(dict(homeworks=raw_data), UserHomeWorks)
    
    async def read_homework_and_user_info_by_db_id(
        self, model: HomeWorkIdDTO
    ) -> HomeWorkAndUserInfoEntity:
        sql = """
            SELECT
                u.db_id,
                u.telegram_user_id,
                u.telegram_chat_id,
                u.direction_training,
                u.email,
                u.surname,
                u.name,
                u.patronymic,
                h.number,
                h.url,
                h.date_time_registration,
                h.evaluation
            FROM
                homeworks AS h
                JOIN
                    users AS u
                    ON u.db_id = h.db_user_id
            WHERE
                h.db_id = %s;
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, astuple(model))
            raw_data = cast(dict[str, Any], await cursor.fetchone())
        return self.retort.load(raw_data, HomeWorkAndUserInfoEntity)
    
    async def read_stats(self) -> dict[str, Any]:
        sql = """
            SELECT
                number,
                COUNT(h.number) AS count
            FROM homeworks AS h
                 JOIN
                    users AS u
                    ON u.db_id = h.db_user_id
            WHERE
                u.direction_training = %s
            GROUP BY h.number
            HAVING number IN (1, 2, 3, 4, 5, 6, 7)
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, (DirectionTrainingType.SMM,))
            raw_data_1 = await cursor.fetchall()
            await cursor.execute(sql, (DirectionTrainingType.COPYRIGHTING,))
            raw_data_2 = await cursor.fetchall()
        return dict(
            smm=parse_data(raw_data_1), copyrighting=parse_data(raw_data_2)
        )
