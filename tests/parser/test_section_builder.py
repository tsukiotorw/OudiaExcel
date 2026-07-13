"""
SectionBuilderのテスト
"""
from pathlib import Path

import pytest

from src.parser.section_builder import (
    SectionBuilderError,
    build_sections,
)
from src.parser.tokens import (
    KeyValueToken,
    SectionEndToken,
    SectionStartToken,
)


def test_build_single_section() -> None:
    tokens = [
        SectionStartToken(1, "Rosen.", "Rosen"),
        KeyValueToken(2, "Name=中央線", "Name", "中央線"),
        SectionEndToken(3, "."),
    ]

    root = build_sections(tokens)

    assert root.name == "Rosen"
    assert len(root.key_values) == 1
    assert len(root.children) == 0

def test_build_child_section() -> None:
    tokens = [
        SectionStartToken(1, "Rosen.", "Rosen"),
        SectionStartToken(2, "Eki.", "Eki"),
        KeyValueToken(3, "Ekimei=東京", "Ekimei", "東京"),
        SectionEndToken(4, "."),
        SectionEndToken(5, "."),
    ]

    root = build_sections(tokens)

    assert len(root.children) == 1

    eki = root.children[0]

    assert eki.name == "Eki"
    assert eki.key_values[0].value == "東京"

def test_build_multiple_child_sections() -> None:
    tokens = [
        SectionStartToken(1, "Rosen.", "Rosen"),
        SectionStartToken(2, "Eki.", "Eki"),
        KeyValueToken(3, "Ekimei=東京", "Ekimei", "東京"),
        SectionEndToken(4, "."),
        SectionStartToken(5, "Eki.", "Eki"),
        KeyValueToken(6, "Ekimei=新宿", "Ekimei", "新宿"),
        SectionEndToken(7, "."),
        SectionEndToken(8, "."),
    ]

    root = build_sections(tokens)

    assert len(root.children) == 2

    assert root.children[0].name == "Eki"
    assert root.children[1].name == "Eki"


def test_section_not_closed() -> None:
    tokens = [
        SectionStartToken(1, "Rosen.", "Rosen"),
        KeyValueToken(2, "Name=中央線", "Name", "中央線"),
    ]
    with pytest.raises(SectionBuilderError):
        build_sections(tokens)

def test_section_end_without_start() -> None:
    tokens = [
        SectionEndToken(1, "."),
    ]

    with pytest.raises(SectionBuilderError):
        build_sections(tokens)
