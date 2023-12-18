from dataclasses import asdict

from adaptix import Retort
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation

from src.application.interfaces.repository.webinar import AbstractWebinar
from src.application.schemas.dto.webinar import AddWebinarDTO, Webinar
from src.infrastructure.repositories.base import BaseOtherCreate, BaseRepository


class WebinarOtherCreate(BaseOtherCreate):
    connect: AsyncConnection
    
    def __init__(self, connect: AsyncConnection) -> None:
        self.connect = connect
    
    async def create_table(self) -> None:
        sql = '''
                CREATE TABLE IF NOT EXISTS webinars(
                    id    SERIAL  PRIMARY KEY  NOT NULL, -- айди вебинара
                    url   TEXT    UNIQUE       NOT NULL, -- ссылка на вебинар
                    name  TEXT                 NOT NULL  -- название вебинара
                );
            '''
        await self.connect.execute(sql)
    
    async def create_index(self) -> None:
        sqls = [
            'CREATE INDEX IF NOT EXISTS webinars_id_index ON webinars(id);'
        ]
        for sql in sqls:
            await self.connect.execute(sql)


class WebinarDuplicateException(Exception):
    url: str
    
    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__()
    
    def __str__(self) -> str:
        return f'<{self.__class__.__name__}>({self.url})'
    
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>({self.url})'


class WebinarRepository(AbstractWebinar, BaseRepository):
    connect: AsyncConnection
    
    def __init__(self, connect: AsyncConnection) -> None:
        self.connect = connect
        self.retort = Retort()
    
    async def add(self, model: AddWebinarDTO) -> None:
        sql = '''
            INSERT INTO webinars(url, name)
            VALUES (%(url)s, %(name)s);
        '''
        async with self.connect.cursor() as cursor:
            try:
                await cursor.execute(sql, asdict(model))
            except UniqueViolation as exception:
                raise WebinarDuplicateException(model.url) from exception
    
    async def get(self, offset: int, count_webinars: int) -> list[Webinar]:
        sql = '''
            SELECT id, url, name
              FROM webinars
            ORDER BY id
            LIMIT %s OFFSET %s;
        '''
        async with self.connect.cursor() as cursor:
            new_cursor = await cursor.execute(sql, (count_webinars, offset))
            raw_data = await new_cursor.fetchall()
        return [
            self.retort.load(data, Webinar)
            for data in raw_data
        ]
