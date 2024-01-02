from aiogram import Router

from webinar.presentation.tgbot.filtering import CheckUserRegisteringFilter
from webinar.presentation.tgbot.handling.user import (
    main_menu,
    question_from_user,
    questions,
    questions_technical_support,
    registrating,
    send_homework,
    webinar_recordings,
)
from webinar.presentation.tgbot.handling.user import my_homeworks


files = [
    registrating,
    main_menu,
    send_homework,
    questions,
    question_from_user,
    questions_technical_support,
    webinar_recordings,
    my_homeworks,
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
