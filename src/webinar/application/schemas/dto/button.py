from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BackButtonDataDTO:
    text: str
    callback_data: str
