from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.enums import MessageEntityType
from aiogram.filters import and_f, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, MessageEntity
from psycopg.errors import UniqueViolation

from src.application.interfaces.repository.homework import AbstractHomeWork
from src.application.schemas.dto.homework import AddHomeWorkDTO, HomeWorkUserId
from src.application.schemas.enums.homework import HomeWorkTypeEnum
from src.application.schemas.types import UserId
from src.presentation.tgbot.keyboard import KeyboardFactory
from src.presentation.tgbot.keyboard.callback_data import HomeWorkCallbackData
from src.presentation.tgbot.states import AskHomeWorkState


route = Router()
route.callback_query.filter(
    or_f(
        and_f(
            HomeWorkCallbackData.filter(),
            AskHomeWorkState.ask_number_homework,
        ),
        F.data == 'hand_in_the_assignment'
    )
)
route.message.filter(
    AskHomeWorkState.ask_url,
    F.entities.extract(F.type == MessageEntityType.URL).as_('urls')
)


@route.callback_query(F.data == 'hand_in_the_assignment')
async def ask_url_homework_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    
    data = await state.get_data()
    if msg_id := data.get('msg_id'):
        await bot.delete_message(
            chat_id=event.message.chat.id,
            message_id=msg_id
        )
    await state.set_state(AskHomeWorkState.ask_url)
    await event.message.edit_text(
        'Отправь ссылку с домашним заданием на Google Docs.',
        reply_markup=keyboard.inline.back('back_to_main_menu')
    )
    await state.update_data(msg_id=event.message.message_id)


@route.message(
    AskHomeWorkState.ask_url,
    ~F.entities.extract(F.type == MessageEntityType.URL)
)
async def not_valid_url(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory
) -> None:
    if event.from_user is None or event.text is None:
        return
    msg = await event.answer(
        'Назад',
        reply_markup=keyboard.inline.back('hand_in_the_assignment')
    )
    data = await state.get_data()
    if msg_id := data.get('msg_id'):
        await bot.delete_message(
            chat_id=event.chat.id,
            message_id=msg_id
        )
    await state.update_data(msg_id=msg.message_id)


@route.message(
    AskHomeWorkState.ask_url,
    F.entities.extract(F.type == MessageEntityType.URL).as_('urls')
)
async def ask_number_homework_handler(
    event: Message,
    bot: Bot,
    state: FSMContext,
    homework_repository: AbstractHomeWork,
    urls: list[MessageEntity],
    keyboard: KeyboardFactory
) -> None:
    if event.from_user is None or event.text is None:
        return
    
    url = urls[-1].extract_from(event.text)
    if not url.startswith('https://docs.google.com'):
        await event.answer('Ссылка не валидная')
        return
    
    raw_ids = await homework_repository.get_by_number_by_user_id(
        HomeWorkUserId(UserId(event.from_user.id))
    )
    if raw_ids:
        ids = list(filter(lambda x: x not in raw_ids, range(1, 7)))
    else:
        ids = list(range(1, 7))
    
    if not ids:
        await event.answer(
            'Вы сдали все домашние задания',
            reply_markup=keyboard.inline.main_menu()
        )
        return
    
    data = await state.get_data()
    if msg_id := data.get('msg_id'):
        await bot.delete_message(
            chat_id=event.chat.id,
            message_id=msg_id
        )
    
    msg = await event.answer(
        'Выбери номер домашнего задания',
        reply_markup=keyboard.inline.select_homework(ids)
    )
    await state.set_data({'homework_url': url})
    await state.set_state(AskHomeWorkState.ask_number_homework)


@route.callback_query(
    HomeWorkCallbackData.filter(),
    AskHomeWorkState.ask_number_homework,
    flags=dict(repo_uow=True)
)
async def add_homework_handler(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    callback_data: HomeWorkCallbackData,
    homework_repository: AbstractHomeWork
) -> None:
    if event.message is None:
        return
    
    user = event.from_user
    data = await state.get_data()
    url = data['homework_url']
    
    try:
        await homework_repository.add(
            AddHomeWorkDTO(
                user_id=UserId(user.id),
                date_time=datetime.now(),
                number=callback_data.number,
                url=url,
                type=HomeWorkTypeEnum.UNDER_INSPECTION
            )
        )
    except UniqueViolation:
        pass
    else:
        await event.message.edit_text(
            'Задание успешно сдано',
            reply_markup=keyboard.inline.main_menu()
        )
        await state.clear()
