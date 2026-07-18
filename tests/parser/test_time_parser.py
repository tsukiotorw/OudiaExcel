"""
Time Parserのテスト
"""
from src.models.railway import (
    Station,
    StopTime,
)
from src.parser.time_parser import parse_stop_times

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

