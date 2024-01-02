from faststream import Context
from faststream.nats import JStream, NatsRouter

from webinar.application.schemas.dto.common import DirectionTrainingDTO
from webinar.application.schemas.enums.direction_type import (
    DirectionTrainingType,
)
from webinar.application.schemas.enums.google_sheets import WorkSheetId
from webinar.infrastructure.adapters.google_sheet import GoogleSheetsAdapter
from webinar.infrastructure.database.repository.user import UserRepositoryImpl


route = NatsRouter()
stream = JStream("webinar_stream")


@route.subscriber("update.google_sheets")
async def update_data_handler(
    _: str,
    google_sheet: GoogleSheetsAdapter = Context(),
    user_repository: UserRepositoryImpl = Context(),
) -> None:
    data = await user_repository.read_user_and_he_homeworks(
        DirectionTrainingDTO(DirectionTrainingType.SMM)
    )
    await google_sheet.update_data(
        work_sheet_id=WorkSheetId.SMM, raw_data=data
    )
    data = await user_repository.read_user_and_he_homeworks(
        DirectionTrainingDTO(DirectionTrainingType.COPYRIGHTING)
    )
    await google_sheet.update_data(
        work_sheet_id=WorkSheetId.SMM, raw_data=data
    )
