from dataclasses import dataclass

from src.application.schemas.enums import DirectionEnum
from src.application.schemas.types import UserId


@dataclass(frozen=True, slots=True)
class AddAdminDTO:
    user_id: UserId
    direction_type: DirectionEnum


@dataclass(frozen=True, slots=True)
class AdminUserId:
    user_id: UserId
