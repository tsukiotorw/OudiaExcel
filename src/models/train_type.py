from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TrainType:
    index: int
    name: str
    short_name: str = ""
