from aiogram import Router

from webinar.presentation.tgbot.handling.admin import main as admin
from webinar.presentation.tgbot.handling.user import main as user


route = Router()

route.include_routers(user.route, admin.route)
