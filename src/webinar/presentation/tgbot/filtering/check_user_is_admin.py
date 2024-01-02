from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject, User

from webinar.application.config import ConfigFactory
from webinar.application.schemas.dto.common import TelegramUserIdDTO
from webinar.application.schemas.types import TelegramUserId
from webinar.infrastructure.adapters.cache import CacheStore
from webinar.infrastructure.database.repository.admin import (
    AdminRepositoryImpl,
)


class CheckUserIsAdminRegisteringFilterImpl(BaseFilter):
    async def __call__(
        self,
        event: TelegramObject,
        event_from_user: User | None,
        admin_repository: AdminRepositoryImpl,
        cache: CacheStore,
        config: ConfigFactory,
    ) -> bool:
        if event_from_user is None:
            return False

        user_id = TelegramUserId(event_from_user.id)
        if user_id == config.config.const.owner_user_id:
            return True

        if user_id in cache.exists_admin:
            return cache.exists_admin[user_id].result

        data = await admin_repository.exists(
            TelegramUserIdDTO(TelegramUserId(user_id))
        )
        cache.exists_admin[user_id] = data
        return data.result
