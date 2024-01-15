from aiogram import Bot
from faststream import (
    Context,
    ContextRepo
)
from psycopg import AsyncConnection
from psycopg.rows import DictRow

from webinar.application.config import ConfigFactory
from webinar.infrastructure.adapters.google_sheet import google_sheets_adapter
from webinar.infrastructure.database.repository.user import UserRepositoryImpl


async def setup_context(
    context: ContextRepo,
    config: ConfigFactory = Context(),
    connect: AsyncConnection[DictRow] = Context(),
) -> None:
    config_ = config.config
    bot = Bot(config_.bot.token)
    repo = UserRepositoryImpl(connect)
    google_sheet = await google_sheets_adapter(
        config_.google_sheets.data, config_.google_sheets.url
    )
    await google_sheet.create_worksheet_and_set_names()
    
    context.set_global("bot", bot)
    context.set_global("config", config)
    context.set_global("user_repository", repo)
    context.set_global("google_sheet", google_sheet)


async def close_connect(bot: Bot = Context()) -> None:
    await bot.session.close()
