from src.models.railway import Direction, Railway
from src.models.station import Station
from src.models.timetable import StationTimetable
from src.timetable.station_timetable_generator import (
    StationTimetableGenerator,
)


def test_generate_station_timetable(
    parsed_railway: Railway,
) -> None:
    """指定駅の駅時刻表を生成できること。"""
    station = parsed_railway.stations[1]

    generator = StationTimetableGenerator(parsed_railway)

    timetable = generator.generate(station)

    assert isinstance(timetable, StationTimetable)
    assert timetable.station_name == "B"



def test_generate_station_timetable_down(
    parsed_railway: Railway,
) -> None:
    """下り駅時刻表が生成されること。"""
    station = parsed_railway.stations[1]

    generator = StationTimetableGenerator(parsed_railway)

    timetable = generator.generate(station)

    assert timetable.down




def test_generate_station_timetable_excludes_pass(
    parsed_railway: Railway,
) -> None:
    """通過列車が駅時刻表から除外されること。"""
    station = parsed_railway.stations[1]

    generator = StationTimetableGenerator(parsed_railway)

    timetable = generator.generate(station)

    up_entries = [
        entry
        for hour in timetable.up
        for entry in hour.entries
    ]

    # B駅を通過する上り列車は駅時刻表に掲載されない。
    assert all(entry.minute != 30 for entry in up_entries)


def test_generate_station_timetable_destination(
    parsed_railway: Railway,
) -> None:
    """列車の最終到着駅が行先として設定されること。"""
    station = parsed_railway.stations[1]

    generator = StationTimetableGenerator(parsed_railway)

    timetable = generator.generate(station)

    down_entries = [
        entry
        for hour in timetable.down
        for entry in hour.entries
    ]

    # B駅の下り列車の行先がD駅になることを確認する。
    assert any(
        entry.destination == "D"
        for entry in down_entries
    )


def test_generate_station_timetable_departure_time(
    parsed_railway: Railway,
) -> None:
    """駅時刻表には出発時刻が使用されること。"""
    station = parsed_railway.stations[1]

    generator = StationTimetableGenerator(parsed_railway)

    timetable = generator.generate(station)

    down_entries = [
        entry
        for hour in timetable.down
        for entry in hour.entries
    ]

    # B駅で到着005 / 出発006となる列車が、
    # 駅時刻表では06分として登録されることを確認する。
    entry = next(
        entry
        for entry in down_entries
        if entry.minute == 6
        and entry.destination == "D"
    )

    assert entry.minute == 6


def test_generate_station_timetable_order(
    parsed_railway: Railway,
) -> None:
    """駅時刻表が04時始まりの順序で並ぶこと。"""
    station = parsed_railway.stations[1]

    generator = StationTimetableGenerator(parsed_railway)

    timetable = generator.generate(station)

    hours = [hour.hour for hour in timetable.down]

    expected_order = sorted(
        hours,
        key=lambda hour: (hour - 4) % 24,
    )

    assert hours == expected_order


def test_generate_station_timetable_train_type(
    parsed_railway: Railway,
) -> None:
    """列車種別が正しく設定されること。"""
    station = parsed_railway.stations[1]

    generator = StationTimetableGenerator(parsed_railway)

    timetable = generator.generate(station)

    down_entries = [
        entry
        for hour in timetable.down
        for entry in hour.entries
    ]

    assert any(
        entry.train_type.name == "普通"
        for entry in down_entries
    )


def test_generate_station_timetable_contains_all_hours(
    parsed_railway: Railway,
) -> None:
    """駅時刻表に04時～翌03時の24時間がすべて含まれること。"""
    station = parsed_railway.stations[1]

    generator = StationTimetableGenerator(parsed_railway)
    timetable = generator.generate(station)

    expected_hours = [
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        0,
        1,
        2,
        3,
    ]

    assert [hour.hour for hour in timetable.down] == expected_hours
    assert [hour.hour for hour in timetable.up] == expected_hours


