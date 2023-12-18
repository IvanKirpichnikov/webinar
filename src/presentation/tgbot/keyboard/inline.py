from functools import lru_cache
from typing import cast

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.application.schemas.dto.homework import HomeWorkDTO, HomeWorkPaginationDTO
from src.application.schemas.dto.webinar import Webinar
from src.application.schemas.enums import DirectionEnum
from src.application.schemas.enums.homework import HomeWorkTypeEnum
from src.presentation.tgbot.keyboard.callback_data import (
    AskDirectionCallbackData,
    HomeWorkActionCallbackData,
    HomeWorkCallbackData,
    HomeWorkPaginationCallbackData,
    SendAnswerQuestionCallbackData,
    SubmitForReviewCallbackData,
    WebinarPaginationCallbackData
)


class InlineKeyboardFactory:
    @property
    def builder(self) -> InlineKeyboardBuilder:
        return InlineKeyboardBuilder()
    
    @lru_cache()
    def ask_direction_admin_to_mailing(self) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            ('SMM', AskDirectionCallbackData(type=DirectionEnum.SMM)),
            ('Копирайтинг', AskDirectionCallbackData(type=DirectionEnum.COPYRIGHTING)),
            ('Все', AskDirectionCallbackData(type='all')),
            ('Назад', 'admin_panel')
        ]
        for text, cd in buttons_data:
            builder.button(text=text, callback_data=cd)
        
        return cast(
            InlineKeyboardMarkup,
            builder.adjust(1).as_markup()
        )
    
    @lru_cache()
    def ask_direction_admin(self) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            ('SMM', AskDirectionCallbackData(type=DirectionEnum.SMM)),
            ('Копирайтинг', AskDirectionCallbackData(type=DirectionEnum.COPYRIGHTING)),
            ('Назад', 'admin_panel')
        ]
        for text, cd in buttons_data:
            builder.button(text=text, callback_data=cd)
        
        return cast(
            InlineKeyboardMarkup,
            builder.adjust(1).as_markup()
        )
    
    @lru_cache()
    def ask_direction(self) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            ('SMM', AskDirectionCallbackData(type=DirectionEnum.SMM)),
            ('Копирайтинг', AskDirectionCallbackData(type=DirectionEnum.COPYRIGHTING))
        ]
        for text, cd in buttons_data:
            builder.button(text=text, callback_data=cd)
        
        return cast(InlineKeyboardMarkup, builder.adjust(1).as_markup())
    
    @lru_cache()
    def main_menu(self) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            ('У меня вопрос', 'i_have_question'),
            ('Записи вебинаров', 'webinar_recordings'),
            ('Сдать задание', 'hand_in_the_assignment'),
            ('Сданные задания', 'submitted_assignment')
        ]
        for text, cd in buttons_data:
            builder.button(text=text, callback_data=cd)
        
        return cast(
            InlineKeyboardMarkup,
            builder.adjust(1).as_markup()
        )
    
    @lru_cache()
    def i_have_question(self) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            ('Тех. поддержка', 'technical_support'),
            ('Вебинары', 'question_webinars'),
            ('Дом. задание', 'question_homework'),
            ('Хочу задать вопрос', 'question_i_want_to_ask_question'),
            ('Назад', 'back_to_main_menu')
        ]
        for text, cd in buttons_data:
            builder.button(text=text, callback_data=cd)
        
        return cast(
            InlineKeyboardMarkup,
            builder.adjust(1).as_markup()
        )
    
    @lru_cache()
    def technical_support(self) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            ('Не открывается урок', 'lesson_won_open'),
            ('Не могу зайти на платформу', 'i_can_log_into_platform'),
            ('...', 'ellipsis'),
            ('Назад', 'i_have_question'),
        ]
        for text, cd in buttons_data:
            builder.button(text=text, callback_data=cd)
        
        return cast(
            InlineKeyboardMarkup,
            builder.adjust(1).as_markup()
        )
    
    @lru_cache(typed=True)
    def back(self, back_callback_data: str) -> InlineKeyboardMarkup:
        builder = self.builder
        builder.button(text='Назад', callback_data=back_callback_data)
        
        return cast(
            InlineKeyboardMarkup,
            builder.as_markup()
        )
    
    @lru_cache(typed=True)
    def send_question(self, back_callback_data: str) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            ('Отправить', 'send_question'),
            ('Назад', back_callback_data)
        ]
        for text, cd in buttons_data:
            builder.button(text=text, callback_data=cd)
        
        return cast(
            InlineKeyboardMarkup,
            builder.adjust(1).as_markup()
        )
    
    def webinars(
        self,
        models: list[Webinar],
        count_webinars_button: int,
        offset: int = 0
    ) -> InlineKeyboardMarkup:
        builder = self.builder
        len_models = len(models)
        
        for model in models:
            builder.button(text=model.name, url=model.url)
        if offset >= 1:
            builder.button(
                text='<',
                callback_data=WebinarPaginationCallbackData(action='back')
            )
        if len_models == count_webinars_button:
            builder.button(
                text='>',
                callback_data=WebinarPaginationCallbackData(action='next')
            )
        builder.button(
            text='Назад',
            callback_data='back_to_main_menu'
        )
        return cast(
            InlineKeyboardMarkup,
            builder.adjust(*[1 for _ in range(len_models)], 2, 1).as_markup()
        )
    
    def select_homework(self, numbers: list[int]) -> InlineKeyboardMarkup:
        builder = self.builder
        for number in numbers:
            builder.button(
                text=f'{number} задание',
                callback_data=HomeWorkCallbackData(number=number)
            )
        builder.button(
            text='Назад',
            callback_data='hand_in_the_assignment'
        )
        return cast(
            InlineKeyboardMarkup,
            builder.adjust(1).as_markup()
        )
    
    def under_revision_homeworks(self, homeworks: list[HomeWorkDTO]) -> InlineKeyboardMarkup:
        builder = self.builder
        for homework in homeworks:
            if homework.type != HomeWorkTypeEnum.UNDER_REVISION:
                continue
            builder.button(
                text=f'№{homework.number} Отправить на проверку',
                callback_data=SubmitForReviewCallbackData(homework_id=homework.id)
            )
        builder.button(
            text='Назад',
            callback_data='back_to_main_menu'
        )
        return cast(
            InlineKeyboardMarkup,
            builder.adjust(1).as_markup()
        )
    
    @lru_cache(typed=True)
    def admin_panel(self, is_super_admin: bool) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            ('Статистика', 'stats'),
            ('Рассылка', 'mailing'),
            ('Задания', 'homeworks'),
            ('Опубликовать запись вебинара', 'publish_webinar_recording'),
            ('Обновить Google таблицы', 'update_google_tables')
        ]
        for text, cd in buttons_data:
            builder.button(text=text, callback_data=cd)
        if is_super_admin:
            builder.button(
                text='Добавить админа',
                callback_data='add_admin'
            )
        return cast(
            InlineKeyboardMarkup,
            builder.adjust(1).as_markup()
        )
    
    @lru_cache(typed=True)
    def webinar_type_(self, user_id: int) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            dict(
                text='SMM',
                callback_data=AskDirectionCallbackData(type=DirectionEnum.SMM)
            ),
            dict(
                text='Копирайтинг',
                callback_data=AskDirectionCallbackData(type=DirectionEnum.COPYRIGHTING)
            ),
            dict(text='Аккаунт', url=f'tg://user?id={user_id}'),
            dict(text='Назад', callback_data='add_admin')
        ]
        for data in buttons_data:
            builder.button(**data)
        
        return cast(
            InlineKeyboardMarkup,
            builder.adjust(1).as_markup()
        )
    
    def pagination_homeworks(
        self,
        models: list[HomeWorkPaginationDTO],
        offset: int
    ) -> InlineKeyboardMarkup:
        builder = self.builder
        len_models = len(models)
        a = 1
        for model in models:
            date_time = model.date_time.strftime('%d.%m')
            patronymic = model.patronymic or ' '
            text = f'№{model.number} {date_time} {model.surname.title()} {model.name[0].title()}.{patronymic[0].title()}'
            builder.button(
                text=text,
                callback_data=HomeWorkPaginationCallbackData(id=model.id)
            )
        if offset > 0:
            builder.button(
                text='<',
                callback_data=HomeWorkActionCallbackData(action='back')
            )
            a += 1
        builder.button(
            text=str(offset + 1),
            callback_data='erfvdawefv'
        )
        if len_models == 10 and offset > 0:
            builder.button(
                text='>',
                callback_data=HomeWorkActionCallbackData(action='next')
            )
            a += 1
        builder.button(
            text='Назад',
            callback_data='admin_panel'
        )
        return cast(
            InlineKeyboardMarkup,
            builder.adjust(*[1 for _ in range(len_models)], a, 1).as_markup()
        )
    
    def check_homework(self, user_id: int) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            dict(text='Принять на работу', callback_data='accept_homework'),
            dict(text='На доработку', callback_data='revision_homework'),
            dict(text='Аккаунт', url=f'tg://user?id={user_id}'),
            dict(text='Отмена', callback_data='homeworks')
        ]
        for data in buttons_data:
            builder.button(**data)
        
        return cast(
            InlineKeyboardMarkup,
            builder.adjust(1).as_markup()
        )
    
    @lru_cache()
    def send_answer(self, number_question: int, chat_id: int) -> InlineKeyboardMarkup:
        builder = self.builder
        builder.button(
            text='Написать ответ',
            callback_data=SendAnswerQuestionCallbackData(number_question=number_question, chat_id=chat_id)
        )
        return cast(
            InlineKeyboardMarkup,
            builder.as_markup()
        )
