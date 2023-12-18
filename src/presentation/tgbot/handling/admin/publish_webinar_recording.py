from aiogram import Bot, F, Router
from aiogram.enums import MessageEntityType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, MessageEntity

from src.application.schemas.dto.webinar import AddWebinarDTO
from src.infrastructure.repositories.webinar import WebinarDuplicateException, WebinarRepository
from src.presentation.tgbot.keyboard import KeyboardFactory
from src.presentation.tgbot.states import AddWebinarState


route = Router()
route.callback_query.filter(F.data == 'publish_webinar_recording')


@route.callback_query(F.data == 'publish_webinar_recording')
async def publish_webinar_recording_handler(
    event: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory
) -> None:
    if event.message is None:
        return
    
    await event.message.edit_text(
        'Пришли ссылку на вебинар',
        reply_markup=keyboard.inline.back('admin_panel')
    )
    await state.set_state(AddWebinarState.ask_url)


@route.message(
    AddWebinarState.ask_url,
    F.entities.extract(F.type == MessageEntityType.URL).as_("urls")
)
async def ask_webinar_name(
    event: Message,
    state: FSMContext,
    keyboard: KeyboardFactory,
    urls: list[MessageEntity]
) -> None:
    if event.text is None:
        return
    
    await event.answer(
        'Пришли дату вебинара и ФИО лектора.\nФормат: "20.07 Иванов И.И."',
        reply_markup=keyboard.inline.back('publish_webinar_recording')
    )
    await state.update_data(url=urls.pop().extract_from(event.text))
    await state.set_state(AddWebinarState.ask_name)


@route.message(
    AddWebinarState.ask_name,
    flags=dict(repo_uow=True)
)
async def get_webinar_name_handler(
    event: Message,
    bot: Bot,
    state: FSMContext,
    keyboard: KeyboardFactory,
    webinar_repository: WebinarRepository,
    is_super_admin: bool
) -> None:
    if event.text is None:
        return
    
    data = await state.get_data()
    await state.clear()
    try:
        await webinar_repository.add(
            AddWebinarDTO(
                url=data['url'],
                name=event.text
            )
        )
    except WebinarDuplicateException:
        await event.answer(
            'Вебинар с такой ссылкой уже есть',
            reply_markup=keyboard.inline.admin_panel(is_super_admin)
        )
        return
    await event.answer(
        'Вебинар добавлен',
        reply_markup=keyboard.inline.admin_panel(is_super_admin)
    )
