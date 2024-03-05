from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from webinar.application.dto.common import TgChatIdDTO
from webinar.application.interactions.base import Interactor
from webinar.application.interfaces.gateways.admin import AdminGateway
from webinar.domain.enums.direction_type import DirectionTrainingType
from webinar.domain.types import TgUserId


@dataclass(frozen=True, slots=True)
class ReadAdminByLettersRangeData:
    telegram_user_id: TgUserId
    direction_training: DirectionTrainingType


class ReadAdminByLettersRange(
    Interactor[ReadAdminByLettersRangeData, TgChatIdDTO | None],
    Protocol
):
    @abstractmethod
    async def __call__(
        self, data: ReadAdminByLettersRangeData
    ) -> TgChatIdDTO | None:
        raise NotImplementedError


class ReadAdminByLettersRangeImpl(ReadAdminByLettersRange):
    _admin_gateway: AdminGateway
    
    def __init__(
        self,
        admin_gateway: AdminGateway
    ) -> None:
        self._admin_gateway = admin_gateway
    
    async def __call__(
        self, data: ReadAdminByLettersRangeData
    ) -> TgChatIdDTO | None:
        result = await self._admin_gateway.read_by_letters_range(data)
        return result
