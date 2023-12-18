from aiogram import Router

from . import add_admin, homeworks, main_menu, publish_webinar_recording, stats, send_question_answer, mailing, update_google_tables


route = Router()
files = [
    main_menu,
    publish_webinar_recording,
    add_admin,
    stats,
    homeworks,
    send_question_answer,
    mailing,
    update_google_tables
]

for file in files:
    route.include_router(file.route)
