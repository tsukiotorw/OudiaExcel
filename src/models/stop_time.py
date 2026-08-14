from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .station import Station


@dataclass(slots=True)
class StopTime:
    station: Station
    order: int

    arrival_time: Optional[str]
    departure_time: Optional[str]

    is_pass: bool

    # OuDiaSecond独自
    track_index: int | None = None
