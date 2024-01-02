from dataclasses import dataclass

from webinar.application.schemas.enums.direction_type import (
    DirectionTrainingType,
)
from webinar.application.schemas.types import TelegramUserId


@dataclass(frozen=True, slots=True)
class TelegramUserIdDTO:
    telegram_user_id: TelegramUserId


@dataclass(frozen=True, slots=True)
class ResultExistsDTO:
    result: bool


@dataclass(frozen=True, slots=True)
class DirectionsTrainingDTO:
    directions_training: list[DirectionTrainingType]


@dataclass(frozen=True, slots=True)
class DirectionTrainingDTO:
    direction_training: DirectionTrainingType


@dataclass(frozen=True, slots=True)
class UserExistsDTO(TelegramUserIdDTO):
    pass
