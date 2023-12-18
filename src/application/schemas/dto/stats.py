from dataclasses import asdict, dataclass


STATS_TEXT = '''
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
'''


@dataclass(frozen=True, slots=True)
class CountHomeWorkDTO:
    smm: int = 0
    copyrighting: int = 0


@dataclass(frozen=True, slots=True)
class CountStatsDTO:
    homework: CountHomeWorkDTO
    users: int = 0
    users_smm: int = 0
    users_copyrighting: int = 0


@dataclass(frozen=True, slots=True)
class HomeWorkTypeStatsDTO:
    first: int = 0
    second: int = 0
    third: int = 0
    fourth: int = 0
    fifth: int = 0
    sixth: int = 0


@dataclass(frozen=True, slots=True)
class HomeWorkStatsDTO:
    smm: HomeWorkTypeStatsDTO
    copyrighting: HomeWorkTypeStatsDTO


@dataclass(frozen=True, slots=True)
class StatsDTO:
    count: CountStatsDTO
    homework: HomeWorkStatsDTO
    
    @property
    def string(self) -> str:
        count = self.count
        h = self.homework
        smm = h.smm
        cop = h.copyrighting
        c = {
            f'smm_{key}': data
            for key, data in asdict(smm).items()
        } | {
            f'copyrighting_{key}': data
            for key, data in asdict(cop).items()
        }
        
        return STATS_TEXT.format(
            users=count.users,
            users_smm=count.users_smm,
            users_copyrighting=count.users_copyrighting,
            smm=count.homework.smm,
            copyrighting=count.homework.copyrighting,
            **c
        )
