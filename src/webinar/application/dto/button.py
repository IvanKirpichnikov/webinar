from dataclasses import dataclass

from webinar.application.dto.base import DataAccessObject


@dataclass(frozen=True, slots=True)
class BackButtonDataDTO(DataAccessObject):
    text: str
    callback_data: str
