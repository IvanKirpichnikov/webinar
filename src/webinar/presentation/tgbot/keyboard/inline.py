from functools import lru_cache
from typing import cast

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from webinar.application.schemas.dto.button import BackButtonDataDTO
from webinar.application.schemas.entities.homework import (
    HomeWorkEntities,
    HOMEWORKS_TEXT,
    UserHomeWorkEntities
)
from webinar.application.schemas.entities.webinar import WebinarEntities
from webinar.application.schemas.enums.direction_type import DirectionTrainingType
from webinar.application.schemas.enums.homework import HomeWorkStatusType
from webinar.application.schemas.types import (
    HomeWorkNumber,
    TelegramChatId,
    TelegramUserId
)
from webinar.presentation.tgbot.keyboard.callback_data import (
    Direction,
    Pagination,
    ReCheckingHomework,
    SelectHomeWorkByDBId,
    SelectHomeWorkByNumber,
    SendAnswerQuestion
)


class InlineKeyboardFactory:
    @property
    def builder(self) -> InlineKeyboardBuilder:
        return InlineKeyboardBuilder()
    
    @lru_cache()
    def main_menu(self) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            ("Записи вебинаров", "webinar_recordings"),
            ("Сдать задание", "send_homework"),
            ("Мои задания", "my_homeworks"),
            ("Тех. поддержка", "technical_support")
        ]
        for text, cd in buttons_data:
            builder.button(text=text, callback_data=cd)
        
        return cast(InlineKeyboardMarkup, builder.adjust(1).as_markup())
    
    @lru_cache()
    def ask_direction_admin_to_mailing(self) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            ("SMM", Direction(type=DirectionTrainingType.SMM)),
            ("Копирайтинг", Direction(type=DirectionTrainingType.COPYRIGHTING)),
            ("Все", Direction(type=DirectionTrainingType.ALl)),
            ("Назад", "admin_panel")
        ]
        for text, callback_data in buttons_data:
            builder.button(text=text, callback_data=callback_data)
        
        return cast(InlineKeyboardMarkup, builder.adjust(1).as_markup())
    
    @lru_cache()
    def directions(
        self,
        model: BackButtonDataDTO | None = None
    ) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data: list[tuple[str, str | Direction]]
        buttons_data = [
            ("SMM", Direction(type=DirectionTrainingType.SMM)),
            ("Копирайтинг", Direction(type=DirectionTrainingType.COPYRIGHTING))
        ]
        if model:
            buttons_data.append((model.text, model.callback_data))
        
        for text, callback_data in buttons_data:
            builder.button(text=text, callback_data=callback_data)
        
        return cast(InlineKeyboardMarkup, builder.adjust(1).as_markup())
    
    @lru_cache()
    def technical_support(self) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            ("Не работает инвайт", "dont_work_invite"),
            ("Не могу зайти на платформу", "i_can_log_into_platform"),
            ("Не грузят уроки", "doesnt_load_lessons"),
            ("Не могу восстановить пароль", "can_reset_password"),
            ("Другая техническая проблема", "question_from_user"),
            ("Назад", "main_menu")
        ]
        for text, callback_data in buttons_data:
            builder.button(text=text, callback_data=callback_data)
        
        return cast(InlineKeyboardMarkup, builder.adjust(1).as_markup())
    
    @lru_cache(typed=True)
    def back(self, back_callback_data: str) -> InlineKeyboardMarkup:
        builder = self.builder
        builder.button(text="Назад", callback_data=back_callback_data)
        return builder.as_markup()
    
    @lru_cache(typed=True)
    def send_question(self, back_callback_data: str) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            ("Отправить", "send_question"),
            ("Назад", back_callback_data),
        ]
        for text, cd in buttons_data:
            builder.button(text=text, callback_data=cd)
        
        return cast(InlineKeyboardMarkup, builder.adjust(1).as_markup())
    
    def pagination_webinars(
        self, model: WebinarEntities, count_webinars_button: int, offset: int
    ) -> InlineKeyboardMarkup:
        builder = self.builder
        
        for webinar in model.webinars:
            builder.button(text=webinar.name, url=webinar.url)
        if offset > 0:
            builder.button(text="<", callback_data=Pagination(action="back"))
        if model.count == count_webinars_button:
            builder.button(text=">", callback_data=Pagination(action="next"))
        builder.button(text="Назад", callback_data="main_menu")
        return cast(
            InlineKeyboardMarkup,
            builder.adjust(*[1 for _ in range(model.count)], 2, 1).as_markup(),
        )
    
    def select_homework(
        self, model: list[HomeWorkNumber]
    ) -> InlineKeyboardMarkup:
        builder = self.builder
        for number in model:
            builder.button(
                text=HOMEWORKS_TEXT[number],
                callback_data=SelectHomeWorkByNumber(number=number),
            )
        builder.button(text="Назад", callback_data="main_menu")
        print(builder)
        return cast(InlineKeyboardMarkup, builder.adjust(1).as_markup())
    
    def under_revision_homeworks(
        self, model: HomeWorkEntities
    ) -> InlineKeyboardMarkup:
        builder = self.builder
        for homework in model.homeworks:
            if homework.status_type == HomeWorkStatusType.UNDER_REVISION:
                number = homework.number
                if number in {1, 2}:
                    a = f'Б №{number}'
                elif number in {3, 4, 5, 6}:
                    a = f'C №{number - 2}'
                else:
                    a = 'Проект'
                builder.button(
                    text=f"{a} Отправить на проверку",
                    callback_data=ReCheckingHomework(db_id=homework.db_id),
                )
        builder.button(text="Назад", callback_data="main_menu")
        return cast(InlineKeyboardMarkup, builder.adjust(1).as_markup())
    
    @lru_cache(typed=True)
    def admin_main_menu(self, is_super_admin: bool) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            ("Статистика", "stats"),
            ("Рассылка", "mailing"),
            ("Домашние задания", "homeworks"),
            ("Опубликовать запись вебинара", "create_webinar"),
            ("Обновить Google таблицу", "update_google_tables"),
        ]
        if is_super_admin:
            buttons_data.append(("Добавить админа", "add_admin"))
        for text, callback_data in buttons_data:
            builder.button(text=text, callback_data=callback_data)
        
        return cast(InlineKeyboardMarkup, builder.adjust(1).as_markup())
    
    def select_direction_training_for(
        self, user_id: TelegramUserId
    ) -> InlineKeyboardMarkup:
        builder = self.builder
        buttons_data = [
            dict(
                text="SMM",
                callback_data=Direction(type=DirectionTrainingType.SMM),
            ),
            dict(
                text="Копирайтинг",
                callback_data=Direction(
                    type=DirectionTrainingType.COPYRIGHTING
                ),
            ),
            dict(text="Аккаунт", url=f"tg://user?id={user_id}"),
            dict(text="Назад", callback_data="add_admin"),
        ]
        for data in buttons_data:
            builder.button(**data)
        
        return cast(InlineKeyboardMarkup, builder.adjust(1).as_markup())
    
    def pagination_homeworks(
        self,
        model: UserHomeWorkEntities,
        offset: int,
        count_homeworks: int,
        count_homeworks_in_pagination: int,
    ) -> InlineKeyboardMarkup:
        builder = self.builder
        len_models = len(model.homeworks)
        xz = 1
        for homework in model.homeworks:
            builder.button(
                text=homework.string(),
                callback_data=SelectHomeWorkByDBId(db_id=homework.db_id),
            )
        if offset > 0:
            xz += 1
            builder.button(text="<", callback_data=Pagination(action="back"))
        builder.button(text=f"{offset + 1}", callback_data="not_implemented")
        if len_models == count_homeworks_in_pagination:
            xz += 1
            builder.button(text=">", callback_data=Pagination(action="next"))
        builder.button(text="Назад", callback_data="admin_panel")
        return cast(
            InlineKeyboardMarkup,
            builder.adjust(*[1 for _ in range(len_models)], xz, 1).as_markup(),
        )
    
    def check_homework(
        self, telegram_user_id: TelegramUserId, evaluation: bool = False
    ) -> InlineKeyboardMarkup:
        builder = self.builder
        if evaluation:
            buttons_data = [
                ("Хорошо", "select_ok"),
                ("Отлично", "revision_good"),
            ]
        else:
            buttons_data = [("Принять работу", "accept_homework")]
        buttons_data.append(("На доработку", "revision_homework"))
        buttons_data.append(("Аккаунт", f"tg://user?id={telegram_user_id}"))
        buttons_data.append(("Назад", "homeworks"))
        
        for text, callback_data in buttons_data:
            if text == "Аккаунт":
                builder.button(text=text, url=callback_data)
                continue
            builder.button(text=text, callback_data=callback_data)
        
        return cast(InlineKeyboardMarkup, builder.adjust(1).as_markup())
    
    @lru_cache()
    def send_answer_question(
        self, chat_id: TelegramChatId, number_question: int,
        user_id: int
    ) -> InlineKeyboardMarkup:
        builder = self.builder
        builder.button(
            text="Написать ответ",
            callback_data=SendAnswerQuestion(
                number_question=number_question, chat_id=chat_id
            ),
        )
        builder.button(
            text="Аккаунт",
            url=f"tg://user?id={user_id}"
        )
        return builder.as_markup()
