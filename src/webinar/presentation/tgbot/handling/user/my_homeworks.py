from aiogram import (
    F,
    Router
)
from aiogram.enums import ParseMode
from aiogram.filters import or_f
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage
)

from webinar.application.exceptions import NotFoundHomeworks
from webinar.application.schemas.dto.common import TelegramUserIdDTO
from webinar.application.schemas.dto.homework import UpdatingTypeByIdDTO
from webinar.application.schemas.enums.homework import HomeWorkStatusType
from webinar.application.schemas.types import TelegramUserId
from webinar.infrastructure.database.repository.homework import HomeWorkRepositoryImpl
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.keyboard.callback_data import ReCheckingHomework


route = Router()
route.callback_query(
    or_f(
        ReCheckingHomework.filter(),
        F.data == "my_homeworks"
    )
)


@route.callback_query(F.data == "my_homeworks")
async def my_homeworks_handler(
    event: CallbackQuery,
    keyboard: KeyboardFactory,
    homework_repository: HomeWorkRepositoryImpl,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        await event.answer('Нет доступа к сообщению. Введите /start', show_alert=True)
        return
    
    dto = TelegramUserIdDTO(TelegramUserId(event.from_user.id))
    try:
        homeworks = await homework_repository.read_all_by_telegram_user_id(dto)
    except NotFoundHomeworks:
        await event.answer("У вас нет домашних заданий", show_alert=True)
        return None
    
    text = (
        'Условные обозначения:\n'
        '⏳ - задание на проверке.\n'
        '❓ - задание отправлено на доработку. Необходимо повторно отправить на проверку.\n'
        '✅ - задание принято.\n\n'
        f'<u>Мои задания</u>\n{homeworks.string()}'
    )
    await event.message.edit_text(
        text=text,
        reply_markup=keyboard.inline.under_revision_homeworks(homeworks),
        disable_web_page_preview=True,
        parse_mode=ParseMode.HTML,
    )


@route.callback_query(ReCheckingHomework.filter(), flags=dict(repo_uow=True))
async def update_homework_handler(
    event: CallbackQuery,
    callback_data: ReCheckingHomework,
    homework_repository: HomeWorkRepositoryImpl,
    keyboard: KeyboardFactory,
) -> None:
    if event.message is None:
        return
    
    await homework_repository.update_type(
        UpdatingTypeByIdDTO(
            db_id=callback_data.db_id,
            status_type=HomeWorkStatusType.UNDER_INSPECTION,
        )
    )
    await my_homeworks_handler(event, keyboard, homework_repository)
