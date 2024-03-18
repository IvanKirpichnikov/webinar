from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import and_f, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, Message

from webinar.application.interfaces.delete_message import DeleteMessageData
from webinar.presentation.annotaded import TgDeleteMessageDepends
from webinar.presentation.inject import inject, InjectStrategy
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.keyboard.callback_data import (
    SendAnswerQuestion,
)
from webinar.presentation.tgbot.states import SendAnswerQuestionState


route = Router()
route.callback_query.filter(
    or_f(
        SendAnswerQuestion.filter(),
        and_f(
            SendAnswerQuestionState.ask_answer,
            F.data == 'back'
        )
    
    )
)
route.message.filter(SendAnswerQuestionState.ask_answer, F.text)


@route.callback_query(SendAnswerQuestion.filter())
async def send_question_callback_handler(
    event: CallbackQuery,
    state: FSMContext,
    callback_data: SendAnswerQuestion,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    question_number = callback_data.number_question
    msg = await event.message.answer(
        f"Введи ответ на вопрос #q{question_number}",
        reply_markup=keyboard.inline.back('back')
    )
    await state.set_state(SendAnswerQuestionState.ask_answer)
    await state.update_data(
        question_number=question_number,
        chat_id=callback_data.chat_id,
        question_msg_id=event.message.message_id,
        msg_id=msg.message_id
    )


@route.callback_query(
    SendAnswerQuestionState.ask_answer,
    F.data == 'back'
)
@inject(InjectStrategy.HANDLER)
async def back(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    tg_message_delete: TgDeleteMessageDepends,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    state_data = await state.get_data()
    msg_id = state_data['msg_id']
    await tg_message_delete(
        DeleteMessageData(
            chat_id=event.message.chat.id,
            message_id=msg_id
        )
    )
    await state.clear()


@route.message(SendAnswerQuestionState.ask_answer, F.text)
@inject(InjectStrategy.HANDLER)
async def send_question_message_handler(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    is_super_admin: bool,
    tg_message_delete: TgDeleteMessageDepends,
) -> None:
    if event.text is None:
        return None
    
    reply_markup = keyboard.inline.admin_main_menu(is_super_admin)
    data = await state.get_data()
    try:
        await bot.send_message(
            data["chat_id"],
            f'Ответ на вопрос #q{data["question_number"]}\n{event.text}',
        )
    except TelegramBadRequest:
        await event.answer(
            "Ошибка. Человек заблокировал бота или он не писал боту",
            reply_markup=reply_markup
        )
        return None
    
    await event.answer(
        "Ответ был успешно отправлен", reply_markup=reply_markup
    )
    await state.clear()
    
    message_ids = [data['msg_id'], data['question_msg_id'], event.message_id]
    await tg_message_delete(
        DeleteMessageData(
            chat_id=event.chat.id,
            message_id=message_ids
        )
    )
