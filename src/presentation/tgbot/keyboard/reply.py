from aiogram.utils.keyboard import ReplyKeyboardBuilder


class ReplyKeyboardFactory:
    @property
    def builder(self) -> ReplyKeyboardBuilder:
        return ReplyKeyboardBuilder()
