from dataclasses import dataclass

from webinar.application.schemas.dto.common import TelegramUserIdDTO
from webinar.application.schemas.enums.direction_type import DirectionTrainingType


@dataclass(frozen=True, slots=True)
class CreateAdminDTO(TelegramUserIdDTO):
    direction_training: DirectionTrainingType
    letters_range: str | None = None
    numbers_range: bool = False

@dataclass(frozen=True, slots=True)
class GetAdminFromDirectionTraining(TelegramUserIdDTO):
    direction_training: DirectionTrainingType
