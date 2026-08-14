from __future__ import annotations

from dataclasses import dataclass, field

from .operation import Operation
from .stop_time import StopTime


@dataclass(slots=True)
class Train:
    number: str
    train_type_index: int
    stop_times: list[StopTime] = field(default_factory=list)
    operations: list[Operation] = field(default_factory=list)
