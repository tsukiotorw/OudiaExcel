"""
Tokenizer層: SourceFileをToken列へ変換します。

責務:
    - SourceFileを受け取る
    - Token列を生成する

構文解析のみを担当します。
"""

from __future__ import annotations

from .reader import SourceFile
from .tokens import (
    BlankToken,
    KeyValueToken,
    SectionEndToken,
    SectionStartToken,
    Token,
)


class TokenizerError(Exception):
    """Tokenizer層で発生する例外。"""

def tokenize(source: SourceFile) -> list[Token]:
    """SourceFileをToken列へ変換します。"""

    tokens: list[Token] = []

    for line_number, raw_line in enumerate(source.lines, start=1):
        token = _tokenize_line(
            line_number=line_number,
            raw_line=raw_line,
        )
        tokens.append(token)

    return tokens

def _tokenize_line(
    line_number: int,
    raw_line: str,
) -> Token:
    """1行をTokenへ変換します。"""

    line = raw_line.rstrip("\r\n")

    if line == "":
        return BlankToken(
            line_number=line_number,
            raw_line=line,
        )
    
    if line == ".":
        return SectionEndToken(
        line_number=line_number,
        raw_line=line,
    )

    if line.endswith("."):
        return SectionStartToken(
            line_number=line_number,
            raw_line=line,
            name=line[:-1],
        )
    
    if "=" in line:
        key, value = line.split("=", 1)

        return KeyValueToken(
            line_number=line_number,
            raw_line=line,
            key=key,
            value=value,
        )

    raise TokenizerError(
        f"{line_number}行目: 未知の構文です: {line}"
    )


