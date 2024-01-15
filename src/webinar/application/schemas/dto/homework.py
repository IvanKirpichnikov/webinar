from dataclasses import dataclass
from datetime import datetime

from webinar.application.schemas.dto.base import DataAccessObject
from webinar.application.schemas.dto.common import TelegramUserIdDTO
from webinar.application.schemas.enums.direction_type import DirectionTrainingType
from webinar.application.schemas.enums.homework import HomeWorkStatusType
from webinar.application.schemas.types import (
    DataBaseId,
    HomeWorkNumber
)


@dataclass(frozen=True, slots=True)
class CreateHomeWorkDTO(TelegramUserIdDTO):
    date_time_registration: datetime
    status_type: HomeWorkStatusType
    number: HomeWorkNumber
    url: str
    comments: str | None = None
    evaluation: str | None = None


@dataclass(frozen=True, slots=True)
class TelegramUserIdAndStatusTypeDTO(TelegramUserIdDTO):
    status_type: HomeWorkStatusType


@dataclass(frozen=True, slots=True)
class UpdatingTypeByIdDTO(DataAccessObject):
    db_id: DataBaseId
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
class HomeWorkPaginationDTO(TelegramUserIdDTO):
    direction_training: list[DirectionTrainingType]
    count_homeworks: int
    limit: int
    offset: int
    numbers_range: bool = False
    letters_range: str | None = None
