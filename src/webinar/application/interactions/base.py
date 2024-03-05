from abc import abstractmethod
from typing import Protocol, TypeVar


IN_DATA = TypeVar('IN_DATA', contravariant=True)
OUT_DATA = TypeVar('OUT_DATA', covariant=True)


class Interactor(Protocol[IN_DATA, OUT_DATA]):
    @abstractmethod
    async def __call__(self, data: IN_DATA) -> OUT_DATA:
        raise NotImplementedError
