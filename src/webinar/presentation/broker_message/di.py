from aiogram import Bot
from faststream import (
    Context,
    ContextRepo,
)

from webinar.application.config import ConfigFactory
from webinar.infrastructure.adapters.google_sheet import google_sheets_adapter


async def setup_context(
    context: ContextRepo,
    config: ConfigFactory = Context(),
) -> None:
    config_ = config.config
    
    
    google_sheet = await google_sheets_adapter(
        config_.google_sheets.data, config_.google_sheets.url
    )
    await google_sheet.create_worksheet_and_set_names()
    
    context.set_global("config", config)
    context.set_global("google_sheet", google_sheet)


async def close_connect(bot: Bot = Context()) -> None:
    await bot.session.close()
