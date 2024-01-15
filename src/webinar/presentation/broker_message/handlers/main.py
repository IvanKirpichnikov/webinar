from faststream.nats import NatsRouter

from webinar.presentation.broker_message.handlers import (
    mailing,
    update_google_sheets
)


route = NatsRouter()
route.include_routers(mailing.route, update_google_sheets.route)
