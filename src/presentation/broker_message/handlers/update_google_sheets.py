from faststream import Context
from faststream.nats import JStream, NatsRouter

from src.infrastructure.google_sheets.adapter import GoogleSheetsAdapter


route = NatsRouter()
stream = JStream('webinar_stream')


@route.subscriber('update.google_sheets')
async def update_data_handler(
    _: str,
    google_sheet: GoogleSheetsAdapter = Context()
) -> None:
    await google_sheet.update_data()
