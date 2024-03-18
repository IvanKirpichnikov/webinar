from typing import (
    Literal,
    TypeAlias,
)

from aiogram.filters.callback_data import CallbackData

from webinar.domain.enums.direction_type import DirectionTrainingType
from webinar.domain.types import (
    DataBaseId,
    TgChatId,
)


PaginationAction: TypeAlias = Literal["back", "next"]


class Direction(CallbackData, prefix="ask_direction"):
    type: DirectionTrainingType


class SendAnswerQuestion(CallbackData, prefix="send_answer_question"):
    number_question: int
    chat_id: TgChatId


class ReCheckingHomework(CallbackData, prefix="re_check"):
    db_id: DataBaseId


class SelectHomeWorkByNumber(CallbackData, prefix="select_homework"):
    number: int


class SelectHomeWorkByDBId(CallbackData, prefix="select_homework"):
    db_id: int


class Pagination(CallbackData, prefix="pagination"):
    action: str
