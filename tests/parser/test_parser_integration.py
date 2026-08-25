"""実データを使ったParser統合テスト。"""

from pathlib import Path

from src.parser.reader import read_file
from src.parser.tokenizer import tokenize
from src.parser.section_builder import build_sections
from src.parser.parser import Parser


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
    assert len(railway.train_types) == 2
    assert len(railway.diagrams) == 2

    train_count = sum(
        len(diagram.trains)
        for diagram in railway.diagrams
    )

    assert train_count == 16

    operation_count = sum(
        len(train.operations)
        for diagram in railway.diagrams
        for train in diagram.trains
    )

    assert operation_count > 0
