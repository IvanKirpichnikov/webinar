# from abc import abstractmethod
# from typing import Protocol
#
# from webinar.application.dto.homework import UpdateHomeWorkStatusDTO
# from webinar.application.interfaces.gateways.homework import HomeWorkGateway
# from webinar.application.interfaces.uow import DBUoW
# from webinar.application.use_case.base import UseCase
#
#
# class UpdateHomeWorkStatus(
#     UseCase[UpdateHomeWorkStatusDTO, None], Protocol
# ):
#     @abstractmethod
#     async def __call__(self, data: UpdateHomeWorkStatusDTO) -> None:
#         raise NotImplementedError
#
#
# class UpdateHomeWorkStatusImpl(UpdateHomeWorkStatus):
#     def __init__(self, uow: DBUoW, gateway: HomeWorkGateway) -> None:
#         self._gateway = gateway
#         self._uow = uow
#
#     async def __call__(self, data: UpdateHomeWorkStatusDTO) -> None:
#         async with self._uow.transaction():
#             await self._gateway.update_type_and_comment()
