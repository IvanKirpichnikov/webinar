from dataclasses import asdict, astuple
from datetime import datetime
from typing import Any, cast

from adaptix import as_is_loader, Retort
from psycopg import AsyncConnection
from psycopg.rows import tuple_row

from src.application.interfaces.repository.homework import AbstractHomeWork
from src.application.schemas.dto.homework import (
    AddHomeWorkDTO,
    GetHomeWorkAllByUserIdByType, GetHomeWorkWithInformationForAdminDTO,
    HomeWorkDTO,
    HomeWorkPaginationDTO,
    HomeWorkUserId,
    HomeWorkWithInformationForAdminDTO,
    NumberHomeWorkDTO,
    PaginationHomeWorkDTO, UpdatingTypeAndCommentByIdDTO,
    UpdatingTypeByIdDTO
)
from src.application.schemas.enums import DirectionEnum
from src.infrastructure.repositories.base import BaseOtherCreate, BaseRepository


class HomeWorkOtherCreateImpl(BaseOtherCreate):
    connect: AsyncConnection
    
    def __init__(self, connect: AsyncConnection) -> None:
        self.connect = connect
    
    async def create_table(self) -> None:
        sql = '''
            CREATE TABLE IF NOT EXISTS homeworks(
                id         SERIAL     PRIMARY KEY,           -- уникальный айди
                user_id    BIGINT     REFERENCES users(id) ON DELETE CASCADE,  -- users.id
                date_time  TIMESTAMP  NOT NULL,              -- дата добавления
                number     SMALLINT   NOT NULL,              -- номер домашнего задания
                url        TEXT       NOT NULL,              -- ссылка на него
                type       TEXT       NOT NULL,              -- тип состояния
                comments   TEXT                              -- комментарии
            );
        '''
        await self.connect.execute(sql)
    
    async def create_index(self) -> None:
        sqls = [
            (
                'CREATE UNIQUE INDEX '
                'IF NOT EXISTS check_numbers_on_homeworks '
                'ON homeworks(user_id, number);'
            ),
            (
                'CREATE INDEX IF NOT EXISTS '
                'homeworks_user_id_index '
                'ON homeworks(user_id)'
            )
        ]
        for sql in sqls:
            await self.connect.execute(sql)


class HomeWorkRepositoryImpl(AbstractHomeWork, BaseRepository):
    connect: AsyncConnection
    
    def __init__(self, connect: AsyncConnection) -> None:
        self.connect = connect
        self.retort = Retort(
            recipe=[
                as_is_loader(datetime)
            ]
        )
    
    async def add(self, model: AddHomeWorkDTO) -> None:
        sql = '''
            INSERT INTO homeworks(
                user_id,
                date_time,
                number,
                url,
                type,
                comments
            )
            SELECT id,
                   %(date_time)s,
                   %(number)s,
                   %(url)s,
                   %(type)s,
                   %(comments)s
              FROM users AS u
             WHERE u.user_id = %(user_id)s;
        '''
        await self.connect.execute(sql, asdict(model))
    
    async def get_by_number_by_user_id(self, model: HomeWorkUserId) -> list[int] | list:
        sql = '''
            SELECT h.number
              FROM homeworks AS h
                   JOIN users AS u
                     ON u.id = h.user_id
             WHERE u.user_id = %s;
        '''
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, astuple(model))
            raw_data = await cursor.fetchall()
        return [
            data['number']
            for data in raw_data
        ]
    
    async def get_all_by_user_id(self, model: HomeWorkUserId) -> list[HomeWorkDTO]:
        sql = '''
            SELECT h.id,
                   h.user_id,
                   h.date_time,
                   h.number,
                   h.url,
                   h.type,
                   h.comments
              FROM homeworks h
                   JOIN users u
                     ON u.id = h.user_id
             WHERE u.user_id = %s
            ORDER BY h.number;
        '''
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, astuple(model))
            raw_data = cast(
                list[dict[str, Any]],
                await cursor.fetchall()
            )
        return [
            self.retort.load(data, HomeWorkDTO)
            for data in raw_data
        ]
    
    async def get_all_by_user_id_and_by_type(self, model: GetHomeWorkAllByUserIdByType) -> list[HomeWorkDTO]:
        sql = '''
            SELECT h.id,
                   h.user_id,
                   h.date_time,
                   h.number,
                   h.url,
                   h.type,
                   h.comments
              FROM homeworks h
                   JOIN users u
                     ON u.id = h.user_id
             WHERE u.user_id = %(user_id)s AND h.type = %(type)s
            ORDER BY h.number;
        '''
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
            raw_data = cast(
                list[dict[str, Any]],
                await cursor.fetchall()
            )
        print(raw_data)
        return [
            self.retort.load(data, HomeWorkDTO)
            for data in raw_data
        ]
    
    async def update_type_and_comment_by_id(self, model: UpdatingTypeAndCommentByIdDTO) -> None:
        sql = '''
            UPDATE homeworks
               SET type = %(type)s, comments = %(comment)s
             WHERE id = %(homework_id)s;
        '''
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
    
    async def update_type(self, model: UpdatingTypeByIdDTO) -> None:
        sql = '''
            UPDATE homeworks
               SET type = %(type)s
             WHERE id = %(homework_id)s;
        '''
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
    
    async def pagination(self, model: PaginationHomeWorkDTO) -> list[HomeWorkPaginationDTO]:
        sql = '''
            SELECT h.id,
                   u.direction,
                   h.number,
                   h.date_time,
                   u.surname,
                   u.name,
                   u.patronymic
              FROM homeworks AS h
                   JOIN users AS u
                     ON u.id = h.user_id
             WHERE h.type = 'under_inspection' AND u.direction = ANY(%(direction_types)s)
            ORDER BY h.date_time
            LIMIT 10 OFFSET %(offset)s
        '''
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
            raw_data = cast(
                list[dict[str, Any]],
                await cursor.fetchall()
            )
        return [
            self.retort.load(data, HomeWorkPaginationDTO)
            for data in raw_data
        ]
    
    async def get_with_information_for_admin(
        self,
        model: GetHomeWorkWithInformationForAdminDTO
    ) -> HomeWorkWithInformationForAdminDTO:
        sql = '''
            SELECT h.id,
                   h.number,
                   h.url,
                   h.date_time,
                   u.user_id,
                   u.chat_id,
                   u.surname,
                   u.name,
                   u.patronymic,
                   u.direction,
                   u.email
              FROM homeworks AS h
                   JOIN users AS u
                     ON u.id = h.user_id
             WHERE h.id = %s;
        '''
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, astuple(model))
            raw_data = cast(
                dict[str, Any],
                await cursor.fetchone()
            )
        return self.retort.load(raw_data, HomeWorkWithInformationForAdminDTO)
