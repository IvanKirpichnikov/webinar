from typing import Final

from aiogram import F, Router
from aiogram.filters import and_f, or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage

from webinar.application.config import ConfigFactory
from webinar.application.exceptions import NotFoundWebinars
from webinar.application.schemas.dto.webinar import PaginationWebinarDTO
from webinar.infrastructure.database.repository.webinar import (
    WebinarRepositoryImpl,
)
from webinar.presentation.tgbot.keyboard import KeyboardFactory
from webinar.presentation.tgbot.keyboard.callback_data import Pagination
from webinar.presentation.tgbot.states import WebinarPaginationState


CALLBACK_DATAS: Final = ["webinar_recordings"]

route = Router()
route.callback_query.filter(
    or_f(
        and_f(F.data.in_(CALLBACK_DATAS), StateFilter("*")),
        and_f(WebinarPaginationState.pagination, Pagination.filter()),
    )
)


@route.callback_query(F.data == "webinar_recordings")
async def webinar_recordings_handler(
    event: CallbackQuery,
    state: FSMContext,
    config: ConfigFactory,
    keyboard: KeyboardFactory,
    webinar_repository: WebinarRepositoryImpl,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return

    count_webinars_button = config.config.const.count_webinars_button
    pagination_dto = PaginationWebinarDTO(
        limit=count_webinars_button, offset=0
    )
    try:
        webinars = await webinar_repository.pagination(pagination_dto)
    except NotFoundWebinars:
        await event.answer("Вебинаров нет.", show_alert=True)
        return None

    await event.message.edit_text(
        "Вебинары",
        reply_markup=keyboard.inline.pagination_webinars(
            webinars, count_webinars_button, 0
        ),
    )
    await state.set_data({"offset": 0})
    await state.set_state(WebinarPaginationState.pagination)
    return None


@route.callback_query(Pagination.filter(), WebinarPaginationState.pagination)
async def webinar_pagination_handler(
    event: CallbackQuery,
    state: FSMContext,
    callback_data: Pagination,
    webinar_repository: WebinarRepositoryImpl,
    keyboard: KeyboardFactory,
    config: ConfigFactory,
) -> None:
    if event.message is None:
        return
    if isinstance(event.message, InaccessibleMessage):
        return

    state_data = await state.get_data()
    old_offset = state_data["offset"]
    count_webinars_button = config.config.const.count_webinars_button
    action = callback_data.action
    offset_table = {"back": old_offset - 1, "next": old_offset + 1}
    new_offset = offset_table[action]
    pagination_dto = PaginationWebinarDTO(
        limit=count_webinars_button, offset=new_offset * count_webinars_button
    )
    try:
        webinars = await webinar_repository.pagination(pagination_dto)
    except NotFoundWebinars:
        if new_offset == 0:
            await event.answer("Вебинаров нет.", show_alert=True)
            return None
        await webinar_recordings_handler(
            event, state, config, keyboard, webinar_repository
        )
        return None
    await event.message.edit_text(
        "Вебинары",
        reply_markup=keyboard.inline.pagination_webinars(
            webinars, count_webinars_button, new_offset
        ),
    )
    await state.update_data(offset=new_offset)
    return None
