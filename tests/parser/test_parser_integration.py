"""実データを使ったParser統合テスト。"""

from src.parser.reader import read_file
from src.parser.tokenizer import tokenize
from src.parser.section_builder import build_sections
from src.models.railway import Direction
from src.models.railway import Railway

from src.models.operation import (
    OperationType,
    OutInDetail,
    NumberChangeDetail,
    JunctionDetail,
    ConnectDetail,
    ReleaseDetail,
    ShuntDetail
)


def test_parse_real_oud2_file(parsed_railway: Railway) -> None:
    """実データの.oud2ファイルを最後まで正常に解析できること。"""
    assert parsed_railway.stations
    assert parsed_railway.train_types
    assert parsed_railway.diagrams


def test_parse_real_oud2_stations(parsed_railway: Railway) -> None:
    """実データから駅が正しく解析されること。"""
    assert len(parsed_railway.stations) == 4

    expected = [
        (0, "A"),
        (1, "B"),
        (2, "C"),
        (3, "D"),
    ]

    for station, (index, name) in zip(
        parsed_railway.stations,
        expected,
    ):
        assert station.index == index
        assert station.name == name


def test_parse_real_oud2_train_types(parsed_railway: Railway) -> None:
    """実データから列車種別が正しく解析されること。"""

    assert len(parsed_railway.train_types) == 2

    expected = [
        (0, "普通", ""),
        (1, "快速", "快"),
    ]

    for train_type, (index, name, short_name) in zip(
        parsed_railway.train_types,
        expected,
    ):
        assert train_type.index == index
        assert train_type.name == name
        assert train_type.short_name == short_name


def test_parse_real_oud2_diagrams(parsed_railway: Railway) -> None:
    """実データからダイヤが正しく解析されること。"""

    assert len(parsed_railway.diagrams) == 2

    expected = [
        (Direction.DOWN, "検証用", 10),
        (Direction.UP, "検証用", 6),
    ]

    for diagram, (direction, name, train_count) in zip(
        parsed_railway.diagrams,
        expected,
    ):
        assert diagram.direction == direction
        assert diagram.name == name
        assert len(diagram.trains) == train_count


def test_parse_real_oud2_trains(parsed_railway: Railway) -> None:
    """実データから列車が正しく解析されること。"""


    down = parsed_railway.diagrams[0]
    up = parsed_railway.diagrams[1]

    assert down.direction == Direction.DOWN
    assert up.direction == Direction.UP

    assert len(down.trains) == 10
    assert len(up.trains) == 6

    for train in down.trains:
        assert train.train_type_index == 0

    for train in up.trains:
        assert train.train_type_index == 1


def test_parse_real_oud2_down_train_stop_times(parsed_railway: Railway) -> None:
    """実データの下り列車の駅時刻が正しく解析されること。"""

    # StopTimes: DOWN train 0
    train = parsed_railway.diagrams[0].trains[0]

    assert len(train.stop_times) == 4

    expected = [
        (0, 0, "A", None, None, False, None),
        (1, 1, "B", None, None, False, None),
        (2, 2, "C", None, "000", False, 0),
        (3, 3, "D", "023", None, False, 0),
    ]

    for stop_time, (
        order,
        station_index,
        station_name,
        arrival_time,
        departure_time,
        is_pass,
        track_index,
    ) in zip(train.stop_times, expected):
        assert stop_time.order == order
        assert stop_time.station.index == station_index
        assert stop_time.station.name == station_name
        assert stop_time.arrival_time == arrival_time
        assert stop_time.departure_time == departure_time
        assert stop_time.is_pass == is_pass
        assert stop_time.track_index == track_index

    # StopTimes: DOWN train 1
    train = parsed_railway.diagrams[0].trains[1]

    assert len(train.stop_times) == 4

    expected = [
        (0, 0, "A", None, "000", False, 0),
        (1, 1, "B", "005", "006", False, 0),
        (2, 2, "C", "009", "015", False, 0),
        (3, 3, "D", "025", None, False, 0),
    ]

    for stop_time, (
        order,
        station_index,
        station_name,
        arrival_time,
        departure_time,
        is_pass,
        track_index,
    ) in zip(train.stop_times, expected):
        assert stop_time.order == order
        assert stop_time.station.index == station_index
        assert stop_time.station.name == station_name
        assert stop_time.arrival_time == arrival_time
        assert stop_time.departure_time == departure_time
        assert stop_time.is_pass == is_pass
        assert stop_time.track_index == track_index


def test_parse_real_oud2_up_train_stop_times(parsed_railway: Railway) -> None:
    """実データの上り列車の駅時刻が正しく解析されること。"""

    # UP train 0
    train = parsed_railway.diagrams[1].trains[0]

    expected = [
        (0, 0, "A", None, "030", False, 0),
        (1, 1, "B", None, None, True, 1),
        (2, 2, "C", None, None, True, 1),
        (3, 3, "D", "100", None, False, 1),
    ]

    assert len(train.stop_times) == len(expected)

    for stop_time, (
        order,
        station_index,
        station_name,
        arrival_time,
        departure_time,
        is_pass,
        track_index,
    ) in zip(train.stop_times, expected):
        assert stop_time.order == order
        assert stop_time.station.index == station_index
        assert stop_time.station.name == station_name
        assert stop_time.arrival_time == arrival_time
        assert stop_time.departure_time == departure_time
        assert stop_time.is_pass == is_pass
        assert stop_time.track_index == track_index


def test_parse_real_oud2_operations(parsed_railway: Railway) -> None:
    """実データのOperationが正しく解析されること。"""

    # Operation Type 0: Shunt
    train = parsed_railway.diagrams[0].trains[6]

    record = next(
        record
        for record in train.operations
        if record.order == 3
    )

    operation = record.operations[0]

    assert operation.type == OperationType.SHUNT
    assert isinstance(operation.detail, ShuntDetail)

    detail = operation.detail

    assert detail.linked_track_index == 0
    assert detail.departure_time == "555"
    assert detail.arrival_time == "600"
    assert detail.show_arrival is False


    # Operation Type 1: Connect
    train = parsed_railway.diagrams[0].trains[7]

    record = next(
        record
        for record in train.operations
        if record.order == 3
    )

    operation = record.operations[0]

    assert operation.type == OperationType.CONNECT
    assert isinstance(operation.detail, ConnectDetail)

    detail = operation.detail

    assert detail.connect_position == 0
    assert detail.connect_time == "655"

    assert len(operation.before_children) == 1
    assert len(operation.after_children) == 0

    before_child = operation.before_children[0]

    assert before_child.type == OperationType.JUNCTION
    assert isinstance(before_child.detail, JunctionDetail)
    assert before_child.detail.time is None
    assert before_child.detail.value is None


    # Operation Type 2: Release
    train = parsed_railway.diagrams[0].trains[8]

    record = next(
        record
        for record in train.operations
        if record.order == 3
    )

    operation = record.operations[0]

    assert operation.type == OperationType.RELEASE
    assert isinstance(operation.detail, ReleaseDetail)

    detail = operation.detail

    assert detail.release_position == 0
    assert detail.release_count == 1
    assert detail.release_time == "755"

    assert len(operation.before_children) == 0
    assert len(operation.after_children) == 1

    after_child = operation.after_children[0]

    assert after_child.type == OperationType.JUNCTION
    assert isinstance(after_child.detail, JunctionDetail)
    assert after_child.detail.time is None
    assert after_child.detail.value == "0"


    # Operation Type 3: OutIn
    train = parsed_railway.diagrams[0].trains[0]

    record = next(
        record
        for record in train.operations
        if record.order == 2
    )

    operation = record.operations[0]

    assert operation.type == OperationType.OUT_IN
    assert isinstance(operation.detail, OutInDetail)

    detail = operation.detail

    assert detail.time == "2359"
    assert detail.train_number == "901"

    assert len(operation.before_children) == 0
    assert len(operation.after_children) == 0


    # Operation Type 5: Junction
    train = parsed_railway.diagrams[0].trains[1]

    record = next(
        record
        for record in train.operations
        if record.order == 3
    )

    operation = record.operations[0]

    assert operation.type == OperationType.JUNCTION
    assert isinstance(operation.detail, JunctionDetail)

    detail = operation.detail

    assert detail.time is None
    assert detail.value == "0"

    assert len(operation.before_children) == 0
    assert len(operation.after_children) == 0


    # Operation Type 6: NumberChange
    train = parsed_railway.diagrams[0].trains[0]

    record = next(
        record
        for record in train.operations
        if record.order == 3
    )

    operation = record.operations[0]

    assert operation.type == OperationType.NUMBER_CHANGE
    assert isinstance(operation.detail, NumberChangeDetail)

    detail = operation.detail

    assert detail.train_number == "ZZZ"

    assert len(operation.before_children) == 0
    assert len(operation.after_children) == 0
