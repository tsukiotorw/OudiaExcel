from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Operation:
    """
    OuDiaSecond独自の運転操作。

    現在はParserでは生文字列のみ保持する。
    詳細な構造化はOperationParserで実施予定。
    """

    name: str
    value: str
