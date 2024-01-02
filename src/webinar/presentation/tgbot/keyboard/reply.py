from functools import lru_cache

from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class ReplyKeyboardFactory:
    @property
    def builder(self) -> ReplyKeyboardBuilder:
        return ReplyKeyboardBuilder()

    @lru_cache()
    def save(self) -> ReplyKeyboardMarkup:
        builder = self.builder
        builder.button(text="Числовой диапазон")
        return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
