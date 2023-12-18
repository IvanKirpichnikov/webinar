from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.application.interfaces.repository.admin import AbstractAdmin
from src.application.schemas.dto.admin import AdminUserId
from src.application.schemas.dto.homework import (
    GetHomeWorkWithInformationForAdminDTO,
    PaginationHomeWorkDTO,
    UpdatingTypeAndCommentByIdDTO,
    UpdatingTypeByIdDTO
)
from src.application.schemas.enums import DirectionEnum
from src.application.schemas.enums.homework import HomeWorkTypeEnum
from src.application.schemas.types import UserId
from src.infrastructure.repositories.homework import AbstractHomeWork
from src.presentation.tgbot.keyboard import KeyboardFactory
from src.presentation.tgbot.keyboard.callback_data import (
    HomeWorkActionCallbackData,
    HomeWorkCallbackData,
    HomeWorkPaginationCallbackData
)
from src.presentation.tgbot.states import AdminHomeWorksState


route = Router()


@route.callback_query(F.data == 'homeworks')
async def pagination(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    homework_repository: AbstractHomeWork,
    admin_repository: AbstractAdmin,
    is_super_admin: bool
) -> None:
    if event.message is None:
        return
    
    await state.update_data(offset=0)
    if is_super_admin:
        direction_types = [DirectionEnum.SMM, DirectionEnum.COPYRIGHTING]
    else:
        direction_types = [await admin_repository.get_direction_type(
            AdminUserId(UserId(event.from_user.id))
        )]
    data = await homework_repository.pagination(
        PaginationHomeWorkDTO(
            offset=0,
            direction_types=direction_types
        )
    )
    if not data:
        await event.message.edit_text(
            'Домашних заданий нету',
            reply_markup=keyboard.inline.admin_panel(is_super_admin)
        )
        return
    await event.message.edit_text(
        'Список сданных работ',
        reply_markup=keyboard.inline.pagination_homeworks(data, 0)
    )
    await state.set_state(AdminHomeWorksState.pagination)


@route.callback_query(
    AdminHomeWorksState.pagination,
    HomeWorkCallbackData.filter()
)
async def pagination_h(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    homework_repository: AbstractHomeWork,
    callback_data: HomeWorkActionCallbackData,
    admin_repository: AbstractAdmin,
    is_super_admin: bool
) -> None:
    if event.message is None:
        return
    data = await state.get_data()
    offset = data.get('offset', 1)
    if callback_data.action == 'back':
        offset -= 1
    else:
        offset += 1
    
    if is_super_admin:
        direction_types = [DirectionEnum.COPYRIGHTING, DirectionEnum.COPYRIGHTING]
    else:
        direction_types = [await admin_repository.get_direction_type(
            AdminUserId(UserId(event.from_user.id))
        )]
    
    homework_data = await homework_repository.pagination(
        PaginationHomeWorkDTO(
            offset=offset * 10,
            direction_types=direction_types
        )
    )
    if offset > 0 and not homework_data:
        offset -= 1
        homework_data = await homework_repository.pagination(
            PaginationHomeWorkDTO(
                offset=offset * 10,
                direction_types=direction_types
            )
        )
    
    await event.message.edit_text(
        'Список сданных работ',
        reply_markup=keyboard.inline.pagination_homeworks(homework_data, offset)
    )
    await state.update_data(offset=offset)
    await state.set_state(AdminHomeWorksState.pagination)


@route.callback_query(
    HomeWorkPaginationCallbackData.filter(),
    AdminHomeWorksState.pagination
)
async def select_homework_handler(
    event: CallbackQuery,
    state: FSMContext,
    keyboard: KeyboardFactory,
    homework_repository: AbstractHomeWork,
    callback_data: HomeWorkPaginationCallbackData,
    admin_repository: AbstractAdmin
) -> None:
    if event.message is None:
        return
    
    homework_id = callback_data.id
    model = await homework_repository.get_with_information_for_admin(
        GetHomeWorkWithInformationForAdminDTO(homework_id)
    )
    sup = f'{model.surname.title()} {model.name[0].title()}.{(model.patronymic or " ").title()}'
    
    await event.message.edit_text(
        (
            f'Работа {sup}\n{model.email}\n'
            f'Направление: {model.direction}\n'
            f'Сдана: {model.date_time.strftime("%d.%m")}\n'
            f'Ссылка: {model.url}'
        ),
        reply_markup=keyboard.inline.check_homework(model.user_id),
        disable_web_page_preview=True
    )
    await state.set_state(AdminHomeWorksState.select_homework)
    await state.update_data(homework_id=homework_id, chat_id=model.chat_id, number=model.number)


@route.callback_query(
    F.data == 'accept_homework',
    flags=dict(repo_uow=True)
)
async def accept_homework_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    homework_repository: AbstractHomeWork,
    is_super_admin: bool
) -> None:
    if event.message is None:
        return
    
    data = await state.get_data()
    chat_id = data['chat_id']
    homework_id = data['homework_id']
    number = data['number']
    await homework_repository.update_type_and_comment_by_id(
        UpdatingTypeAndCommentByIdDTO(
            homework_id=homework_id,
            type=HomeWorkTypeEnum.UNDER_REVISION,
            comment=''
        )
    )
    await bot.send_message(
        chat_id=chat_id,
        text=f'Домашнее задание {number} был принят'
    )
    await state.clear()
    await event.message.edit_text(
        'Админка',
        reply_markup=keyboard.inline.admin_panel(is_super_admin)
    )


@route.callback_query(F.data == 'revision_homework', AdminHomeWorksState.select_homework)
async def revision_homework_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    homework_repository: AbstractHomeWork
) -> None:
    if event.message is None:
        return
    
    await event.message.edit_text('Пришли комментарий')
    await state.set_state(AdminHomeWorksState.ask_comments)


@route.message(
    F.text, AdminHomeWorksState.ask_comments,
    flags=dict(repo_uow=True)
)
async def ask_comments_handler(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    homework_repository: AbstractHomeWork,
    is_super_admin: bool
) -> None:
    if event.text is None:
        return
    
    data = await state.get_data()
    chat_id = data['chat_id']
    homework_id = data['homework_id']
    number = data['number']
    await homework_repository.update_type_and_comment_by_id(
        UpdatingTypeAndCommentByIdDTO(
            homework_id=homework_id,
            type=HomeWorkTypeEnum.UNDER_REVISION,
            comment=event.text
        )
    )
    await bot.send_message(
        chat_id=chat_id,
        text=f'Домашнее задание {number} был отправлен с комментарием:\n{event.text}'
    )
    await state.clear()
    await event.answer(
        'Админка',
        reply_markup=keyboard.inline.admin_panel(is_super_admin)
    )
