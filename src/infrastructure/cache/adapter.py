from cachetools import TTLCache


class CacheAdapter:
    check_user: TTLCache
    user_is_admin: TTLCache
    
    def __init__(self) -> None:
        self.check_user = TTLCache(10000, 10)
        self.user_is_admin = TTLCache(1000, 100)
