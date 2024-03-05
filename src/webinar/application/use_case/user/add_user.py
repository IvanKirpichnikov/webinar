from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from webinar.application.interfaces.gateways.user import UserGateway
from webinar.application.interfaces.uow import DBUoW
from webinar.application.use_case.base import UseCase
from webinar.domain.enums.direction_type import DirectionTrainingType
from webinar.domain.types import TgChatId, TgUserId


@dataclass(frozen=True, slots=True)
class AddUserDTO:
    telegram_user_id: TgUserId
    telegram_chat_id: TgChatId
    date_time_registration: datetime
    direction_training: DirectionTrainingType
    email: str
    surname: str
    name: str
    patronymic: str | None = None


class AddUserUseCase(UseCase[AddUserDTO, None], Protocol):
    @abstractmethod
    async def __call__(self, model: AddUserDTO) -> None:
        raise NotImplementedError


class AddUserUseCaseImpl(AddUserUseCase):
    _db_uow: DBUoW
    _user_gateway: UserGateway
    
    def __init__(
        self,
        db_uow: DBUoW,
        user_gateway: UserGateway
    ) -> None:
        self._db_uow = db_uow
        self._user_gateway = user_gateway
    
    async def __call__(self, model: AddUserDTO) -> None:
        async with self._db_uow.transaction():
            await self._user_gateway.create(model)
