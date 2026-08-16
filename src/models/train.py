from __future__ import annotations

from dataclasses import dataclass, field

from .operation import OperationRecord
from .stop_time import StopTime


@dataclass(slots=True)
class Train:
    number: str
    train_type_index: int
    stop_times: list[StopTime] = field(default_factory=list)
    operations: list[OperationRecord] = field(default_factory=list)
