from contextlib import suppress
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.enums import MessageEntityType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import and_f, CommandStart, or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    Message,
    MessageEntity,
)

from webinar.application.schemas.dto.common import ResultExistsDTO
from webinar.application.schemas.dto.user import CreateUserDTO
from webinar.application.schemas.enums.direction_type import (
    DirectionTrainingType,
)
from webinar.application.schemas.types import TelegramChatId, TelegramUserId
from webinar.infrastructure.adapters.cache import CacheStore
from webinar.infrastructure.database.repository.user import UserRepositoryImpl
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.keyboard.callback_data import Direction
from webinar.presentation.tgbot.states import RegisteringState


route = Router()


def get_sup(sup_: str) -> tuple[str, str, str | None]:
    sup = sup_.split(" ")
    surname = sup[0]
    name = sup[1]
    try:
        patronymic = sup[2]
    except IndexError:
        patronymic = None
    return surname, name, patronymic


@route.message(
    or_f(CommandStart(), and_f(F.text == "Отмена", RegisteringState.ask_sup))
)
async def ask_direction_message_handler(
    event: Message, state: FSMContext, keyboard: KeyboardFactory
) -> None:
    await event.answer(
        "Здравствуйте, слушатель!\n" "Выберите направление",
        reply_markup=keyboard.inline.directions(),
    )
    await state.set_data({})
    await state.set_state(RegisteringState.ask_direction)


@route.callback_query(F.data == "ask_direction")
async def ask_direction_callback_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        await event.answer('Нет доступа к сообщению. Введите /start', show_alert=True)
        return
    
    await event.message.edit_text(
        "Здравствуйте, слушатель!\n" "Выберите направление",
        reply_markup=keyboard.inline.directions(),
    )
    state_data = await state.get_data()
    if msg_id := state_data.get("msg_id"):
        if msg_id != event.message.message_id:
            with suppress(TelegramBadRequest):
                await bot.delete_message(
                    chat_id=event.message.chat.id, message_id=msg_id
                )
    await state.set_state(RegisteringState.ask_direction)


@route.callback_query(
    StateFilter(RegisteringState.ask_direction, RegisteringState.ask_email),
    or_f(Direction.filter(), F.data == "ask_sup_back"),
)
async def ask_sup_callback_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    callback_data: Direction | None = None,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        await event.answer('Нет доступа к сообщению. Введите /start', show_alert=True)
        return
    
    data = await state.get_data()
    await event.message.edit_text(
        (
            "Введите ФИО в следующем формате: <Фамилия> <Имя> <Отчество>\n"
            "Например Иванов Иван Иванович.\n"
            "В случае отсутствия отчества, вы можете не писать его."
        ),
        reply_markup=keyboard.inline.back("ask_direction"),
        parse_mode=None,
    )
    if callback_data:
        await state.update_data(
            direction=callback_data.type, msg_id=event.message.message_id
        )
    
    if msg_id := data.get("msg_id"):
        if msg_id != event.message.message_id:
            with suppress(TelegramBadRequest):
                await bot.delete_message(
                    chat_id=event.message.chat.id, message_id=msg_id
                )
    await state.set_state(RegisteringState.ask_sup)


@route.callback_query(F.data == "send_sup", RegisteringState.ask_email)
async def ask_sup_callback_handler_sup(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        await event.answer('Нет доступа к сообщению. Введите /start', show_alert=True)
        return
    
    await event.message.edit_text(
        (
            "Введите ФИО в следующем формате: Ф И О\n"
            "Например Иванов Иван Иванович.\n"
            "В случае отсутствия отчества, вы можете не писать его."
        ),
        reply_markup=keyboard.inline.back("ask_direction"),
    )
    data = await state.get_data()
    if msg_id := data.get("msg_id"):
        if msg_id != event.message.message_id:
            with suppress(TelegramBadRequest):
                await bot.delete_message(
                    chat_id=event.message.chat.id, message_id=msg_id
                )
    await state.update_data(msg_id=event.message.message_id)
    await state.set_state(RegisteringState.ask_sup)


@route.message(RegisteringState.ask_sup, ~F.text.split(" ").len().in_({2, 3}))
async def not_valid_sup(
    event: Message, bot: Bot, state: FSMContext, keyboard: KeyboardFactory
) -> None:
    with suppress(TelegramBadRequest):
        await event.delete()
    msg = await event.answer(
        (
            "Введите ФИО в следующем формате: Ф И О\n"
            "Например Иванов Иван Иванович.\n"
            "В случае отсутствия отчества, вы можете не писать его."
        ),
        reply_markup=keyboard.inline.back("ask_direction"),
    )
    state_data = await state.get_data()
    if msg_id := state_data.get("msg_id"):
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id=event.chat.id, message_id=msg_id)
    await state.update_data(msg_id=msg.message_id)
    await state.set_state(RegisteringState.ask_sup)


@route.message(RegisteringState.ask_sup, F.text.split(" ").len().in_({2, 3}))
async def ask_email_handler(
    event: Message, bot: Bot, state: FSMContext, keyboard: KeyboardFactory
) -> None:
    with suppress(TelegramBadRequest):
        await event.delete()
    msg = await event.answer(
        "Пришлите почту, которую вы указывали при регистрации на курс.",
        reply_markup=keyboard.inline.back("send_sup"),
    )
    state_data = await state.get_data()
    if msg_id := state_data.get("msg_id"):
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id=event.chat.id, message_id=msg_id)
    await state.update_data(sup=event.text, msg_id=msg.message_id)
    await state.set_state(RegisteringState.ask_email)


@route.message(
    RegisteringState.ask_email,
    ~F.entities.extract(F.type == MessageEntityType.EMAIL),
)
async def not_valid_email(
    event: Message, bot: Bot, state: FSMContext, keyboard: KeyboardFactory
) -> None:
    msg = await event.answer(
        "Вы отправили не ту почту. Повторите попытку",
        reply_markup=keyboard.inline.back("send_sup"),
    )
    data = await state.get_data()
    if msg_id := data.get("msg_id"):
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id=event.chat.id, message_id=msg_id)
    await state.update_data(msg_id=msg.message_id)


@route.message(
    RegisteringState.ask_email,
    F.entities.extract(F.type == MessageEntityType.EMAIL)[-1].as_(
        "email_entity"
    ),
    flags=dict(repo_uow=True),
)
async def finish_handler(
    event: Message,
    bot: Bot,
    state: FSMContext,
    cache: CacheStore,
    keyboard: KeyboardFactory,
    user_repository: UserRepositoryImpl,
    email_entity: MessageEntity,
) -> None:
    if event.text is None:
        return
    if event.from_user is None:
        return
    
    state_data = await state.get_data()
    chat_id = TelegramChatId(event.chat.id)
    user_id = TelegramUserId(event.from_user.id)
    email = email_entity.extract_from(event.text)
    direction = state_data["direction"]
    surname, name, patronymic = get_sup(state_data["sup"])
    
    if msg_id := state_data.get("msg_id"):
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id=event.chat.id, message_id=msg_id)
    await user_repository.create(
        CreateUserDTO(
            telegram_user_id=user_id,
            telegram_chat_id=chat_id,
            date_time_registration=datetime.now(),
            direction_training=DirectionTrainingType(direction),
            surname=surname,
            name=name,
            patronymic=patronymic,
            email=email,
        )
    )
    cache.exists_user[user_id] = ResultExistsDTO(True)
    with suppress(TelegramBadRequest):
        await event.delete()
    
    await event.answer(
        "Главное меню", reply_markup=keyboard.inline.main_menu()
    )
