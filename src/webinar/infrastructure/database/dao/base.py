from abc import ABC, abstractmethod


class BaseDAO(ABC):
    pass


class BaseOtherCreate(ABC):
    @abstractmethod
    async def create_table(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_index(self) -> None:
        raise NotImplementedError
