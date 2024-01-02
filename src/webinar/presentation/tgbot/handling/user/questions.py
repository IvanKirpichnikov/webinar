from contextlib import suppress

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage

from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.states import SendYourQuestion


CALLBACK_DATAS = [
    "questions",
    "technical_support",
    "question_webinars",
    "question_homework",
    "question_from_user",
]

route = Router()
route.callback_query.filter(F.data.in_(CALLBACK_DATAS))


@route.callback_query(F.data == "questions")
async def i_have_question_handler(
    event: CallbackQuery, keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return

    await event.message.edit_text(
        "По какой теме вопрос?", reply_markup=keyboard.inline.have_question()
    )


# technical_support.py
@route.callback_query(F.data == "technical_support")
async def technical_support_handler(
    event: CallbackQuery, keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return

    await event.message.edit_text(
        "Какая проблема?", reply_markup=keyboard.inline.technical_support()
    )


@route.callback_query(F.data == "question_webinars")
async def question_webinars_handler(
    event: CallbackQuery, keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return

    await event.message.edit_text(
        "Помощь по вебинарам", reply_markup=keyboard.inline.back("questions")
    )


@route.callback_query(F.data == "question_homework")
async def question_homework_handler(
    event: CallbackQuery, keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return

    await event.message.edit_text(
        "Помощь по дз", reply_markup=keyboard.inline.back("questions")
    )


# question_from_user.py
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
        return

    await event.message.delete()
    state_data = await state.get_data()
    msg = await event.message.answer(
        text="Пришли свой вопрос. Можете добавить фото или видео",
        reply_markup=keyboard.inline.back("questions"),
    )
    if msg_id_ := state_data.get("msg_id"):
        if msg_id_ == event.message.message_id:
            with suppress(TelegramBadRequest):
                await bot.delete_message(
                    chat_id=event.message.chat.id, message_id=msg_id_
                )

    if msg_id_1 := state_data.get("msg_id"):
        if msg_id_1 != event.message.message_id:
            await bot.delete_message(
                chat_id=event.message.chat.id, message_id=msg_id_1
            )
    if msg_id_2 := state_data.get("msg_id_2"):
        if msg_id_2 != event.message.message_id:
            await bot.delete_message(
                chat_id=event.message.chat.id, message_id=msg_id_2
            )

    await state.update_data(msg_id=msg.message_id)
    await state.set_state(SendYourQuestion.ask_question)
