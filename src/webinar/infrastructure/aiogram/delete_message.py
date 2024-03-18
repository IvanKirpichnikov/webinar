from logging import getLogger

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from webinar.application.interfaces.delete_message import DeleteMessageData, TgDeleteMessage


class AiogramDeleteMessage(TgDeleteMessage):
    logger = getLogger(__name__)
    
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
    
    async def __call__(self, data: DeleteMessageData) -> None:
        if isinstance(data.message_id, list):
            try:
                await self.bot.delete_messages(
                    chat_id=data.chat_id,
                    message_ids=data.message_id
                )
            except TelegramBadRequest:
                self.logger.info(
                    'No delete deleted messages id (%r) in %r.'
                    % (data.message_id, data.chat_id)
                )
            else:
                self.logger.info(
                    'Deleted messages id (%r) in %r.'
                    % (data.message_id, data.chat_id)
                )
            return None
        
        if data.message_id == data.inline_message_id:
            return None
        
        try:
            await self.bot.delete_message(
                chat_id=data.chat_id,
                message_id=data.message_id
            )
        except TelegramBadRequest:
            self.logger.info(
                'No deleted message id (%r) in %r.'
                % (data.message_id, data.chat_id)
            )
        else:
            self.logger.info(
                'Deleted message id (%r) in %r.'
                % (data.message_id, data.chat_id)
            )
            
