from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject, User

from webinar.application.schemas.dto.common import TelegramUserIdDTO
from webinar.application.schemas.types import TelegramUserId
from webinar.infrastructure.adapters.cache import CacheStore
from webinar.infrastructure.database.repository.user import UserRepositoryImpl


class CheckUserRegisteringFilter(BaseFilter):
    async def __call__(
        self,
        event: TelegramObject,
        event_from_user: User | None,
        user_repository: UserRepositoryImpl,
        cache: CacheStore,
    ) -> bool:
        if event_from_user is None:
            return False

        user_id = TelegramUserId(event_from_user.id)
        if user_id in cache.exists_user:
            return cache.exists_user[user_id].result

        data = await user_repository.exists(TelegramUserIdDTO(user_id))
        cache.exists_user[user_id] = data
        return data.result
