from contextlib import suppress
from random import randint
from typing import Final

from aiogram import (
    Bot,
    F,
    html,
    Router
)
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import (
    or_f,
    StateFilter
)
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    Message
)

from webinar.application.config import ConfigFactory
from webinar.application.exceptions import NotFoundAdmin
from webinar.application.schemas.dto.admin import GetAdminFromDirectionTraining
from webinar.application.schemas.dto.common import TelegramUserIdDTO
from webinar.application.schemas.types import (
    TelegramChatId,
    TelegramUserId
)
from webinar.infrastructure.database.repository.admin import (
    AdminRepositoryImpl,
)
from webinar.infrastructure.database.repository.user import UserRepositoryImpl
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.states import SendYourQuestion


CALLBACK_DATAS: Final = [
    'question_from_user',
    "question_i_want_to_ask_question_repeated",
    "send_question",
]

route = Router()
route.message.filter(StateFilter(SendYourQuestion))
route.callback_query.filter(F.data.in_(CALLBACK_DATAS))


@route.callback_query(F.data == "question_from_user")
async def v_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        await event.answer('Нет доступа к сообщению. Введите /start', show_alert=True)
        return
    with suppress(TelegramBadRequest):
        await event.message.delete()
    
    state_data = await state.get_data()
    msg = await event.message.answer(
        text="Пришли свой вопрос. Можете добавить фото или видео",
        reply_markup=keyboard.inline.back("technical_support"),
    )
    if msg_id_ := state_data.get("msg_id"):
        if msg_id_ == event.message.message_id:
            with suppress(TelegramBadRequest):
                await bot.delete_message(
                    chat_id=event.message.chat.id, message_id=msg_id_
                )
    
    if msg_id_1 := state_data.get("msg_id"):
        if msg_id_1 != event.message.message_id:
            with suppress(TelegramBadRequest):
                await bot.delete_message(
                    chat_id=event.message.chat.id, message_id=msg_id_1
                )
    if msg_id_2 := state_data.get("msg_id_2"):
        if msg_id_2 != event.message.message_id:
            with suppress(TelegramBadRequest):
                await bot.delete_message(
                    chat_id=event.message.chat.id, message_id=msg_id_2
                )
    
    await state.update_data(msg_id=msg.message_id)
    await state.set_state(SendYourQuestion.ask_question)


@route.message(
    F.content_type.in_(
        {ContentType.TEXT, ContentType.PHOTO, ContentType.VIDEO}
    ),
    or_f(F.text, F.caption),
    SendYourQuestion.ask_question,
)
async def get_question_handler(
    event: Message, bot: Bot, state: FSMContext, keyboard: KeyboardFactory
) -> None:
    if event.text:
        text_attr = "text"
        question_text = html.quote(event.text)
    elif event.caption:
        text_attr = "caption"
        question_text = html.quote(event.caption)
    else:
        raise ValueError
    
    state_data = await state.get_data()
    if msg_id := state_data.get("msg_id"):
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id=event.chat.id, message_id=msg_id)
    
    number_question = randint(1000, 9999)
    text = f'Ваш вопрос. Номер #q{number_question} \n"{question_text}"'
    reply_markup = keyboard.inline.send_question("technical_support")
    new_event = event.model_copy(update={text_attr: text}).as_(bot)
    await new_event.send_copy(chat_id=event.chat.id, reply_markup=reply_markup)
    with suppress(TelegramBadRequest):
        await event.delete()
    await state.set_state(SendYourQuestion.ask_confirmation_send)
    await state.update_data(
        number_question=number_question,
        question_text=question_text,
        text_attr=text_attr
    )


@route.callback_query(
    F.data == "send_question", SendYourQuestion.ask_confirmation_send
)
async def send_question_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    admin_repository: AdminRepositoryImpl,
    user_repository: UserRepositoryImpl,
    keyboard: KeyboardFactory,
    config: ConfigFactory,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        await event.answer('Нет доступа к сообщению. Введите /start', show_alert=True)
        return
    telegram_user_id = TelegramUserId(event.from_user.id)
    telegram_user_id_dto = TelegramUserIdDTO(telegram_user_id)
    user_entity = await user_repository.read_by_telegram_user_id(telegram_user_id_dto)
    dto = GetAdminFromDirectionTraining(
        telegram_user_id=telegram_user_id,
        direction_training=user_entity.direction_training
    )
    state_data = await state.get_data()
    try:
        admin_entity = await admin_repository.get_admin_by_letters_range_from_user_or_random(dto)
        admin_chat_id = admin_entity.telegram_chat_id
    except NotFoundAdmin:
        admin_chat_id = config.config.const.owner_chat_id
    
    number_question = state_data["number_question"]
    chat_id = event.message.chat.id
    
    text = (
        f'ФИО: {user_entity.sup}\n'
        f'Почта: {user_entity.email}\n'
        f'Номер вопроса: #q{state_data["number_question"]}\n'
        f'Вопрос: {state_data["question_text"]}'
    )
    new_model = event.message.model_copy(
        update={
            state_data['text_attr']: text,
            'reply_markup': keyboard.inline.send_answer_question(
                chat_id=TelegramChatId(chat_id),
                number_question=number_question,
                user_id=event.from_user.id
            )
        }
    ).as_(bot)
    if new_model is None:
        return None
    if isinstance(new_model, InaccessibleMessage):
        return None
    
    await new_model.send_copy(chat_id=admin_chat_id)
    await event.message.edit_reply_markup()
    await event.message.answer(
        f"Ваш вопрос был отправлен. Номер вопроса: #q{number_question} \nГлавное меню.",
        reply_markup=keyboard.inline.main_menu(),
    )
    await state.clear()
