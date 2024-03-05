from dishka import provide, Provider, Scope

from webinar.application.interfaces.delete_message import TgDeleteMessage
from webinar.infrastructure.aiogram.delete_message import AiogramDeleteMessage


class OtherProvider(Provider):
    scope = Scope.REQUEST
    
    aiogram_delete_message = provide(
        source=AiogramDeleteMessage,
        provides=TgDeleteMessage
    )
