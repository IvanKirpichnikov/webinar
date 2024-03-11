from contextlib import suppress

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ErrorEvent, InaccessibleMessage, Message

from webinar.application.dto.common import TgUserIdDTO
from webinar.application.dto.homework import (
    HomeWorkIdDTO,
    HomeWorkPaginationDTO,
    UpdateHomeworkEvolutionAndStatusDTO, UpdatingTypeAndCommentByIdDTO,
)
from webinar.application.interfaces.delete_message import DeleteMessageData
from webinar.application.use_case.homeworks.read_for_pagination import NoFoundHomeworksForPagination
from webinar.config import ConfigFactory
from webinar.domain.enums.direction_type import DirectionTrainingType
from webinar.domain.enums.homework import EvaluationType, HomeWorkStatusType
from webinar.domain.models.homework import HOMEWORKS_TEXT_FROM_SPREADSHEETS
from webinar.domain.types import TgUserId
from webinar.infrastructure.postgres.repository.homework import (
    HomeWorkRepositoryImpl,
)
from webinar.presentation.annotaded import (
    ReadAdminDataByTgUserIdDepends,
    ReadHomeworkAndUserInfoByDBIdDepends,
    ReadUserHomeworksForPaginationDepends,
    TgDeleteMessageDepends, UpdateHomeworkEvolutionAndStatusDepends,
)
from webinar.presentation.inject import inject, InjectStrategy
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.keyboard.callback_data import (
    Pagination,
    SelectHomeWorkByDBId,
)
from webinar.presentation.tgbot.states import AdminHomeWorksState


route = Router()


@route.errors(ExceptionTypeFilter(KeyError))
async def error_key(error: ErrorEvent, state: FSMContext, keyboard, is_super_admin) -> None:
    update = error.update
    if update.message:
        message = update.message
    elif update.callback_query:
        if update.callback_query.message:
            message = update.callback_query.message
            if isinstance(message, InaccessibleMessage):
                raise error.exception
        else:
            raise error.exception
    else:
        raise error.exception
    await message.answer(
        "Админка",
        reply_markup=keyboard.inline.admin_main_menu(is_super_admin)
    )
    await state.clear()


@route.callback_query(F.data == "homeworks")
@inject(InjectStrategy.HANDLER)
async def pagination_handler(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    read_admin_data: ReadAdminDataByTgUserIdDepends,
    read_user_homeworks: ReadUserHomeworksForPaginationDepends,
    tg_message_delete: TgDeleteMessageDepends,
    config: ConfigFactory,
    is_super_admin: bool,
) -> None:
    if event.message is None:
        return
    message = event.message
    if isinstance(message, InaccessibleMessage):
        return
    
    telegram_user_id = TgUserId(event.from_user.id)
    count_homeworks = (
        100_000_000 if is_super_admin else config.config.const.count_homeworks
    )
    count_homeworks_in_pagination = config.config.const.count_homeworks_in_pagination
    if is_super_admin:
        direction_training = [
            DirectionTrainingType.SMM,
            DirectionTrainingType.COPYRIGHTING,
        ]
        letters_range, numbers_range = None, True
    else:
        admin_entity = await read_admin_data(
            TgUserIdDTO(telegram_user_id)
        )
        direction_training = [admin_entity.direction_training]
        letters_range = admin_entity.letters_range
        numbers_range = admin_entity.numbers_range
    
    try:
        homework_entity = await read_user_homeworks(
            HomeWorkPaginationDTO(
                telegram_user_id=telegram_user_id,
                count_homeworks=count_homeworks,
                direction_training=direction_training,
                numbers_range=numbers_range,
                letters_range=letters_range,
                limit=count_homeworks_in_pagination,
                offset=0 * count_homeworks_in_pagination,
            )
        )
    except NoFoundHomeworksForPagination:
        await event.answer("Домашних заданий нет", show_alert=True)
        return None
    try:
        await message.edit_text(
            "Список сданных работ",
            reply_markup=keyboard.inline.pagination_homeworks(
                model=homework_entity,
                offset=0,
                count_homeworks=count_homeworks,
                count_homeworks_in_pagination=config.config.const.count_homeworks_in_pagination,
            ),
        )
    except TelegramBadRequest:
        await tg_message_delete(
            DeleteMessageData(
                chat_id=event.message.chat.id,
                message_id=event.message.message_id
            )
        )
        await message.answer(
            "Список сданных работ",
            reply_markup=keyboard.inline.pagination_homeworks(
                model=homework_entity,
                offset=0,
                count_homeworks=count_homeworks,
                count_homeworks_in_pagination=config.config.const.count_homeworks_in_pagination,
            ),
        )
    await state.update_data(offset=0)
    await state.set_state(AdminHomeWorksState.pagination)


@route.callback_query(AdminHomeWorksState.pagination, Pagination.filter())
@inject(InjectStrategy.HANDLER)
async def pagination_h(
    event: CallbackQuery,
    state: FSMContext,
    callback_data: Pagination,
    keyboard: KeyboardFactory,
    config: ConfigFactory,
    is_super_admin: bool,
    read_admin_data: ReadAdminDataByTgUserIdDepends,
    read_user_homeworks: ReadUserHomeworksForPaginationDepends,
    tg_message_delete: TgDeleteMessageDepends,
) -> None:
    if event.message is None:
        return
    message = event.message
    if isinstance(message, InaccessibleMessage):
        return
    
    state_data = await state.get_data()
    old_offset = state_data.get("offset", 1)
    offset_table = dict(back=old_offset - 1, next=old_offset + 1)
    new_offset = offset_table[callback_data.action]
    telegram_user_id = TgUserId(event.from_user.id)
    count_homeworks = (
        config.config.const.count_homeworks if not is_super_admin else 100_000_000
    )
    count_homeworks_in_pagination = config.config.const.count_homeworks_in_pagination
    if is_super_admin:
        direction_training = [
            DirectionTrainingType.SMM,
            DirectionTrainingType.COPYRIGHTING,
        ]
        letters_range, numbers_range = None, True
    else:
        admin_entity = await read_admin_data(TgUserIdDTO(telegram_user_id))
        direction_training = [admin_entity.direction_training]
        letters_range = admin_entity.letters_range
        numbers_range = admin_entity.numbers_range
    
    try:
        homework_entity = await read_user_homeworks(
            HomeWorkPaginationDTO(
                telegram_user_id=telegram_user_id,
                count_homeworks=count_homeworks,
                direction_training=direction_training,
                numbers_range=numbers_range,
                letters_range=letters_range,
                limit=count_homeworks_in_pagination,
                offset=new_offset * count_homeworks_in_pagination,
            )
        )
    except NoFoundHomeworksForPagination:
        await pagination_handler(
            event,
            state,
            keyboard,
            read_admin_data,
            read_user_homeworks,
            tg_message_delete,
            config,
            is_super_admin,
        )
        return None
    
    await message.edit_text(
        "Список сданных работ",
        reply_markup=keyboard.inline.pagination_homeworks(
            model=homework_entity,
            offset=new_offset,
            count_homeworks=count_homeworks,
            count_homeworks_in_pagination=count_homeworks_in_pagination,
        ),
    )
    await state.update_data(offset=new_offset)
    await state.set_state(AdminHomeWorksState.pagination)


@route.callback_query(
    SelectHomeWorkByDBId.filter(), AdminHomeWorksState.pagination
)
@inject(InjectStrategy.HANDLER)
async def select_homework_handler(
    event: CallbackQuery,
    state: FSMContext,
    callback_data: SelectHomeWorkByDBId,
    use_case: ReadHomeworkAndUserInfoByDBIdDepends,
    keyboard: KeyboardFactory,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    homework_db_id = callback_data.db_id
    model = await use_case(HomeWorkIdDTO(homework_db_id))
    surname = model.surname.title()
    name = model.name[0].title()
    date_time = model.date_time_registration.strftime("%d.%m")
    
    if patronymic := model.patronymic:
        sup = f"{surname} {name}.{patronymic[0].title()}"
    else:
        sup = f"{surname} {name}."
    
    try:
        await event.message.edit_text(
            f"Работа {sup}\n{model.email}\n"
            f"Направление: {model.direction_training}\n"
            f"Сдана: {date_time}\n"
            f"Ссылка: {model.url}",
            reply_markup=keyboard.inline.check_homework(
                model.telegram_user_id,
                True if model.number == 7 else False
            ),
            disable_web_page_preview=True,
        )
    except TelegramBadRequest:
        await event.message.edit_text(
            f"Работа {sup}\n{model.email}\n"
            f"Направление: {model.direction_training}\n"
            f"Сдана: {date_time}\n"
            f"Ссылка: {model.url}",
            reply_markup=keyboard.inline.check_homework(
                model.telegram_user_id,
                True if model.number == 7 else False,
                True
            ),
            disable_web_page_preview=True,
        )
    await state.set_state(AdminHomeWorksState.select_homework)
    await state.update_data(
        homework_db_id=homework_db_id,
        telegram_chat_id=model.telegram_chat_id,
        number=model.number,
    )


@route.callback_query(
    F.data.in_({"revision_good", "select_ok"}),
    AdminHomeWorksState.select_homework,
    flags=dict(repo_uow=True),
)
@inject(InjectStrategy.HANDLER)
async def xz_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    use_case: UpdateHomeworkEvolutionAndStatusDepends,
    is_super_admin: bool,
) -> None:
    if event.message is None:
        return None
    if isinstance(event.message, InaccessibleMessage):
        return None
    if event.data is None:
        return None
    
    evaluation = EvaluationType.OK if event.data == "select_ok" else EvaluationType.COOL
    state_data = await state.get_data()
    await use_case(
        UpdateHomeworkEvolutionAndStatusDTO(
            db_id=state_data["homework_db_id"],
            status_type=HomeWorkStatusType.ACCEPTED,
            evaluation=evaluation,
        )
    )
    await event.message.edit_text(
        "Админка", reply_markup=keyboard.inline.admin_main_menu(is_super_admin)
    )
    await state.clear()


@route.callback_query(F.data == "accept_homework", flags=dict(repo_uow=True))
@inject(InjectStrategy.HANDLER)
async def accept_homework_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    is_super_admin: bool,
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
    await homework_repository.update_type(
        UpdatingTypeByIdDTO(
            db_id=state_data["homework_db_id"],
            status_type=HomeWorkStatusType.ACCEPTED,
        )
    )
    await bot.send_message(
        chat_id=state_data["telegram_chat_id"],
        text=f'<u>{HOMEWORKS_TEXT_FROM_SPREADSHEETS[state_data["number"]]}</u> была принята',
    )
    await event.message.edit_text(
        "Админка", reply_markup=keyboard.inline.admin_main_menu(is_super_admin)
    )
    await state.clear()


@route.callback_query(
    F.data == "revision_homework", AdminHomeWorksState.select_homework
)
async def revision_homework_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    homework_repository: HomeWorkRepositoryImpl,
    keyboard: KeyboardFactory,
) -> None:
    if event.message is None:
        return
    message = event.message
    if isinstance(message, InaccessibleMessage):
        return
    
    await message.edit_text("Пришли комментарий")
    await state.set_state(AdminHomeWorksState.ask_comments)
    await state.update_data(msg_id=event.message.message_id)


@route.message(
    F.text, AdminHomeWorksState.ask_comments, flags=dict(repo_uow=True)
)
async def ask_comments_handler(
    event: Message,
    bot: Bot,
    state: FSMContext,
    homework_repository: HomeWorkRepositoryImpl,
    keyboard: KeyboardFactory,
    is_super_admin: bool,
) -> None:
    if event.text is None:
        return
    
    comments = event.text
    with suppress(TelegramBadRequest):
        await event.delete()
    state_data = await state.get_data()
    if msg_id_ := state_data.get("msg_id"):
        with suppress(TelegramBadRequest):
            await bot.delete_message(
                chat_id=event.chat.id, message_id=msg_id_
            )
    await homework_repository.update_type_and_comment(
        UpdatingTypeAndCommentByIdDTO(
            db_id=state_data["homework_db_id"],
            status_type=HomeWorkStatusType.UNDER_REVISION,
            comments=comments
        )
    )
    await bot.send_message(
        chat_id=state_data["telegram_chat_id"],
        text=f'<u>{HOMEWORKS_TEXT_FROM_SPREADSHEETS[state_data["number"]]}</u> был отправлен с '
             f'комментарием:\n'
             f'{comments}',
    )
    await event.answer(
        "Админка",
        reply_markup=keyboard.inline.admin_main_menu(is_super_admin)
    )
    await state.clear()
