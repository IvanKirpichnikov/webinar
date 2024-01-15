from dataclasses import dataclass

from webinar.application.schemas.dto.base import DataAccessObject
from webinar.application.schemas.enums.direction_type import DirectionTrainingType
from webinar.application.schemas.types import (
    TelegramChatId,
    TelegramUserId
)


@dataclass(frozen=True, slots=True)
class TelegramUserIdDTO(DataAccessObject):
    telegram_user_id: TelegramUserId


@dataclass(frozen=True, slots=True)
class TelegramChatIdDTO(DataAccessObject):
    telegram_chat_id: TelegramChatId


@dataclass(frozen=True, slots=True)
class ResultExistsDTO(DataAccessObject):
    result: bool


@dataclass(frozen=True, slots=True)
class DirectionsTrainingDTO(DataAccessObject):
    directions_training: list[DirectionTrainingType]


@dataclass(frozen=True, slots=True)
class DirectionTrainingDTO(DataAccessObject):
    direction_training: DirectionTrainingType
