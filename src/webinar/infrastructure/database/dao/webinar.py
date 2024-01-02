from dataclasses import asdict
from typing import Any, cast

from adaptix import Retort
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation
from psycopg.rows import DictRow

from webinar.application.exceptions import DuplicateWebinar, NotFoundWebinars
from webinar.application.interfaces.dao.webinar import AbstractWebinarDAO
from webinar.application.schemas.dto.webinar import (
    CreateWebinarDTO,
    PaginationWebinarDTO,
)
from webinar.application.schemas.entities.webinar import WebinarEntities
from webinar.infrastructure.database.dao.base import BaseDAO, BaseOtherCreate


class WebinarOtherCreateImpl(BaseOtherCreate):
    connect: AsyncConnection[DictRow]

    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect

    async def create_table(self) -> None:
        sql = """
                CREATE TABLE IF NOT EXISTS webinars(
                    db_id  SERIAL  PRIMARY KEY  NOT NULL, -- айди вебинара
                    url    TEXT    UNIQUE       NOT NULL, -- ссылка на вебинар
                    name   TEXT                 NOT NULL  -- название вебинара
                );
            """
        await self.connect.execute(sql)

    async def create_index(self) -> None:
        sqls = [
            "CREATE INDEX IF NOT EXISTS webinars_id_index ON webinars(db_id);"
        ]
        for sql in sqls:
            await self.connect.execute(sql)


class WebinarDAOImpl(AbstractWebinarDAO, BaseDAO):
    connect: AsyncConnection[DictRow]

    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect
        self.retort = Retort()

    async def create(self, model: CreateWebinarDTO) -> None:
        sql = """
            INSERT INTO webinars(url, name)
            VALUES (%(url)s, %(name)s);
        """
        async with self.connect.cursor() as cursor:
            try:
                await cursor.execute(sql, asdict(model))
            except UniqueViolation as exception:
                raise DuplicateWebinar from exception

    async def pagination(self, model: PaginationWebinarDTO) -> WebinarEntities:
        sql = """
            SELECT db_id,
                   url,
                   name
              FROM webinars
            ORDER BY db_id
            LIMIT %(limit)s OFFSET %(offset)s;
        """
        async with self.connect.cursor() as cursor:
            await cursor.execute(sql, asdict(model))
            raw_data = cast(list[dict[str, Any]], await cursor.fetchall())
        if not raw_data:
            raise NotFoundWebinars
        return self.retort.load({"webinars": raw_data}, WebinarEntities)
