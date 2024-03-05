from contextlib import suppress

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from webinar.application.interfaces.delete_message import DeleteMessageData, TgDeleteMessage


class AiogramDeleteMessage(TgDeleteMessage):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
    
    async def __call__(self, data: DeleteMessageData) -> None:
        with suppress(TelegramBadRequest):
            if isinstance(data.message_id, list):
                await self.bot.delete_messages(
                    chat_id=data.chat_id,
                    message_ids=data.message_id
                )
                return None
            
            if data.message_id == data.inline_message_id:
                return None
            await self.bot.delete_message(
                chat_id=data.chat_id,
                message_id=data.message_id
            )
