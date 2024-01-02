from dataclasses import dataclass, field

from webinar.application.schemas.types import DataBaseId


@dataclass(frozen=True, slots=True)
class WebinarEntity:
    db_id: DataBaseId
    url: str
    name: str


@dataclass(slots=True)
class WebinarEntities:
    webinars: list[WebinarEntity]
    count: int = field(init=False)

    def __post_init__(self) -> None:
        self.count = len(self.webinars)
