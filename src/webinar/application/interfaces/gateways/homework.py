from abc import abstractmethod
from typing import Any, Protocol, TYPE_CHECKING

from webinar.application.dto.common import DbIdDTO, TgUserIdDTO
from webinar.application.dto.homework import (
    HomeWorkIdDTO,
    HomeWorkPaginationDTO,
    TgUserIdAndStatusTypeDTO,
    UpdateHomeworkEvolutionAndStatusDTO,
    UpdateHomeworkStatusAndCommentByIdDTO,
    UpdateHomeWorkStatusDTO,
)
from webinar.domain.models.homework import (
    HomeWorkAndUserInfoEntity,
    HomeWorks,
    UserHomeWorks,
)


if TYPE_CHECKING:
    from webinar.application.use_case.homeworks.add_user_homework import AddUserHomeWorkDTO


class HomeWorkGateway(Protocol):
    @abstractmethod
    async def add_user_homework(self, model: 'AddUserHomeWorkDTO') -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def delete_by_db_id(self, model: DbIdDTO) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def read_all_by_telegram_user_id(
        self, model: TgUserIdDTO
    ) -> HomeWorks | None:
        raise NotImplementedError
    
    @abstractmethod
    async def read_all_by_telegram_user_id_and_status_type(
        self, model: TgUserIdAndStatusTypeDTO
    ) -> HomeWorks:
        raise NotImplementedError
    
    @abstractmethod
    async def update_status(self, model: UpdateHomeWorkStatusDTO) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def update_type_and_comment(
        self, model: UpdateHomeworkStatusAndCommentByIdDTO
    ) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def read_from_letters_range(
        self, model: HomeWorkPaginationDTO
    ) -> UserHomeWorks | None:
        raise NotImplementedError
    
    @abstractmethod
    async def read_from_numbers_range(
        self, model: HomeWorkPaginationDTO
    ) -> UserHomeWorks | None:
        raise NotImplementedError
    
    @abstractmethod
    async def read_from_offset(
        self, model: HomeWorkPaginationDTO
    ) -> UserHomeWorks | None:
        raise NotImplementedError
    
    @abstractmethod
    async def read_stats(self) -> dict[str, Any]:
        raise NotImplementedError
    
    @abstractmethod
    async def read_homework_and_user_info_by_db_id(
        self, model: HomeWorkIdDTO
    ) -> HomeWorkAndUserInfoEntity:
        raise NotImplementedError
    
    @abstractmethod
    async def update_evolution_and_status(
        self, model: UpdateHomeworkEvolutionAndStatusDTO
    ) -> None:
        raise NotImplementedError
