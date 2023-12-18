from abc import ABC, abstractmethod

from src.application.schemas.dto.user import AddUserDto


class AbstractUser(ABC):
    @abstractmethod
    async def add(self, model: AddUserDto) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def check(self, user_id: int) -> bool:
        raise NotImplementedError
