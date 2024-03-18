from aiogram import F, Router
from aiogram.types import CallbackQuery, InaccessibleMessage

from webinar.presentation.annotaded import GetStatsDepends
from webinar.presentation.inject import inject, InjectStrategy
from webinar.presentation.tgbot.keyboard import KeyboardFactory


route = Router()
route.callback_query.filter(F.data == "stats")


@route.callback_query(F.data == "stats")
@inject(InjectStrategy.HANDLER)
async def stats_handler(
    event: CallbackQuery,
    use_case: GetStatsDepends,
    keyboard: KeyboardFactory,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    stats = await use_case()
    await event.message.edit_text(
        stats.string, reply_markup=keyboard.inline.back("admin_panel")
    )
