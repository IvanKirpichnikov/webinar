from aiogram.filters import BaseFilter
from aiogram.types import (
    TelegramObject,
    User,
)

from webinar.application.dto.common import TgUserIdDTO
from webinar.domain.types import TgUserId
from webinar.infrastructure.adapters.cache import CacheStore
from webinar.presentation.annotaded import UserIsExistsDepends
from webinar.presentation.inject import inject, InjectStrategy


class CheckUserRegisteringFilter(BaseFilter):
    @inject(InjectStrategy.HANDLER)
    async def __call__(
        self,
        event: TelegramObject,
        event_from_user: User | None,
        use_case: UserIsExistsDepends,
        cache: CacheStore
    ) -> bool:
        if event_from_user is None:
            return False
        
        user_id = TgUserId(event_from_user.id)
        if user_id in cache.exists_user:
            return cache.exists_user[user_id].result
        
        data = await use_case(TgUserIdDTO(user_id))
        cache.exists_user[user_id] = data
        return data.result
