from dataclasses import asdict, dataclass
from typing import Any

from webinar.application.schemas.entities.homework import HomeWorkStatsEntities
from webinar.application.schemas.entities.user import UserStatsEntity


STATS_TEXT = """
Статистика:
Всего пользователей: {users}
Смм: {users_smm}
Копирайтинг: {users_copyrighting}

Сдано заданий:
 Смм:
  Всего: {smm}
  1 задание: {smm_first}
  2 задание: {smm_second}
  3 задание: {smm_third}
  4 задание: {smm_fourth}
  5 задание: {smm_fifth}
  6 задание: {smm_sixth}
 Копирайтинг:
  Всего: {copyrighting}
  1 задание: {copyrighting_first}
  2 задание: {copyrighting_second}
  3 задание: {copyrighting_third}
  4 задание: {copyrighting_fourth}
  5 задание: {copyrighting_fifth}
  6 задание: {copyrighting_sixth}
"""


@dataclass(frozen=True, slots=True)
class StatsEntity:
    users: UserStatsEntity
    homework: HomeWorkStatsEntities

    @property
    def string(self) -> str:
        user = self.users
        homework = self.homework
        homeworks: dict[str, Any] = {
            f"smm_{key}": data for key, data in asdict(homework.smm).items()
        } | {
            f"copyrighting_{key}": data
            for key, data in asdict(homework.copyrighting).items()
        }

        return STATS_TEXT.format(
            users=user.users,
            users_smm=user.smm,
            users_copyrighting=user.copyrighting,
            smm=user.homework.smm,
            copyrighting=user.homework.copyrighting,
            **homeworks,
        )
