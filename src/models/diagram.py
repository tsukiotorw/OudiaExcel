from __future__ import annotations

from dataclasses import dataclass, field

from .railway import Direction
from .train import Train


@dataclass(slots=True)
class Diagram:
    name: str
    direction: Direction
    trains: list[Train] = field(default_factory=list)
