from aiogram import Bot
from faststream import Context, ContextRepo
from psycopg import AsyncConnection
from psycopg.rows import dict_row

from src.application.config import ConfigFactory
from src.infrastructure.google_sheets.adapter import google_sheets_adapter
from src.infrastructure.repositories.user import UserRepository


async def setup_context(
    context: ContextRepo,
    config: ConfigFactory = Context()
) -> None:
    c = config.config
    bot = Bot(c.bot.token)
    connect = await AsyncConnection.connect(
        config.config.psql.url,
        row_factory=dict_row
    )
    repo = UserRepository(connect)
    google_sheet = await google_sheets_adapter(c.google_sheets.data, repo, c.google_sheets.url)
    await google_sheet.create_worksheet_and_set_names()
    context.set_global('bot', bot)
    context.set_global('config', config)
    context.set_global('connect', connect)
    context.set_global('user_repository', repo)
    context.set_global('google_sheet', google_sheet)


async def close_connect(connect: AsyncConnection = Context(), bot: Bot = Context()) -> None:
    await connect.close()
    await bot.session.close()
