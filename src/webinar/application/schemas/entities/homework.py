from dataclasses import dataclass
from datetime import datetime
from typing import Final

from aiogram import html

from webinar.application.schemas.entities.user import UserEntity
from webinar.application.schemas.enums.homework import HomeWorkStatusType
from webinar.application.schemas.types import (
    DataBaseId,
    HomeWorkNumber,
    TelegramUserId,
)


HOMEWORK_RU: Final = {
    HomeWorkStatusType.ACCEPTED: "Сдано",
    HomeWorkStatusType.UNDER_INSPECTION: "На проверке",
    HomeWorkStatusType.UNDER_REVISION: "На доработке",
}

HOMEWORK_EMOJI: Final = {
    HomeWorkStatusType.ACCEPTED: "✅",
    HomeWorkStatusType.UNDER_INSPECTION: "⌛",
    HomeWorkStatusType.UNDER_REVISION: "❓",
}


@dataclass(slots=True)
class HomeWorkEntity:
    db_id: DataBaseId
    db_user_id: TelegramUserId
    date_time_registration: datetime
    status_type: HomeWorkStatusType
    number: HomeWorkNumber
    url: str
    comments: str | None = None
    evaluation: str | None = None

    def __post_init__(self) -> None:
        if self.status_type != HomeWorkStatusType.UNDER_REVISION:
            self.comments = None

    def string(self, russian_language: bool = False) -> str:
        status_type = HOMEWORK_EMOJI[self.status_type]
        if russian_language:
            status_type = HOMEWORK_RU[self.status_type]
        number = f"№ {self.number}"
        date_time = self.date_time_registration.strftime("%d.%m")
        url = html.link("ссылка", self.url)
        comments = self.comments
        evaluation = self.evaluation

        if evaluation:
            return f"{status_type} {number} {date_time} {url}\n{evaluation}"
        if comments:
            return f"{status_type} {number} {date_time} {url}\n{html.quote(comments)}"
        return f"{status_type} {number} {date_time} {url}"


@dataclass(frozen=True, slots=True)
class HomeWorkEntities:
    homeworks: list[HomeWorkEntity]

    def string(self) -> str:
        return "\n".join(map(lambda x: x.string(), self.homeworks))


@dataclass(frozen=True, slots=True)
class UserHomeWorkEntity:
    db_id: DataBaseId
    date_time_registration: datetime
    number: HomeWorkNumber
    surname: str
    name: str
    patronymic: str | None = None
    evaluation: str | None = None

    def string(self) -> str:
        date_time = self.date_time_registration.strftime("%d.%m")
        number = self.number
        surname = self.surname[0].title()
        name = self.name[0].title()
        patronymic = self.patronymic
        if patronymic:
            patronymic = patronymic[0].title()
            return f"№{number} {date_time} {surname} {name}.{patronymic}."
        return f"№{number} {date_time} {surname} {name}."


@dataclass(frozen=True, slots=True)
class UserHomeWorkEntities:
    homeworks: list[UserHomeWorkEntity]


@dataclass(frozen=True, slots=True)
class HomeWorkAndUserInfoEntity(UserEntity):
    date_time_registration: datetime
    number: HomeWorkNumber
    url: str
    evaluation: str | None = None


@dataclass(frozen=True, slots=True)
class HomeWorkStatsEntity:
    first: int = 0
    second: int = 0
    third: int = 0
    fourth: int = 0
    fifth: int = 0
    sixth: int = 0
    seventh: int = 0


@dataclass(frozen=True, slots=True)
class HomeWorkStatsEntities:
    smm: HomeWorkStatsEntity
    copyrighting: HomeWorkStatsEntity
