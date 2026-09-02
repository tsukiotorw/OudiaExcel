from __future__ import annotations

from dataclasses import dataclass

from src.models.train_type import TrainType


@dataclass(frozen=True)
class TimetableEntry:
    """駅時刻表に掲載する列車情報。"""

    minute: int
    destination: str
    train_type: TrainType
    train_number: str


@dataclass(frozen=True)
class TimetableHour:
    """駅時刻表の1時間分。"""

    hour: int
    entries: list[TimetableEntry]


@dataclass(frozen=True)
class StationTimetable:
    """1駅分の駅時刻表。"""

    station_name: str
    down: list[TimetableHour]
    up: list[TimetableHour]

