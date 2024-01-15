from contextlib import suppress
from typing import Callable

from google.oauth2.service_account import Credentials
from gspread import Cell
from gspread.exceptions import APIError
from gspread_asyncio import (
    AsyncioGspreadClient,
    AsyncioGspreadClientManager,
    AsyncioGspreadSpreadsheet,
    AsyncioGspreadWorksheet
)

from webinar.application.schemas.dto.user import UpdateUserDataGoogleSheetsDto
from webinar.application.schemas.enums.google_sheets import WorkSheetId


HOMEWORKS_TEXT_FROM_SPREADSHEETS = {
    1: 'Базовый модуль Практическая работа №1',
    2: 'Базовый модуль Практическая работа №2',
    3: 'Специализация Практическая работа №1',
    4: 'Специализация Практическая работа №2',
    5: 'Специализация Практическая работа №3',
    6: 'Специализация Практическая работа №4',
    7: 'Специализация Практическая работа №5 проект'
}


class GoogleSheetsAdapter:
    connect: AsyncioGspreadClient
    spread_sheets: AsyncioGspreadSpreadsheet
    
    def __init__(
        self,
        connect: AsyncioGspreadClient,
        spread_sheets: AsyncioGspreadSpreadsheet,
    ) -> None:
        self.connect = connect
        self.spread_sheets = spread_sheets
    
    async def worksheet(self, index: WorkSheetId) -> AsyncioGspreadWorksheet:
        return await self.spread_sheets.get_worksheet(index)
    
    async def _set_column_name(
        self, worksheet: AsyncioGspreadWorksheet
    ) -> None:
        data = [
            Cell(1, 1, "ФИО"),
            Cell(1, 2, "Почта"),
            Cell(1, 3, "Telegram ID"),
            *[
                Cell(1, num + 3, HOMEWORKS_TEXT_FROM_SPREADSHEETS[num])
                for num in range(1, 8)
            ]
        ]
        await worksheet.update_cells(data)
    
    async def _create_worksheet_and_set_names(
        self,
        spread_sheet: AsyncioGspreadSpreadsheet,
        title: str,
        rows: int,
        cols: int,
        worksheet_id: int
    ) -> None:
        try:
            worksheet = await spread_sheet.add_worksheet(title, rows, cols, worksheet_id)
        except APIError:
            worksheet = await spread_sheet.get_worksheet(worksheet_id)
        await self._set_column_name(worksheet)
        worksheet.ws.update_title(title)
    
    async def create_worksheet_and_set_names(self) -> None:
        spread_sheets = self.spread_sheets
        with suppress(APIError):
            await self._create_worksheet_and_set_names(
                spread_sheet=spread_sheets,
                title="SMM",
                rows=100000,
                cols=10,
                worksheet_id=WorkSheetId.SMM.value,
            )
            await self._create_worksheet_and_set_names(
                spread_sheet=spread_sheets,
                title="Копирайтинг",
                rows=100000,
                cols=10,
                worksheet_id=WorkSheetId.COPYRIGHTING.value,
            )
    
    async def update_data(
        self,
        work_sheet_id: WorkSheetId,
        raw_data: list[UpdateUserDataGoogleSheetsDto],
    ) -> None:
        worksheet = await self.worksheet(work_sheet_id)
        datas = [
            [user.sup, user.email, user.telegram_user_id, *user.homeworks_data]
            for user in raw_data
        ]
        await worksheet.update(
            range_name=f"A2:J{len(raw_data) + 1}", values=datas
        )


def get_creds(info: dict[str, str]) -> Callable[[], Credentials]:
    def func() -> Credentials:
        creds = Credentials.from_service_account_info(info)
        scoped = creds.with_scopes(
            [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
        )
        return scoped
    
    return func


async def google_sheets_adapter(
    info: dict[str, str], url: str
) -> GoogleSheetsAdapter:
    gspread = AsyncioGspreadClientManager(get_creds(info))
    gspread_connect = await gspread.authorize()
    spread_sheets = await gspread_connect.open_by_url(url)
    return GoogleSheetsAdapter(gspread_connect, spread_sheets)
