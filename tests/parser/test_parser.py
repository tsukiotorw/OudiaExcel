"""
Parserのテスト
"""
from src.models.railway import Railway, Direction
from src.models.station import Station
from src.models.diagram import Diagram
from src.models.train import Train
from src.models.train_type import TrainType
from src.models.operation import Operation

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
                name="Eki",
                key_values=[
                    KeyValueToken(
                        line_number=4,
                        raw_line="Ekimei=東京",
                        key="Ekimei",
                        value="東京",
                    )
                ],
            ),
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
                                    ),
                                    KeyValueToken(
                                        line_number=8,
                                        raw_line="EkiJikoku=1;500$0",
                                        key="EkiJikoku",
                                        value="1;500$0",
                                    ),
                                    KeyValueToken(
                                        line_number=9,
                                        raw_line="Operation14B=5/$",
                                        key="Operation14B",
                                        value="5/$",
                                    ),
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

    assert train.train_type_index == 0

    assert len(train.stop_times) == 1

    stop_time = train.stop_times[0]

    assert stop_time.station.name == "東京"
    assert stop_time.order == 0
    assert stop_time.departure_time == "500"
    assert stop_time.arrival_time is None
    assert stop_time.is_pass is False
    assert stop_time.track_index == 0

    assert len(train.operations) == 1

    operation = train.operations[0]

    assert operation.name == "Operation14B"
    assert operation.value == "5/$"


def test_parse_train_types():
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
            ),
            SectionNode(
                line_number=4,
                name="Ressyasyubetsu",
                key_values=[
                    KeyValueToken(
                        line_number=5,
                        raw_line="Syubetsumei=貨物",
                        key="Syubetsumei",
                        value="貨物",
                    ),
                    KeyValueToken(
                        line_number=6,
                        raw_line="Ryakusyou=貨",
                        key="Ryakusyou",
                        value="貨",
                    )
                ]
            )
        ],
    )

    parser = Parser()

    railway = parser.parse(root)

    assert len(railway.train_types) == 1

    train_type = railway.train_types[0]

    assert train_type.index == 0
    assert train_type.name == "貨物"
    assert train_type.short_name == "貨"
