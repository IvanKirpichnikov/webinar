from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, Message

from webinar.presentation.tgbot.keyboard import KeyboardFactory


route = Router()


@route.message(Command("admin_panel"))
async def admin_menu_message_handler(
    event: Message,
    state: FSMContext,
    keyboard: KeyboardFactory,
    is_super_admin: bool,
) -> None:
    await event.answer(
        "Админка", reply_markup=keyboard.inline.admin_main_menu(is_super_admin)
    )
    await state.clear()


@route.callback_query(F.data == "admin_panel")
async def admin_menu_callback_handler(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    is_super_admin: bool,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return

    await event.message.edit_text(
        "Админка", reply_markup=keyboard.inline.admin_main_menu(is_super_admin)
    )
    await state.clear()
