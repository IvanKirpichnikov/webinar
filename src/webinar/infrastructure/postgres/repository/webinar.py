from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.application.dto.webinar import (
    CreateWebinarDTO,
)
from webinar.infrastructure.postgres.gateways.webinar import PostgresWebinarGateway
from webinar.infrastructure.postgres.repository.base import BaseRepository


class WebinarRepositoryImpl(BaseRepository):
    connect: AsyncConnection[DictRow]
    
    def __init__(self, connect: AsyncConnection[DictRow]) -> None:
        self.connect = connect
    
    def dao(self) -> PostgresWebinarGateway:
        return PostgresWebinarGateway(self.connect)
    
    async def create(self, model: CreateWebinarDTO) -> None:
        dao = self.dao()
        return await dao.create(model)
