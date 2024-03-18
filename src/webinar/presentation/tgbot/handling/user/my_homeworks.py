from aiogram import (
    F,
    Router,
)
from aiogram.enums import ParseMode
from aiogram.filters import or_f
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
)

from webinar.application.dto.common import TgUserIdDTO
from webinar.application.dto.homework import UpdateHomeWorkStatusDTO
from webinar.application.use_case.homeworks.read_user_homeworks import ReadUserHomeworkError
from webinar.domain.enums.homework import HomeWorkStatusType
from webinar.domain.types import TgUserId
from webinar.presentation.annotaded import ReadUserHomeWorksDepends, UpdateHomeWorkStatusDepends
from webinar.presentation.inject import inject, InjectStrategy
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.keyboard.callback_data import ReCheckingHomework


route = Router()
route.callback_query(
    or_f(
        ReCheckingHomework.filter(),
        F.data == "my_homeworks"
    )
)


async def _my_homeworks_handler(
    event: CallbackQuery,
    keyboard: KeyboardFactory,
    read_user_homeworks: ReadUserHomeWorksDepends,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return
    
    try:
        homeworks = await read_user_homeworks(
            TgUserIdDTO(TgUserId(event.from_user.id))
        )
    except ReadUserHomeworkError:
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

@route.callback_query(F.data == "my_homeworks")
@inject(InjectStrategy.HANDLER)
async def my_homeworks_handler(
    event: CallbackQuery,
    keyboard: KeyboardFactory,
    read_user_homeworks: ReadUserHomeWorksDepends,
) -> None:
    await _my_homeworks_handler(event, keyboard, read_user_homeworks)


@route.callback_query(ReCheckingHomework.filter(), flags=dict(repo_uow=True))
@inject(InjectStrategy.HANDLER)
async def update_homework_handler(
    event: CallbackQuery,
    callback_data: ReCheckingHomework,
    keyboard: KeyboardFactory,
    update_homework_status: UpdateHomeWorkStatusDepends,
    read_user_homeworks: ReadUserHomeWorksDepends,
) -> None:
    if event.message is None:
        return
    
    await update_homework_status(
        UpdateHomeWorkStatusDTO(
            db_id=callback_data.db_id,
            status_type=HomeWorkStatusType.UNDER_INSPECTION,
        )
    )
    await _my_homeworks_handler(event, keyboard, read_user_homeworks)
