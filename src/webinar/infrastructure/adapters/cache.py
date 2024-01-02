from typing import MutableMapping

from cachetools import TTLCache

from webinar.application.schemas.dto.common import ResultExistsDTO
from webinar.application.schemas.types import TelegramUserId


class CacheStore:
    exists_user: MutableMapping[TelegramUserId, ResultExistsDTO]
    exists_admin: MutableMapping[TelegramUserId, ResultExistsDTO]

    __slots__ = ("exists_user", "exists_admin")

    def __init__(self) -> None:
        self.exists_user = TTLCache(16384, 256)
        self.exists_admin = TTLCache(4096, 128)
