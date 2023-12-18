from dataclasses import asdict
from typing import AsyncGenerator, cast, Literal

from psycopg import AsyncConnection
from psycopg.rows import dict_row, tuple_row

from src.application.interfaces.repository.user import AbstractUser
from src.application.schemas.dto.homework import HOMEWORK_TYPES_RU
from src.application.schemas.dto.user import AddUserDto, UpdateUserDataGoogleSheetsDto, UserMailingDTO
from src.application.schemas.enums import DirectionEnum
from src.application.schemas.enums.homework import HomeWorkTypeEnum
from src.infrastructure.repositories.base import BaseOtherCreate, BaseRepository


class UserOtherCreate(BaseOtherCreate):
    connect: AsyncConnection
    
    def __init__(self, connect: AsyncConnection) -> None:
        self.connect = connect
    
    async def create_table(self) -> None:
        sql = '''
            CREATE TABLE IF NOT EXISTS users(
                id          SERIAL     PRIMARY KEY,            -- Уникальный айди
                date_time   TIMESTAMP  NOT NULL,               -- Дата и время регистрации
                user_id     BIGINT     NOT NULL      UNIQUE,   -- Юзер айди
                chat_id     BIGINT     NOT NULL      UNIQUE,   -- Чат айди
                surname     TEXT       NOT NULL,               -- Фамилия
                name        TEXT       NOT NULL,               -- Имя
                patronymic  TEXT       NULL,                   -- Отчество
                email       TEXT       NOT NULL,               -- Почта
                direction   TEXT       NOT NULL                -- Направление
            );
        '''
        await self.connect.execute(sql)
    
    async def create_index(self) -> None:
        sqls = [
            'CREATE INDEX IF NOT EXISTS users_id_index ON users(id);',
            'CREATE INDEX IF NOT EXISTS users_user_id_index ON users(user_id);',
            # 'CREATE INDEX IF NOT EXISTS users_date_time_id_index ON users(date_time);'
        ]
        for sql in sqls:
            await self.connect.execute(sql)


class UserRepository(AbstractUser, BaseRepository):
    connect: AsyncConnection
    
    def __init__(self, connect: AsyncConnection) -> None:
        self.connect = connect
    
    async def add(self, model: AddUserDto) -> None:
        sql = '''
            INSERT INTO users(
                date_time,
                user_id,
                chat_id,
                surname,
                name,
                patronymic,
                email,
                direction
            )
            VALUES(
                %(date_time)s,
                %(user_id)s,
                %(chat_id)s,
                %(surname)s,
                %(name)s,
                %(patronymic)s,
                %(email)s,
                %(direction)s
            )
            ON CONFLICT DO NOTHING;
        '''
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
    
    async def get_all_from_direction_type(
        self,
        direction_type: list[DirectionEnum]
    ) -> AsyncGenerator[UserMailingDTO, None]:
        sql = 'SELECT chat_id FROM users WHERE direction = ANY(%s)'
        
        async with self.connect.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(sql, (direction_type,))
            raw_data = await cursor.fetchall()
        
        for data in raw_data:
            yield UserMailingDTO(data.get('chat_id'))
    
    async def check(self, user_id: int) -> bool:
        sql = '''
            SELECT EXISTS(
                SELECT id
                  FROM users
                 WHERE user_id = %s
            ) AS check;
        '''
        async with self.connect.cursor(row_factory=tuple_row) as cursor:
            new_cursor = await cursor.execute(sql, (user_id,))
            data = cast(
                tuple[Literal[0, 1]],
                await new_cursor.fetchone()
            )
            return bool(data[-1])
    
    async def select_for_spreadsheets(self, type_: DirectionEnum) -> list[UpdateUserDataGoogleSheetsDto]:
        sql_1 = '''
            SELECT id, user_id as telegram_id, surname, name, patronymic, email
            FROM users WHERE direction = %s;
        '''
        sql_2 = '''
            SELECT h.number, h.type
            FROM homeworks AS h
            JOIN users AS u ON u.id = h.user_id
            WHERE u.user_id = %s
            ORDER BY h.number;
        '''
        datas = []
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql_1, (type_,))
            raw_data_1 = await cursor.fetchall()
            for data_1 in raw_data_1:
                await cursor.execute(sql_2, (data_1['telegram_id'],))
                raw_data_2 = await cursor.fetchall()
                
                homeworks = [None for _ in range(7)]
                for data_2 in raw_data_2:
                    raw_type = data_2.get('type')
                    if raw_type is None:
                        type_ = None  # type: ignore
                    else:
                        type_ = HOMEWORK_TYPES_RU[HomeWorkTypeEnum(raw_type)]
                    number = data_2['number']
                    homeworks[number - 1] = type_
                
                datas.append(
                    UpdateUserDataGoogleSheetsDto(
                        sup=(
                            f'{data_1["surname"]}'
                            f'{(data_1["name"])[0].upper()}.'
                            f'{(data_1.get("patronymic") or " ")[0].upper()}'
                        ),
                        telegram_id=data_1['telegram_id'],
                        email=data_1['email'],
                        homeworks_types=cast(list[str | None], homeworks)
                    )
                )
        return datas
