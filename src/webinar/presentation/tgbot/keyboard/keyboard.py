from webinar.presentation.tgbot.keyboard.inline import InlineKeyboardFactory
from webinar.presentation.tgbot.keyboard.reply import ReplyKeyboardFactory


class KeyboardFactory:
    def __init__(self) -> None:
        self.reply = ReplyKeyboardFactory()
        self.inline = InlineKeyboardFactory()
