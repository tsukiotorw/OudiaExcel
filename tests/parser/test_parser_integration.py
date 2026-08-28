"""実データを使ったParser統合テスト。"""

from pathlib import Path

from src.parser.reader import read_file
from src.parser.tokenizer import tokenize
from src.parser.section_builder import build_sections
from src.parser.parser import Parser
from src.models.railway import Direction


EXAMPLE_FILE = (
    Path(__file__).resolve().parents[2]
    / "examples"
    / "解析用.oud2"
)


def test_parse_real_oud2_file() -> None:
    """実際の.oud2ファイルをReaderからParserまで通して解析できること。"""

    source = read_file(EXAMPLE_FILE)

    assert source.encoding == "utf-8-sig"

    tokens = tokenize(source)

    assert len(tokens) == len(source.lines)

    root = build_sections(tokens)

    assert root.name == "Rosen"

    railway = Parser().parse(root)

    assert len(railway.stations) == 4

    assert [
        (station.index, station.name)
        for station in railway.stations
    ] == [
        (0, "A"),
        (1, "B"),
        (2, "C"),
        (3, "D"),
    ]

    assert len(railway.train_types) == 2

    assert [
        (train_type.index, train_type.name, train_type.short_name)
        for train_type in railway.train_types
    ] == [
        (0, "普通", ""),
        (1, "快速", "快"),
    ]

    assert len(railway.diagrams) == 2

    assert [
        (diagram.name, diagram.direction)
        for diagram in railway.diagrams
    ] == [
        ("検証用", Direction.DOWN),
        ("検証用", Direction.UP),
    ]

    train_count = sum(
        len(diagram.trains)
        for diagram in railway.diagrams
    )

    assert train_count == 16

    assert len(railway.diagrams[0].trains) == 10
    assert len(railway.diagrams[1].trains) == 6

    assert all(
        train.train_type_index == 0
        for train in railway.diagrams[0].trains
    )

    assert all(
        train.train_type_index == 1
        for train in railway.diagrams[1].trains
    )

    assert all(
        len(train.stop_times) == 4
        for diagram in railway.diagrams
        for train in diagram.trains
    )

    operation_count = sum(
        len(train.operations)
        for diagram in railway.diagrams
        for train in diagram.trains
    )

    assert operation_count > 0
