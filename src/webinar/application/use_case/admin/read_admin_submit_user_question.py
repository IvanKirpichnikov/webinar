from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from webinar.application.dto.common import DirectionsTrainingDTO, TgChatIdDTO
from webinar.application.interactions.admin.read_admin_by_letters_range import (
    ReadAdminByLettersRange,
    ReadAdminByLettersRangeData,
)
from webinar.application.interactions.admin.read_random_admin import ReadRandomAdmin
from webinar.application.use_case.base import UseCase
from webinar.domain.enums.direction_type import DirectionTrainingType
from webinar.domain.types import TgUserId


@dataclass
class ReadAdminSubmitUserQuestionData:
    telegram_user_id: TgUserId
    direction_training: DirectionTrainingType


class ReadAdminSubmitUserQuestion(
    UseCase[ReadAdminSubmitUserQuestionData, TgChatIdDTO | None],
    Protocol
):
    @abstractmethod
    async def __call__(
        self, data: ReadAdminSubmitUserQuestionData
    ) -> TgChatIdDTO | None:
        raise NotImplementedError


class ReadAdminSubmitUserQuestionImpl(
    ReadAdminSubmitUserQuestion
):
    _read_random_admin: ReadRandomAdmin
    _read_admin_by_letters_range: ReadAdminByLettersRange
    
    def __init__(
        self,
        read_random_admin: ReadRandomAdmin,
        read_admin_by_letters_range: ReadAdminByLettersRange,
    ) -> None:
        self._read_random_admin = read_random_admin
        self._read_admin_by_letters_range = read_admin_by_letters_range
    
    async def __call__(
        self, data: ReadAdminSubmitUserQuestionData
    ) -> TgChatIdDTO | None:
        result = await self._read_admin_by_letters_range(
            ReadAdminByLettersRangeData(
                telegram_user_id=data.telegram_user_id,
                direction_training=data.direction_training,
            )
        )
        if result is None:
            result = await self._read_random_admin(
                DirectionsTrainingDTO(
                    directions_training=[data.direction_training]
                )
            )
        return result
