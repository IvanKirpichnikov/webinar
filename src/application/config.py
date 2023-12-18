from dataclasses import dataclass

from adaptix import Chain, loader, P, Retort
from orjson import orjson
from toml import load


@dataclass(frozen=True, slots=True)
class _BotConfig:
    token: str


@dataclass(frozen=True, slots=True)
class _PSQLConfig:
    url: str


@dataclass(frozen=True, slots=True)
class _GoogleSheetsConfig:
    data: dict[str, str]
    url: str


@dataclass(frozen=True, slots=True)
class _NATSConfig:
    url: str


@dataclass(frozen=True, slots=True)
class _ConstConfig:
    admin_chat_id: int
    owner_user_id: int
    count_webinars_button: int


@dataclass(frozen=True, slots=True)
class _Config:
    bot: _BotConfig
    psql: _PSQLConfig
    nats: _NATSConfig
    google_sheets: _GoogleSheetsConfig
    const: _ConstConfig


class ConfigFactory:
    retort: Retort
    _cache_config: _Config | None
    
    def __init__(self) -> None:
        self.retort = Retort(
            recipe=[
                loader(P[_GoogleSheetsConfig].data, orjson.loads, Chain.FIRST),
            ],
        )
        self._cache_config = None
    
    @property
    def config(self) -> _Config:
        if self._cache_config is not None:
            return self._cache_config
        
        raw_data = load('configs/config.toml')
        data = self.retort.load(raw_data, _Config)
        self._cache_config = data
        
        return data
