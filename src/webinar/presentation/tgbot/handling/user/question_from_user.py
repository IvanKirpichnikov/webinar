from random import randint
from typing import Final

from aiogram import Bot, F, html, Router
from aiogram.enums import ContentType
from aiogram.filters import or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, Message

from webinar.application.config import ConfigFactory
from webinar.application.exceptions import NotFoundAdmin
from webinar.application.schemas.types import TelegramChatId
from webinar.infrastructure.database.repository.admin import (
    AdminRepositoryImpl,
)
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.states import SendYourQuestion


CALLBACK_DATAS: Final = [
    "question_i_want_to_ask_question_repeated",
    "send_question",
]

route = Router()
filter_1 = StateFilter(SendYourQuestion)
route.message.filter(filter_1)
route.callback_query.filter(F.data.in_(CALLBACK_DATAS), filter_1)


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
        await bot.delete_message(chat_id=event.chat.id, message_id=msg_id)
    number_question = randint(1000, 9999)
    text = f'Ваш вопрос. Номер #q{number_question} \n"{question_text}"'
    reply_markup = keyboard.inline.send_question("question_from_user")
    new_event = event.model_copy(update={text_attr: text}).as_(bot)
    await new_event.send_copy(chat_id=event.chat.id, reply_markup=reply_markup)

    await event.delete()
    await state.set_state(SendYourQuestion.ask_confirmation_send)
    await state.update_data(number_question=number_question)


@route.callback_query(
    F.data == "send_question", SendYourQuestion.ask_confirmation_send
)
async def send_question_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    admin_repository: AdminRepositoryImpl,
    keyboard: KeyboardFactory,
    config: ConfigFactory,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return

    state_data = await state.get_data()
    try:
        admin_entity = await admin_repository.read_random()
        admin_chat_id = admin_entity.telegram_chat_id
    except NotFoundAdmin:
        admin_chat_id = config.config.const.owner_user_id

    number_question = state_data["number_question"]
    chat_id = event.message.chat.id

    await event.message.copy_to(
        chat_id=admin_chat_id,
        reply_markup=keyboard.inline.send_answer_question(
            chat_id=TelegramChatId(chat_id), number_question=number_question
        ),
    )
    await event.message.edit_reply_markup()
    await event.message.answer(
        f"Ваш вопрос был отправлен. Номер вопроса: #q{number_question} \nГлавное меню.",
        reply_markup=keyboard.inline.main_menu(),
    )
    # if msg_id := state_data.get('msg_id'):
    #     await bot.delete_message(
    #         chat_id=event.message.chat.id,
    #         message_id=msg_id
    #     )
    await state.clear()
