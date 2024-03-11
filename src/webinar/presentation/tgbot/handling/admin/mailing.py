import lz4.frame
import orjson
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, Message
from faststream.nats import NatsBroker

from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.keyboard.callback_data import Direction
from webinar.presentation.tgbot.states import MailingState


route = Router()


@route.callback_query(F.data.in_({"mailing", 'back'}))
async def ask_direction_handler(
    event: CallbackQuery, state: FSMContext, keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        await event.answer('Нет доступа к сообщению. Введите /start', show_alert=True)
        return
    
    await event.message.edit_text(
        "Выбери направление",
        reply_markup=keyboard.inline.ask_direction_admin_to_mailing(),
    )
    await state.set_state(MailingState.ask_direction)


@route.callback_query(MailingState.ask_direction, Direction.filter())
async def ask_mailing_handler(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    callback_data: Direction,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        await event.answer('Нет доступа к сообщению. Введите /start', show_alert=True)
        return
    
    await event.message.edit_text(
        "Введи сообщение",
        reply_markup=keyboard.inline.back('back')
    )
    await state.set_state(MailingState.ask_message)
    await state.update_data(direction_training=callback_data.type)


@route.message(MailingState.ask_message)
async def mailing_handler(
    event: Message,
    state: FSMContext,
    keyboard: KeyboardFactory,
    is_super_admin: bool,
    broker: NatsBroker,
) -> None:
    state_data = await state.get_data()
    payload = dict(
        admin_chat_id=event.chat.id,
        mailing_msg_id=event.message_id,
        direction_training=state_data["direction_training"],
    )
    await broker.publish(
        message=lz4.frame.compress(orjson.dumps(payload)),
        subject="start-mailing-aa",
    )
    await event.answer(
        "Рассылка началась",
        reply_markup=keyboard.inline.admin_main_menu(is_super_admin),
    )
    await state.clear()
