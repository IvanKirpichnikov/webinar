from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CountHomeWorkDTO:
    smm: int = 0
    copyrighting: int = 0
