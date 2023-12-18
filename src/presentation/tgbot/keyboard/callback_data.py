from typing import Literal

from aiogram.filters.callback_data import CallbackData

from src.application.schemas.enums import DirectionEnum


class WebinarPaginationCallbackData(CallbackData, prefix='webinar_pagination'):
    action: Literal['back', 'next']


class HomeWorkCallbackData(CallbackData, prefix='homework'):
    number: int


class SubmitForReviewCallbackData(CallbackData, prefix='submit_for_review'):
    homework_id: int


class AskDirectionCallbackData(CallbackData, prefix='ask_direction'):
    type: DirectionEnum | Literal['all']


class HomeWorkActionCallbackData(CallbackData, prefix='hm_pag'):
    action: Literal['back', 'next']


class HomeWorkPaginationCallbackData(CallbackData, prefix='hm_pag'):
    id: int


class SendAnswerQuestionCallbackData(CallbackData, prefix='send_answer'):
    number_question: int
    chat_id: int
