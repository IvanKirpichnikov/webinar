from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.presentation.tgbot.keyboard import KeyboardFactory
from src.presentation.tgbot.keyboard.callback_data import SendAnswerQuestionCallbackData
from src.presentation.tgbot.states import SendAnswerQuestionState


route = Router()
route.callback_query.filter(
    SendAnswerQuestionCallbackData.filter()
)
route.message.filter(
    SendAnswerQuestionState.ask_answer,
    F.text
)


@route.callback_query(SendAnswerQuestionCallbackData.filter())
async def send_question_callback_handler(
    event: CallbackQuery,
    state: FSMContext,
    callback_data: SendAnswerQuestionCallbackData
) -> None:
    if event.message is None:
        return
    
    question_number = callback_data.number_question
    await event.message.answer(f'Введи ответ на вопрос номер: {question_number}')
    await state.update_data(question_number=question_number, chat_id=callback_data.chat_id)
    await state.set_state(SendAnswerQuestionState.ask_answer)


@route.message(
    SendAnswerQuestionState.ask_answer,
    F.text
)
async def send_question_message_handler(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    is_super_admin: bool
) -> None:
    data = await state.get_data()
    await state.clear()
    user_chat_id = data['chat_id']
    question_number = data['question_number']
    
    try:
        await bot.send_message(
            user_chat_id,
            f'Ответ на вопрос номер: #{question_number}\n{event.text}'
        )
    except TelegramBadRequest as e:
        await event.answer('Ошибка', reply_markup=keyboard.inline.admin_panel(is_super_admin))
    else:
        await event.answer('Ответ был успешно отправлен', reply_markup=keyboard.inline.admin_panel(is_super_admin))
