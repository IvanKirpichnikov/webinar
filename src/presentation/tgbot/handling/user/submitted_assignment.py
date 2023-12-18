from aiogram import F, Router
from aiogram.filters import or_f
from aiogram.types import CallbackQuery

from src.application.interfaces.repository.homework import AbstractHomeWork
from src.application.schemas.dto.homework import HomeWorkUserId, UpdatingTypeByIdDTO
from src.application.schemas.enums.homework import HomeWorkTypeEnum
from src.application.schemas.types import UserId
from src.presentation.tgbot.keyboard import KeyboardFactory
from src.presentation.tgbot.keyboard.callback_data import SubmitForReviewCallbackData


route = Router()
route.callback_query(
    or_f(
        SubmitForReviewCallbackData.filter(),
        F.data == 'submitted_assignment'
    )
)


@route.callback_query(F.data == 'submitted_assignment')
async def submitted_assignment_handler(
    event: CallbackQuery,
    keyboard: KeyboardFactory,
    homework_repository: AbstractHomeWork
) -> None:
    if event.message is None:
        return
    
    homeworks = await homework_repository.get_all_by_user_id(
        HomeWorkUserId(UserId(event.from_user.id))
    )
    text = '\n'.join([homework.string for homework in homeworks])
    await event.message.edit_text(
        f'<u>Мои задания</u>\n{text}',
        reply_markup=keyboard.inline.under_revision_homeworks(homeworks),
        disable_web_page_preview=True
    )


@route.callback_query(
    SubmitForReviewCallbackData.filter(),
    flags=dict(repo_uow=True)
)
async def update_homework_type_handler(
    event: CallbackQuery,
    callback_data: SubmitForReviewCallbackData,
    homework_repository: AbstractHomeWork,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    
    await homework_repository.update_type(
        UpdatingTypeByIdDTO(
            homework_id=callback_data.homework_id,
            type=HomeWorkTypeEnum.UNDER_INSPECTION
        )
    )
    await submitted_assignment_handler(
        event, keyboard, homework_repository
    )
