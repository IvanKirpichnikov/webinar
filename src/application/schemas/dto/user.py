from dataclasses import dataclass
from typing import NewType

from src.application.schemas.dto.homework import HomeWorkSpreadSheetDTO
from src.application.schemas.enums import DirectionEnum


UserId = NewType('UserId', int)
IsoDateTime = NewType('IsoDateTime', str)


@dataclass(frozen=True, slots=True)
class AddUserDto:
    date_time: IsoDateTime
    user_id: UserId
    chat_id: int
    surname: str
    name: str
    patronymic: str | None
    email: str
    direction: DirectionEnum


@dataclass(frozen=True, slots=True)
class UserDto:
    id: int
    date_time: IsoDateTime
    user_id: UserId
    chat_id: int
    surname: str
    name: str
    patronymic: str | None
    email: str
    direction: DirectionEnum


@dataclass(frozen=True, slots=True)
class UserMailingDTO:
    chat_id: int


@dataclass(frozen=True, slots=True)
class UpdateUserDataGoogleSheetsDto:
    sup: str
    email: str
    telegram_id: UserId
    homeworks_types: list[str | None]
