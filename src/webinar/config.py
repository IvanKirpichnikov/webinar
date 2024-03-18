from dataclasses import dataclass

import toml
from adaptix import (
    Chain,
    loader,
    P,
    Retort,
)
from orjson import loads

from webinar.domain.types import (
    TgChatId,
    TgUserId,
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
    owner_chat_id: TgChatId
    owner_user_id: TgUserId
    count_webinars_button: int
    count_homeworks: int
    count_homeworks_in_pagination: int


@dataclass(frozen=True, slots=True)
class Config:
    bot: _BotConfig
    psql: _PSQLConfig
    nats: _NATSConfig
    google_sheets: _GoogleSheetsConfig
    const: _ConstConfig


class ConfigFactory:
    _cache_config: Config | None = None
    retort = Retort(
        recipe=[
            loader(P[_GoogleSheetsConfig].data, loads, Chain.FIRST),
        ],
    )
    
    @property
    def config(self) -> Config:
        if self._cache_config is not None:
            return self._cache_config
        
        raw_data = toml.load("configs/config.toml")
        data = self.retort.load(raw_data, Config)
        self._cache_config = data
        
        return data
