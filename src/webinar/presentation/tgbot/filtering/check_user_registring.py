from aiogram.filters import BaseFilter
from aiogram.types import (
    TelegramObject,
    User
)

from webinar.application.dto import TgUserIdDTO
from webinar.domain.types import TgUserId
from webinar.infrastructure.adapters.cache import CacheStore
from webinar.infrastructure.postgres.repository.user import UserRepositoryImpl


class CheckUserRegisteringFilter(BaseFilter):
    async def __call__(
        self,
        event: TelegramObject,
        event_from_user: User | None,
        user_repository: UserRepositoryImpl,
        cache: CacheStore
    ) -> bool:
        if event_from_user is None:
            return False
        
        user_id = TgUserId(event_from_user.id)
        if user_id in cache.exists_user:
            return cache.exists_user[user_id].result
        
        dto = TgUserIdDTO(user_id)
        data = await user_repository.exists(dto)
        cache.exists_user[user_id] = data
        return data.result
