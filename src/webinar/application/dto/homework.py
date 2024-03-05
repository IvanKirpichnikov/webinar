from dataclasses import dataclass

from webinar.application.dto.base import DataAccessObject
from webinar.application.dto.common import TgUserIdDTO
from webinar.domain.enums.direction_type import DirectionTrainingType
from webinar.domain.enums.homework import HomeWorkStatusType





@dataclass(frozen=True, slots=True)
class TgUserIdAndStatusTypeDTO(TgUserIdDTO):
    status_type: HomeWorkStatusType





@dataclass(frozen=True, slots=True)
class UpdatingTypeAndCommentByIdDTO(UpdatingTypeByIdDTO):
    comments: str | None = None


@dataclass(frozen=True, slots=True)
class UpdatingEvaluationByIdDTO(UpdatingTypeByIdDTO):
    evaluation: str


@dataclass(frozen=True, slots=True)
class HomeWorkIdDTO(DataAccessObject):
    db_id: int


@dataclass(frozen=True, slots=True)
class HomeWorkPaginationDTO(TgUserIdDTO):
    direction_training: list[DirectionTrainingType]
    count_homeworks: int
    limit: int
    offset: int
    numbers_range: bool = False
    letters_range: str | None = None
