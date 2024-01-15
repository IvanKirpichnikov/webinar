from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, Message

from webinar.application.config import ConfigFactory
from webinar.application.exceptions import NotFoundHomeworks
from webinar.application.schemas.dto.common import TelegramUserIdDTO
from webinar.application.schemas.dto.homework import (
    HomeWorkIdDTO,
    HomeWorkPaginationDTO,
    UpdatingEvaluationByIdDTO,
    UpdatingTypeAndCommentByIdDTO,
    UpdatingTypeByIdDTO,
)
from webinar.application.schemas.enums.direction_type import (
    DirectionTrainingType,
)
from webinar.application.schemas.enums.homework import (
    EvaluationType,
    HomeWorkStatusType,
)
from webinar.application.schemas.types import TelegramUserId
from webinar.infrastructure.database.repository.admin import (
    AdminRepositoryImpl,
)
from webinar.infrastructure.database.repository.homework import (
    HomeWorkRepositoryImpl,
)
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.keyboard.callback_data import (
    Pagination,
    SelectHomeWorkByDBId,
)
from webinar.presentation.tgbot.states import AdminHomeWorksState


route = Router()


@route.callback_query(F.data == "homeworks")
async def pagination_handler(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    homework_repository: HomeWorkRepositoryImpl,
    admin_repository: AdminRepositoryImpl,
    config: ConfigFactory,
    is_super_admin: bool,
) -> None:
    if event.message is None:
        return
    message = event.message
    if isinstance(message, InaccessibleMessage):
        return

    telegram_user_id = TelegramUserId(event.from_user.id)
    count_homeworks = (
        10**20 if is_super_admin else config.config.const.count_homeworks
    )
    count_homeworks_in_pagination = (
        config.config.const.count_homeworks_in_pagination
    )
    if is_super_admin:
        direction_training = [
            DirectionTrainingType.SMM,
            DirectionTrainingType.COPYRIGHTING,
        ]
        letters_range, numbers_range = None, True
    else:
        admin_entity = await admin_repository.read_data_by_telegram_user_id(
            TelegramUserIdDTO(telegram_user_id)
        )
        direction_training = [admin_entity.direction_training]
        letters_range = admin_entity.letters_range
        numbers_range = admin_entity.numbers_range

    homework_dto = HomeWorkPaginationDTO(
        telegram_user_id=telegram_user_id,
        count_homeworks=count_homeworks,
        direction_training=direction_training,
        numbers_range=numbers_range,
        letters_range=letters_range,
        limit=count_homeworks_in_pagination,
        offset=0 * count_homeworks_in_pagination,
    )
    try:
        homework_entity = await homework_repository.read_pagination(
            homework_dto
        )
    except NotFoundHomeworks:
        await event.answer("Домашних заданий нет", show_alert=True)
        return None

    await message.edit_text(
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
async def pagination_h(
    event: CallbackQuery,
    state: FSMContext,
    homework_repository: HomeWorkRepositoryImpl,
    admin_repository: AdminRepositoryImpl,
    callback_data: Pagination,
    keyboard: KeyboardFactory,
    config: ConfigFactory,
    is_super_admin: bool,
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
    telegram_user_id = TelegramUserId(event.from_user.id)
    count_homeworks = (
        config.config.const.count_homeworks if not is_super_admin else 10**20
    )
    count_homeworks_in_pagination = (
        config.config.const.count_homeworks_in_pagination
    )
    if is_super_admin:
        direction_training = [
            DirectionTrainingType.SMM,
            DirectionTrainingType.COPYRIGHTING,
        ]
        letters_range, numbers_range = None, True
    else:
        admin_entity = await admin_repository.read_data_by_telegram_user_id(
            TelegramUserIdDTO(telegram_user_id)
        )
        direction_training = [admin_entity.direction_training]
        letters_range = admin_entity.letters_range
        numbers_range = admin_entity.numbers_range

    homework_dto = HomeWorkPaginationDTO(
        telegram_user_id=telegram_user_id,
        count_homeworks=count_homeworks,
        direction_training=direction_training,
        numbers_range=numbers_range,
        letters_range=letters_range,
        limit=count_homeworks_in_pagination,
        offset=new_offset * count_homeworks_in_pagination,
    )
    try:
        homework_entity = await homework_repository.read_pagination(
            homework_dto
        )
    except NotFoundHomeworks:
        await pagination_handler(
            event,
            state,
            keyboard,
            homework_repository,
            admin_repository,
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
async def select_homework_handler(
    event: CallbackQuery,
    state: FSMContext,
    homework_repository: HomeWorkRepositoryImpl,
    admin_repository: AdminRepositoryImpl,
    callback_data: SelectHomeWorkByDBId,
    keyboard: KeyboardFactory,
) -> None:
    if event.message is None:
        return
    message = event.message
    if isinstance(message, InaccessibleMessage):
        return

    homework_db_id = callback_data.db_id
    model = await homework_repository.read_homework_by_db_id_and_user_info(
        HomeWorkIdDTO(homework_db_id)
    )
    surname = model.surname.title()
    name = model.name[0].title()
    date_time = model.date_time_registration.strftime("%d.%m")

    if patronymic := model.patronymic:
        sup = f"{surname} {name}.{patronymic[0].title()}"
    else:
        sup = f"{surname} {name}."

    await message.edit_text(
        (
            f"Работа {sup}\n{model.email}\n"
            f"Направление: {model.direction_training}\n"
            f"Сдана: {date_time}\n"
            f"Ссылка: {model.url}"
        ),
        reply_markup=keyboard.inline.check_homework(
            model.telegram_user_id, True if model.number == 7 else False
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
async def xz_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    homework_repository: HomeWorkRepositoryImpl,
    keyboard: KeyboardFactory,
    is_super_admin: bool,
) -> None:
    if event.message is None:
        return
    message = event.message
    if isinstance(message, InaccessibleMessage):
        return

    if event.data is None:
        return

    cd = event.data
    evaluation = (
        EvaluationType.OK if cd == "select_ok" else EvaluationType.COOL
    )
    state_data = await state.get_data()
    await homework_repository.update_evaluation(
        UpdatingEvaluationByIdDTO(
            db_id=state_data["homework_db_id"],
            status_type=HomeWorkStatusType.ACCEPTED,
            evaluation=evaluation,
        )
    )
    await message.edit_text(
        "Админка", reply_markup=keyboard.inline.admin_main_menu(is_super_admin)
    )
    await state.clear()


@route.callback_query(F.data == "accept_homework", flags=dict(repo_uow=True))
async def accept_homework_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    homework_repository: HomeWorkRepositoryImpl,
    keyboard: KeyboardFactory,
    is_super_admin: bool,
) -> None:
    if event.message is None:
        return
    message = event.message
    if isinstance(message, InaccessibleMessage):
        return

    state_data = await state.get_data()
    await homework_repository.update_type(
        UpdatingTypeByIdDTO(
            db_id=state_data["homework_db_id"],
            status_type=HomeWorkStatusType.ACCEPTED,
        )
    )
    await bot.send_message(
        chat_id=state_data["telegram_chat_id"],
        text=f'Домашнее задание {state_data["number"]} был принят',
    )
    await message.edit_text(
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
    state_data = await state.get_data()
    await homework_repository.update_type_and_comment(
        UpdatingTypeAndCommentByIdDTO(
            db_id=state_data["homework_db_id"],
            status_type=HomeWorkStatusType.UNDER_REVISION,
            comments=comments,
        )
    )
    await bot.send_message(
        chat_id=state_data["telegram_chat_id"],
        text=f'<u>Домашнее задание {state_data["number"]}</u> был отправлен с комментарием:\n{comments}',
    )
    await event.answer(
        "Админка", reply_markup=keyboard.inline.admin_main_menu(is_super_admin)
    )
    await state.clear()
