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

from src.application.schemas.dto.user import UpdateUserDataGoogleSheetsDto
from src.application.schemas.enums import DirectionEnum
from src.infrastructure.repositories.user import UserRepository


class GoogleSheetsAdapter:
    connect: AsyncioGspreadClient
    user_repository: UserRepository
    spread_sheets: AsyncioGspreadSpreadsheet
    
    def __init__(
        self,
        connect: AsyncioGspreadClient,
        spread_sheets: AsyncioGspreadSpreadsheet,
        user_repository: UserRepository
    ) -> None:
        self.user_repository = user_repository
        self.connect = connect
        self.spread_sheets = spread_sheets
    
    async def _set_column_name(self, worksheet: AsyncioGspreadWorksheet) -> None:
        data = [
            Cell(1, 1, 'ФИО'),
            Cell(1, 2, 'Почта'),
            Cell(1, 3, 'Telegram ID'),
            *[
                Cell(1, num + 3, f'{num} Задание')
                for num in range(1, 7)
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
            await spread_sheet.add_worksheet(title, rows, cols)
        except APIError:
            pass
        worksheet = await spread_sheet.get_worksheet(worksheet_id)
        await self._set_column_name(worksheet)
    
    async def create_worksheet_and_set_names(self) -> None:
        spread_sheets = self.spread_sheets
        await self._create_worksheet_and_set_names(spread_sheets, 'SMM', 100000, 9, 0)
        await self._create_worksheet_and_set_names(spread_sheets, 'Копирайтинг', 100000, 9, 1)
    
    async def worksheet(self, index: int) -> AsyncioGspreadWorksheet:
        return await self.spread_sheets.get_worksheet(index)
    
    async def _update_data(
        self,
        raw_data: list[UpdateUserDataGoogleSheetsDto],
        worksheet: AsyncioGspreadWorksheet
    ) -> None:
        datas = [
            [
                data.sup,
                data.email,
                data.telegram_id,
                *data.homeworks_types
            ]
            for data in raw_data
        ]
        await worksheet.update(
            range_name=f'A2:I{len(raw_data) + 1}',
            values=datas
        )
    
    async def update_data(self) -> None:
        ws = await self.worksheet(0)
        raw_data = await self.user_repository.select_for_spreadsheets(DirectionEnum.SMM)
        await self._update_data(raw_data, ws)
        
        ws = await self.worksheet(1)
        raw_data = await self.user_repository.select_for_spreadsheets(DirectionEnum.COPYRIGHTING)
        await self._update_data(raw_data, ws)


def get_creds(info) -> Callable[[], Credentials]:
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


async def google_sheets_adapter(info: dict[str, str], user_repository: UserRepository, url: str) -> GoogleSheetsAdapter:
    gspread = AsyncioGspreadClientManager(get_creds(info))
    gspread_connect = await gspread.authorize()
    spread_sheets = await gspread_connect.open_by_url(url)
    return GoogleSheetsAdapter(
        gspread_connect, spread_sheets, user_repository
    )
