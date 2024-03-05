from dataclasses import dataclass

from webinar.application.dto.base import DataAccessObject
from webinar.domain.types import (
    TgUserId,
)


@dataclass(frozen=True, slots=True)
class UpdateUserDataGoogleSheetsDto(DataAccessObject):
    telegram_user_id: TgUserId
    homeworks_data: list[str | None]
    email: str
    sup: str
