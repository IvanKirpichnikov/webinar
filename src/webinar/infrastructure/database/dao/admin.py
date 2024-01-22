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
    Retort
)
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation
from psycopg.rows import DictRow

from webinar.application.exceptions import (
    AdminCreated,
    NotFoundAdmin
)
from webinar.application.interfaces.dao.admin import AbstractAdminDAO
from webinar.application.schemas.dto.admin import CreateAdminDTO, GetAdminFromDirectionTraining
from webinar.application.schemas.dto.common import (
    DirectionsTrainingDTO,
    ResultExistsDTO,
    TelegramChatIdDTO,
    TelegramUserIdDTO,
)
from webinar.application.schemas.entities.admin import (
    AdminDataInfoEntity,
    AdminEntities,
    AdminEntity,
)
from webinar.application.schemas.types import (
    TelegramChatId
)
from webinar.infrastructure.database.dao.base import (
    BaseDAO,
    BaseOtherCreate
)


class AdminOtherCreateImpl(BaseOtherCreate):
    connect: AsyncConnection[DictRow]
    
    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect
    
    async def create_table(self) -> None:
        sql = """
            CREATE TABLE IF NOT EXISTS admins(
                db_user_id          BIGINT  PRIMARY KEY  REFERENCES users(db_id) ON DELETE CASCADE,
                direction_training  TEXT    NOT NULL,
                letters_range       TEXT,
                numbers_range       BOOL
            );
        """
        await self.connect.execute(sql)
    
    async def create_index(self) -> None:
        pass


class AdminDAOImpl(AbstractAdminDAO, BaseDAO):
    connect: AsyncConnection[DictRow]
    
    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect
        self.retort = Retort(recipe=[as_is_loader(datetime)])
    
    async def create(self, model: CreateAdminDTO) -> None:
        sql = """
            INSERT INTO admins(
                db_user_id,
                direction_training,
                letters_range,
                numbers_range
            )
            SELECT u.db_id,
                   %(direction_training)s,
                   %(letters_range)s,
                   %(numbers_range)s
              FROM users AS u
             WHERE u.telegram_user_id = %(telegram_user_id)s;
        """
        async with self.connect.cursor() as cursor:
            try:
                await cursor.execute(sql, asdict(model))
            except UniqueViolation as error:
                raise AdminCreated from error
    
    async def exists(self, model: TelegramUserIdDTO) -> ResultExistsDTO:
        sql = """
            SELECT EXISTS(
                SELECT u.db_id
                  FROM admins AS a
                       JOIN users AS u
                         ON u.db_id = a.db_user_id
                 WHERE u.telegram_user_id = %s
            ) AS exists;
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, astuple(model))
            data = cast(Mapping[str, bool] | None, await cursor.fetchone())
        if data is None:
            return ResultExistsDTO(False)
        return ResultExistsDTO(data["exists"])
    
    async def read_by_telegram_user_id(
        self, model: TelegramUserIdDTO
    ) -> AdminEntity:
        sql = """
            SELECT a.direction_training,
                   a.letters_range,
                   a.numbers_range,
                   u.db_id,
                   u.telegram_user_id,
                   u.telegram_chat_id,
                   u.date_time_registration,
                   u.direction_training,
                   u.email,
                   u.surname,
                   u.name,
                   u.patronymic
            FROM admins AS a
                JOIN users AS u
                ON u.db_id = a.db_user_id
            WHERE u.telegram_user_id = %s;
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, astuple(model))
            raw_data = cast(Mapping[str, Any] | None, await cursor.fetchone())
        if raw_data is None:
            raise ValueError
        return self.retort.load(raw_data, AdminEntity)
    
    async def read_all_by_direction_training(
        self, model: DirectionsTrainingDTO
    ) -> AdminEntities:
        sql = """
            SELECT a.direction_training,
                   a.letters_range,
                   a.numbers_range,
                   u.db_id,
                   u.telegram_user_id,
                   u.telegram_chat_id,
                   u.date_time_registration,
                   u.direction_training,
                   u.email,
                   u.surname,
                   u.name,
                   u.patronymic
            FROM admins AS a
                JOIN users AS u
                ON u.db_id = a.db_user_id
            WHERE u.direction_training = ANY(%s);
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, astuple(model))
            raw_data = cast(list[Mapping[str, Any]], await cursor.fetchall())
        if raw_data is None:
            raise NotFoundAdmin
        return self.retort.load(dict(admins=raw_data), AdminEntities)
    
    async def read_data_by_telegram_user_id(
        self, model: TelegramUserIdDTO
    ) -> AdminDataInfoEntity:
        sql = """
            SELECT a.db_user_id,
                   a.direction_training,
                   a.letters_range,
                   a.numbers_range
            FROM admins AS a
                JOIN users AS u
                ON u.db_id = a.db_user_id
            WHERE u.telegram_user_id = %s;
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, astuple(model))
            raw_data = cast(Mapping[str, Any] | None, await cursor.fetchone())
        if raw_data is None:
            raise ValueError
        return self.retort.load(raw_data, AdminDataInfoEntity)
    
    async def get_admin_by_letters_range_from_user(
        self,
        model: GetAdminFromDirectionTraining
    ) -> TelegramChatIdDTO:
        sql = '''
            SELECT u.telegram_chat_id
            FROM admins AS a
                JOIN users AS u
                  ON u.db_id = a.db_user_id
            WHERE (
                SELECT LOWER(SUBSTRING(surname, 1, 1))
                  FROM users
                 WHERE telegram_user_id = %(telegram_user_id)s
            ) = ANY(STRING_TO_ARRAY(a.letters_range, NULL))
            AND a.direction_training = %(direction_training)s
            ORDER BY RANDOM()
            LIMIT 1;
        '''
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
            raw_data = await cursor.fetchone()
        print(raw_data, model)
        if not raw_data:
            raise NotFoundAdmin
        return TelegramChatIdDTO(
            TelegramChatId(
                raw_data['telegram_chat_id']
            )
        )
    
    async def read_random_by_direction_training(self, model: DirectionsTrainingDTO) -> AdminEntity:
        sql = """
            SELECT
                a.db_user_id,
                a.direction_training,
                a.letters_range,
                a.numbers_range,
                u.db_id,
                u.telegram_user_id,
                u.telegram_chat_id,
                u.date_time_registration,
                u.direction_training,
                u.email,
                u.surname,
                u.name,
                u.patronymic
            FROM
                admins AS a
            JOIN
                users AS u
                ON u.db_id = a.db_user_id
            WHERE a.direction_training = %s
            ORDER BY RANDOM();
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, astuple(model))
            raw_data = cast(Mapping[str, Any] | None, await cursor.fetchone())
        if raw_data is None:
            raise NotFoundAdmin
        return self.retort.load(raw_data, AdminEntity)
    
    async def read_random(self) -> AdminEntity:
        sql = """
            SELECT
                a.db_user_id,
                a.direction_training,
                a.letters_range,
                a.numbers_range,
                u.db_id,
                u.telegram_user_id,
                u.telegram_chat_id,
                u.date_time_registration,
                u.direction_training,
                u.email,
                u.surname,
                u.name,
                u.patronymic
            FROM
                admins AS a
            JOIN
                users AS u
                ON u.db_id = a.db_user_id
            ORDER BY RANDOM();
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql)
            raw_data = cast(Mapping[str, Any] | None, await cursor.fetchone())
        if raw_data is None:
            raise NotFoundAdmin
        return self.retort.load(raw_data, AdminEntity)
