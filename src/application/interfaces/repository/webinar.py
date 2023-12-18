from abc import ABC, abstractmethod

from src.application.schemas.dto.webinar import AddWebinarDTO, Webinar


class AbstractWebinar(ABC):
    @abstractmethod
    async def add(self, model: AddWebinarDTO) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def get(self, offset: int, count_webinars: int) -> list[Webinar]:
        raise NotImplementedError
