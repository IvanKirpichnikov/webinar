from dataclasses import (
    asdict,
    astuple
)
from datetime import datetime
from typing import (
    Any,
    cast,
    Mapping
)

from adaptix import (
    as_is_loader,
    name_mapping,
    Retort
)
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.application.exceptions import (
    NotFoundUser,
    NotFoundUsers
)
from webinar.application.interfaces.dao.user import AbstractUserDAO
from webinar.application.schemas.dto.common import (
    DirectionsTrainingDTO,
    DirectionTrainingDTO,
    ResultExistsDTO,
    TelegramUserIdDTO,
)
from webinar.application.schemas.dto.user import (
    CreateUserDTO,
    UpdateUserDataGoogleSheetsDto,
)
from webinar.application.schemas.entities.homework import HOMEWORK_RU
from webinar.application.schemas.entities.user import (
    UserEntities,
    UserEntity,
    UserStatsEntity
)
from webinar.application.schemas.enums.homework import HomeWorkStatusType
from webinar.application.schemas.types import TelegramUserId
from webinar.infrastructure.database.dao.base import (
    BaseDAO,
    BaseOtherCreate
)


class UserOtherCreateImpl(BaseOtherCreate):
    connect: AsyncConnection[DictRow]
    
    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect
    
    async def create_table(self) -> None:
        sql = """
            CREATE TABLE IF NOT EXISTS users(
                db_id                   SERIAL     PRIMARY KEY,            -- Уникальный айди
                telegram_user_id        BIGINT     NOT NULL      UNIQUE,   -- Юзер айди
                telegram_chat_id        BIGINT     NOT NULL      UNIQUE,   -- Чат айди
                date_time_registration  TIMESTAMP  NOT NULL,               -- Дата и время регистрации
                direction_training      TEXT       NOT NULL,               -- Направление
                email                   TEXT       NOT NULL,               -- Почта
                surname                 TEXT       NOT NULL,               -- Фамилия
                name                    TEXT       NOT NULL,               -- Имя
                patronymic              TEXT                               -- Отчество
            );
        """
        await self.connect.execute(sql)
    
    async def create_index(self) -> None:
        sqls = [
            "CREATE INDEX IF NOT EXISTS users_db_id_index ON users(db_id);",
            "CREATE INDEX IF NOT EXISTS users_user_id_index ON users(telegram_user_id);",
            # 'CREATE INDEX IF NOT EXISTS users_date_time_id_index ON users(date_time);'
        ]
        for sql in sqls:
            await self.connect.execute(sql)


class UserDAOImpl(AbstractUserDAO, BaseDAO):
    connect: AsyncConnection[DictRow]
    retort: Retort
    
    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect
        self.retort = Retort(
            recipe=[
                as_is_loader(datetime),
                name_mapping(UserStatsEntity, extra_in="homework"),
            ]
        )
    
    async def read_by_telegram_user_id(
        self, model: TelegramUserIdDTO
    ) -> UserEntity:
        sql = """
            SELECT db_id,
                   telegram_user_id,
                   telegram_chat_id,
                   date_time_registration,
                   direction_training,
                   email,
                   surname,
                   name,
                   patronymic
              FROM users
             WHERE telegram_user_id = %(telegram_user_id)s
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
            raw_data = cast(Mapping[str, Any], await cursor.fetchone())
        if not raw_data:
            raise NotFoundUser
        return self.retort.load(raw_data, UserEntity)
    
    async def create(self, model: CreateUserDTO) -> None:
        sql = """
            INSERT INTO users(
                telegram_user_id,
                telegram_chat_id,
                date_time_registration,
                direction_training,
                email,
                surname,
                name,
                patronymic
            )
            VALUES(
                %(telegram_user_id)s,
                %(telegram_chat_id)s,
                %(date_time_registration)s,
                %(direction_training)s,
                %(email)s,
                %(surname)s,
                %(name)s,
                %(patronymic)s
            )
            ON CONFLICT DO NOTHING;
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
    
    async def exists(self, model: TelegramUserIdDTO) -> ResultExistsDTO:
        sql = """
            SELECT EXISTS(
                SELECT db_id
                  FROM users
                 WHERE telegram_user_id = %s
            ) AS data;
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, astuple(model))
            raw_data = cast(Mapping[str, bool] | None, await cursor.fetchone())
        
        if raw_data is None:
            return ResultExistsDTO(False)
        return ResultExistsDTO(raw_data["data"])
    
    async def read_all_by_direction_training(
        self, model: DirectionsTrainingDTO
    ) -> UserEntities:
        sql = """
            SELECT db_id,
                   telegram_user_id,
                   telegram_chat_id,
                   date_time_registration,
                   direction_training,
                   email,
                   surname,
                   name,
                   patronymic
              FROM users
             WHERE direction_training = ANY(%s)
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, astuple(model))
            raw_data = cast(list[Mapping[str, Any]], await cursor.fetchall())
        if not raw_data:
            raise NotFoundUsers
        return self.retort.load({"users": raw_data}, UserEntities)
    
    async def read_stats(self) -> Mapping[str, int]:
        sql = """
            WITH users_data AS (
                SELECT
                    COUNT(db_id) AS users,
                    COUNT(db_id) FILTER(
                        WHERE direction_training = 'SMM'
                    ) AS smm,
                    COUNT(db_id) FILTER(
                        WHERE direction_training = 'Копирайтинг'
                    ) AS copyrighting
                FROM
                    users
            ), homeworks_data AS (
                SELECT
                    COUNT(h.db_id) FILTER(
                        WHERE u.direction_training = 'SMM'
                    ) AS homework_smm,
                    COUNT(h.db_id) FILTER(
                        WHERE u.direction_training = 'Копирайтинг'
                    ) AS homework_copyrighting
                FROM
                    homeworks AS h
                    JOIN
                        users AS u
                        ON u.db_id=h.db_user_id
            )
            SELECT *
            FROM
              users_data,
              homeworks_data
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql)
            raw_data = cast(Mapping[str, int], await cursor.fetchone())
        return raw_data
    
    async def read_user_and_he_homeworks(
        self, model: DirectionTrainingDTO
    ) -> list[UpdateUserDataGoogleSheetsDto]:
        sql_1 = """
            SELECT
                db_id,
                telegram_user_id,
                surname,
                name,
                patronymic,
                email
            FROM
                users
            WHERE
                direction_training = %s;
        """
        sql_2 = """
            SELECT
                h.number,
                h.status_type,
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
        datas = []
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql_1, (model.direction_training,))
            raw_data_1 = await cursor.fetchall()
            for data_1 in raw_data_1:
                homeworks: list[str | None] = [None for _ in range(7)]
                telegram_user_id = TelegramUserId(data_1["telegram_user_id"])
                await cursor.execute(sql_2, (telegram_user_id,))
                raw_data_2 = await cursor.fetchall()
                for data_2 in raw_data_2:
                    raw_status_type = data_2.get("status_type")
                    print(raw_data_2)
                    if data_2['number'] == 7:
                        status_type = data_2['evaluation'] or 'Не оценен'
                    else:
                        status_type = (
                            HOMEWORK_RU[HomeWorkStatusType(raw_status_type)]
                            if raw_status_type
                            else None
                        )
                    homeworks[data_2["number"] - 1] = status_type
                datas.append(
                    UpdateUserDataGoogleSheetsDto(
                        telegram_user_id=telegram_user_id,
                        homeworks_data=homeworks,
                        sup=(
                            f'{data_1["surname"]} '
                            f'{(data_1["name"])[0].upper()}.'
                            f'{(data_1.get("patronymic") or " ")[0].upper()}'
                        ),
                        email=data_1["email"],
                    )
                )
        return datas
