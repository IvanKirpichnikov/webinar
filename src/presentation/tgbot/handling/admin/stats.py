from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.application.interfaces.repository.stats import AbstractStats
from src.presentation.tgbot.keyboard import KeyboardFactory


route = Router()
route.callback_query.filter(F.data == 'stats')


@route.callback_query(F.data == 'stats')
async def stats_handler(
    event: CallbackQuery,
    keyboard: KeyboardFactory,
    stats_repository: AbstractStats
) -> None:
    if event.message is None:
        return
    
    stats = await stats_repository.stats()
    await event.message.edit_text(
        stats.string,
        reply_markup=keyboard.inline.back('admin_panel')
    )
