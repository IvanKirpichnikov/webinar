from aiogram.filters import BaseFilter
from aiogram.types import (
    TelegramObject,
    User,
)

from webinar.application.dto.common import TgUserIdDTO
from webinar.domain.types import TgUserId
from webinar.infrastructure.adapters.cache import CacheStore
from webinar.presentation.annotaded import ConfigDepends, UserIsAdminDepends
from webinar.presentation.inject import inject, InjectStrategy


class CheckUserIsAdminRegisteringFilterImpl(BaseFilter):
    @inject(InjectStrategy.HANDLER)
    async def __call__(
        self,
        event: TelegramObject,
        event_from_user: User | None,
        use_case: UserIsAdminDepends,
        config: ConfigDepends,
        cache: CacheStore
    ) -> bool:
        if event_from_user is None:
            return False
        
        user_id = TgUserId(event_from_user.id)
        if user_id == config.const.owner_user_id:
            return True
        
        if user_id in cache.exists_admin:
            return cache.exists_admin[user_id].result
        
        dto = TgUserIdDTO(TgUserId(user_id))
        data = await use_case(dto)
        cache.exists_admin[user_id] = data
        return data.result
