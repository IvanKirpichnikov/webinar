from abc import abstractmethod
from typing import Protocol

from webinar.application.schemas.dto.webinar import (
    CreateWebinarDTO,
    PaginationWebinarDTO,
)
from webinar.application.schemas.entities.webinar import WebinarEntities


class AbstractWebinarDAO(Protocol):
    @abstractmethod
    async def create(self, model: CreateWebinarDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def pagination(self, model: PaginationWebinarDTO) -> WebinarEntities:
        raise NotImplementedError
