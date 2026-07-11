from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Optional


class Direction(StrEnum):
    UP = "up"
    DOWN = "down"


@dataclass
class Railway:
    name: str
    stations: list["Station"] = field(default_factory=list)
    diagrams: list["Diagram"] = field(default_factory=list)


@dataclass
class Station:
    index: int
    name: str


@dataclass
class Train:
    number: str
    train_type: str
    stop_times: list["StopTime"] = field(default_factory=list)


@dataclass
class StopTime:
    station: "Station"
    order: int
    arrival_time: Optional[str] = None
    departure_time: Optional[str] = None
    is_pass: bool = False


@dataclass
class Diagram:
    name: str
    direction: Direction
    trains: list["Train"] = field(default_factory=list)
