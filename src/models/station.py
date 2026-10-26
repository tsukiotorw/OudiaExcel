
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Station:
    """路線上の駅。"""

    index: int
    name: str
    short_name: str = ""
    is_no_mark: bool = False

    @property
    def display_name(self) -> str:
        """略称が設定されていれば略称、なければ正式名称を返す。"""
        return self.short_name or self.name
