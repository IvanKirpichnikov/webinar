from aiogram.filters import BaseFilter
from aiogram.types import Message, TelegramObject, User

from src.application.interfaces.repository.user import AbstractUser
from src.infrastructure.cache import CacheAdapter


class CheckUserRegisteringFilter(BaseFilter):
    async def __call__(
        self,
        event: TelegramObject,
        event_from_user: User | None,
        user_repository: AbstractUser,
        cache: CacheAdapter
    ) -> bool:
        if event_from_user is None:
            return False
        
        user_id = event_from_user.id
        
        if user_id in cache.check_user:
            return cache.check_user[user_id]
        
        data = await user_repository.check(user_id)
        cache.check_user[user_id] = data
        return data
