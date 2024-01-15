from dataclasses import dataclass

from webinar.application.schemas.dto.base import DataAccessObject


@dataclass(frozen=True, slots=True)
class CreateWebinarDTO(DataAccessObject):
    url: str
    name: str


@dataclass(frozen=True, slots=True)
class PaginationWebinarDTO(DataAccessObject):
    limit: int
    offset: int
