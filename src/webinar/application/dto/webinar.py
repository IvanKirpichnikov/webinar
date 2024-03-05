from dataclasses import dataclass

from webinar.application.dto.base import DataAccessObject


@dataclass(frozen=True, slots=True)
class CreateWebinarDTO(DataAccessObject):
    url: str
    name: str


