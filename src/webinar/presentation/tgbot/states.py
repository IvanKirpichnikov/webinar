from aiogram.fsm.state import State, StatesGroup


class RegisteringState(StatesGroup):
    ask_direction = State()
    ask_sup = State()
    ask_email = State()


class SendYourQuestion(StatesGroup):
    ask_question = State()
    ask_confirmation_send = State()


class WebinarPaginationState(StatesGroup):
    pagination = State()


class AskHomeWorkState(StatesGroup):
    ask_url = State()
    ask_number = State()


class AddWebinarState(StatesGroup):
    ask_url = State()
    ask_name = State()


class AddAdminState(StatesGroup):
    ask_user_id = State()
    ask_range_or_numb = State()
    ask_webinar_type = State()


class AdminHomeWorksState(StatesGroup):
    ask_comments = State()
    pagination = State()
    select_homework = State()


class SendAnswerQuestionState(StatesGroup):
    ask_answer = State()


class MailingState(StatesGroup):
    ask_direction = State()
    ask_message = State()
