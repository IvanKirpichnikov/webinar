from dataclasses import asdict, dataclass
from typing import Any

from webinar.domain.models.homework import HomeWorkStatsEntities


STATS_TEXT = """
Статистика:
Всего пользователей: {users}
Смм: {users_smm}
Копирайтинг: {users_copyrighting}

Сдана заданий:
 Смм:
  Всего: {smm}
  Базовый модуль: {smm_first}
  Базовый модуль: {smm_second}
  Специализация: {smm_third}
  Специализация: {smm_fourth}
  Специализация: {smm_fifth}
  Специализация: {smm_sixth}
  Проект: {smm_seventh}
 Копирайтинг:
  Всего: {copyrighting}
  Базовый модуль: {copyrighting_first}
  Базовый модуль: {copyrighting_second}
  Специализация: {copyrighting_third}
  Специализация: {copyrighting_fourth}
  Специализация: {copyrighting_fifth}
  Специализация: {copyrighting_sixth}
  Проект: {copyrighting_seventh}
"""


@dataclass(frozen=True, slots=True)
class UserStats:
    homework_smm: int = 0
    homework_copyrighting: int = 0
    users: int = 0
    smm: int = 0
    copyrighting: int = 0


@dataclass(frozen=True, slots=True)
class Stats:
    users: UserStats
    homework: HomeWorkStatsEntities
    
    @property
    def string(self) -> str:
        user = self.users
        homework = self.homework
        homeworks: dict[str, Any] = (
            {
                f"smm_{key}": data for key, data in asdict(homework.smm).items()
            } | {
                f"copyrighting_{key}": data
                for key, data in asdict(homework.copyrighting).items()
            }
        )
        
        return STATS_TEXT.format(
            users=user.users,
            users_smm=user.smm,
            users_copyrighting=user.copyrighting,
            smm=user.homework_smm,
            copyrighting=user.homework_copyrighting,
            **homeworks,
        )
