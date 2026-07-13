from __future__ import annotations

from dataclasses import dataclass, field

from .tokens import KeyValueToken


@dataclass
class SectionNode:
    """
    Section構造を表すノード。
    """

    line_number: int
    name: str

    key_values: list[KeyValueToken] = field(default_factory=list)

    children: list["SectionNode"] = field(default_factory=list)
    