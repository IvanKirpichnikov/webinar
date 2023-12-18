from typing import Any, Awaitable, Callable, cast

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from src.application.config import ConfigFactory


class IsSuperAdminMiddlewareImpl(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = cast(User | None, data.get('event_from_user'))
        if user is None:
            return await handler(event, data)
        
        config = cast(ConfigFactory, data.get('config'))
        owner_user_id = config.config.const.owner_user_id
        data['is_super_admin'] = owner_user_id == user.id
        return await handler(event, data)
