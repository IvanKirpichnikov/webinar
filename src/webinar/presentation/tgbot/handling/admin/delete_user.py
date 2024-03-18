from aiogram import F, Router
from aiogram.enums import MessageEntityType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, MessageEntity

from webinar.application.dto.common import EmailDTO, ResultExistsDTO
from webinar.application.exceptions import NotFoundUser
from webinar.application.interfaces.delete_message import DeleteMessageData
from webinar.infrastructure.adapters.cache import CacheStore
from webinar.presentation.annotaded import DeleteUserByEmailDepends, TgDeleteMessageDepends
from webinar.presentation.inject import inject, InjectStrategy
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.states import DeleteUser


route = Router(name=__name__)


@route.callback_query(F.data == 'delete_user')
async def ask_user_email(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
) -> None:
    if not isinstance(event.message, Message):
        return None
    
    await event.message.edit_text(
        text='Пришлите почту слушателя',
        reply_markup=keyboard.inline.back('admin_panel')
    )
    await state.set_state(DeleteUser.ask_email)
    await state.set_data({'msg_id': event.message.message_id})


@route.message(F.entities.extract(F.type != MessageEntityType.EMAIL), DeleteUser.ask_email)
async def not_valid_message(
    event: Message, keyboard: KeyboardFactory,
) -> None:
    await event.answer(
        text='Пришлите почту слушателя',
        reply_markup=keyboard.inline.back('admin_panel')
    )
    await event.delete()


@route.message(
    F.entities.extract(F.type == MessageEntityType.EMAIL)[-1].as_("email_entity"),
    DeleteUser.ask_email
)
@inject(InjectStrategy.HANDLER)
async def ask_confirm(
    event: Message,
    state: FSMContext,
    keyboard: KeyboardFactory,
    email_entity: MessageEntity,
    tg_delete_message: TgDeleteMessageDepends,
) -> None:
    if event.text is None:
        return None
    
    email = email_entity.extract_from(event.text)
    state_data = await state.get_data()
    await event.answer(
        f'Удалить пользователя с почтой {email}',
        reply_markup=keyboard.inline.yes_or_back('delete_user')
    )
    await state.set_data({'email': email})
    await state.set_state(DeleteUser.confirm)
    
    message_ids = [event.message_id, state_data['msg_id']]
    await tg_delete_message(
        DeleteMessageData(
            chat_id=event.chat.id,
            message_id=message_ids
        )
    )


@route.callback_query(F.data == 'yes', DeleteUser.confirm)
@inject(InjectStrategy.HANDLER)
async def delete_user(
    event: CallbackQuery,
    state: FSMContext,
    use_case: DeleteUserByEmailDepends,
    keyboard: KeyboardFactory,
    is_super_admin: bool,
    cache: CacheStore,
) -> None:
    if not isinstance(event.message, Message):
        return None
    
    state_data = await state.get_data()
    await state.clear()
    
    email: str = state_data['email']
    try:
        user_id = await use_case(EmailDTO(email))
    except NotFoundUser:
        text = f'Слушатель с почтой {email} не найден'
    else:
        if user_id is None:
            text = f'Слушатель с почтой {email} не удален'
        else:
            text = f'Слушатель с почтой {email} удален'
            cache.exists_user[user_id] = ResultExistsDTO(False)
    await event.message.edit_text(
        text,
        reply_markup=keyboard.inline.admin_main_menu(is_super_admin)
    )
