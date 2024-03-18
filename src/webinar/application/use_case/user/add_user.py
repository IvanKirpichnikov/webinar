from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from logging import getLogger
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
    async def __call__(self, data: AddUserDTO) -> None:
        raise NotImplementedError


class AddUserUseCaseImpl(AddUserUseCase):
    logger = getLogger(__name__)
    
    def __init__(
        self,
        uow: DBUoW,
        gateway: UserGateway
    ) -> None:
        self._uow = uow
        self._gateway = gateway
    
    async def __call__(self, data: AddUserDTO) -> None:
        async with self._uow.transaction():
            await self._gateway.create(data)
            self.logger.info('Create user. %r' % data)
