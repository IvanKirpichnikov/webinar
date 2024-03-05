from dataclasses import dataclass

from webinar.application.dto.common import TgUserIdDTO
from webinar.domain.enums.direction_type import DirectionTrainingType


@dataclass(frozen=True, slots=True)
class CreateAdminDTO(TgUserIdDTO):
    direction_training: DirectionTrainingType
    letters_range: str | None = None
    numbers_range: bool = False

@dataclass(frozen=True, slots=True)
class GetAdminFromDirectionTraining(TgUserIdDTO):
    direction_training: DirectionTrainingType
