from contextlib import suppress
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.enums import MessageEntityType
from aiogram.filters import and_f, CommandStart, or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, MessageEntity

from src.application.interfaces.repository.user import AbstractUser
from src.application.schemas.dto.user import AddUserDto, IsoDateTime, UserId
from src.application.schemas.enums import DirectionEnum
from src.infrastructure.cache import CacheAdapter
from src.presentation.tgbot.keyboard import KeyboardFactory
from src.presentation.tgbot.keyboard.callback_data import AskDirectionCallbackData
from src.presentation.tgbot.states import RegisteringState


route = Router()


def get_sup(sup_: str) -> tuple[str, str, str | None]:
    sup = sup_.split(' ')
    surname = sup[0]
    name = sup[1]
    patronymic = None
    with suppress(IndexError):
        patronymic = sup[2]
    
    return surname, name, patronymic


@route.message(
    or_f(
        CommandStart(),
        and_f(
            F.text == 'Отмена',
            RegisteringState.ask_sup
        )
    )
)
async def ask_direction_message_handler(
    event: Message,
    state: FSMContext,
    keyboard: KeyboardFactory
) -> None:
    await event.answer(
        'Привет, студент!\nВыбери направление.',
        reply_markup=keyboard.inline.ask_direction()
    )
    await state.set_data({})
    await state.set_state(RegisteringState.ask_direction)


@route.callback_query(F.data == 'ask_direction_back')
async def ask_direction_callback_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    
    await event.message.edit_text(
        'Привет, студент!\nВыбери направление.',
        reply_markup=keyboard.inline.ask_direction()
    )
    data = await state.get_data()
    if msg_id := data.get('msg_id'):
        if msg_id != event.message.message_id:
            await bot.delete_message(
                chat_id=event.message.chat.id,
                message_id=msg_id
            )
    await state.set_state(RegisteringState.ask_direction)


@route.callback_query(
    StateFilter(
        RegisteringState.ask_direction,
        RegisteringState.ask_email
    ),
    or_f(
        AskDirectionCallbackData.filter(),
        F.data == 'ask_sup_back'
    )
)
async def ask_sup_callback_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    callback_data: AskDirectionCallbackData | None = None
) -> None:
    if event.message is None:
        return None
    
    data = await state.get_data()
    await event.message.edit_text(
        (
            'Введите ФИО в следующем формате: Ф И О\n'
            'Например Иванов Иван Иванович.\n'
            'В случае отсутствия отчества, вы можете не писать его.'
        ),
        reply_markup=keyboard.inline.back('ask_direction_back')
    )
    if callback_data:
        await state.update_data(direction=callback_data.type, msg_id=event.message.message_id)
    
    if msg_id := data.get('msg_id'):
        if msg_id != event.message.message_id:
            await bot.delete_message(
                chat_id=event.message.chat.id,
                message_id=msg_id
            )
    await state.set_state(RegisteringState.ask_sup)


@route.callback_query(
    F.data == 'send_sup',
    RegisteringState.ask_email
)
async def ask_sup_callback_handler_sup(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    
    msg = await event.message.edit_text(
        (
            'Введите ФИО в следующем формате: Ф И О\n'
            'Например Иванов Иван Иванович.\n'
            'В случае отсутствия отчества, вы можете не писать его.'
        ),
        reply_markup=keyboard.inline.back('ask_direction_back')
    )
    data = await state.get_data()
    if msg_id := data.get('msg_id'):
        if msg_id != event.message.message_id:
            await bot.delete_message(
                chat_id=event.message.chat.id,
                message_id=msg_id
            )
    await state.update_data(msg_id=event.message.message_id)
    await state.set_state(RegisteringState.ask_sup)


@route.message(
    RegisteringState.ask_sup,
    ~F.text.split(' ').len().in_({2, 3})
)
async def not_valid_sup(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory
) -> None:
    msg = await event.answer(
        (
            'Введите ФИО в следующем формате: Ф И О\n'
            'Например Иванов Иван Иванович.\n'
            'В случае отсутствия отчества, вы можете не писать его.'
        ),
        reply_markup=keyboard.inline.back('ask_direction_back')
    )
    data = await state.get_data()
    if msg_id := data.get('msg_id'):
        await bot.delete_message(
            chat_id=event.chat.id,
            message_id=msg_id
        )
    
    await state.update_data(msg_id=msg.message_id)
    await state.set_state(RegisteringState.ask_sup)


@route.message(
    RegisteringState.ask_sup,
    F.text.split(' ').len().in_({2, 3})
)
async def ask_email_handler(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory
) -> None:
    msg = await event.answer(
        'Теперь пришли почту',
        reply_markup=keyboard.inline.back('send_sup')
    )
    data = await state.get_data()
    if msg_id := data.get('msg_id'):
        await bot.delete_message(
            chat_id=event.chat.id,
            message_id=msg_id
        )
    
    await state.update_data(sup=event.text, msg_id=msg.message_id)
    await state.set_state(RegisteringState.ask_email)


@route.message(
    RegisteringState.ask_email,
    ~F.entities.extract(F.type == MessageEntityType.EMAIL)
)
async def not_valid_email(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory
) -> None:
    msg = await event.answer(
        'Вы отправили не ту почту. Повторите попытку',
        reply_markup=keyboard.inline.back('send_sup')
    )
    data = await state.get_data()
    if msg_id := data.get('msg_id'):
        await bot.delete_message(
            chat_id=event.chat.id,
            message_id=msg_id
        )
    
    await state.update_data(msg_id=msg.message_id)


@route.message(
    RegisteringState.ask_email,
    F.entities.extract(F.type == MessageEntityType.EMAIL).as_("emails"),
    flags=dict(repo_uow=True)
)
async def finish_handler(
    event: Message,
    bot: Bot,
    state: FSMContext,
    cache: CacheAdapter,
    keyboard: KeyboardFactory,
    user_repository: AbstractUser,
    emails: list[MessageEntity]
) -> None:
    if event.text is None:
        return
    if event.from_user is None:
        return
    
    chat_id = event.chat.id
    user_id = event.from_user.id
    data = await state.get_data()
    direction = data['direction']
    surname, name, patronymic = get_sup(data['sup'])
    email = emails.pop().extract_from(event.text)
    
    data = await state.get_data()
    if msg_id := data.get('msg_id'):
        await bot.delete_message(
            chat_id=event.chat.id,
            message_id=msg_id
        )
    
    await user_repository.add(
        AddUserDto(
            date_time=IsoDateTime(datetime.now().isoformat()),
            user_id=UserId(user_id),
            chat_id=event.chat.id,
            surname=surname,
            name=name,
            patronymic=patronymic,
            email=email,
            direction=DirectionEnum(direction)
        )
    )
    cache.check_user[user_id] = True
    await event.answer(
        'Главное меню',
        reply_markup=keyboard.inline.main_menu()
    )
