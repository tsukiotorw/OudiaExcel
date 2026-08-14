from __future__ import annotations

from dataclasses import dataclass, field

from .diagram import Diagram
from .station import Station
from .train_type import TrainType


@dataclass(slots=True)
class Railway:
    name: str
    stations: list[Station] = field(default_factory=list)
    train_types: list[TrainType] = field(default_factory=list)
    diagrams: list[Diagram] = field(default_factory=list)
