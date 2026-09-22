from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from src.models.railway import Railway
from src.timetable.excel_writer import ExcelWriter
from src.timetable.station_timetable_generator import (
    StationTimetableGenerator,
)

from src.timetable.display_config import TimetableDisplayConfig


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

    assert worksheet["D1"].value == "B駅 時刻表"
    assert worksheet["A3"].value == "下り"


def test_write_station_timetable_layout(
    parsed_railway: Railway,
    tmp_path,
) -> None:
    """駅時刻表が2行/時間の左右配置で出力されること。"""
    station = parsed_railway.stations[1]

    generator = StationTimetableGenerator(parsed_railway)
    timetable = generator.generate(station)

    output_path = tmp_path / "station_timetable.xlsx"

    writer = ExcelWriter()
    writer.write(timetable, output_path)

    workbook = load_workbook(output_path)
    worksheet = workbook[timetable.station_name]

    # 下り
    assert worksheet["A3"].value == "下り"

    # 下りは4時から開始
    assert worksheet["A4"].value == 4
    assert worksheet["A6"].value == 5
    assert worksheet["A8"].value == 6

    # 上りの開始位置を確認
    down_width = max(
        len(hour.entries)
        for hour in timetable.down
    ) + 1

    up_start_column = (
        1
        + down_width
        + writer._DIRECTION_GAP
    )

    up_start_cell = worksheet.cell(
        row=3,
        column=up_start_column,
    )

    assert up_start_cell.value == "上り"

    # 上りも4時から開始
    up_hour_cell = worksheet.cell(
        row=4,
        column=up_start_column,
    )

    assert up_hour_cell.value == 4


def test_write_station_timetable_entry(
    parsed_railway: Railway,
    tmp_path,
) -> None:
    """列車の行先・種別・分がExcelへ出力されること。"""
    station = parsed_railway.stations[1]

    generator = StationTimetableGenerator(parsed_railway)
    timetable = generator.generate(station)

    output_path = tmp_path / "station_timetable.xlsx"

    writer = ExcelWriter()
    writer.write(timetable, output_path)

    workbook = load_workbook(output_path)
    worksheet = workbook[timetable.station_name]

    # 4時台の下りデータを確認
    hour = timetable.down[0]

    assert hour.hour == 4
    assert hour.entries

    entry = hour.entries[0]

    # A列が時なので、最初の列車はB列
    assert worksheet["B4"].value == (
        entry.destination + entry.train_type.short_name
    )
    assert worksheet["B5"].value == entry.minute


def test_write_train_type_colors(
    parsed_railway: Railway,
    tmp_path,
) -> None:
    """列車種別に応じて文字色が設定されること。"""
    station = parsed_railway.stations[1]

    generator = StationTimetableGenerator(parsed_railway)
    timetable = generator.generate(station)

    # 列車種別の文字色とセルの色塗りを設定する
    display_config = TimetableDisplayConfig(
        train_type_colors={
            0: "008000",
            1: "0000FF",
        },
        header_fill="D9EAD3",
        hour_fill="F2F2F2",
    )

    # ↓↓↓ ここにデバッグ出力を追加 ↓↓↓
    # ↑↑↑ ここまで ↑↑↑

    output_path = tmp_path / "station_timetable.xlsx"

    print(f"output_path = {output_path}")

    writer = ExcelWriter(
        display_config=display_config,
    )

    writer.write(
        timetable,
        output_path,
    )

    workbook = load_workbook(output_path)
    worksheet = workbook[timetable.station_name]

    # 4時台の最初の下り列車
    entry = timetable.down[0].entries[0]

    expected_color = display_config.get_train_type_color(
        entry.train_type.index
    )

    # ↓↓↓ ここにもデバッグ出力を追加 ↓↓↓
    # ↑↑↑ ここまで ↑↑↑

    assert worksheet["B4"].font.color.type == "rgb"
    assert worksheet["B4"].font.color.rgb == (
        "FF" + expected_color
    )


def test_write_header_display_config(
    parsed_railway: Railway,
    tmp_path,
) -> None:
    """ヘッダの表示設定がExcelへ反映されること。"""
    station = parsed_railway.stations[1]
    generator = StationTimetableGenerator(parsed_railway)
    timetable = generator.generate(station)

    display_config = TimetableDisplayConfig(
        header_fill="D9EAD3",
        header_font_color="FF0000",
        header_font_name="ＭＳ ゴシック",
        header_font_size=14,
    )

    output_path = tmp_path / "station_timetable.xlsx"

    writer = ExcelWriter(
        display_config=display_config,
    )
    writer.write(
        timetable,
        output_path,
    )

    workbook = load_workbook(output_path)
    worksheet = workbook[timetable.station_name]

    cell = worksheet["A3"]

    assert cell.fill.fgColor.rgb == "FFD9EAD3"
    assert cell.font.color.type == "rgb"
    assert cell.font.color.rgb == "FFFF0000"
    assert cell.font.name == "ＭＳ ゴシック"
    assert cell.font.sz == 14

def test_write_hour_display_config(
    parsed_railway: Railway,
    tmp_path,
) -> None:
    """時刻欄の表示設定がExcelへ反映されること。"""
    station = parsed_railway.stations[1]
    generator = StationTimetableGenerator(parsed_railway)
    timetable = generator.generate(station)

    display_config = TimetableDisplayConfig(
        hour_fill="F2F2F2",
        hour_font_color="0000FF",
        hour_font_name="ＭＳ ゴシック",
        hour_font_size=11,
    )

    output_path = tmp_path / "station_timetable.xlsx"

    writer = ExcelWriter(
        display_config=display_config,
    )
    writer.write(
        timetable,
        output_path,
    )

    workbook = load_workbook(output_path)
    worksheet = workbook[timetable.station_name]

    cell = worksheet["A4"]

    assert cell.fill.fgColor.rgb == "FFF2F2F2"
    assert cell.font.color.type == "rgb"
    assert cell.font.color.rgb == "FF0000FF"
    assert cell.font.name == "ＭＳ ゴシック"
    assert cell.font.sz == 11


def test_write_train_display_config(
    parsed_railway: Railway,
    tmp_path,
) -> None:
    """列車欄の表示設定がExcelへ反映されること。"""
    station = parsed_railway.stations[1]
    generator = StationTimetableGenerator(parsed_railway)
    timetable = generator.generate(station)

    display_config = TimetableDisplayConfig(
        train_fill="FFF2CC",
        train_font_color="800080",
    )

    output_path = tmp_path / "station_timetable.xlsx"

    writer = ExcelWriter(
        display_config=display_config,
    )
    writer.write(
        timetable,
        output_path,
    )

    workbook = load_workbook(output_path)
    worksheet = workbook[timetable.station_name]

    cell = worksheet["B4"]

    assert cell.fill.fgColor.rgb == "FFFFF2CC"
    assert cell.font.color.type == "rgb"
    assert cell.font.color.rgb == "FF800080"


def test_train_type_color_takes_priority_over_train_font_color(
    parsed_railway: Railway,
    tmp_path,
) -> None:
    """列車種別の文字色が共通の列車文字色より優先されること。"""
    station = parsed_railway.stations[1]
    generator = StationTimetableGenerator(parsed_railway)
    timetable = generator.generate(station)

    display_config = TimetableDisplayConfig(
        train_font_color="000000",
        train_type_colors={
            0: "008000",
            1: "0000FF",
        },
    )

    output_path = tmp_path / "station_timetable.xlsx"

    writer = ExcelWriter(
        display_config=display_config,
    )
    writer.write(
        timetable,
        output_path,
    )

    workbook = load_workbook(output_path)
    worksheet = workbook[timetable.station_name]

    entry = timetable.down[0].entries[0]
    expected_color = display_config.get_train_type_color(
        entry.train_type.index
    )

    cell = worksheet["B4"]

    assert expected_color is not None
    assert cell.font.color.type == "rgb"
    assert cell.font.color.rgb == "FF" + expected_color


def test_write_station_timetable_legend(
    parsed_railway: Railway,
    tmp_path,
) -> None:
    """駅時刻表に列車種別の凡例が出力されること。"""
    station = parsed_railway.stations[1]

    generator = StationTimetableGenerator(parsed_railway)
    timetable = generator.generate(station)

    output_path = tmp_path / "station_timetable.xlsx"

    writer = ExcelWriter()
    writer.write(timetable, output_path)

    workbook = load_workbook(output_path)
    worksheet = workbook[timetable.station_name]

    legend_row = 53

    # 「凡例」が出力される。
    label_cell = worksheet.cell(
        row=legend_row,
        column=1,
    )
    assert label_cell.value == "凡例"

    # 「普通」「快速」が凡例として出力される。
    assert worksheet.cell(
        row=legend_row,
        column=2,
    ).value == "普通"

    assert worksheet.cell(
        row=legend_row + 1,
        column=2,
    ).value == "快速"

    # 「凡例」が列車種別の行数分、縦結合される。
    assert f"A{legend_row}:A{legend_row + 1}" in {
        str(cell_range)
        for cell_range in worksheet.merged_cells.ranges
    }

    # 各列車種別の説明領域が、時刻表全体の横幅まで結合される。
    down_width = writer._max_entry_count(timetable.down) + 1
    up_width = writer._max_entry_count(timetable.up) + 1

    down_start_column = 1
    up_start_column = (
        down_start_column
        + down_width
        + writer._DIRECTION_GAP
    )
    end_column = up_start_column + up_width - 1

    assert (
        f"B{legend_row}:{get_column_letter(end_column)}{legend_row}"
        in {
            str(cell_range)
            for cell_range in worksheet.merged_cells.ranges
        }
    )

    assert (
        f"B{legend_row + 1}:{get_column_letter(end_column)}{legend_row + 1}"
        in {
            str(cell_range)
            for cell_range in worksheet.merged_cells.ranges
        }
    )

    # 「凡例」ラベルの外観。
    assert label_cell.fill.fgColor.rgb == "FF000000"
    assert label_cell.font.name == "源ノ角ゴシック JP Heavy"
    assert label_cell.font.sz == 8

    # 説明領域の外観。
    legend_cell = worksheet.cell(
        row=legend_row,
        column=2,
    )

    assert legend_cell.fill.fgColor.rgb == "FFFAFAFA"
    assert legend_cell.font.name == "源ノ角ゴシック JP"
    assert legend_cell.font.sz == 8

    # 凡例の行高。
    assert worksheet.row_dimensions[legend_row].height == 24.2
    assert worksheet.row_dimensions[legend_row + 1].height == 24.2
