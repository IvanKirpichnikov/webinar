from dataclasses import dataclass
from datetime import datetime

from webinar.application.schemas.enums.direction_type import (
    DirectionTrainingType,
)
from webinar.application.schemas.types import TelegramUserId, UserDataBaseId


@dataclass(frozen=True, slots=True)
class UserEntity:
    db_id: UserDataBaseId
    telegram_user_id: TelegramUserId
    telegram_chat_id: int
    date_time_registration: datetime
    direction_training: DirectionTrainingType
    email: str
    surname: str
    name: str
    patronymic: str | None

    @property
    def surname_and_name(self) -> str:
        return f"{self.surname} {self.name}"

    @property
    def sup(self) -> str:
        if self.patronymic:
            return f"{self.surname} {self.name} {self.patronymic}"
        return f"{self.surname} {self.name}"


@dataclass(frozen=True, slots=True)
class UserEntities:
    users: list[UserEntity]


@dataclass(frozen=True, slots=True)
class UserStatsEntity:
    homework_smm: int = 0
    homework_copyrighting: int = 0
    users: int = 0
    smm: int = 0
    copyrighting: int = 0
