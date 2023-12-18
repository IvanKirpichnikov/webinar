from abc import ABC, abstractmethod

from src.application.schemas.dto.homework import (
    AddHomeWorkDTO,
    GetHomeWorkAllByUserIdByType, GetHomeWorkWithInformationForAdminDTO, HomeWorkDTO,
    HomeWorkPaginationDTO, HomeWorkUserId,
    HomeWorkWithInformationForAdminDTO, PaginationHomeWorkDTO, UpdatingTypeAndCommentByIdDTO, UpdatingTypeByIdDTO
)
from src.application.schemas.enums.homework import HomeWorkTypeEnum


class AbstractHomeWork(ABC):
    @abstractmethod
    async def add(self, model: AddHomeWorkDTO) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_number_by_user_id(self, model: HomeWorkUserId) -> list[int] | list:
        raise NotImplementedError
    
    @abstractmethod
    async def get_all_by_user_id(self, model: HomeWorkUserId) -> list[HomeWorkDTO]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_all_by_user_id_and_by_type(self, model: GetHomeWorkAllByUserIdByType) -> list[HomeWorkDTO]:
        raise NotImplementedError
    
    @abstractmethod
    async def update_type_and_comment_by_id(self, model: UpdatingTypeAndCommentByIdDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_type(self, model: UpdatingTypeByIdDTO) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def pagination(self, model: PaginationHomeWorkDTO) -> list[HomeWorkPaginationDTO]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_with_information_for_admin(
        self,
        model: GetHomeWorkWithInformationForAdminDTO
    ) -> HomeWorkWithInformationForAdminDTO:
        raise NotImplementedError
