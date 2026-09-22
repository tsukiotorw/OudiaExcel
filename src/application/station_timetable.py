from src.models.railway import Railway
from src.models.station import Station
from src.models.timetable import StationTimetable
from src.timetable.station_timetable_generator import StationTimetableGenerator


def generate_station_timetable(
    railway: Railway,
    station: Station,
) -> StationTimetable:
    """指定された駅の駅時刻表を生成する。"""
    generator = StationTimetableGenerator(railway)

    return generator.generate(station)
