from aiogram import F, html, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage

from webinar.presentation.tgbot.keyboard import KeyboardFactory


CALLBACK_DATAS = [
    'technical_support',
    "dont_work_invite",
    "i_can_log_into_platform",
    "doesnt_load_lessons",
    "can_reset_password",
]

INSTRUCTION = f"""
- Сбросить кеш
- Обновить браузер до последней версии
- Открывать уроки в браузере Гугл хром
- Уменьшить разрешение видео
- Так как в курсе много уроков, загружается большое количество информации, мобильная связь может не потянуть.
Попробуйте подключиться к стабильной сети, для более быстрой загрузки
- Системные требования к устройствам, соблюдение которых поможет избежать возможных сбоев в работе платформы,
Вы можете посмотреть 👉
{html.link('здесь', "https://docs.google.com/file/d/1Lm0mhC04BhmkDGVNRf4EbEBF-CfE2Ibf/edit?usp=docslist_api&filetype=msword")}👈
 

Мы советуем просматривать уроки и выполнять задания тестирования, используя компьютер либо ноутбук. При этом версия
браузера должна быть не ниже рекомендованной.

Если Ваша проблема уже описана в рекомендациях и требованиях, рассмотрение Вашего вопроса техниками может быть отложено.

Мы не можем гарантировать нормальную работу платформы, если технические требования Вами не соблюдены‼️
"""

route = Router()
route.callback_query.filter(F.data.in_(CALLBACK_DATAS))


# technical_support.py
@route.callback_query(F.data == "technical_support")
async def technical_support_handler(
    event: CallbackQuery,
    keyboard: KeyboardFactory,
    state: FSMContext
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    await event.message.edit_text(
        "Какая проблема?",
        reply_markup=keyboard.inline.technical_support()
    )
    await state.clear()


@route.callback_query(F.data == "dont_work_invite")
async def dont_work_invite_handler(
    event: CallbackQuery, keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    await event.message.edit_text(
        "Посмотрите внимательно инструкцию. Попробуйте скопировать инвайт код из инструкции и вставить\n"
        + INSTRUCTION,
        reply_markup=keyboard.inline.back("technical_support"),
    )


@route.callback_query(F.data == "i_can_log_into_platform")
async def i_can_log_into_platform_handler(
    event: CallbackQuery, keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    await event.message.edit_text(
        INSTRUCTION, reply_markup=keyboard.inline.back("technical_support")
    )


@route.callback_query(F.data == "doesnt_load_lessons")
async def doesnt_load_lessons_handler(
    event: CallbackQuery, keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    await event.message.edit_text(
        "Перегрузите страницу, войдите через другой браузер, почистите кеш\n"
        + INSTRUCTION,
        reply_markup=keyboard.inline.back("technical_support"),
    )


@route.callback_query(F.data == "can_reset_password")
async def can_reset_password_handler(
    event: CallbackQuery, keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    await event.message.edit_text(
        "Нужно прислать ФИО и почту, чтобы мы создали новый пароль.\n\n"
        "<u>Чтобы это сделать:</u>\n"
        "1. Нажмите кнопку <code>Назад.</code>\n"
        "2. Нажмите кнопку <code>«Сформулируйте ваш вопрос».</code>\n"
        "3. Напишите и отправьте <code>«Не могу восстановить пароль».</code>\n",
        reply_markup=keyboard.inline.back("technical_support"),
        parse_mode=ParseMode.HTML
    )
