from dataclasses import dataclass, field

from webinar.domain.types import DataBaseId


@dataclass(frozen=True, slots=True)
class Webinar:
    db_id: DataBaseId
    url: str
    name: str


@dataclass(slots=True)
class Webinars:
    webinars: list[Webinar]
    count: int = field(init=False)

    def __post_init__(self) -> None:
        self.count = len(self.webinars)
