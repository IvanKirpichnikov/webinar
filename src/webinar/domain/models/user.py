from dataclasses import dataclass
from datetime import datetime

from webinar.domain.enums.direction_type import (
    DirectionTrainingType,
)
from webinar.domain.types import TgUserId, UserDataBaseId


@dataclass(frozen=True, slots=True)
class User:
    db_id: UserDataBaseId
    telegram_user_id: TgUserId
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
class Users:
    users: list[User]
