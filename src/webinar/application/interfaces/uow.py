from abc import abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncIterator, Protocol


class UnitOfWork(Protocol):
    @abstractmethod  # type: ignore
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        raise NotImplementedError
    
    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError


class DBUoW(UnitOfWork, Protocol):
    pass
