"""
Time Parserのテスト
"""
from src.models.railway import (
    Station,
    StopTime,
)
from src.parser.time_parser import (
    parse_stop_times,
    RecordType,
    TimeParser,
)




def create_station(
    index: int = 0,
    name: str = "東京",
) -> Station:
    """
    駅データのテストデータファクトリ
    """
    return Station(
        index=index,
        name=name,
    )


def test_parse_single_departure() -> None:
    """
    発時刻のみのStopTimeを生成できること。
    """

    stations = [
        create_station(0,"東京")
    ]

    stop_times = parse_stop_times(
        "1;500$0",
        stations,
    )

    assert len(stop_times) == 1

    stop = stop_times[0]

    assert stop.station.name == "東京"
    assert stop.order == 0
    assert stop.arrival_time is None
    assert stop.departure_time == "500"
    assert stop.is_pass is False


def test_parse_arrival_departure() -> None:
    """
    発時刻/着時刻を解析できること。
    """

    stations = [
        create_station(0, "新宿")
    ]

    stop_times = parse_stop_times(
        "1;503/504$0",
        stations,
    )

    stop = stop_times[0]

    assert stop.arrival_time == "503"
    assert stop.departure_time == "504"
    assert stop.is_pass is False


def test_parse_terminal_station() -> None:
    """
    終着駅を解析できること。
    """

    stations = [
        create_station(0, "高尾"),
    ]

    stop_times = parse_stop_times(
        "1;536/$0",
        stations,
    )

    stop = stop_times[0]

    assert stop.arrival_time == "536"
    assert stop.departure_time is None

def test_parse_origin_station() -> None:
    """
    始発駅を解析できること。
    """

    stations = [
        create_station(0, "東京"),
    ]

    stop_times = parse_stop_times(
        "1;/430$0",
        stations,
    )

    stop = stop_times[0]

    assert stop.arrival_time is None
    assert stop.departure_time == "430"


def test_detect_empty_record() -> None:
    """
    空レコードを判定できること。
    """

    parser = TimeParser()

    assert parser._detect_record_type("") is RecordType.EMPTY


def test_detect_normal_record() -> None:
    """
    通常レコードを判定できること。
    """

    parser = TimeParser()

    assert (
        parser._detect_record_type("1;500$0")
        is RecordType.TIME
    )


def test_detect_pass_record_without_time() -> None:
    """
    通過時刻なしレコードも TIME と判定できること。
    """

    assert (
        TimeParser._detect_record_type("2$1")
        is RecordType.TIME
    )

def test_parse_track_index() -> None:
    """
    track_index を解析できること。
    """

    stations = [
        create_station(0, "東京"),
    ]

    stop_times = parse_stop_times(
        "1;503/504$2",
        stations,
    )

    assert stop_times[0].track_index == 2

def test_parse_pass_record() -> None:
    """
    通過レコードを解析できること。
    """

    stations = [
        create_station(0, "東京"),
    ]

    stop_times = parse_stop_times(
        "2;551$1",
        stations,
    )

    assert stop_times[0].is_pass is True
    assert stop_times[0].arrival_time == "551"
    assert stop_times[0].departure_time is None
    assert stop_times[0].track_index == 1


def test_parse_pass_record_without_time() -> None:
    """
    通過時刻なしレコードを解析できること。
    """

    stations = [
        create_station(0, "東京"),
    ]

    stop_time = TimeParser.parse(
        record="2$1",
        station=stations,
        order=0,
    )

    assert stop_time.is_pass is True
    assert stop_time.arrival_time is None
    assert stop_time.departure_time is None
    assert stop_time.track_index == 1

