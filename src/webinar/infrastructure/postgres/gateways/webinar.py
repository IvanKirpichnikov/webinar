from dataclasses import asdict
from typing import Any, cast

from adaptix import Retort
from psycopg.errors import UniqueViolation

from webinar.application.dto.webinar import (
    CreateWebinarDTO,
)
from webinar.application.exceptions import DuplicateWebinar
from webinar.application.interfaces.gateways.webinar import WebinarGateway
from webinar.application.use_case.webinars.get_pagination import GetPaginationWebinarsData
from webinar.domain.models.webinar import Webinars
from webinar.infrastructure.postgres.gateways.base import BaseOtherCreate, PostgresGateway


class WebinarOtherCreateImpl(BaseOtherCreate):
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


class PostgresWebinarGateway(PostgresGateway, WebinarGateway):
    retort = Retort()
    
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
    
    async def pagination(self, model: GetPaginationWebinarsData) -> Webinars | None:
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
            return None
        return self.retort.load({"webinars": raw_data}, Webinars)
