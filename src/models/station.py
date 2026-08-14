from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Station:
    index: int
    name: str
