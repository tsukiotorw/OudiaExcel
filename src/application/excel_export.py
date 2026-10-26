from pathlib import Path

from src.models.timetable import StationTimetable
from src.timetable.display_config import TimetableDisplayConfig
from src.timetable.excel_writer import ExcelWriter


def export_station_timetable(
    timetable: StationTimetable,
    output_path: Path,
    display_config: TimetableDisplayConfig | None = None,
) -> None:
    writer = ExcelWriter(display_config=display_config)
    writer.write(timetable, output_path)

