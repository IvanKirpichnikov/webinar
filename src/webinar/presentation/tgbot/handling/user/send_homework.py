from datetime import datetime
from typing import cast

from aiogram import F, Router
from aiogram.enums import MessageEntityType
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    Message,
    MessageEntity,
)

from webinar.application.dto.common import TgUserIdDTO
from webinar.application.interfaces.delete_message import DeleteMessageData
from webinar.application.use_case.homeworks.add_user_homework import AddUserHomeWorkDTO
from webinar.application.use_case.homeworks.read_user_homeworks import ReadUserHomeworkError
from webinar.domain.enums.homework import HomeWorkStatusType
from webinar.domain.types import HomeWorkNumber, TgUserId
from webinar.presentation.annotaded import (
    AddUserHomeWorkDepends,
    ReadUserHomeWorksDepends,
    TgDeleteMessageDepends,
)
from webinar.presentation.inject import inject, InjectStrategy
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.keyboard.callback_data import (
    SelectHomeWorkByNumber,
)
from webinar.presentation.tgbot.states import AskHomeWorkState


route = Router()


@route.callback_query(F.data == "send_homework")
@inject(InjectStrategy.HANDLER)
async def select_homework_number(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    tg_delete_message: TgDeleteMessageDepends,
    read_user_homeworks: ReadUserHomeWorksDepends
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    message_ids = [event.message.message_id]
    state_data = await state.get_data()
    if message_id := state_data.get("msg_id"):
        message_ids.append(message_id)
    await tg_delete_message(
        DeleteMessageData(
            chat_id=event.message.chat.id,
            message_id=message_id
        )
    )
    try:
        homeworks = await read_user_homeworks(
            TgUserIdDTO(TgUserId(event.from_user.id))
        )
    except ReadUserHomeworkError:
        ids = list(range(1, 8))
    else:
        if len(homeworks.homeworks) == 7:
            await event.answer(
                "Вы сдали все домашние задания", show_alert=True
            )
            return None
        ids = list(
            filter(
                lambda x: x not in list(
                    map(lambda y: y.number, homeworks.homeworks)
                ),
                range(1, 8),
            )
        )
    
    try:
        await event.message.edit_text(
            "Выбери номер домашнего задания",
            reply_markup=keyboard.inline.select_homework(cast(list[HomeWorkNumber], ids))
        )
    except TelegramBadRequest:
        await event.message.answer(
            "Выбери номер домашнего задания",
            reply_markup=keyboard.inline.select_homework(cast(list[HomeWorkNumber], ids))
        )
    await state.set_state(AskHomeWorkState.ask_number)


@route.callback_query(
    AskHomeWorkState.ask_number, SelectHomeWorkByNumber.filter()
)
async def ask_url_homework_handler(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    callback_data: SelectHomeWorkByNumber,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    await event.message.edit_text(
        "Отправь ссылку с домашним заданием на Google Docs.\n"
        "Проверьте, чтоб в вашей работе были ссылки на прокомментированные вами работы.",
        reply_markup=keyboard.inline.back("send_homework"),
    )
    await state.update_data(
        msg_id=event.message.message_id,
        number=callback_data.number
    )
    await state.set_state(AskHomeWorkState.ask_url)


@route.message(
    AskHomeWorkState.ask_url,
    F.entities.extract(F.type == MessageEntityType.URL)[0].as_("url_entity"),
    flags=dict(repo_uow=True),
)
@inject(InjectStrategy.HANDLER)
async def add_homework_handler(
    event: Message,
    state: FSMContext,
    url_entity: MessageEntity,
    keyboard: KeyboardFactory,
    add_user_homework: AddUserHomeWorkDepends,
    tg_delete_message: TgDeleteMessageDepends,
) -> None:
    if event.text is None:
        return None
    if event.from_user is None:
        return None
    
    url = url_entity.extract_from(event.text)
    if not url.startswith("https://docs.google.com"):
        await _not_valid_url(event, state, keyboard, tg_delete_message)
        return None
    
    state_data = await state.get_data()
    message_ids = [event.message_id]
    if msg_id := state_data.get("msg_id"):
        message_ids.append(msg_id)
    await tg_delete_message(
        DeleteMessageData(
            chat_id=event.chat.id,
            message_id=message_ids
        )
    )
    
    await add_user_homework(
        AddUserHomeWorkDTO(
            telegram_user_id=TgUserId(event.from_user.id),
            date_time_registration=datetime.now(),
            status_type=HomeWorkStatusType.UNDER_INSPECTION,
            number=state_data["number"],
            url=url,
        )
    )
    await event.answer(
        "<b>Работа отправлена на проверку</b>",
        reply_markup=keyboard.inline.main_menu()
    )
    await state.clear()


@route.message(AskHomeWorkState.ask_url)
@inject(InjectStrategy.HANDLER)
async def not_valid_url(
    event: Message,
    state: FSMContext,
    keyboard: KeyboardFactory,
    tg_delete_message: TgDeleteMessageDepends
) -> None:
    await _not_valid_url(event, state, keyboard, tg_delete_message)


async def _not_valid_url(
    event: Message,
    state: FSMContext,
    keyboard: KeyboardFactory,
    tg_delete_message: TgDeleteMessageDepends
) -> None:
    state_data = await state.get_data()
    message_ids = [event.message_id]
    if msg_id := state_data.get("msg_id"):
        message_ids.append(msg_id)
    
    await tg_delete_message(
        DeleteMessageData(
            chat_id=event.chat.id,
            message_id=message_ids
        )
    )
    msg = await event.answer(
        "Вы отправили неправильную ссылку",
        reply_markup=keyboard.inline.back("send_homework"),
    )
    await state.update_data(msg_id=msg.message_id)
