from aiogram import F, Router
from aiogram.types import CallbackQuery
from faststream.nats import NatsBroker

from webinar.presentation.tgbot.keyboard import KeyboardFactory


route = Router()


@route.callback_query(F.data == "update_google_tables")
async def update_google_tables_handler(
    event: CallbackQuery,
    broker: NatsBroker,
    keyboard: KeyboardFactory,
    is_super_admin: bool,
) -> None:
    await broker.publish(message="", subject="update.google_sheets")
    await event.answer("Обновление произошло", show_alert=True)
