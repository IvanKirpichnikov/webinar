from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.presentation.tgbot.keyboard import KeyboardFactory
from src.presentation.tgbot.states import SendYourQuestion


CALLBACK_DATAS = [
    'i_have_question',
    'technical_support',
    'question_webinars',
    'question_homework',
    'question_i_want_to_ask_question'
]

route = Router()
route.callback_query.filter(F.data.in_(CALLBACK_DATAS))


@route.callback_query(F.data == 'i_have_question')
async def i_have_question_handler(
    event: CallbackQuery,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    
    await event.message.edit_text(
        'По какой теме вопрос?',
        reply_markup=keyboard.inline.i_have_question()
    )


# technical_support.py
@route.callback_query(F.data == 'technical_support')
async def technical_support_handler(
    event: CallbackQuery,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    
    await event.message.edit_text(
        'Какая проблема?',
        reply_markup=keyboard.inline.technical_support()
    )


@route.callback_query(F.data == 'question_webinars')
async def question_webinars_handler(
    event: CallbackQuery,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    
    await event.message.edit_text(
        'Помощь по вебинарам',
        reply_markup=keyboard.inline.back('i_have_question')
    )


@route.callback_query(F.data == 'question_homework')
async def question_homework_handler(
    event: CallbackQuery,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    
    await event.message.edit_text(
        'Помощь по дз',
        reply_markup=keyboard.inline.back('i_have_question')
    )


# i_want_to_ask_question.py
@route.callback_query(F.data == 'question_i_want_to_ask_question')
async def i_want_to_ask_question_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    
    msg_data = dict(
        text='Пришли свой вопрос. Можете добавить фото или видео',
        reply_markup=keyboard.inline.back('i_have_question')
    )
    msg_id = event.message.message_id
    try:
        await event.message.edit_text(**msg_data)  # type: ignore
    except TelegramBadRequest:
        msg = await event.message.answer(**msg_data)  # type: ignore
        msg_id = msg.message_id
    
    data = await state.get_data()
    if msg_id_ := data.get('msg_id'):
        if msg_id_ != event.message.message_id:
            await bot.delete_message(
                chat_id=event.message.chat.id,
                message_id=msg_id_
            )
    
    await state.update_data(msg_id=msg_id)
    await state.set_state(SendYourQuestion.ask_question)
