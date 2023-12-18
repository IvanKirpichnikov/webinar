from dataclasses import dataclass
from datetime import datetime
from typing import Final

from src.application.schemas.enums import DirectionEnum
from src.application.schemas.enums.homework import HomeWorkTypeEnum
from src.application.schemas.types import UserId


HOMEWORK_TYPES: Final = {
    HomeWorkTypeEnum.ACCEPTED: '✅',
    HomeWorkTypeEnum.UNDER_INSPECTION: '⌛',
    HomeWorkTypeEnum.UNDER_REVISION: '❓'
}

HOMEWORK_TYPES_RU: Final = {
    HomeWorkTypeEnum.ACCEPTED: 'Сдано',
    HomeWorkTypeEnum.UNDER_INSPECTION: 'На проверке',
    HomeWorkTypeEnum.UNDER_REVISION: 'На доработке'
}


@dataclass(frozen=True, slots=True)
class AddHomeWorkDTO:
    user_id: UserId
    date_time: datetime
    number: int
    url: str
    type: HomeWorkTypeEnum
    comments: str | None = None


@dataclass(frozen=True, slots=True)
class HomeWorkUserId:
    user_id: UserId


@dataclass(frozen=True, slots=True)
class HomeWorkDTO:
    id: int
    user_id: UserId
    date_time: datetime
    number: int
    url: str
    type: str
    comments: str | None = None
    
    @property
    def string(self) -> str:
        type_ = HOMEWORK_TYPES.get(HomeWorkTypeEnum(self.type))
        dt = self.date_time.strftime('%m.%d.%y')
        
        if type_ is None:
            raise ValueError('Not support homework type')
        final_str = f'{type_} №{self.number} {dt} <a href="{self.url}">ссылка</a>'
        if self.comments:
            final_str += f'\nКомментарий: {self.comments}'
        return final_str


@dataclass(frozen=True, slots=True)
class UpdatingTypeAndCommentByIdDTO:
    homework_id: int
    type: HomeWorkTypeEnum
    comment: str


@dataclass(frozen=True, slots=True)
class UpdatingTypeByIdDTO:
    homework_id: int
    type: HomeWorkTypeEnum


@dataclass(frozen=True, slots=True)
class GetHomeWorkAllByUserIdByType:
    user_id: UserId
    type: list[HomeWorkTypeEnum]
    

@dataclass(frozen=True, slots=True)
class GetHomeWorkWithInformationForAdminDTO:
    homework_id: int


@dataclass(frozen=True, slots=True)
class HomeWorkWithInformationForAdminDTO:
    id: int
    number: int
    url: str
    date_time: datetime
    user_id: UserId
    chat_id: int
    surname: str
    name: str
    direction: DirectionEnum
    email: str
    patronymic: str | None = None


@dataclass(frozen=True, slots=True)
class PaginationHomeWorkDTO:
    offset: int
    direction_types: list[DirectionEnum]


@dataclass(frozen=True, slots=True)
class HomeWorkPaginationDTO:
    id: int
    number: int
    date_time: datetime
    surname: str
    name: str
    patronymic: str | None = None


@dataclass(frozen=True, slots=True)
class NumberHomeWorkDTO:
    number: int


@dataclass(frozen=True, slots=True)
class HomeWorkSpreadSheetDTO:
    type_1: str | None = None
    type_2: str | None = None
    type_3: str | None = None
    type_4: str | None = None
    type_5: str | None = None
    type_6: str | None = None
