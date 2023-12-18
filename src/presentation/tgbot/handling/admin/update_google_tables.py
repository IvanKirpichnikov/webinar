from aiogram import F, Router
from aiogram.types import CallbackQuery
from faststream.nats import NatsBroker

from src.infrastructure.google_sheets.adapter import GoogleSheetsAdapter


route = Router()


@route.callback_query(F.data == 'update_google_tables')
async def update_google_tables_handler(
    _: CallbackQuery,
    broker: NatsBroker
) -> None:
    await _.message.edit_text('Обновления произошло')
    await broker.publish(
        message='',
        subject='update.google_sheets'
    )
