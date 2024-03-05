from abc import abstractmethod
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from psycopg.errors import UniqueViolation

from webinar.application.dto.common import TgUserIdDTO
from webinar.application.interfaces.gateways.homework import HomeWorkGateway
from webinar.application.interfaces.uow import DBUoW
from webinar.application.use_case.base import UseCase
from webinar.domain.enums.homework import HomeWorkStatusType
from webinar.domain.types import HomeWorkNumber, TgUserId


@dataclass(frozen=True, slots=True)
class AddUserHomeWorkDTO(TgUserIdDTO):
    telegram_user_id: TgUserId
    date_time_registration: datetime
    status_type: HomeWorkStatusType
    number: HomeWorkNumber
    url: str
    comments: str | None = None
    evaluation: str | None = None


class AddUserHomeWork(UseCase[AddUserHomeWorkDTO, None], Protocol):
    @abstractmethod
    async def __call__(self, data: AddUserHomeWorkDTO) -> None:
        raise NotImplementedError


class AddUserHomeWorkImpl(AddUserHomeWork):
    _db_uow: DBUoW
    _homework_gateway: HomeWorkGateway
    
    def __init__(
        self,
        db_uow: DBUoW,
        homework_gateway: HomeWorkGateway,
    ) -> None:
        self._db_uow = db_uow
        self._homework_gateway = homework_gateway
    
    async def __call__(self, data: AddUserHomeWorkDTO) -> None:
        async with self._db_uow.transaction():
            with suppress(UniqueViolation):
                await self._homework_gateway.add_user_homework(data)
