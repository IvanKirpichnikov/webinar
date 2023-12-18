import lz4.frame
import orjson
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from faststream.nats import NatsBroker

from src.application.schemas.enums import DirectionEnum
from src.presentation.tgbot.keyboard import KeyboardFactory
from src.presentation.tgbot.keyboard.callback_data import AskDirectionCallbackData
from src.presentation.tgbot.states import MailingState


route = Router()


@route.callback_query(F.data == 'mailing')
async def ask_direction_handler(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    await event.message.edit_text(
        'Выбери направление',
        reply_markup=keyboard.inline.ask_direction_admin_to_mailing()
    )
    await state.set_state(MailingState.ask_direction)


@route.callback_query(MailingState.ask_direction, AskDirectionCallbackData.filter())
async def ask_mailing_handler(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    callback_data: AskDirectionCallbackData
) -> None:
    if event.message is None:
        return
    if callback_data.type == 'all':
        direction_type = [DirectionEnum.SMM.value, DirectionEnum.COPYRIGHTING.value]
    else:
        direction_type = [callback_data.type.value]
    
    await state.update_data(direction_type=direction_type)
    await event.message.edit_text('Введи сообщение')
    await state.set_state(MailingState.ask_message)


@route.message(MailingState.ask_message, F.text)
async def mailing_handler(
    event: Message,
    broker: NatsBroker,
    keyboard: KeyboardFactory,
    state: FSMContext,
    is_super_admin: bool
) -> None:
    await event.answer('Рассылка началась', reply_markup=keyboard.inline.admin_panel(is_super_admin))
    data = await state.get_data()
    payload = dict(
        admin_chat_id=event.chat.id,
        mailing_msg_id=event.message_id,
        direction_type=data.get('direction_type')
    )
    await broker.publish(
        message=lz4.frame.compress(orjson.dumps(payload)),
        subject='start-mailing',
    )
    await state.clear()
