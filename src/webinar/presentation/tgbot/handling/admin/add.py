from contextlib import suppress

from aiogram import (
    Bot,
    F,
    Router
)
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import (
    and_f,
    MagicData,
    or_f,
    StateFilter
)
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    Message
)

from webinar.application.exceptions import (
    AdminCreated,
    NotFoundAdmin
)
from webinar.application.schemas.dto.admin import CreateAdminDTO
from webinar.application.schemas.dto.common import (
    DirectionsTrainingDTO,
    ResultExistsDTO,
)
from webinar.application.schemas.enums.direction_type import (
    DirectionTrainingType,
)
from webinar.application.schemas.types import TelegramUserId
from webinar.infrastructure.adapters.cache import CacheStore
from webinar.infrastructure.database.repository.admin import (
    AdminRepositoryImpl,
)
from webinar.infrastructure.word_range.main import parse_letters_range
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.keyboard.callback_data import Direction
from webinar.presentation.tgbot.states import AddAdminState


route = Router()
route.callback_query.filter(
    MagicData(F.is_super_admin),
    or_f(
        F.data == "add_admin",
        and_f(Direction.filter(), AddAdminState.ask_webinar_type),
    ),
)
route.message.filter(MagicData(F.is_super_admin), StateFilter(AddAdminState))


@route.callback_query(F.data == "add_admin")
async def ask_user_id(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    admin_repository: AdminRepositoryImpl,
    keyboard: KeyboardFactory,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        await event.answer('Нет доступа к сообщению. Введите /start', show_alert=True)
        return
    
    state_data = await state.get_data()
    if msg_id_ := state_data.get("msg_id"):
        with suppress(TelegramBadRequest):
            await bot.delete_message(
                chat_id=event.message.chat.id, message_id=msg_id_
            )
    smm_dto = DirectionsTrainingDTO([DirectionTrainingType.SMM])
    copyrighting_dto = DirectionsTrainingDTO(
        [DirectionTrainingType.COPYRIGHTING]
    )
    
    try:
        admin_entities = await admin_repository.read_all_by_direction_training(smm_dto)
    except NotFoundAdmin:
        smm_text = ""
    else:
        smm_text = admin_entities.string()
    try:
        admin_entities = await admin_repository.read_all_by_direction_training(copyrighting_dto)
    except NotFoundAdmin:
        copyrighting_text = ""
    else:
        copyrighting_text = admin_entities.string()
    
    msg_data = dict(
        text=f"Пришли телеграм айди администратора\n\nCMM:\n{smm_text}\n\nКопирайтинг:\n{copyrighting_text}",
        reply_markup=keyboard.inline.back("admin_panel")
    )
    try:
        await event.message.edit_text(**msg_data)  # type: ignore
    except TelegramBadRequest:
        msg = await event.message.answer(**msg_data)  # type: ignore
        msg_id = msg.message_id
    else:
        msg_id = event.message.message_id
    
    await state.set_data({"msg_id": msg_id})
    await state.set_state(AddAdminState.ask_user_id)


@route.message(F.text.as_("user_id"), AddAdminState.ask_user_id)
async def ask_webinar_type(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    user_id: str,
    is_super_admin: bool,
) -> None:
    try:
        user_id = TelegramUserId(user_id)
    except ValueError:
        msg = await event.answer(
            "Вы отправили не правильный айди. Повторите попытку.",
            reply_markup=keyboard.inline.back("add_admin"),
        )
        await state.set_data({"msg_id": msg.message_id})
        return None
    
    state_data = await state.get_data()
    if msg_id_ := state_data.get("msg_id"):
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id=event.chat.id, message_id=msg_id_)
    try:
        msg = await event.answer(
            "Вы хотите добавить этого юзера?\nЗа какое направление он будет отвечает?",
            reply_markup=keyboard.inline.select_direction_training_for(
                user_id
            ),
        )
    except TelegramBadRequest:
        msg = await event.answer(
            "Пользователь с данным user_id не писал боту",
            reply_markup=keyboard.inline.admin_main_menu(is_super_admin),
        )
        await state.set_data({"msg_id": msg.message_id})
        return
    with suppress(TelegramBadRequest):
        await event.delete()
    await state.set_data({"msg_id": msg.message_id, "user_id": user_id})
    await state.set_state(AddAdminState.ask_webinar_type)


@route.callback_query(AddAdminState.ask_webinar_type, Direction.filter())
async def ask_range_or_numb_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    callback_data: Direction,
    keyboard: KeyboardFactory,
) -> None:
    if event.message is None:
        return
    message = event.message
    if isinstance(message, InaccessibleMessage):
        return
    
    state_data = await state.get_data()
    if msg_id := state_data.get("msg_id"):
        with suppress(TelegramBadRequest):
            await bot.delete_message(
                chat_id=event.message.chat.id, message_id=msg_id
            )
    msg = await message.answer(
        "Введи диапазон букв или выбери числовой диапазон. Диапазон букв А-В",
        reply_markup=keyboard.reply.save(),
    )
    await state.update_data(
        msg_id=msg.message_id, direction_training=callback_data.type
    )
    await state.set_state(AddAdminState.ask_range_or_numb)


@route.message(AddAdminState.ask_range_or_numb, flags=dict(repo_uow=True))
async def get_word_range(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    admin_repository: AdminRepositoryImpl,
    is_super_admin: bool,
    cache: CacheStore,
) -> None:
    if event.from_user is None or event.text is None:
        return
    
    state_data = await state.get_data()
    if msg_id := state_data.get("msg_id"):
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id=event.chat.id, message_id=msg_id)
    user_id = TelegramUserId(state_data["user_id"])
    if event.text == "Числовой диапазон":
        model = CreateAdminDTO(
            telegram_user_id=user_id,
            direction_training=state_data["direction_training"],
            numbers_range=True,
        )
    else:
        try:
            letters_range = parse_letters_range(event.text)
        except ValueError:
            msg = await event.answer(
                "Не правильный формат. Введи еще раз",
                reply_markup=keyboard.inline.back("add_admin"),
            )
            await state.update_data(msg_id=msg.message_id)
            return None
        except KeyError:
            msg = await event.answer(
                "Вы ввели не русские буквы. Введи еще раз",
                reply_markup=keyboard.inline.back("add_admin"),
            )
            await state.update_data(msg_id=msg.message_id)
            return None
        else:
            model = CreateAdminDTO(
                telegram_user_id=user_id,
                direction_training=state_data["direction_training"],
                letters_range=letters_range,
            )
    
    try:
        await admin_repository.create(model)
    except AdminCreated:
        await event.answer(
            text="Пользователь уже добавлен в качестве администратора",
            reply_markup=keyboard.inline.admin_main_menu(is_super_admin),
        )
        return None
    await event.answer(
        "Вы добавили администратора",
        reply_markup=keyboard.inline.admin_main_menu(is_super_admin),
    )
    cache.exists_admin[TelegramUserId(event.from_user.id)] = ResultExistsDTO(
        True
    )
    with suppress(TelegramBadRequest):
        await event.delete()
    await state.clear()
