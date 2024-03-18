from random import randint
from typing import Final

from aiogram import Bot, F, html, Router
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    Message,
)

from webinar.application.dto.common import TgUserIdDTO
from webinar.application.exceptions import NotFoundAdmin
from webinar.application.interfaces.delete_message import DeleteMessageData
from webinar.application.use_case.admin.read_admin_submit_user_question import \
    ReadAdminSubmitUserQuestionData
from webinar.config import ConfigFactory
from webinar.domain.types import TgChatId, TgUserId
from webinar.presentation.annotaded import (
    ReadAdminSubmitUserQuestionDepends,
    ReadUserDataDepends,
    TgDeleteMessageDepends,
)
from webinar.presentation.inject import inject, InjectStrategy
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
@inject(InjectStrategy.HANDLER)
async def v_handler(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    tg_delete_message: TgDeleteMessageDepends,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    state_data = await state.get_data()
    message_ids = [event.message.message_id]
    if message_id := state_data.get("msg_id"):
        message_ids.append(message_id)
    if message_id := state_data.get("msg_id_2"):
        message_ids.append(message_id)
    await tg_delete_message(
        DeleteMessageData(
            chat_id=event.message.chat.id,
            message_id=message_ids,
            inline_message_id=event.message.message_id
        )
    )
    msg = await event.message.answer(
        text="Пришли свой вопрос. Можете добавить фото или видео",
        reply_markup=keyboard.inline.back("technical_support"),
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
@inject(InjectStrategy.HANDLER)
async def get_question_handler(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    tg_delete_message: TgDeleteMessageDepends,
) -> None:
    if event.text:
        text_attribute = "text"
        question_text = html.quote(event.text)
    elif event.caption:
        text_attribute = "caption"
        question_text = html.quote(event.caption)
    else:
        raise ValueError
    
    state_data = await state.get_data()
    message_ids = [event.message_id]
    if message_id := state_data.get("msg_id"):
        message_ids.append(message_id)
    await tg_delete_message(
        DeleteMessageData(
            chat_id=event.chat.id,
            message_id=message_ids
        )
    )
    
    number_question = randint(1000, 9999)
    new_event = event.model_copy(
        update={
            text_attribute: f'Ваш вопрос. Номер #q{number_question} \n"{question_text}"'
        },
    ).as_(bot)
    await new_event.send_copy(
        chat_id=event.chat.id,
        reply_markup=keyboard.inline.send_question("technical_support")
    )
    await state.set_state(SendYourQuestion.ask_confirmation_send)
    await state.update_data(
        number_question=number_question,
        question_text=question_text,
        text_attribute=text_attribute
    )


@route.callback_query(
    F.data == "send_question", SendYourQuestion.ask_confirmation_send
)
@inject(InjectStrategy.HANDLER)
async def send_question_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    config: ConfigFactory,
    read_user_data: ReadUserDataDepends,
    read_admin_submit_user_question: ReadAdminSubmitUserQuestionDepends
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    telegram_user_id = TgUserId(event.from_user.id)
    user_entity = await read_user_data(TgUserIdDTO(telegram_user_id))
    state_data = await state.get_data()
    try:
        admin_chat_id_dto = await read_admin_submit_user_question(
            ReadAdminSubmitUserQuestionData(
                telegram_user_id=telegram_user_id,
                direction_training=user_entity.direction_training
            )
        )
    except NotFoundAdmin:
        admin_chat_id = config.config.const.owner_chat_id
    else:
        if admin_chat_id_dto is None:
            admin_chat_id = config.config.const.owner_chat_id
        else:
            admin_chat_id = admin_chat_id_dto.telegram_chat_id
    
    number_question = state_data["number_question"]
    chat_id = event.message.chat.id
    if event.from_user.username:
        url = '@' + event.from_user.username
    else:
        url = html.link(event.from_user.full_name, f"tg://user?id={event.from_user.id}")
    text = (
        f'ФИО: {user_entity.sup}\n'
        f'Телеграм: {url}\n'
        f'Почта: {user_entity.email}\n'
        f'Номер вопроса: #q{state_data["number_question"]}\n'
        f'Вопрос: {state_data["question_text"]}'
    )
    new_model = event.message.model_copy(
        update={
            state_data['text_attribute']: text,
            'reply_markup': keyboard.inline.send_answer_question(
                chat_id=TgChatId(chat_id),
                number_question=number_question,
                user_id=event.from_user.id,
                url=True,
            )
        }
    ).as_(bot)
    if isinstance(new_model, InaccessibleMessage):
        return None
    
    try:
        await new_model.send_copy(chat_id=admin_chat_id, parse_mode='HTML')
    except TelegramBadRequest:
        new_model = new_model.model_copy(
            update={
                'reply_markup': keyboard.inline.send_answer_question(
                    chat_id=TgChatId(chat_id),
                    number_question=number_question,
                    user_id=event.from_user.id,
                    url=False,
                )
            }
        ).as_(bot)
        await new_model.send_copy(chat_id=admin_chat_id)
    
    await event.message.delete_reply_markup()
    await event.message.answer(
        f"Ваш вопрос был отправлен. Номер вопроса: #q{number_question} \nГлавное меню.",
        reply_markup=keyboard.inline.main_menu(),
    )
    await state.clear()
