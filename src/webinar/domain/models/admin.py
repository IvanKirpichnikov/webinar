from dataclasses import dataclass

from webinar.domain.enums.direction_type import DirectionTrainingType
from webinar.domain.types import UserDataBaseId
from webinar.domain.models.user import User


@dataclass(frozen=True, slots=True)
class Admin(User):
    direction_training: DirectionTrainingType
    letters_range: str | None = None
    numbers_range: bool = False
    
    def string(self) -> str:
        name = self.name.title()
        surname = self.surname.title()
        if raw_lr := self.letters_range:
            letters_range = f'{raw_lr[0]}-{raw_lr[-1]}'.title()
            return f"{name} {surname} {letters_range}"
        
        return f"{name} {surname}"


@dataclass(frozen=True, slots=True)
class Admins:
    admins: list[Admin]
    
    def string(self) -> str:
        data = map(lambda x: x.string(), self.admins)
        return "\n".join(data)


@dataclass(frozen=True, slots=True)
class AdminDataInfo:
    db_user_id: UserDataBaseId
    direction_training: DirectionTrainingType
    letters_range: str | None = None
    numbers_range: bool = False
