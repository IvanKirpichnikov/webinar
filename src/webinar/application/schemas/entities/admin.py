from dataclasses import dataclass

from webinar.application.schemas.entities.user import UserEntity
from webinar.application.schemas.enums.direction_type import DirectionTrainingType
from webinar.application.schemas.types import UserDataBaseId


@dataclass(frozen=True, slots=True)
class AdminEntity(UserEntity):
    direction_training: DirectionTrainingType
    letters_range: str | None = None
    numbers_range: bool = False
    
    def string(self) -> str:
        name = self.name.title()
        surname = self.surname.title()
        return f"{name} {surname}"


@dataclass(frozen=True, slots=True)
class AdminEntities:
    admins: list[AdminEntity]
    
    def string(self) -> str:
        data = map(lambda x: x.string(), self.admins)
        return "\n".join(data)


@dataclass(frozen=True, slots=True)
class AdminDataInfoEntity:
    db_user_id: UserDataBaseId
    direction_training: DirectionTrainingType
    letters_range: str | None = None
    numbers_range: bool = False
