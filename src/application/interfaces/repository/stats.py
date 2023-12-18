from abc import ABC, abstractmethod

from src.application.schemas.dto.stats import CountStatsDTO, HomeWorkStatsDTO, StatsDTO


class AbstractStats(ABC):
    @abstractmethod
    async def get_count_users(self) -> CountStatsDTO:
        raise NotImplementedError
    
    @abstractmethod
    async def get_homework_stats(self) -> HomeWorkStatsDTO:
        raise NotImplementedError
    
    @abstractmethod
    async def stats(self) -> StatsDTO:
        raise NotImplementedError
