"""
Tokenizerのテスト
"""

from pathlib import Path

import pytest

from src.parser.reader import SourceFile
from src.parser.tokenizer import TokenizerError, tokenize
from src.parser.tokens import (
    BlankToken,
    KeyValueToken,
    SectionEndToken,
    SectionStartToken,
)


def create_source(*lines: str) -> SourceFile:
    """
    テスト用のSourceFileを生成します。
    """

    return SourceFile(
        lines=list(lines),
        encoding="utf-8",
        path=Path("dummy.oud2"),
    )


def test_key_value_token() -> None:
    """
    key=value が KeyValueToken になること。
    """

    source = create_source(
        "Name=中央線\n",
    )

    tokens = tokenize(source)

    assert len(tokens) == 1

    token = tokens[0]

    assert isinstance(token, KeyValueToken)
    assert token.key == "Name"
    assert token.value == "中央線"


def test_section_start() -> None:
    """
    Section開始を認識できること。
    """

    source = create_source(
        "Eki.\n",
    )

    tokens = tokenize(source)

    assert len(tokens) == 1

    token = tokens[0]

    assert isinstance(token, SectionStartToken)
    assert token.name == "Eki"


def test_section_end() -> None:
    """
    Section終了を認識できること。
    """

    source = create_source(
        ".\n",
    )

    tokens = tokenize(source)

    assert len(tokens) == 1

    token = tokens[0]

    assert isinstance(token, SectionEndToken)


def test_blank() -> None:
    """
    空行を認識できること。
    """

    source = create_source(
        "\n",
    )

    tokens = tokenize(source)

    assert len(tokens) == 1

    token = tokens[0]

    assert isinstance(token, BlankToken)


def test_invalid_line() -> None:
    """
    不正な行はTokenizerErrorになること。
    """

    source = create_source(
        "????????\n",
    )

    with pytest.raises(TokenizerError):
        tokenize(source)
