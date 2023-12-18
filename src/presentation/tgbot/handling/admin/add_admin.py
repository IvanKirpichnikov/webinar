from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import and_f, MagicData, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from psycopg.errors import UniqueViolation

from src.application.interfaces.repository.admin import AbstractAdmin
from src.application.schemas.dto.admin import AddAdminDTO
from src.application.schemas.types import UserId
from src.presentation.tgbot.keyboard import KeyboardFactory
from src.presentation.tgbot.keyboard.callback_data import AskDirectionCallbackData
from src.presentation.tgbot.states import AddAdminState


route = Router()
route.callback_query.filter(
    MagicData(F.is_super_admin == True),
    or_f(
        F.data == 'add_admin',
        and_f(
            AskDirectionCallbackData.filter(),
            AddAdminState.ask_webinar_type
        )
    )
)
route.message.filter(
    MagicData(F.is_super_admin == True),
    AddAdminState.ask_user_id,
    F.text.cast(int)
)


@route.callback_query(F.data == 'add_admin')
async def ask_user_id(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    
    msg = await event.message.edit_text(
        'Пришли телеграм айди администратора',
        reply_markup=keyboard.inline.back('admin_panel')
    )
    await state.set_data({'msg_id': msg.message_id})
    await state.set_state(AddAdminState.ask_user_id)


@route.message(
    F.text.as_('user_id'),
    AddAdminState.ask_user_id
)
async def ask_webinar_type(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    user_id: str
) -> None:
    try:
        user_id = int(user_id)
    except ValueError:
        msg = await event.answer('Не валидный user_id. Ведите повторно')
        await state.set_data({'msg_id': msg.message_id})
        return
    
    data = await state.get_data()
    if msg_id_ := data.get('msg_id'):
        await bot.delete_message(
            chat_id=event.chat.id,
            message_id=msg_id_
        )
    try:
        msg = await event.answer(
            'Вы хотите добавить этого юзера?\nЗа какое направление он будет отвечает?',
            reply_markup=keyboard.inline.webinar_type_(user_id)
        )
    except TelegramBadRequest:
        msg = await event.answer('Не валидный user_id. Ведите повторно')
        await state.set_data({'msg_id': msg.message_id})
        return
    
    await state.set_data({'msg_id': msg.message_id, 'user_id': user_id})
    await state.set_state(AddAdminState.ask_webinar_type)


@route.callback_query(
    AddAdminState.ask_webinar_type,
    AskDirectionCallbackData.filter(),
    flags=dict(repo_uow=True)
)
async def finish_handler(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    callback_data: AskDirectionCallbackData,
    admin_repository: AbstractAdmin
) -> None:
    if event.message is None:
        return
    
    data = await state.get_data()
    user_id = data['user_id']
    try:
        await admin_repository.add(
            AddAdminDTO(
                user_id=UserId(user_id),
                direction_type=callback_data.type
            )
        )
    except UniqueViolation:
        await event.message.edit_text(
            text='Пользователь уже добавлен в качестве администратора',
            reply_markup=keyboard.inline.admin_panel(True)
        )
        return
    await event.message.edit_text(
        'Вы добавили администратора',
        reply_markup=keyboard.inline.admin_panel(True)
    )
