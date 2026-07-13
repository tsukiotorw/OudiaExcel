"""
Tokenizerで使用するTokenを定義します。

責務:
    - Tokenクラスの定義
    - Tokenの種類を定義する

このモジュールはTokenの定義のみを担当します。
TokenizerやParserの処理は含みません。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    """
    Tokenの基底クラス。

    Attributes:
        line_number:
            元ファイルの行番号（1始まり）
        raw_line:
            元の行文字列（改行除去後）
    """

    line_number: int
    raw_line: str


@dataclass(frozen=True)
class KeyValueToken(Token):
    """
    key=value形式のToken。

    Example:
        Name=中央線
    """

    key: str
    value: str


@dataclass(frozen=True)
class SectionStartToken(Token):
    """
    セクション開始Token。

    Example:
        Eki.
        Ressya.
        Dia.
    """

    name: str


@dataclass(frozen=True)
class SectionEndToken(Token):
    """
    セクション終了Token。

    Example:
        .
    """


@dataclass(frozen=True)
class BlankToken(Token):
    """
    空行Token。
    """


@dataclass(frozen=True)
class CommentToken(Token):
    """
    コメントToken。

    OudiaSecondにコメント構文が存在する場合のみ使用する。
    現段階では未使用。
    """
