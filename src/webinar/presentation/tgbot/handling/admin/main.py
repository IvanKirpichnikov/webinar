from aiogram import Router

from . import (
    add,
    create_webinar,
    delete_user,
    homeworks,
    mailing,
    main_menu,
    send_question_answer,
    stats,
    update_google_tables,
)
from ...filtering.check_user_is_admin import (
    CheckUserIsAdminRegisteringFilterImpl,
)


route = Router()
files = [
    main_menu,
    create_webinar,
    add,
    stats,
    homeworks,
    send_question_answer,
    mailing,
    update_google_tables,
    delete_user
]

for file in files:
    route.include_router(file.route)

f = CheckUserIsAdminRegisteringFilterImpl()
route.message.filter(f)
route.callback_query.filter(f)
