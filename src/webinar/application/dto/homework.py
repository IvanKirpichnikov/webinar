from dataclasses import dataclass

from webinar.domain.enums.direction_type import DirectionTrainingType
from webinar.domain.enums.homework import HomeWorkStatusType
from webinar.domain.types import DataBaseId, TgUserId


@dataclass(frozen=True, slots=True)
class UpdateHomeWorkStatusDTO:
    db_id: DataBaseId
    status_type: HomeWorkStatusType


@dataclass(frozen=True, slots=True)
class TgUserIdAndStatusTypeDTO:
    telegram_user_id: TgUserId
    status_type: HomeWorkStatusType


@dataclass(frozen=True, slots=True)
class UpdateHomeworkTypeDTO:
    db_id: int


@dataclass(frozen=True, slots=True)
class UpdateHomeworkStatusAndCommentByIdDTO:
    db_id: DataBaseId
    status_type: HomeWorkStatusType
    comments: str


@dataclass(frozen=True, slots=True)
class UpdateHomeworkEvolutionAndStatusDTO:
    db_id: int
    status_type: HomeWorkStatusType
    evaluation: str


@dataclass(frozen=True, slots=True)
class HomeWorkIdDTO:
    db_id: int


@dataclass(frozen=True, slots=True)
class HomeWorkPaginationDTO:
    telegram_user_id: TgUserId
    direction_training: list[DirectionTrainingType]
    count_homeworks: int
    limit: int
    offset: int
    numbers_range: bool = False
    letters_range: str | None = None
