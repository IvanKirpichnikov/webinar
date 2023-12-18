from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.presentation.tgbot.keyboard import KeyboardFactory


CALLBACK_DATAS = [
    'lesson_won_open',
    'i_can_log_into_platform',
    'ellipsis'
]

route = Router()
route.callback_query.filter(F.data.in_(CALLBACK_DATAS))


@route.callback_query(F.data == 'lesson_won_open')
async def lesson_won_open_handler(
    event: CallbackQuery,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    
    await event.message.edit_text(
        'Инструкция не открывается урок',
        reply_markup=keyboard.inline.back('technical_support')
    )


@route.callback_query(F.data == 'i_can_log_into_platform')
async def i_can_log_into_platform_handler(
    event: CallbackQuery,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    
    await event.message.edit_text(
        'Инструкция не могу зайти на платформу',
        reply_markup=keyboard.inline.back('technical_support')
    )


@route.callback_query(F.data == 'ellipsis')
async def ellipsis_handler(
    event: CallbackQuery,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    
    await event.message.edit_text(
        '...',
        reply_markup=keyboard.inline.back('technical_support')
    )
