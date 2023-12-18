from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Webinar:
    id: int
    url: str
    name: str


@dataclass(frozen=True, slots=True)
class AddWebinarDTO:
    url: str
    name: str
