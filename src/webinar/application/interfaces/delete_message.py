from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol, TypeVar


IN_DATA = TypeVar('IN_DATA', contravariant=True)
OUT_DATA = TypeVar('OUT_DATA', covariant=True)


class DeleteMessage(Protocol[IN_DATA, OUT_DATA]):
    @abstractmethod
    async def __call__(self, data: IN_DATA) -> OUT_DATA:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class DeleteMessageData:
    chat_id: int
    message_id: list[int] | int
    inline_message_id: int | None = None


class TgDeleteMessage(DeleteMessage[DeleteMessageData, None], Protocol):
    pass
