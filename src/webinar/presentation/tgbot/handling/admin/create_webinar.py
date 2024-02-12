from contextlib import suppress

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

from webinar.application.exceptions import DuplicateWebinar
from webinar.application.schemas.dto.webinar import CreateWebinarDTO
from webinar.infrastructure.database.repository.webinar import (
    WebinarRepositoryImpl,
)
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.states import AddWebinarState


route = Router()
route.callback_query.filter(F.data == "create_webinar")


@route.callback_query(F.data == "create_webinar")
async def ash_webinar_url_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
) -> None:
    if event.message is None:
        return
    message = event.message
    if isinstance(message, InaccessibleMessage):
        return

    await message.edit_text(
        "Пришли ссылку на вебинар",
        reply_markup=keyboard.inline.back("admin_panel"),
    )
    await state.set_state(AddWebinarState.ask_url)
    await state.update_data(msg_id=event.message.message_id)


@route.message(
    AddWebinarState.ask_url,
    F.entities.extract(F.type == MessageEntityType.URL)[-1].as_("url_entity"),
)
async def ask_webinar_name(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    url_entity: MessageEntity,
) -> None:
    if event.text is None:
        return

    url = url_entity.extract_from(event.text)
    state_data = await state.get_data()
    if msg_id := state_data.get("msg_id"):
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id=event.chat.id, message_id=msg_id)
    with suppress(TelegramBadRequest):
        await event.delete()
    msg = await event.answer(
        'Пришли дату вебинара и ФИО лектора.\nФормат: "20.07 Иванов И.И."',
        reply_markup=keyboard.inline.back("publish_webinar_recording"),
    )
    await state.update_data(url=url, msg_id=msg.message_id)
    await state.set_state(AddWebinarState.ask_name)


@route.message(AddWebinarState.ask_name, flags=dict(repo_uow=True))
async def get_webinar_name_handler(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    webinar_repository: WebinarRepositoryImpl,
    is_super_admin: bool,
) -> None:
    if event.text is None:
        return

    state_data = await state.get_data()
    if msg_id := state_data.get("msg_id"):
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id=event.chat.id, message_id=msg_id)
    try:
        await webinar_repository.create(
            CreateWebinarDTO(url=state_data["url"], name=event.text)
        )
    except DuplicateWebinar:
        msg = await event.answer(
            "Вебинар с такой ссылкой уже есть. Введи другую ссылку",
            reply_markup=keyboard.inline.admin_main_menu(is_super_admin),
        )
        await state.update_data(msg_id=msg.message_id)
        await state.set_state(AddWebinarState.ask_url)
        return None

    await event.answer(
        "Вебинар добавлен",
        reply_markup=keyboard.inline.admin_main_menu(is_super_admin),
    )
    with suppress(TelegramBadRequest):
        await event.delete()
    await state.clear()
