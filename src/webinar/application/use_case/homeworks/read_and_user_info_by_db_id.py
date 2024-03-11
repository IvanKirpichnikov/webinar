from abc import abstractmethod
from typing import Protocol

from webinar.application.dto.homework import HomeWorkIdDTO
from webinar.application.interfaces.gateways.homework import HomeWorkGateway
from webinar.application.use_case.base import UseCase
from webinar.domain.models.homework import HomeWorkAndUserInfoEntity


class ReadHomeworkAndUserInfoByDBId(
    UseCase[HomeWorkIdDTO, HomeWorkAndUserInfoEntity], Protocol
):
    @abstractmethod
    async def __call__(self, data: HomeWorkIdDTO) -> HomeWorkAndUserInfoEntity:
        raise NotImplementedError


class ReadHomeworkAndUserInfoByDBIdImpl(ReadHomeworkAndUserInfoByDBId):
    def __init__(self, gateway: HomeWorkGateway) -> None:
        self._gateway = gateway
    
    async def __call__(self, data: HomeWorkIdDTO) -> HomeWorkAndUserInfoEntity:
        result = await self._gateway.read_homework_and_user_info_by_db_id(data)
        return result
