from dataclasses import dataclass

import toml
from adaptix import (
    Chain,
    loader,
    P,
    Retort
)
from orjson import loads

from webinar.application.schemas.types import (
    TelegramChatId,
    TelegramUserId
)


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
    owner_chat_id: TelegramChatId
    owner_user_id: TelegramUserId
    count_webinars_button: int
    count_homeworks: int
    count_homeworks_in_pagination: int


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
        self._cache_config = None
        self.retort = Retort(
            recipe=[
                loader(P[_GoogleSheetsConfig].data, loads, Chain.FIRST),
            ],
        )
    
    @property
    def config(self) -> _Config:
        if self._cache_config is not None:
            return self._cache_config
        
        raw_data = toml.load("configs/config.toml")
        data = self.retort.load(raw_data, _Config)
        self._cache_config = data
        
        return data
