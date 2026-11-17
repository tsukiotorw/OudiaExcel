import pytest
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.cell.rich_text import CellRichText

from src.models.railway import Railway
from src.timetable.excel_writer import ExcelWriter
from src.timetable.station_timetable_generator import (
    StationTimetableGenerator,
)

from src.timetable.display_config import TimetableDisplayConfig
from src.models.station import Station
from src.models.timetable import (
    StationTimetable,
    TimetableEntry,
    TimetableHour,
)
from src.models.train_type import TrainType
from src.timetable.display_layout import get_entry_layout


def _first_marked_entry(hours):
    return next(
        entry
        for hour in hours
        for entry in hour.entries
        if not entry.destination.is_no_mark
        and entry.destination.display_name
    )


def _legend_timetable(
    train_type_count: int,
    down_destination_count: int,
    up_destination_count: int,
    down_entries_per_hour: int = 1,
    up_entries_per_hour: int = 1,
    down_no_mark: set[int] | None = None,
) -> StationTimetable:
    train_types = [
        TrainType(index, f"Train type {index}", f"T{index}")
        for index in range(train_type_count)
    ]
    entry_train_type = (
        train_types[0]
        if train_types
        else TrainType(99, "Unused train type")
    )
    down_no_mark = down_no_mark or set()

    def make_hours(
        direction: str,
        destination_count: int,
        entries_per_hour: int,
        index_offset: int,
    ) -> list[TimetableHour]:
        entries = [
            TimetableEntry(
                minute=index,
                destination=Station(
                    index=index_offset + index,
                    name=f"{direction} station {index}",
                    short_name=f"{direction}{index}",
                    is_no_mark=direction == "Down" and index in down_no_mark,
                ),
                train_type=entry_train_type,
                train_number=f"{direction}{index}",
            )
            for index in range(destination_count)
        ]
        return [
            TimetableHour(
                hour=4 + group_index,
                entries=entries[
                    group_index:group_index + entries_per_hour
                ],
            )
            for group_index in range(0, destination_count, entries_per_hour)
        ]

    return StationTimetable(
        station_name="Legend test",
        down=make_hours(
            "Down",
            down_destination_count,
            down_entries_per_hour,
            0,
        ),
        up=make_hours(
            "Up",
            up_destination_count,
            up_entries_per_hour,
            100,
        ),
        train_types=train_types,
    )


def _single_entry_timetable(source, entry, hour: int = 4) -> StationTimetable:
    return StationTimetable(
        station_name=source.station_name,
        down=[TimetableHour(hour, [entry])],
        up=[],
        train_types=source.train_types,
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
    expected_destination = (
        entry.destination.display_name
        if (
            writer.display_config.show_destination
            and not entry.destination.is_no_mark
        )
        else ""
    )

    expected_train_type = (
        entry.train_type.short_name
        if (
            writer.display_config.use_train_type_short_name
            and entry.train_type.short_name
        )
        else entry.train_type.name
    )

    if not writer.display_config.train_type_column_visible.get(
        entry.train_type.index,
        True,
    ):
        expected_train_type = ""

    expected_metadata = " ".join(
        part
        for part in (expected_destination, expected_train_type)
        if part
    )

    assert worksheet["B4"].value == expected_metadata

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

    # 凡例項目は既存列幅内で折り返される。
    assert worksheet.cell(
        row=legend_row,
        column=2,
    ).value == "普通"

    assert worksheet.cell(
        row=legend_row + 1,
        column=2,
    ).value == "快速"

    # 「凡例」ラベルは項目全体の高さに合わせて縦結合する。
    assert f"A{legend_row}:A{legend_row + 1}" in {
        str(cell_range)
        for cell_range in worksheet.merged_cells.ranges
    }

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


def test_write_legend_wraps_train_types_and_preserves_order(
    tmp_path,
) -> None:
    timetable = _legend_timetable(4, 0, 0)
    config = TimetableDisplayConfig(
        use_train_type_short_name=True,
        train_type_visible={1: False},
    )
    output_path = tmp_path / "wrapped_train_types.xlsx"

    ExcelWriter(config).write(timetable, output_path)

    worksheet = load_workbook(output_path)[timetable.station_name]
    legend_row = next(
        row
        for row in range(1, worksheet.max_row + 1)
        if worksheet.cell(row=row, column=1).value == "凡例"
    )
    assert [
        worksheet.cell(row=legend_row + offset, column=2).value
        for offset in range(3)
    ] == ["T0", "T2", "T3"]
    assert f"A{legend_row}:A{legend_row + 2}" in {
        str(cell_range)
        for cell_range in worksheet.merged_cells.ranges
    }


def test_write_legend_wraps_destinations_and_preserves_formatting(
    tmp_path,
) -> None:
    timetable = _legend_timetable(
        1,
        3,
        0,
        down_no_mark={1},
    )
    config = TimetableDisplayConfig(
        train_type_colors={0: "112233"},
        legend_fill="E1E2E3",
        legend_font_color="445566",
        legend_font_name="Arial",
        legend_font_size=9,
        legend_label_fill="010203",
        legend_label_font_color="FFFFFF",
        legend_label_font_name="Calibri",
        legend_label_font_size=10,
    )
    config.legend_border.left.enabled = True
    config.legend_border.left.color = "AABBCC"
    output_path = tmp_path / "wrapped_destinations.xlsx"

    ExcelWriter(config).write(timetable, output_path)

    worksheet = load_workbook(output_path)[timetable.station_name]
    legend_row = next(
        row
        for row in range(1, worksheet.max_row + 1)
        if worksheet.cell(row=row, column=1).value == "凡例"
    )
    assert [
        worksheet.cell(row=legend_row + offset, column=2).value
        for offset in range(4)
    ] == [
        "Train type 0",
        "Down0＝Down station 0",
        "無印＝Down station 1",
        "Down2＝Down station 2",
    ]

    label_cell = worksheet.cell(row=legend_row, column=1)
    assert label_cell.fill.fgColor.rgb == "FF010203"
    assert label_cell.font.name == "Calibri"
    assert label_cell.font.sz == 10

    train_type_cell = worksheet.cell(row=legend_row, column=2)
    assert train_type_cell.fill.fgColor.rgb == "FFE1E2E3"
    assert train_type_cell.font.name == "Arial"
    assert train_type_cell.font.sz == 9
    assert train_type_cell.font.color.rgb == "FF112233"
    assert train_type_cell.border.left.style == "thin"
    assert train_type_cell.border.left.color.rgb == "FFAABBCC"

    destination_cell = worksheet.cell(row=legend_row + 1, column=2)
    assert destination_cell.font.color.rgb == "FF445566"
    assert destination_cell.fill.fgColor.rgb == "FFE1E2E3"
    assert destination_cell.alignment.wrap_text is True
    assert f"A{legend_row}:A{legend_row + 3}" in {
        str(cell_range)
        for cell_range in worksheet.merged_cells.ranges
    }


def test_write_legend_wraps_down_and_up_independently(
    tmp_path,
) -> None:
    timetable = _legend_timetable(
        0,
        1,
        5,
        up_entries_per_hour=2,
    )
    output_path = tmp_path / "asymmetric_legend.xlsx"

    ExcelWriter().write(timetable, output_path)

    worksheet = load_workbook(output_path)[timetable.station_name]
    legend_row = next(
        row
        for row in range(1, worksheet.max_row + 1)
        if worksheet.cell(row=row, column=1).value == "凡例"
    )
    assert worksheet.cell(row=legend_row, column=2).value == (
        "Down0＝Down station 0"
    )
    assert f"A{legend_row}:A{legend_row}" not in {
        str(cell_range)
        for cell_range in worksheet.merged_cells.ranges
    }
    assert [
        worksheet.cell(row=legend_row + offset, column=6).value
        for offset in range(2)
    ] == ["Up0＝Up station 0", "Up2＝Up station 2"]
    assert [
        worksheet.cell(row=legend_row + offset, column=7).value
        for offset in range(2)
    ] == ["Up1＝Up station 1", "Up3＝Up station 3"]
    assert worksheet.cell(row=legend_row + 2, column=6).value == (
        "Up4＝Up station 4"
    )
    assert f"E{legend_row}:E{legend_row + 2}" in {
        str(cell_range)
        for cell_range in worksheet.merged_cells.ranges
    }


def test_write_center_hour_column_wraps_legend(
    tmp_path,
) -> None:
    timetable = _legend_timetable(
        2,
        4,
        0,
        down_entries_per_hour=2,
    )
    output_path = tmp_path / "center_wrapped_legend.xlsx"

    ExcelWriter(
        TimetableDisplayConfig(hour_column_mode="center")
    ).write(timetable, output_path)

    worksheet = load_workbook(output_path)[timetable.station_name]
    legend_row = next(
        row
        for row in range(1, worksheet.max_row + 1)
        if worksheet.cell(row=row, column=1).value == "凡例"
    )
    assert [
        worksheet.cell(row=legend_row + offset, column=2).value
        for offset in range(2)
    ] == ["Train type 0", "Train type 1"]
    assert [
        worksheet.cell(row=legend_row + offset, column=2).value
        for offset in range(2, 6)
    ] == [
        "Down0＝Down station 0",
        "Down1＝Down station 1",
        "Down2＝Down station 2",
        "Down3＝Down station 3",
    ]
    assert worksheet.cell(row=legend_row, column=3).value is None
    assert worksheet.cell(row=legend_row, column=4).value == "凡例"
    assert worksheet.column_dimensions["A"].width == 7
    assert worksheet.column_dimensions["B"].width == 7
    assert worksheet.column_dimensions["C"].width == 4
    assert worksheet.column_dimensions["D"].width == 7


def test_write_center_legend_with_no_item_columns_stacks_below_label(
    tmp_path,
) -> None:
    timetable = _legend_timetable(2, 2, 0)
    output_path = tmp_path / "center_vertical_legend.xlsx"

    ExcelWriter(
        TimetableDisplayConfig(hour_column_mode="center")
    ).write(timetable, output_path)

    worksheet = load_workbook(output_path)[timetable.station_name]
    legend_row = next(
        row
        for row in range(1, worksheet.max_row + 1)
        if worksheet.cell(row=row, column=1).value == "凡例"
    )
    assert [
        worksheet.cell(row=legend_row + offset, column=1).value
        for offset in range(1, 5)
    ] == [
        "Train type 0",
        "Train type 1",
        "Down0＝Down station 0",
        "Down1＝Down station 1",
    ]
    assert f"A{legend_row}:A{legend_row}" not in {
        str(cell_range)
        for cell_range in worksheet.merged_cells.ranges
    }
    assert worksheet.cell(row=legend_row, column=2).value is None


def test_write_timetable_without_legend_items_does_not_add_legend(
    tmp_path,
) -> None:
    timetable = _legend_timetable(0, 0, 0)
    output_path = tmp_path / "no_legend.xlsx"

    ExcelWriter().write(timetable, output_path)

    worksheet = load_workbook(output_path)[timetable.station_name]
    assert all(
        cell.value != "凡例"
        for row in worksheet.iter_rows()
        for cell in row
    )


@pytest.mark.parametrize(
    ("destination_position", "train_type_position", "order"),
    [
        ("top", "top", "destination_first"),
        ("bottom", "bottom", "destination_first"),
        ("top", "bottom", "destination_first"),
        ("bottom", "top", "train_type_first"),
    ],
)
def test_write_entry_layout_positions(
    parsed_railway: Railway,
    tmp_path,
    destination_position: str,
    train_type_position: str,
    order: str,
) -> None:
    station = parsed_railway.stations[1]
    source = StationTimetableGenerator(parsed_railway).generate(station)
    entry = _first_marked_entry(source.down)
    timetable = _single_entry_timetable(source, entry)
    config = TimetableDisplayConfig(
        destination_position=destination_position,
        train_type_position=train_type_position,
        metadata_order=order,
    )
    output_path = tmp_path / "layout.xlsx"

    ExcelWriter(config).write(timetable, output_path)

    worksheet = load_workbook(output_path)[timetable.station_name]
    expected_type = (
        entry.train_type.short_name
        if config.use_train_type_short_name and entry.train_type.short_name
        else entry.train_type.name
    )
    expected_values = {
        "destination": entry.destination.display_name,
        "train_type": expected_type,
        "minute": entry.minute,
    }

    layout = get_entry_layout(entry, config)
    assert len(layout) == (
        3
        if destination_position != train_type_position
        or destination_position == "bottom"
        else 2
    )
    for row_offset, kinds in enumerate(layout):
        expected = (
            expected_values["minute"]
            if kinds == ["minute"]
            else " ".join(
                str(expected_values[kind])
                for kind in kinds
            )
            if kinds
            else None
        )
        cell_value = worksheet.cell(row=4 + row_offset, column=2).value
        assert cell_value == expected


def test_write_entry_layout_respects_visibility(
    parsed_railway: Railway,
    tmp_path,
) -> None:
    station = parsed_railway.stations[1]
    source = StationTimetableGenerator(parsed_railway).generate(station)
    entry = _first_marked_entry(source.down)
    timetable = _single_entry_timetable(source, entry)
    config = TimetableDisplayConfig(
        show_destination=False,
        train_type_position="bottom",
    )
    config.train_type_column_visible[entry.train_type.index] = False
    output_path = tmp_path / "hidden.xlsx"

    ExcelWriter(config).write(timetable, output_path)

    worksheet = load_workbook(output_path)[timetable.station_name]
    assert worksheet["B4"].value is None
    assert worksheet["B5"].value == entry.minute


def test_write_entry_fonts_and_train_type_color_priority(
    parsed_railway: Railway,
    tmp_path,
) -> None:
    station = parsed_railway.stations[1]
    source = StationTimetableGenerator(parsed_railway).generate(station)
    entry = _first_marked_entry(source.down)
    timetable = _single_entry_timetable(source, entry)
    config = TimetableDisplayConfig(
        destination_position="top",
        train_type_position="bottom",
        destination_font_name="Arial",
        destination_font_size=9,
        destination_font_color="112233",
        train_type_font_name="ＭＳ ゴシック",
        train_type_font_size=11,
        train_type_font_color="445566",
        minute_font_mode="train_type",
        train_type_colors={entry.train_type.index: "00AA00"},
    )
    output_path = tmp_path / "fonts.xlsx"

    ExcelWriter(config).write(timetable, output_path)

    worksheet = load_workbook(output_path)[timetable.station_name]
    assert worksheet["B4"].font.name == "Arial"
    assert worksheet["B4"].font.sz == 9
    assert worksheet["B4"].font.color.rgb == "FF00AA00"
    assert worksheet["B5"].font.name == "ＭＳ ゴシック"
    assert worksheet["B5"].font.sz == 11
    assert worksheet["B5"].font.color.rgb == "FF00AA00"
    assert worksheet["B6"].font.color.rgb == "FF00AA00"


def test_write_same_row_items_with_independent_rich_text_styles(
    parsed_railway: Railway,
    tmp_path,
) -> None:
    station = parsed_railway.stations[1]
    source = StationTimetableGenerator(parsed_railway).generate(station)
    entry = _first_marked_entry(source.down)
    timetable = _single_entry_timetable(source, entry)
    config = TimetableDisplayConfig(
        destination_font_name="Arial",
        destination_font_size=9,
        destination_font_color="112233",
        train_type_font_name="ＭＳ ゴシック",
        train_type_font_size=11,
        train_type_font_color="445566",
    )
    output_path = tmp_path / "rich-text.xlsx"

    ExcelWriter(config).write(timetable, output_path)

    cell = load_workbook(output_path, rich_text=True)[timetable.station_name][
        "B4"
    ]
    assert isinstance(cell.value, CellRichText)
    assert str(cell.value) == (
        f"{entry.destination.display_name} {entry.train_type.name}"
    )
    assert cell.value[0].font.rFont == "Arial"
    assert cell.value[0].font.sz == 9
    assert cell.value[0].font.color.rgb == "FF112233"
    assert cell.value[2].font.rFont == "ＭＳ ゴシック"
    assert cell.value[2].font.sz == 11
    assert cell.value[2].font.color.rgb == "FF445566"


def test_write_striped_and_train_type_fills(
    parsed_railway: Railway,
    tmp_path,
) -> None:
    station = parsed_railway.stations[1]
    source = StationTimetableGenerator(parsed_railway).generate(station)
    entry = _first_marked_entry(source.down)
    timetable = StationTimetable(
        station_name=source.station_name,
        down=[
            TimetableHour(4, [entry]),
            TimetableHour(5, [entry]),
        ],
        up=[],
        train_types=source.train_types,
    )
    config = TimetableDisplayConfig(
        destination_position="top",
        train_type_position="bottom",
        train_fill="AA0000",
        train_type_fills={entry.train_type.index: "FFCC00"},
    )
    output_path = tmp_path / "fills.xlsx"

    ExcelWriter(config).write(timetable, output_path)

    worksheet = load_workbook(output_path)[timetable.station_name]
    assert worksheet["B4"].fill.fgColor.rgb == "FFFFCC00"
    assert worksheet["B5"].fill.fgColor.rgb == "FFFFCC00"
    assert worksheet["B6"].fill.fgColor.rgb == "FFFFCC00"

    config.train_type_fills.clear()
    config.train_fill = None
    config.striped_train_fill = True
    output_path = tmp_path / "striped.xlsx"
    ExcelWriter(config).write(timetable, output_path)
    worksheet = load_workbook(output_path)[timetable.station_name]
    assert worksheet["B4"].fill.fgColor.rgb == "FFC8E6C9"
    assert worksheet["B7"].fill.fgColor.rgb == "FFFAFAFA"

    config.striped_train_fill = False
    output_path = tmp_path / "unstriped.xlsx"
    ExcelWriter(config).write(timetable, output_path)
    worksheet = load_workbook(output_path)[timetable.station_name]
    assert worksheet["B4"].fill.fgColor.rgb == "FFFAFAFA"
    assert worksheet["B7"].fill.fgColor.rgb == "FFFAFAFA"


def test_write_center_hour_column_merges_asymmetric_hours(
    parsed_railway: Railway,
    tmp_path,
) -> None:
    station = parsed_railway.stations[1]
    source = StationTimetableGenerator(parsed_railway).generate(station)
    entry = _first_marked_entry(source.down)
    timetable = StationTimetable(
        station_name=source.station_name,
        down=[
            TimetableHour(4, [entry]),
            TimetableHour(7, []),
        ],
        up=[
            TimetableHour(5, [entry]),
            TimetableHour(7, []),
        ],
        train_types=source.train_types,
    )
    config = TimetableDisplayConfig(hour_column_mode="center")
    output_path = tmp_path / "center.xlsx"

    ExcelWriter(config).write(timetable, output_path)

    worksheet = load_workbook(output_path)[timetable.station_name]
    assert worksheet["A3"].value == "下り"
    assert worksheet["C3"].value == "上り"
    assert [worksheet.cell(row=row, column=2).value for row in (4, 6, 8)] == [
        4,
        5,
        7,
    ]
