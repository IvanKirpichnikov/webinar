from dataclasses import dataclass

from webinar.application.dto.base import DataAccessObject
from webinar.domain.enums.direction_type import DirectionTrainingType
from webinar.domain.types import (
    TgChatId,
    TgUserId
)


@dataclass(frozen=True, slots=True)
class TgUserIdDTO(DataAccessObject):
    telegram_user_id: TgUserId


@dataclass(frozen=True, slots=True)
class TgChatIdDTO(DataAccessObject):
    telegram_chat_id: TgChatId


@dataclass(frozen=True, slots=True)
class ResultExistsDTO(DataAccessObject):
    result: bool


@dataclass(frozen=True, slots=True)
class DirectionsTrainingDTO(DataAccessObject):
    directions_training: list[DirectionTrainingType]


@dataclass(frozen=True, slots=True)
class DirectionTrainingDTO(DataAccessObject):
    direction_training: DirectionTrainingType
