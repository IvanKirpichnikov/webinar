from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import and_f, MagicData, or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, Message

from webinar.application.dto.admin import CreateAdminDTO
from webinar.application.dto.common import DirectionsTrainingDTO, ResultExistsDTO
from webinar.application.exceptions import (
    AdminCreated,
)
from webinar.application.interfaces.delete_message import DeleteMessageData
from webinar.application.use_case.admin.read_all_by_direction_training import \
    NotFoundAdminsToTrainingDirection
from webinar.domain.enums.direction_type import DirectionTrainingType
from webinar.domain.types import TgUserId
from webinar.infrastructure.adapters.cache import CacheStore
from webinar.infrastructure.word_range import parse_letters_range
from webinar.presentation.annotaded import (
    CreateAdminDepends, ReadAllAdminByDirectionTrainingDepends,
    TgDeleteMessageDepends,
)
from webinar.presentation.inject import inject, InjectStrategy
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
@inject(InjectStrategy.HANDLER)
async def ask_user_id(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    tg_delete_message: TgDeleteMessageDepends,
    read_admins_by_dt: ReadAllAdminByDirectionTrainingDepends,
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
                message_id=message_id
            )
        )
    try:
        admin_entities = await read_admins_by_dt(
            DirectionsTrainingDTO([DirectionTrainingType.SMM])
        )
    except NotFoundAdminsToTrainingDirection:
        smm_text = ""
    else:
        smm_text = admin_entities.string()
    try:
        admin_entities = await read_admins_by_dt(
            DirectionsTrainingDTO(
                [DirectionTrainingType.COPYRIGHTING]
            )
        )
    except NotFoundAdminsToTrainingDirection:
        copyrighting_text = ""
    else:
        copyrighting_text = admin_entities.string()
    
    msg_data = dict(
        text=f"Пришли телеграм айди администратора\n\nCMM:\n{smm_text}\n\nКопирайтинг:\n"
             f"{copyrighting_text}",
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
@inject(InjectStrategy.HANDLER)
async def ask_webinar_type(
    event: Message,
    state: FSMContext,
    keyboard: KeyboardFactory,
    is_super_admin: bool,
    tg_delete_message: TgDeleteMessageDepends,
    user_id: str,
) -> None:
    try:
        user_id = TgUserId(user_id)
    except ValueError:
        msg = await event.answer(
            "Вы отправили не правильный айди. Повторите попытку.",
            reply_markup=keyboard.inline.back("add_admin"),
        )
        await state.set_data({"msg_id": msg.message_id})
        return None
    
    message_ids = [event.message_id]
    state_data = await state.get_data()
    if message_id := state_data.get("msg_id"):
        message_ids.append(message_id)
    
    await tg_delete_message(
        DeleteMessageData(
            chat_id=event.chat.id,
            message_id=message_id
        )
    )
    
    try:
        try:
            msg = await event.answer(
                "Вы хотите добавить этого юзера?\nЗа какое направление он будет отвечает?",
                reply_markup=keyboard.inline.select_direction_training_for(
                    user_id
                ),
            )
        except TelegramBadRequest:
            msg = await event.answer(
                "Вы хотите добавить этого юзера?\nЗа какое направление он будет отвечает?",
                reply_markup=keyboard.inline.select_direction_training_for(
                    user_id, True
                ),
            )
    except TelegramBadRequest:
        msg = await event.answer(
            "Пользователь с данным user_id не писал боту",
            reply_markup=keyboard.inline.admin_main_menu(is_super_admin),
        )
        await state.set_data({"msg_id": msg.message_id})
        return None
    
    await state.set_data({"msg_id": msg.message_id, "user_id": user_id})
    await state.set_state(AddAdminState.ask_webinar_type)


@route.callback_query(AddAdminState.ask_webinar_type, Direction.filter())
@inject(InjectStrategy.HANDLER)
async def ask_range_or_numb_handler(
    event: CallbackQuery,
    state: FSMContext,
    callback_data: Direction,
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
                message_id=message_id
            )
        )
    
    msg = await event.message.answer(
        "Введи диапазон букв или выбери числовой диапазон. Диапазон букв А-В",
        reply_markup=keyboard.reply.save(),
    )
    await state.update_data(
        msg_id=msg.message_id,
        direction_training=callback_data.type
    )
    await state.set_state(AddAdminState.ask_range_or_numb)


@route.message(AddAdminState.ask_range_or_numb, flags=dict(repo_uow=True))
@inject(InjectStrategy.HANDLER)
async def get_word_range(
    event: Message,
    state: FSMContext,
    keyboard: KeyboardFactory,
    is_super_admin: bool,
    cache: CacheStore,
    tg_delete_message: TgDeleteMessageDepends,
    use_case: CreateAdminDepends
) -> None:
    if event.from_user is None:
        return None
    if event.text is None:
        return None
    
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
    tg_user_id = TgUserId(state_data["user_id"])
    if event.text == "Числовой диапазон":
        model = CreateAdminDTO(
            telegram_user_id=tg_user_id,
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
                telegram_user_id=tg_user_id,
                direction_training=state_data["direction_training"],
                letters_range=letters_range,
            )
    
    try:
        await use_case(model)
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
    cache.exists_admin[TgUserId(event.from_user.id)] = ResultExistsDTO(
        True
    )
    await state.clear()
