from contextlib import suppress
from datetime import datetime

from aiogram import F, Router
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

from webinar.application.dto.common import ResultExistsDTO
from webinar.application.interfaces.delete_message import DeleteMessageData
from webinar.application.use_case.user.add_user import AddUserDTO
from webinar.domain.enums.direction_type import DirectionTrainingType
from webinar.domain.types import TgChatId, TgUserId
from webinar.infrastructure.adapters.cache import CacheStore
from webinar.presentation.annotaded import AddUserUseCaseDepends, TgDeleteMessageDepends
from webinar.presentation.inject import inject, InjectStrategy
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
    or_f(
        CommandStart(),
        and_f(F.text == "Отмена", RegisteringState.ask_sup)
    )
)
async def ask_direction_message_handler(
    event: Message,
    state: FSMContext,
    keyboard: KeyboardFactory
) -> None:
    await event.answer(
        "Здравствуйте, слушатель!\n" "Выберите направление",
        reply_markup=keyboard.inline.directions(),
    )
    await state.set_data({})
    await state.set_state(RegisteringState.ask_direction)


@route.callback_query(F.data == "ask_direction")
@inject(InjectStrategy.HANDLER)
async def ask_direction_callback_handler(
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
    if message_id := state_data.get("msg_id"):
        await tg_delete_message(
            DeleteMessageData(
                chat_id=event.message.chat.id,
                inline_message_id=event.message.message_id,
                message_id=message_id,
            )
        )
    await state.set_state(RegisteringState.ask_direction)
    await event.message.edit_text(
        "Здравствуйте, слушатель!\n" "Выберите направление",
        reply_markup=keyboard.inline.directions(),
    )


@route.callback_query(
    StateFilter(RegisteringState.ask_direction, RegisteringState.ask_email),
    or_f(Direction.filter(), F.data == "ask_sup_back"),
)
@inject(InjectStrategy.HANDLER)
async def ask_sup_callback_handler(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    tg_delete_message: TgDeleteMessageDepends,
    callback_data: Direction | None = None,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    data = await state.get_data()
    if message_id := data.get("msg_id"):
        await tg_delete_message(
            DeleteMessageData(
                chat_id=event.message.chat.id,
                inline_message_id=event.message.message_id,
                message_id=message_id,
            )
        )
    if callback_data:
        await state.update_data(
            direction=callback_data.type,
            msg_id=event.message.message_id
        )
    await state.set_state(RegisteringState.ask_sup)
    await event.message.edit_text(
        (
            "Введите ФИО в следующем формате: <Фамилия> <Имя> <Отчество>\n"
            "Например Иванов Иван Иванович.\n"
            "В случае отсутствия отчества, вы можете не писать его."
        ),
        reply_markup=keyboard.inline.back("ask_direction"),
        parse_mode=None,
    )


@route.callback_query(F.data == "send_sup", RegisteringState.ask_email)
@inject(InjectStrategy.HANDLER)
async def ask_sup_callback_handler_sup(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    tg_delete_message: TgDeleteMessageDepends,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    data = await state.get_data()
    if message_id := data.get("msg_id"):
        await tg_delete_message(
            DeleteMessageData(
                chat_id=event.message.chat.id,
                inline_message_id=event.message.message_id,
                message_id=message_id,
            )
        )
    await state.update_data(msg_id=event.message.message_id)
    await event.message.edit_text(
        "Введите ФИО в следующем формате: Ф И О\n"
        "Например Иванов Иван Иванович.\n"
        "В случае отсутствия отчества, вы можете не писать его.",
        reply_markup=keyboard.inline.back("ask_direction"),
    )
    await state.set_state(RegisteringState.ask_sup)


@route.message(RegisteringState.ask_sup, ~F.text.split(" ").len().in_({2, 3}))
@inject(InjectStrategy.HANDLER)
async def not_valid_sup(
    event: Message,
    state: FSMContext,
    keyboard: KeyboardFactory,
    tg_delete_message: TgDeleteMessageDepends,
) -> None:
    with suppress(TelegramBadRequest):
        await event.delete()
    
    state_data = await state.get_data()
    
    message_ids = [event.message_id]
    if message_id := state_data.get("msg_id"):
        message_ids.append(message_id)
    await tg_delete_message(
        DeleteMessageData(
            chat_id=event.chat.id,
            message_id=message_ids,
        )
    )
    
    msg = await event.answer(
        "Введите ФИО в следующем формате: Ф И О\n"
        "Например Иванов Иван Иванович.\n"
        "В случае отсутствия отчества, вы можете не писать его.",
        reply_markup=keyboard.inline.back("ask_direction"),
    )
    await state.update_data(msg_id=msg.message_id)
    await state.set_state(RegisteringState.ask_sup)


@route.message(RegisteringState.ask_sup, F.text.split(" ").len().in_({2, 3}))
@inject(InjectStrategy.HANDLER)
async def ask_email_handler(
    event: Message,
    state: FSMContext,
    keyboard: KeyboardFactory,
    tg_delete_message: TgDeleteMessageDepends,
) -> None:
    with suppress(TelegramBadRequest):
        await event.delete()
    
    state_data = await state.get_data()
    
    message_ids = [event.message_id]
    if message_id := state_data.get("msg_id"):
        message_ids.append(message_id)
    
    await tg_delete_message(
        DeleteMessageData(
            chat_id=event.chat.id,
            message_id=message_ids,
        )
    )
    msg = await event.answer(
        "Пришлите почту, которую вы указывали при регистрации на курс.",
        reply_markup=keyboard.inline.back("send_sup"),
    )
    await state.update_data(sup=event.text, msg_id=msg.message_id)
    await state.set_state(RegisteringState.ask_email)


@route.message(
    RegisteringState.ask_email,
    ~F.entities.extract(F.type == MessageEntityType.EMAIL),
)
@inject(InjectStrategy.HANDLER)
async def not_valid_email(
    event: Message,
    state: FSMContext,
    keyboard: KeyboardFactory,
    tg_delete_message: TgDeleteMessageDepends,
) -> None:
    state_data = await state.get_data()
    if message_id := state_data.get("msg_id"):
        await tg_delete_message(
            DeleteMessageData(
                chat_id=event.chat.id,
                message_id=message_id,
            )
        )
    msg = await event.answer(
        "Вы отправили не ту почту. Повторите попытку",
        reply_markup=keyboard.inline.back("send_sup"),
    )
    await state.update_data(msg_id=msg.message_id)


@route.message(
    RegisteringState.ask_email,
    F.entities.extract(F.type == MessageEntityType.EMAIL)[-1].as_(
        "email_entity"
    ),
    flags=dict(repo_uow=True),
)
@inject(InjectStrategy.HANDLER)
async def finish_handler(
    event: Message,
    state: FSMContext,
    cache: CacheStore,
    keyboard: KeyboardFactory,
    email_entity: MessageEntity,
    add_user_use_case: AddUserUseCaseDepends,
    tg_delete_message: TgDeleteMessageDepends,
) -> None:
    if event.text is None:
        return
    if event.from_user is None:
        return
    
    state_data = await state.get_data()
    message_ids = [event.message_id]
    if message_id := state_data.get("msg_id"):
        message_ids.append(message_id)
    
    await tg_delete_message(
        DeleteMessageData(
            chat_id=event.chat.id,
            message_id=message_ids,
        )
    )
    telegram_user_id = TgUserId(event.from_user.id)
    surname, name, patronymic = get_sup(state_data["sup"])
    await add_user_use_case(
        AddUserDTO(
            telegram_user_id=telegram_user_id,
            telegram_chat_id=TgChatId(event.chat.id),
            date_time_registration=datetime.now(),
            direction_training=DirectionTrainingType(state_data["direction"]),
            surname=surname,
            name=name,
            patronymic=patronymic,
            email=email_entity.extract_from(event.text),
        )
    )
    cache.exists_user[telegram_user_id] = ResultExistsDTO(True)
    await event.answer(
        "Главное меню", reply_markup=keyboard.inline.main_menu()
    )
