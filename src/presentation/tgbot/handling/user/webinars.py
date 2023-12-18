from typing import Final

from aiogram import F, Router
from aiogram.filters import or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.application.config import ConfigFactory
from src.application.interfaces.repository.webinar import AbstractWebinar
from src.presentation.tgbot.keyboard import KeyboardFactory
from src.presentation.tgbot.keyboard.callback_data import WebinarPaginationCallbackData
from src.presentation.tgbot.states import WebinarPaginationState


CALLBACK_DATAS: Final = [
    'webinar_recordings'
]

route = Router()
route.callback_query.filter(
    or_f(
        F.data.in_(CALLBACK_DATAS),
        WebinarPaginationCallbackData.filter()
    ),
    or_f(
        WebinarPaginationState.pagination,
        StateFilter('*')
    )
)


@route.callback_query(F.data == 'webinar_recordings')
async def webinar_recordings_handler(
    event: CallbackQuery,
    state: FSMContext,
    config: ConfigFactory,
    keyboard: KeyboardFactory,
    webinar_repository: AbstractWebinar
) -> None:
    if event.message is None:
        return
    
    count_webinars_button = config.config.const.count_webinars_button
    webinars = await webinar_repository.get(0, count_webinars_button)
    
    await event.message.edit_text(
        'Вебинары',
        reply_markup=keyboard.inline.webinars(webinars, count_webinars_button)
    )
    await state.set_data(dict(offset_webinar_pagination=0))
    await state.set_state(WebinarPaginationState.pagination)


@route.callback_query(
    WebinarPaginationCallbackData.filter(),
    WebinarPaginationState.pagination
)
async def webinar_pagination_handler(
    event: CallbackQuery,
    state: FSMContext,
    config: ConfigFactory,
    keyboard: KeyboardFactory,
    webinar_repository: AbstractWebinar,
    callback_data: WebinarPaginationCallbackData
) -> None:
    if event.message is None:
        return
    
    state_data = await state.get_data()
    action = callback_data.action
    offset = state_data.get('offset_webinar_pagination', 0)
    count_webinars_button = config.config.const.count_webinars_button
    
    if action == 'back':
        offset -= 1
    elif action == 'next':
        offset += 1
    
    webinars = await webinar_repository.get(
        offset * count_webinars_button,
        count_webinars_button
    )
    
    if offset > 0 and not webinars:
        return
    
    await event.message.edit_reply_markup(
        'Вебинары',
        reply_markup=keyboard.inline.webinars(webinars, count_webinars_button, offset)
    )
    await state.update_data(offset_webinar_pagination=offset)
    await state.set_state(WebinarPaginationState.pagination)
