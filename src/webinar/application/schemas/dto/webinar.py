from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateWebinarDTO:
    url: str
    name: str


@dataclass(frozen=True, slots=True)
class PaginationWebinarDTO:
    limit: int
    offset: int
