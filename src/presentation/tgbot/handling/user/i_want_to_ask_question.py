from random import randint
from typing import Final

from aiogram import Bot, F, Router, html
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.application.config import ConfigFactory
from src.application.interfaces.repository.admin import AbstractAdmin
from src.presentation.tgbot.keyboard import KeyboardFactory
from src.presentation.tgbot.states import SendYourQuestion


CALLBACK_DATAS: Final = [
    'question_i_want_to_ask_question_repeated',
    'send_question',

]

route = Router()
filter_1 = StateFilter(SendYourQuestion)
route.message.filter(filter_1)
route.callback_query.filter(F.data.in_(CALLBACK_DATAS), filter_1)


@route.message(
    F.content_type.in_(
        {
            ContentType.TEXT,
            ContentType.PHOTO,
            ContentType.VIDEO
        }
    ),
    or_f(F.text, F.caption),
    SendYourQuestion.ask_question
)
async def get_question_handler(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory
) -> None:
    await event.delete()
    text = html.quote(event.text or event.caption) if event.text or event.caption else None
    if event.text:
        msg_data = dict(type='text')
        type = 'text'
    elif event.photo:
        msg_data = dict(type='photo', file_id=event.photo.pop().file_id)
        type = 'photo'
    elif event.video:
        msg_data = dict(type='video', file_id=event.video.file_id)
        type = 'video'
    else:
        return
    
    if type == 'text':
        msg = await event.answer(
            f'Ваш вопрос:\n"{text}"',
            reply_markup=keyboard.inline.send_question('question_i_want_to_ask_question'),
            disable_web_page_preview=True
        )
    elif type == 'photo':
        msg = await event.answer_photo(
            msg_data['file_id'],
            f'Ваш вопрос:\n"{text}"',
            reply_markup=keyboard.inline.send_question('question_i_want_to_ask_question'),
            disable_web_page_preview=True
        )
    elif type == 'video':
        msg = await event.answer_video(
            msg_data['file_id'],
            caption=f'Ваш вопрос:\n"{text}"',
            reply_markup=keyboard.inline.send_question('question_i_want_to_ask_question'),
            disable_web_page_preview=True
        )
    else:
        return
    
    data = await state.get_data()
    if msg_id := data.get('msg_id'):
        await bot.delete_message(
            chat_id=event.chat.id,
            message_id=msg_id
        )
    await state.update_data(
        msg_id=msg.message_id,
        type=type,
        text=text,
        file_id=msg_data.get('file_id')
    )
    await state.set_state(SendYourQuestion.ask_confirmation_send)


@route.callback_query(
    F.data == 'send_question',
    SendYourQuestion.ask_confirmation_send
)
async def send_question_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    admin_repository: AbstractAdmin,
    config: ConfigFactory
) -> None:
    if event.message is None:
        return
    
    data = await state.get_data()
    type = data['type']
    await state.clear()
    config_ = config.config
    chat_id = event.message.chat.id
    
    number_question = randint(1, 1000)
    admin_chat_id = await admin_repository.get_random_chat_id_admin() or config_.const.owner_user_id
    text = f'Вопрос #{number_question}\n\n{data["text"]}'
    try:
        if type == 'text':
            await bot.send_message(
                chat_id=admin_chat_id,
                text=text,
                reply_markup=keyboard.inline.send_answer(number_question, chat_id)
            )
        elif type == 'photo':
            await bot.send_photo(
                chat_id=admin_chat_id,
                photo=data['file_id'],
                caption=text,
                reply_markup=keyboard.inline.send_answer(number_question, chat_id)
            )
        elif type == 'video':
            await bot.send_video(
                chat_id=admin_chat_id,
                video=data['file_id'],
                caption=text,
                reply_markup=keyboard.inline.send_answer(number_question, chat_id)
            )
    except TelegramBadRequest as e:
        raise e
    
    if msg_id := data.get('msg_id'):
        await bot.delete_message(
            chat_id=event.message.chat.id,
            message_id=msg_id
        )
    
    await event.message.answer(
        f'Ваш вопрос был отправлен. Номер вопроса: #{number_question} \nГлавное меню.',
        reply_markup=keyboard.inline.main_menu()
    )
    await bot.send_message(
        admin_chat_id,
        f'Вопрос номер #{number_question}'
    )
