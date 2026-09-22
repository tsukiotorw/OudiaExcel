from pathlib import Path

from src.models.timetable import StationTimetable
from src.timetable.excel_writer import ExcelWriter


def export_station_timetable(
    timetable: StationTimetable,
    output_path: Path,
) -> None:
    writer = ExcelWriter()
    writer.write(timetable, output_path)
