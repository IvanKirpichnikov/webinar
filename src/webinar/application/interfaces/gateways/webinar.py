from abc import abstractmethod
from typing import Protocol, TYPE_CHECKING

from webinar.application.dto.webinar import CreateWebinarDTO
from webinar.domain.models.webinar import Webinars

if TYPE_CHECKING:
    from webinar.application.use_case.webinars.get_pagination import GetPaginationWebinarsData

class WebinarGateway(Protocol):
    @abstractmethod
    async def create(self, model: CreateWebinarDTO) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def pagination(self, model: 'GetPaginationWebinarsData') -> Webinars | None:
        raise NotImplementedError
