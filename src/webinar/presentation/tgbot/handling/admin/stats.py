from aiogram import F, Router
from aiogram.types import CallbackQuery, InaccessibleMessage

from webinar.infrastructure.database.repository.stats import (
    StatsRepositoryImpl,
)
from webinar.presentation.tgbot.keyboard import KeyboardFactory


route = Router()
route.callback_query.filter(F.data == "stats")


@route.callback_query(F.data == "stats")
async def stats_handler(
    event: CallbackQuery,
    stats_repository: StatsRepositoryImpl,
    keyboard: KeyboardFactory,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return

    stats = await stats_repository.read()
    await event.message.edit_text(
        stats.string, reply_markup=keyboard.inline.back("admin_panel")
    )
