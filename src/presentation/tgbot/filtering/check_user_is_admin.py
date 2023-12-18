from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject, User

from src.application.config import ConfigFactory
from src.application.interfaces.repository.admin import AbstractAdmin
from src.application.schemas.dto.admin import AdminUserId
from src.application.schemas.types import UserId
from src.infrastructure.cache import CacheAdapter


class CheckUserIsAdminRegisteringFilterImpl(BaseFilter):
    async def __call__(
        self,
        event: TelegramObject,
        event_from_user: User | None,
        admin_repository: AbstractAdmin,
        cache: CacheAdapter,
        config: ConfigFactory
    ) -> bool:
        if event_from_user is None:
            return False
        
        user_id = event_from_user.id
        if user_id == config.config.const.owner_user_id:
            return True
        
        if user_id in cache.user_is_admin:
            return cache.user_is_admin[user_id]
        
        data = await admin_repository.exists(
            AdminUserId(UserId(user_id))
        )
        cache.check_user[user_id] = data
        return data
