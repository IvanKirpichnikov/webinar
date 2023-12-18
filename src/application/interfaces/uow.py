from abc import ABC, abstractmethod


class AbstractUnitOfWork(ABC):
    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
