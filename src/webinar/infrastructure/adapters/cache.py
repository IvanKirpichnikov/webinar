from typing import MutableMapping

from cachetools import TTLCache

from webinar.application.dto.common import ResultExistsDTO
from webinar.domain.types import TgUserId


class CacheStore:
    exists_user: MutableMapping[TgUserId, ResultExistsDTO]
    exists_admin: MutableMapping[TgUserId, ResultExistsDTO]
    
    __slots__ = ("exists_user", "exists_admin")
    
    def __init__(self) -> None:
        self.exists_user = TTLCache(16384, 256)
        self.exists_admin = TTLCache(4096, 128)
