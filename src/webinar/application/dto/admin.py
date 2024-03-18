from dataclasses import dataclass

from webinar.application.dto.common import TgUserIdDTO
from webinar.domain.enums.direction_type import DirectionTrainingType
from webinar.domain.types import TgUserId


@dataclass(frozen=True, slots=True)
class ReadAdminByLettersRangeData:
    telegram_user_id: TgUserId
    direction_training: DirectionTrainingType


@dataclass(frozen=True, slots=True)
class CreateAdminDTO(TgUserIdDTO):
    direction_training: DirectionTrainingType
    letters_range: str | None = None
    numbers_range: bool = False
