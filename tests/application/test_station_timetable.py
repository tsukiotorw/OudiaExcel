from pathlib import Path

from src.application.oud2_loader import load_oud2
from src.application.station_timetable import generate_station_timetable
from src.models.timetable import StationTimetable


EXAMPLE_FILE = Path("examples/解析用.oud2")


def test_generate_station_timetable() -> None:
    railway = load_oud2(EXAMPLE_FILE)
    station = railway.stations[1]

    timetable = generate_station_timetable(
        railway,
        station,
    )

    assert isinstance(timetable, StationTimetable)
    assert timetable.station_name == "B"
    assert len(timetable.down) == 24
    assert len(timetable.up) == 24
