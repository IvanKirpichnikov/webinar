from abc import ABC, abstractmethod

from src.application.schemas.dto.admin import AddAdminDTO, AdminUserId
from src.application.schemas.enums import DirectionEnum


class AbstractAdmin(ABC):
    @abstractmethod
    async def add(self, model: AddAdminDTO) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def exists(self, model: AdminUserId) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    async def get_direction_type(self, model: AdminUserId) -> DirectionEnum:
        raise NotImplementedError
        
    @abstractmethod
    async def get_random_chat_id_admin(self) -> int:
        raise NotImplementedError
    
