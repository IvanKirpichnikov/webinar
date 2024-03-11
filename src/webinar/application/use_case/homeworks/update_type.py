from webinar.application.use_case.base import UseCase


class UpdateHomeWorkStatus(UseCase[, None], Protocol):
    @abstractmethod
    async def __call__(self, data: UpdateHomeWorkStatusDTO) -> None: