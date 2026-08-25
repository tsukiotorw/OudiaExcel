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


def test_build_sections_ignores_file_level_key_values() -> None:
    """Section外のファイルレベルKeyValueを無視できること。"""

    tokens = [
        KeyValueToken(
            line_number=1,
            raw_line="FileType=OuDiaSecond.1.16",
            key="FileType",
            value="OuDiaSecond.1.16",
        ),
        SectionStartToken(
            line_number=2,
            raw_line="Rosen.",
            name="Rosen",
        ),
        KeyValueToken(
            line_number=3,
            raw_line="Name=中央線",
            key="Name",
            value="中央線",
        ),
        SectionEndToken(
            line_number=4,
            raw_line=".",
        ),
        KeyValueToken(
            line_number=5,
            raw_line="FileTypeAppComment=OuDiaSecondV2 Ver. 2.06.20",
            key="FileTypeAppComment",
            value="OuDiaSecondV2 Ver. 2.06.20",
        ),
    ]

    root = build_sections(tokens)

    assert root.name == "Rosen"
    assert len(root.key_values) == 1
    assert root.key_values[0].key == "Name"
    assert root.key_values[0].value == "中央線"


def test_build_sections_uses_rosen_as_root() -> None:
    """トップレベルのRosenをrootとして、それ以外を無視すること。"""

    tokens = [
        KeyValueToken(
            1,
            "FileType=OuDiaSecond.1.16",
            "FileType",
            "OuDiaSecond.1.16",
        ),
        SectionStartToken(2, "Rosen.", "Rosen"),
        KeyValueToken(3, "Name=中央線", "Name", "中央線"),
        SectionStartToken(4, "Eki.", "Eki"),
        KeyValueToken(5, "Ekimei=東京", "Ekimei", "東京"),
        SectionEndToken(6, "."),
        SectionEndToken(7, "."),
        SectionStartToken(8, "DispProp.", "DispProp"),
        KeyValueToken(9, "XPos=123", "XPos", "123"),
        SectionEndToken(10, "."),
        SectionStartToken(11, "WindowPlacement.", "WindowPlacement"),
        SectionStartToken(12, "ChildWindow.", "ChildWindow"),
        KeyValueToken(13, "Name=test", "Name", "test"),
        SectionEndToken(14, "."),
        SectionEndToken(15, "."),
    ]

    root = build_sections(tokens)

    assert root.name == "Rosen"
    assert root.key_values[0].key == "Name"
    assert len(root.children) == 1
    assert root.children[0].name == "Eki"


def test_build_sections_requires_rosen_root() -> None:
    """Rosen Sectionが存在しない場合はエラーになること。"""

    tokens = [
        SectionStartToken(1, "DispProp.", "DispProp"),
        SectionEndToken(2, "."),
    ]

    with pytest.raises(SectionBuilderError):
        build_sections(tokens)

