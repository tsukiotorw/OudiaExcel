"""
Parserのテスト
"""

from src.models.railway import (
    Diagram,
    Direction,
    Railway,
    Station,
)
from src.parser.parser import Parser
from src.parser.section import SectionNode
from src.parser.tokens import KeyValueToken


def test_parse_railway_name() -> None:
    """
    Railway名を取得できること。
    """

    root = SectionNode(
        line_number=1,
        name="Rosen",
        key_values=[
            KeyValueToken(
                line_number=2,
                raw_line="Name=中央線",
                key="Name",
                value="中央線",
            )
        ],
    )

    parser = Parser()

    railway = parser.parse(root)

    assert isinstance(railway, Railway)
    assert railway.name == "中央線"


def test_parse_station() -> None:
    """
    Stationを生成できること。
    """

    root = SectionNode(
        line_number=1,
        name="Rosen",
        key_values=[
            KeyValueToken(
                line_number=2,
                raw_line="Name=中央線",
                key="Name",
                value="中央線",
            )
        ],
        children=[
            SectionNode(
                line_number=3,
                name="Eki",
                key_values=[
                    KeyValueToken(
                        line_number=4,
                        raw_line="Ekimei=東京",
                        key="Ekimei",
                        value="東京",
                    )
                ],
            )
        ],
    )

    parser = Parser()

    railway = parser.parse(root)

    assert len(railway.stations) == 1

    station = railway.stations[0]

    assert isinstance(station, Station)
    assert station.index == 0
    assert station.name == "東京"


def test_parse_diagrams() -> None:
    """
    Diaから上下2つのDiagramを生成できること。
    """

    root = SectionNode(
        line_number=1,
        name="Rosen",
        key_values=[
            KeyValueToken(
                line_number=2,
                raw_line="Name=中央線",
                key="Name",
                value="中央線",
            )
        ],
        children=[
            SectionNode(
                line_number=3,
                name="Dia",
                key_values=[
                    KeyValueToken(
                        line_number=4,
                        raw_line="DiaName=平日",
                        key="DiaName",
                        value="平日",
                    )
                ],
                children=[
                    SectionNode(
                        line_number=5,
                        name="Kudari",
                    ),
                    SectionNode(
                        line_number=6,
                        name="Nobori",
                    ),
                ],
            )
        ],
    )

    parser = Parser()

    railway = parser.parse(root)

    assert len(railway.diagrams) == 2

    assert railway.diagrams[0].name == "平日"
    assert railway.diagrams[0].direction == Direction.DOWN

    assert railway.diagrams[1].name == "平日"
    assert railway.diagrams[1].direction == Direction.UP


def test_parse_train() -> None:
    """
    RessyaからTrainを生成できること。
    """

    root = SectionNode(
        line_number=1,
        name="Rosen",
        key_values=[
            KeyValueToken(
                line_number=2,
                raw_line="Name=中央線",
                key="Name",
                value="中央線",
            )
        ],
        children=[
            SectionNode(
                line_number=3,
                name="Dia",
                key_values=[
                    KeyValueToken(
                        line_number=4,
                        raw_line="DiaName=平日",
                        key="DiaName",
                        value="平日",
                    )
                ],
                children=[
                    SectionNode(
                        line_number=5,
                        name="Kudari",
                        children=[
                            SectionNode(
                                line_number=6,
                                name="Ressya",
                                key_values=[
                                    KeyValueToken(
                                        line_number=7,
                                        raw_line="Syubetsu=0",
                                        key="Syubetsu",
                                        value="0",
                                    )
                                ],
                            )
                        ],
                    )
                ],
            )
        ],
    )

    railway = Parser().parse(root)

    assert len(railway.diagrams) == 1

    diagram = railway.diagrams[0]

    assert len(diagram.trains) == 1

    train = diagram.trains[0]

    assert train.train_type == "0"
