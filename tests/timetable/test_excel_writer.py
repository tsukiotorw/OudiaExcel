from openpyxl import load_workbook

from src.models.railway import Railway
from src.timetable.excel_writer import ExcelWriter
from src.timetable.station_timetable_generator import (
    StationTimetableGenerator,
)


def test_write_station_timetable(
    parsed_railway: Railway,
    tmp_path,
) -> None:
    """駅時刻表をExcelファイルへ出力できること。"""
    station = parsed_railway.stations[1]

    generator = StationTimetableGenerator(parsed_railway)
    timetable = generator.generate(station)

    output_path = tmp_path / "station_timetable.xlsx"

    writer = ExcelWriter()
    writer.write(timetable, output_path)

    assert output_path.exists()

    workbook = load_workbook(output_path)

    assert timetable.station_name in workbook.sheetnames

    worksheet = workbook[timetable.station_name]

    assert worksheet["A1"].value == "下り"
    assert worksheet["A2"].value == "時"
    assert worksheet["B2"].value == "分"
    assert worksheet["C2"].value == "行先"
    assert worksheet["D2"].value == "種別"
