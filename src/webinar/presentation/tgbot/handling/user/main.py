from aiogram import Router

from webinar.presentation.tgbot.filtering import CheckUserRegisteringFilter
from webinar.presentation.tgbot.handling.user import (
    main_menu,
    my_homeworks,
    question_from_user,
    registrating,
    send_homework,
    technical_support,
    webinar_recordings
)


files = [
    main_menu,
    my_homeworks,
    question_from_user,
    registrating,
    send_homework,
    technical_support,
    webinar_recordings
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
