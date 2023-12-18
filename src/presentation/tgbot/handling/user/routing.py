from aiogram import Router

from src.presentation.tgbot.filtering import CheckUserRegisteringFilter
from src.presentation.tgbot.handling.user import (
    hand_in_the_assignment,
    i_have_question,
    i_want_to_ask_question,
    main_menu,
    registrating,
    submitted_assignment,
    technical_support,
    webinars
)


files = [
    registrating,
    main_menu,
    i_have_question,
    i_want_to_ask_question,
    technical_support,
    webinars,
    hand_in_the_assignment,
    submitted_assignment
]
check_user = CheckUserRegisteringFilter()
route = Router()
for file in files:
    r = file.route
    if file != registrating:
        r.message.filter(check_user)
        r.callback_query.filter(check_user)
    else:
        r.message.filter(~check_user)
        r.callback_query.filter(~check_user)
    route.include_router(file.route)
