from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, Message

from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.keyboard.callback_data import (
    SendAnswerQuestion,
)
from webinar.presentation.tgbot.states import SendAnswerQuestionState


route = Router()
route.callback_query.filter(SendAnswerQuestion.filter())
route.message.filter(SendAnswerQuestionState.ask_answer, F.text)


@route.callback_query(SendAnswerQuestion.filter())
async def send_question_callback_handler(
    event: CallbackQuery, state: FSMContext, callback_data: SendAnswerQuestion
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return

    question_number = callback_data.number_question
    await event.message.edit_reply_markup()
    await event.message.answer(f"Введи ответ на вопрос %q{question_number}")
    await state.set_state(SendAnswerQuestionState.ask_answer)
    await state.update_data(
        question_number=question_number, chat_id=callback_data.chat_id
    )


@route.message(SendAnswerQuestionState.ask_answer, F.text)
async def send_question_message_handler(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    is_super_admin: bool,
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
        await event.answer("Ошибка", reply_markup=reply_markup)
        return None

    await event.answer(
        "Ответ был успешно отправлен", reply_markup=reply_markup
    )
    await state.clear()
