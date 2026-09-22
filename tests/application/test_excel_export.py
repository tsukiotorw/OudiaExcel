from pathlib import Path

from openpyxl import load_workbook

from src.application.excel_export import export_station_timetable
from src.application.oud2_loader import load_oud2
from src.application.station_timetable import generate_station_timetable


EXAMPLE_FILE = Path(__file__).parents[2] / "examples" / "解析用.oud2"


def test_export_station_timetable(
    tmp_path: Path,
) -> None:
    """駅時刻表をExcelファイルへ出力できること。"""
    railway = load_oud2(EXAMPLE_FILE)
    station = railway.stations[1]
    timetable = generate_station_timetable(
        railway,
        station,
    )

    output_path = tmp_path / "station_timetable.xlsx"

    export_station_timetable(
        timetable,
        output_path,
    )

    assert output_path.exists()

    workbook = load_workbook(output_path)
    worksheet = workbook[timetable.station_name]

    assert worksheet["D1"].value == "B駅 時刻表"
    assert worksheet["A3"].value == "下り"
