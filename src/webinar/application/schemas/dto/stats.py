from dataclasses import dataclass

from webinar.application.schemas.dto.base import DataAccessObject


@dataclass(frozen=True, slots=True)
class CountHomeWorkDTO(DataAccessObject):
    smm: int = 0
    copyrighting: int = 0
