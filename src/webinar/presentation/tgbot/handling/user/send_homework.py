from contextlib import suppress
from datetime import datetime
from typing import cast

from aiogram import Bot, F, Router
from aiogram.enums import MessageEntityType
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    Message,
    MessageEntity,
)
from psycopg.errors import UniqueViolation

from webinar.application.exceptions import NotFoundHomeworks
from webinar.application.schemas.dto.common import TelegramUserIdDTO
from webinar.application.schemas.dto.homework import CreateHomeWorkDTO
from webinar.application.schemas.enums.homework import HomeWorkStatusType
from webinar.application.schemas.types import HomeWorkNumber, TelegramUserId
from webinar.infrastructure.database.repository.homework import (
    HomeWorkRepositoryImpl,
)
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.keyboard.callback_data import (
    SelectHomeWorkByNumber,
)
from webinar.presentation.tgbot.states import AskHomeWorkState


route = Router()


# route.callback_query.filter(
#     or_f(
#         and_f(
#             HomeWorkCallbackData.filter(),
#             AskHomeWorkState.ask_number,
#         ),
#         F.data == 'send_homework'
#     )
# )
# route.message.filter(
#     AskHomeWorkState.ask_url,
#     F.entities.extract(F.type == MessageEntityType.URL)
# )


@route.callback_query(F.data == "send_homework")
async def select_homework_number(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    homework_repository: HomeWorkRepositoryImpl,
    keyboard: KeyboardFactory,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return

    state_data = await state.get_data()
    if msg_id := state_data.get("msg_id"):
        if msg_id != event.message.message_id:
            with suppress(TelegramBadRequest):
                await bot.delete_message(
                    chat_id=event.message.chat.id, message_id=msg_id
                )
    homeworks_dto = TelegramUserIdDTO(TelegramUserId(event.from_user.id))
    try:
        homeworks = await homework_repository.read_all_by_telegram_user_id(
            homeworks_dto
        )
    except NotFoundHomeworks:
        ids = list(range(1, 8))
    else:
        ids = list(
            filter(
                lambda x: x
                not in list(map(lambda y: y.number, homeworks.homeworks)),
                range(1, 8),
            )
        )
        if len(homeworks.homeworks) == 7:
            await event.answer(
                "Вы сдали все домашние задания", show_alert=True
            )
            return None

    await event.message.edit_text(
        "Выбери номер домашнего задания",
        reply_markup=keyboard.inline.select_homework(
            cast(list[HomeWorkNumber], ids)
        ),
    )
    await state.set_state(AskHomeWorkState.ask_number)


@route.callback_query(
    AskHomeWorkState.ask_number, SelectHomeWorkByNumber.filter()
)
async def ask_url_homework_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    callback_data: SelectHomeWorkByNumber,
    keyboard: KeyboardFactory,
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
        msg_id=event.message.message_id, number=callback_data.number
    )
    await state.set_state(AskHomeWorkState.ask_url)


@route.message(
    AskHomeWorkState.ask_url,
    ~F.entities.extract(F.type == MessageEntityType.URL),
)
async def not_valid_url(
    event: Message, bot: Bot, state: FSMContext, keyboard: KeyboardFactory
) -> None:
    state_data = await state.get_data()
    if msg_id := state_data.get("msg_id"):
        await bot.delete_message(chat_id=event.chat.id, message_id=msg_id)
    msg = await event.answer(
        "Вы отправили не правильную ссылку",
        reply_markup=keyboard.inline.back("send_homework"),
    )
    await event.delete()
    await state.update_data(msg_id=msg.message_id)
    return None


@route.message(
    AskHomeWorkState.ask_url,
    F.entities.extract(F.type == MessageEntityType.URL)[-1].as_("url_entity"),
    flags=dict(repo_uow=True),
)
async def add_homework_handler(
    event: Message,
    bot: Bot,
    state: FSMContext,
    homework_repository: HomeWorkRepositoryImpl,
    url_entity: MessageEntity,
    keyboard: KeyboardFactory,
) -> None:
    if event.text is None:
        return None
    if event.from_user is None:
        return None

    user = event.from_user
    url = url_entity.extract_from(event.text)
    if not url.startswith("https://docs.google.com"):
        await not_valid_url(event, bot, state, keyboard)
        return None

    state_data = await state.get_data()
    if msg_id := state_data.get("msg_id"):
        await bot.delete_message(chat_id=event.chat.id, message_id=msg_id)
    number = state_data["number"]
    with suppress(UniqueViolation):
        await homework_repository.create(
            CreateHomeWorkDTO(
                telegram_user_id=TelegramUserId(user.id),
                date_time_registration=datetime.now(),
                status_type=HomeWorkStatusType.UNDER_INSPECTION,
                number=number,
                url=url,
            )
        )
    await event.answer(
        "Задание успешно сдано", reply_markup=keyboard.inline.main_menu()
    )
    await event.delete()
    await state.clear()
    return None
