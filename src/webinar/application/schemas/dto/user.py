from dataclasses import dataclass
from datetime import datetime

from webinar.application.schemas.dto.common import TelegramUserIdDTO
from webinar.application.schemas.enums.direction_type import (
    DirectionTrainingType,
)
from webinar.application.schemas.types import TelegramChatId, TelegramUserId


@dataclass(frozen=True, slots=True)
class CreateUserDTO(TelegramUserIdDTO):
    telegram_chat_id: TelegramChatId
    date_time_registration: datetime
    direction_training: DirectionTrainingType
    email: str
    surname: str
    name: str
    patronymic: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateUserDataGoogleSheetsDto:
    telegram_user_id: TelegramUserId
    homeworks_data: list[str | None]
    email: str
    sup: str
