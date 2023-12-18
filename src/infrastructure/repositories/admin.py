from dataclasses import astuple
from typing import Any, cast

from psycopg import AsyncConnection

from src.application.interfaces.repository.admin import AbstractAdmin
from src.application.schemas.dto.admin import AddAdminDTO, AdminUserId
from src.application.schemas.enums import DirectionEnum
from src.infrastructure.repositories.base import BaseOtherCreate, BaseRepository


class AdminOtherCreateImpl(BaseOtherCreate):
    connect: AsyncConnection
    
    def __init__(self, connect: AsyncConnection) -> None:
        self.connect = connect
    
    async def create_table(self) -> None:
        sql = '''
            CREATE TABLE IF NOT EXISTS admins(
                user_id         BIGINT  PRIMARY KEY  REFERENCES users(id) ON DELETE CASCADE,
                direction_type  TEXT    NOT NULL
            );
        '''
        await self.connect.execute(sql)
    
    async def create_index(self) -> None:
        pass


class AdminRepositoryImpl(AbstractAdmin, BaseRepository):
    connect: AsyncConnection
    
    def __init__(self, connect: AsyncConnection) -> None:
        self.connect = connect
    
    async def add(self, model: AddAdminDTO) -> None:
        sql = '''
            INSERT INTO admins(
                user_id,
                direction_type
            )
            SELECT u.id, %s
              FROM users AS u
             WHERE u.user_id = %s;
        '''
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, astuple(model)[::-1])
    
    async def exists(self, model: AdminUserId) -> bool:
        sql = '''
            SELECT EXISTS(
                SELECT u.id
                  FROM admins AS a
                       JOIN users AS u
                         ON u.id = a.user_id
                 WHERE u.user_id = %s
            ) AS exists;
        '''
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, astuple(model))
            raw_data = cast(
                dict[str, int],
                await cursor.fetchone()
            )
        return bool(raw_data.get('exists', False))
    
    async def get_direction_type(self, model: AdminUserId) -> DirectionEnum:
        sql = '''
            SELECT a.direction_type
              FROM admins AS a
                   JOIN users AS u
                     ON u.id = a.user_id
             WHERE u.user_id = %s
        '''
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, astuple(model))
            raw_data = await cursor.fetchone()
        return DirectionEnum(raw_data['direction_type'])
    
    async def get_random_chat_id_admin(self) -> int | None:
        sql = '''
            SELECT chat_id
              FROM users AS u
                   JOIN admins AS a
                     ON a.user_id = u.id
            ORDER BY RANDOM();
        '''
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql)
            raw_data = cast(
                dict[str, Any] | None,
                await cursor.fetchone()
            )
        if raw_data is None:
            return None
        return cast(int, raw_data.get('chat_id'))
