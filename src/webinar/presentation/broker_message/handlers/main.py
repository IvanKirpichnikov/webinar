from faststream.nats import NatsRouter

from webinar.presentation.broker_message.handlers import update_google_sheets
from webinar.presentation.broker_message.handlers import mailing


route = NatsRouter()
route.include_routers(mailing.route, update_google_sheets.route)
