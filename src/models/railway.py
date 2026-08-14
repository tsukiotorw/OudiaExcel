from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from .train_type import TrainType


class Direction(StrEnum):
    UP = "up"
    DOWN = "down"


@dataclass(slots=True)
class Railway:
    name: str
    stations: list["Station"] = field(default_factory=list)
    train_types: list[TrainType] = field(default_factory=list)
    diagrams: list["Diagram"] = field(default_factory=list)
