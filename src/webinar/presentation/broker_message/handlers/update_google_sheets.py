from faststream import Context
from faststream.nats import NatsRouter

from webinar.application.schemas.dto.common import DirectionTrainingDTO
from webinar.application.schemas.enums.direction_type import (
    DirectionTrainingType,
)
from webinar.application.schemas.enums.google_sheets import WorkSheetId
from webinar.infrastructure.adapters.google_sheet import GoogleSheetsAdapter
from webinar.infrastructure.database.repository.user import UserRepositoryImpl


route = NatsRouter()


@route.subscriber("update.google_sheets")
async def update_data_handler(
    _: str,
    google_sheet: GoogleSheetsAdapter = Context(),
    user_repository: UserRepositoryImpl = Context(),
) -> None:
    training_types = [
        (DirectionTrainingType.SMM, WorkSheetId.SMM),
        (DirectionTrainingType.COPYRIGHTING, WorkSheetId.COPYRIGHTING)
    ]
    for training_type, work_sheet_id in training_types:
        dto = DirectionTrainingDTO(training_type)
        data = await user_repository.read_user_and_he_homeworks(dto)
        await google_sheet.update_data(
            work_sheet_id=work_sheet_id,
            raw_data=data
        )
    await google_sheet.create_worksheet_and_set_names()
