from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.application.exceptions import NotFoundWebinars
from webinar.application.schemas.dto.webinar import (
    CreateWebinarDTO,
    PaginationWebinarDTO,
)
from webinar.application.schemas.entities.webinar import WebinarEntities
from webinar.infrastructure.database.dao.webinar import WebinarDAOImpl
from webinar.infrastructure.database.repository.base import BaseRepository


class WebinarRepositoryImpl(BaseRepository):
    connect: AsyncConnection[DictRow]

    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect

    def dao(self) -> WebinarDAOImpl:
        return WebinarDAOImpl(self.connect)

    async def create(self, model: CreateWebinarDTO) -> None:
        dao = self.dao()
        return await dao.create(model)

    async def pagination(self, model: PaginationWebinarDTO) -> WebinarEntities:
        dao = self.dao()
        data = await dao.pagination(model)

        if data.count > 0 and not data.webinars:
            raise NotFoundWebinars

        return data
