from aiogram import F, Router
from aiogram.enums import MessageEntityType
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    Message,
    MessageEntity,
)

from webinar.application.dto.webinar import CreateWebinarDTO
from webinar.application.exceptions import DuplicateWebinar
from webinar.application.interfaces.delete_message import DeleteMessageData
from webinar.presentation.annotaded import CreateWebinarDepends, TgDeleteMessageDepends
from webinar.presentation.inject import inject, InjectStrategy
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.states import AddWebinarState


route = Router()
route.callback_query.filter(F.data == "create_webinar")


@route.callback_query(F.data == "create_webinar")
async def ash_webinar_url_handler(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    await event.message.edit_text(
        "Пришли ссылку на вебинар",
        reply_markup=keyboard.inline.back("admin_panel"),
    )
    await state.set_state(AddWebinarState.ask_url)
    await state.update_data(msg_id=event.message.message_id)


@route.message(
    AddWebinarState.ask_url,
    F.entities.extract(F.type == MessageEntityType.URL)[-1].as_("url_entity"),
)
@inject(InjectStrategy.HANDLER)
async def ask_webinar_name(
    event: Message,
    state: FSMContext,
    keyboard: KeyboardFactory,
    url_entity: MessageEntity,
    tg_delete_message: TgDeleteMessageDepends
) -> None:
    if event.text is None:
        return
    
    url = url_entity.extract_from(event.text)
    
    message_ids = [event.message_id]
    state_data = await state.get_data()
    if message_id := state_data.get("msg_id"):
        message_ids.append(message_id)
    
    await tg_delete_message(
        DeleteMessageData(
            chat_id=event.chat.id,
            message_id=message_ids
        )
    )
    
    msg = await event.answer(
        'Пришли дату вебинара и ФИО лектора.\nФормат: "20.07 Иванов И.И."',
        reply_markup=keyboard.inline.back("publish_webinar_recording"),
    )
    await state.update_data(url=url, msg_id=msg.message_id)
    await state.set_state(AddWebinarState.ask_name)


@route.message(AddWebinarState.ask_name, flags=dict(repo_uow=True))
@inject(InjectStrategy.HANDLER)
async def get_webinar_name_handler(
    event: Message,
    state: FSMContext,
    keyboard: KeyboardFactory,
    is_super_admin: bool,
    tg_delete_message: TgDeleteMessageDepends,
    use_case: CreateWebinarDepends,
) -> None:
    if event.text is None:
        return
    
    state_data = await state.get_data()
    message_ids = [event.message_id]
    state_data = await state.get_data()
    if message_id := state_data.get("msg_id"):
        message_ids.append(message_id)
    
    await tg_delete_message(
        DeleteMessageData(
            chat_id=event.chat.id,
            message_id=message_ids
        )
    )
    try:
        await use_case(
            CreateWebinarDTO(
                url=state_data["url"],
                name=event.text
            )
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
    await state.clear()
