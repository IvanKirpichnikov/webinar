from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject, User
from dishka.async_container import AsyncContainer


class ContainerMiddleware(BaseMiddleware):
    _container: AsyncContainer
    
    def __init__(self, container: AsyncContainer):
        self._container = container
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        context = {
            User | None: data['event_from_user'],
            FSMContext: data['state'],
            TelegramObject: event,
            Bot: data['bot'],
        }
        
        async with self._container(context=context) as container:
            data["dishka_container"] = container
            return await handler(event, data)
