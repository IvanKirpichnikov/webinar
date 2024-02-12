from aiogram import (
    F,
    Router
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    Message
)

from webinar.presentation.tgbot.keyboard import KeyboardFactory


route = Router()
route.message.filter(CommandStart())
route.callback_query.filter(F.data == "main_menu")


@route.message(CommandStart())
async def main_menu_message_handler(
    event: Message, state: FSMContext, keyboard: KeyboardFactory
) -> None:
    await event.answer(
        "Главное меню",
        reply_markup=keyboard.inline.main_menu()
    )
    await state.clear()


@route.callback_query(F.data == "main_menu")
async def main_menu_callback_handler(
    event: CallbackQuery, state: FSMContext, keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return None
    if isinstance(event.message, InaccessibleMessage):
        await event.answer('Нет доступа к сообщению. Введите /start', show_alert=True)
        return None
    
    await event.message.edit_text(
        "Главное меню",
        reply_markup=keyboard.inline.main_menu()
    )
    await state.clear()
