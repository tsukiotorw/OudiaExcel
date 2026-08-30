"""実データを使ったParser統合テスト。"""

from pathlib import Path

from src.parser.reader import read_file
from src.parser.tokenizer import tokenize
from src.parser.section_builder import build_sections
from src.parser.parser import Parser
from src.models.railway import Direction

from src.models.operation import (
    OperationType,
    OutInDetail,
    NumberChangeDetail,
    JunctionDetail,
    ConnectDetail,
    ReleaseDetail
)


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

    # ここに確認用のコードを入れる
    # ここまで

    # Stations
    assert len(railway.stations) == 4

    expected_stations = [
        (0, "A"),
        (1, "B"),
        (2, "C"),
        (3, "D"),
    ]

    for station, (expected_index, expected_name) in zip(
        railway.stations,
        expected_stations,
    ):
        assert station.index == expected_index
        assert station.name == expected_name


    assert [
        (station.index, station.name)
        for station in railway.stations
    ] == [
        (0, "A"),
        (1, "B"),
        (2, "C"),
        (3, "D"),
    ]

    # TrainTypes
    assert len(railway.train_types) == 2

    expected_train_types = [
        (0, "普通", ""),
        (1, "快速", "快"),
    ]

    for train_type, (
        expected_index,
        expected_name,
        expected_short_name,
    ) in zip(
        railway.train_types,
        expected_train_types,
    ):
        assert train_type.index == expected_index
        assert train_type.name == expected_name
        assert train_type.short_name == expected_short_name


    # Diagrams
    assert len(railway.diagrams) == 2

    down = railway.diagrams[0]
    assert down.name == "検証用"
    assert down.direction == Direction.DOWN
    assert len(down.trains) == 10

    up = railway.diagrams[1]
    assert up.name == "検証用"
    assert up.direction == Direction.UP
    assert len(up.trains) == 6


    train_count = sum(
        len(diagram.trains)
        for diagram in railway.diagrams
    )

    assert train_count == 16

    # Trains
    down_trains = railway.diagrams[0].trains
    up_trains = railway.diagrams[1].trains

    assert len(down_trains) == 10
    assert len(up_trains) == 6

    for train in down_trains:
        assert train.number == ""
        assert train.train_type_index == 0
        assert len(train.stop_times) == 4
        assert len(train.operations) == 2

    for index, train in enumerate(up_trains):
        assert train.number == ""
        assert train.train_type_index == 1
        assert len(train.stop_times) == 4

        if index < 4:
            assert len(train.operations) == 2
        else:
            assert len(train.operations) == 3


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

    first_train = railway.diagrams[0].trains[0]

    assert [
        (
            stop_time.order,
            stop_time.station.index,
            stop_time.station.name,
            stop_time.arrival_time,
            stop_time.departure_time,
            stop_time.is_pass,
            stop_time.track_index,
        )
        for stop_time in first_train.stop_times
    ] == [
        (0, 0, "A", None, None, False, None),
        (1, 1, "B", None, None, False, None),
        (2, 2, "C", None, "000", False, 0),
        (3, 3, "D", "023", None, False, 0),
    ]

    # 到着・発車の両方を持つ通常停車
    second_down_train = railway.diagrams[0].trains[1]

    assert (
        second_down_train.stop_times[1].station.name,
        second_down_train.stop_times[1].arrival_time,
        second_down_train.stop_times[1].departure_time,
        second_down_train.stop_times[1].is_pass,
        second_down_train.stop_times[1].track_index,
    ) == (
        "B",
        "005",
        "006",
        False,
        0,
    )

    # 通過
    first_up_train = railway.diagrams[1].trains[0]

    assert (
        first_up_train.stop_times[1].station.name,
        first_up_train.stop_times[1].arrival_time,
        first_up_train.stop_times[1].departure_time,
        first_up_train.stop_times[1].is_pass,
        first_up_train.stop_times[1].track_index,
    ) == (
        "B",
        None,
        None,
        True,
        1,
    )

    for diagram in railway.diagrams:
        for train in diagram.trains:
            assert [stop_time.order for stop_time in train.stop_times] == [
                0, 1, 2, 3
            ]

            assert [
                stop_time.station.index
                for stop_time in train.stop_times
            ] == [0, 1, 2, 3]

            assert [
                stop_time.station.name
                for stop_time in train.stop_times
            ] == ["A", "B", "C", "D"]

    first_train = railway.diagrams[0].trains[0]

    assert len(first_train.operations) == 2

    # Operation order=2
    record = first_train.operations[0]

    assert record.order == 2
    assert record.is_before is True
    assert len(record.operations) == 1

    operation = record.operations[0]

    assert operation.type == OperationType.OUT_IN
    assert isinstance(operation.detail, OutInDetail)
    assert operation.detail.time == "2359"
    assert operation.detail.train_number == "901"
    assert operation.before_children == []
    assert operation.after_children == []

    # Operation order=3
    record = first_train.operations[1]

    assert record.order == 3
    assert record.is_before is False
    assert len(record.operations) == 2

    operation = record.operations[0]

    assert operation.type == OperationType.NUMBER_CHANGE
    assert isinstance(operation.detail, NumberChangeDetail)
    assert operation.detail.train_number == "ZZZ"

    operation = record.operations[1]

    assert operation.type == OperationType.JUNCTION
    assert isinstance(operation.detail, JunctionDetail)
    assert operation.detail.time is None
    assert operation.detail.value == "0"

    first_up_train = railway.diagrams[1].trains[0]

    assert len(first_up_train.operations) == 2

    # Operation order=0
    record = first_up_train.operations[0]

    assert record.order == 0
    assert record.is_before is True
    assert len(record.operations) == 1

    operation = record.operations[0]

    assert operation.type == OperationType.JUNCTION
    assert isinstance(operation.detail, JunctionDetail)
    assert operation.detail.time is None
    assert operation.detail.value is None
    assert operation.before_children == []
    assert operation.after_children == []

    # Operation order=3
    record = first_up_train.operations[1]

    assert record.order == 3
    assert record.is_before is False
    assert len(record.operations) == 1

    operation = record.operations[0]

    assert operation.type == OperationType.JUNCTION
    assert isinstance(operation.detail, JunctionDetail)
    assert operation.detail.time is None
    assert operation.detail.value == "0"
    assert operation.before_children == []
    assert operation.after_children == []

    # Nested Operation
    down_train_7 = railway.diagrams[0].trains[7]

    record = next(
        record
        for record in down_train_7.operations
        if record.order == 3
    )

    assert record.is_before is False
    assert len(record.operations) == 2

    # 親Operation: Connect
    operation = record.operations[0]

    assert operation.type == OperationType.CONNECT
    assert isinstance(operation.detail, ConnectDetail)
    assert operation.detail.connect_position == 0
    assert operation.detail.connect_time == "655"

    assert len(operation.before_children) == 1
    assert operation.after_children == []

    # 子Operation: Junction
    child = operation.before_children[0]

    assert child.type == OperationType.JUNCTION
    assert isinstance(child.detail, JunctionDetail)
    assert child.detail.time is None
    assert child.detail.value is None

    assert child.before_children == []
    assert child.after_children == []

    # 同じRecord内の2つ目のOperation
    operation = record.operations[1]

    assert operation.type == OperationType.JUNCTION
    assert isinstance(operation.detail, JunctionDetail)
    assert operation.detail.time is None
    assert operation.detail.value == "0"

    assert operation.before_children == []
    assert operation.after_children == []

    # Nested Operation: after_children
    down_train_8 = railway.diagrams[0].trains[8]

    record = next(
        record
        for record in down_train_8.operations
        if record.order == 3
    )

    assert record.is_before is False
    assert len(record.operations) == 2

    # 親Operation: Release
    operation = record.operations[0]

    assert operation.type == OperationType.RELEASE
    assert isinstance(operation.detail, ReleaseDetail)
    assert operation.detail.release_position == 0
    assert operation.detail.release_count == 1
    assert operation.detail.release_time == "755"

    assert operation.before_children == []
    assert len(operation.after_children) == 1

    # 子Operation: Junction
    child = operation.after_children[0]

    assert child.type == OperationType.JUNCTION
    assert isinstance(child.detail, JunctionDetail)
    assert child.detail.time is None
    assert child.detail.value == "0"

    assert child.before_children == []
    assert child.after_children == []

    # 同じRecord内の2つ目のOperation
    operation = record.operations[1]

    assert operation.type == OperationType.JUNCTION
    assert isinstance(operation.detail, JunctionDetail)
    assert operation.detail.time is None
    assert operation.detail.value == "0"

    assert operation.before_children == []
    assert operation.after_children == []

    operation_count = sum(
        len(train.operations)
        for diagram in railway.diagrams
        for train in diagram.trains
    )

    assert operation_count > 0


    # StopTimes: DOWN train 0
    stop_times = railway.diagrams[0].trains[0].stop_times

    assert len(stop_times) == 4

    expected_stop_times = [
        (0, 0, "A", None, None, False, None),
        (1, 1, "B", None, None, False, None),
        (2, 2, "C", None, "000", False, 0),
        (3, 3, "D", "023", None, False, 0),
    ]

    for stop_time, (
        expected_order,
        expected_station_index,
        expected_station_name,
        expected_arrival,
        expected_departure,
        expected_is_pass,
        expected_track_index,
    ) in zip(stop_times, expected_stop_times):
        assert stop_time.order == expected_order
        assert stop_time.station.index == expected_station_index
        assert stop_time.station.name == expected_station_name
        assert stop_time.arrival_time == expected_arrival
        assert stop_time.departure_time == expected_departure
        assert stop_time.is_pass == expected_is_pass
        assert stop_time.track_index == expected_track_index

    # StopTimes: DOWN train 1
    stop_times = railway.diagrams[0].trains[1].stop_times

    assert len(stop_times) == 4

    expected_stop_times = [
        (0, 0, "A", None, "000", False, 0),
        (1, 1, "B", "005", "006", False, 0),
        (2, 2, "C", "009", "015", False, 0),
        (3, 3, "D", "025", None, False, 0),
    ]

    for stop_time, (
        expected_order,
        expected_station_index,
        expected_station_name,
        expected_arrival,
        expected_departure,
        expected_is_pass,
        expected_track_index,
    ) in zip(stop_times, expected_stop_times):
        assert stop_time.order == expected_order
        assert stop_time.station.index == expected_station_index
        assert stop_time.station.name == expected_station_name
        assert stop_time.arrival_time == expected_arrival
        assert stop_time.departure_time == expected_departure
        assert stop_time.is_pass == expected_is_pass
        assert stop_time.track_index == expected_track_index

    # StopTimes: UP train 0 pass stations
    stop_times = railway.diagrams[1].trains[0].stop_times

    assert len(stop_times) == 4

    # B駅
    stop_time = stop_times[1]

    assert stop_time.order == 1
    assert stop_time.station.index == 1
    assert stop_time.station.name == "B"
    assert stop_time.arrival_time is None
    assert stop_time.departure_time is None
    assert stop_time.is_pass is True
    assert stop_time.track_index == 1

    # C駅
    stop_time = stop_times[2]

    assert stop_time.order == 2
    assert stop_time.station.index == 2
    assert stop_time.station.name == "C"
    assert stop_time.arrival_time is None
    assert stop_time.departure_time is None
    assert stop_time.is_pass is True
    assert stop_time.track_index == 1


    # StopTimes: UP train 0
    stop_times = railway.diagrams[1].trains[0].stop_times

    assert len(stop_times) == 4

    expected_stop_times = [
        (0, 0, "A", None, "030", False, 0),
        (1, 1, "B", None, None, True, 1),
        (2, 2, "C", None, None, True, 1),
        (3, 3, "D", "100", None, False, 1),
    ]

    for stop_time, (
        expected_order,
        expected_station_index,
        expected_station_name,
        expected_arrival,
        expected_departure,
        expected_is_pass,
        expected_track_index,
    ) in zip(stop_times, expected_stop_times):
        assert stop_time.order == expected_order
        assert stop_time.station.index == expected_station_index
        assert stop_time.station.name == expected_station_name
        assert stop_time.arrival_time == expected_arrival
        assert stop_time.departure_time == expected_departure
        assert stop_time.is_pass == expected_is_pass
        assert stop_time.track_index == expected_track_index


