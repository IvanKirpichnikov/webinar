from faststream import Context
from faststream.nats import NatsRouter
from psycopg import AsyncConnection
from psycopg.rows import dict_row, DictRow
from psycopg_pool import AsyncConnectionPool

from webinar.application.dto.common import DirectionTrainingDTO
from webinar.domain.enums.direction_type import DirectionTrainingType
from webinar.infrastructure.google_sheets.enums import WorkSheetId
from webinar.infrastructure.google_sheets.gateway import GoogleSheetsAdapter
from webinar.infrastructure.postgres.gateways.user import PostgresUserGateway


route = NatsRouter()


@route.subscriber("update.google_sheets")
async def update_data_handler(
    _: str,
    google_sheet: GoogleSheetsAdapter = Context(),
    pool: AsyncConnectionPool[AsyncConnection[DictRow]] = Context(),
) -> None:
    training_types = [
        (DirectionTrainingType.SMM, WorkSheetId.SMM),
        (DirectionTrainingType.COPYRIGHTING, WorkSheetId.COPYRIGHTING)
    ]
    async with pool.connection() as connect:
        connect.row_factory = dict_row
        for training_type, work_sheet_id in training_types:
            dto = DirectionTrainingDTO(training_type)
            data = await PostgresUserGateway(connect).read_user_and_he_homeworks(dto)
            await google_sheet.update_data(
                work_sheet_id=work_sheet_id,
                raw_data=data
            )
    await google_sheet.create_worksheet_and_set_names()
