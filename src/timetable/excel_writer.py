from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.cell.rich_text import CellRichText, InlineFont, TextBlock
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from src.models.timetable import (
    TimetableEntry,
    StationTimetable,
    TimetableHour,
)
from src.models.train_type import TrainType

from src.timetable.display_config import TimetableDisplayConfig
from src.timetable.display_layout import (
    HourSlot,
    get_entry_layout,
    merge_timetable_hours,
)

class ExcelWriter:
    """StationTimetableをExcelファイルへ出力する。"""

    _DIRECTION_GAP = 2
    _HOUR_ROWS = 2

    def __init__(
        self,
        display_config: TimetableDisplayConfig | None = None,
    ) -> None:
        self.display_config = (
            display_config
            if display_config is not None
            else TimetableDisplayConfig()
        )

    def write(
        self,
        timetable: StationTimetable,
        output_path: Path,
    ) -> None:
        """駅時刻表をExcelファイルとして出力する。"""
        workbook = Workbook()
        worksheet = workbook.active

        if worksheet is None:
            raise RuntimeError("ワークシートを取得できません。")

        worksheet.title = timetable.station_name


        start_row = 3
        slots = merge_timetable_hours(timetable.down, timetable.up)
        down_train_width = max(
            max((len(slot.down_entries) for slot in slots), default=0),
            1,
        )
        up_train_width = max(
            max((len(slot.up_entries) for slot in slots), default=0),
            1,
        )
        central_hour_column = self.display_config.hour_column_mode == "center"

        up_start_column = 1
        if central_hour_column:
            up_width = up_train_width
            central_column = up_start_column + up_width
            down_start_column = central_column + 1
            down_width = down_train_width
            title_column = central_column + 1
            column_groups = (
                (up_start_column, up_width),
                (central_column, 1),
                (down_start_column, down_width),
            )
            column_widths = {
                **{
                    column: self.display_config.train_column_width
                    for column in range(
                        up_start_column,
                        up_start_column + up_width,
                    )
                },
                central_column: 4,
                **{
                    column: self.display_config.train_column_width
                    for column in range(
                        down_start_column,
                        down_start_column + down_width,
                    )
                },
            }
            train_starts = (up_start_column, down_start_column)
            hour_columns = (central_column, central_column)
        else:
            up_width = up_train_width + 1
            down_width = down_train_width + 1
            down_start_column = (
                up_start_column
                + up_width
                + self._DIRECTION_GAP
            )
            title_column = down_start_column
            column_groups = (
                (up_start_column, up_width),
                (down_start_column, down_width),
            )
            column_widths = {
                up_start_column: 4,
                down_start_column: 4,
                **{
                    column: self.display_config.train_column_width
                    for column in range(
                        up_start_column + 1,
                        up_start_column + up_width,
                    )
                },
                **{
                    column: self.display_config.train_column_width
                    for column in range(
                        down_start_column + 1,
                        down_start_column + down_width,
                    )
                },
            }
            train_starts = (
                up_start_column + 1,
                down_start_column + 1,
            )
            hour_columns = (up_start_column, down_start_column)

        self._write_title(
            worksheet=worksheet,
            station_name=timetable.station_name,
            title_column=title_column,
        )
        self._write_direction_header(
            worksheet,
            start_row,
            up_start_column,
            self.display_config.up_header_text,
            up_width,
            "up",
        )
        self._write_direction_header(
            worksheet,
            start_row,
            down_start_column,
            self.display_config.down_header_text,
            down_width,
            "down",
        )
        if central_hour_column:
            header_cell = worksheet.cell(
                row=start_row,
                column=hour_columns[0],
            )
            header_cell.fill = self._create_fill(
                self.display_config.header_fill
            ) or PatternFill()
            header_cell.border = self._create_border(
                self.display_config.header_border
            )

        row = start_row + 1
        for slot in slots:
            row_count = self._hour_row_count(slot)
            self._write_hour_column(
                worksheet,
                row,
                hour_columns[0],
                slot.hour if central_hour_column or slot.up_present else None,
                slot.hour,
                row_count,
                "up" if central_hour_column else "up",
            )
            if not central_hour_column:
                self._write_hour_column(
                    worksheet,
                    row,
                    hour_columns[1],
                    slot.hour if slot.down_present else None,
                    slot.hour,
                    row_count,
                    "down",
                )
            self._write_hour_entries(
                worksheet,
                row,
                train_starts[0],
                slot.up_entries,
                slot.hour,
                row_count,
                "up",
            )
            self._write_hour_entries(
                worksheet,
                row,
                train_starts[1],
                slot.down_entries,
                slot.hour,
                row_count,
                "down",
            )
            self._set_hour_row_heights(worksheet, row, row_count)
            row += row_count

        table_end_row = row
        self._apply_layout(
            worksheet=worksheet,
            column_groups=column_groups,
            column_widths=column_widths,
            table_end_row=table_end_row,
        )

        self._write_legend(
            worksheet=worksheet,
            row=table_end_row + 1,
            down_start_column=down_start_column,
            up_start_column=up_start_column,
            timetable=timetable,
        )

        workbook.save(output_path)


    @staticmethod
    def _max_entry_count(
        hours: list[TimetableHour],
    ) -> int:
        """1時間あたりの最大列車本数を求める。"""
        if not hours:
            return 0

        return max(
            len(hour.entries)
            for hour in hours
        )


    def _write_title(
        self,
        worksheet,
        station_name: str,
        title_column: int = 11,
    ) -> None:
        """駅名タイトルを書き込む。"""
        config = self.display_config

        cell = worksheet.cell(
            row=1,
            column=title_column - 1,
            value=f"{station_name}駅 時刻表",
        )

        cell.font = Font(
            name=config.title_font_name,
            size=config.title_font_size,
            bold=True,
            color=self._to_excel_color(
                config.title_font_color
            ),
        )

        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
        )

        title_fill = self._create_fill(config.title_fill)
        if title_fill is not None:
            cell.fill = title_fill

        cell.border = self._create_border(
            config.title_border
        )


    def _write_direction_header(
        self,
        worksheet,
        row: int,
        start_column: int,
        title: str,
        width: int,
        direction: str,
    ) -> None:
        end_column = start_column + width - 1
        direction_fill = (
            self.display_config.up_header_fill
            if direction == "up"
            else self.display_config.down_header_fill
        )
        header_fill = self._create_fill(
            direction_fill or self.display_config.header_fill
        )

        for column in range(start_column, end_column + 1):
            cell = worksheet.cell(
                row=row,
                column=column,
            )
            cell.fill = header_fill or PatternFill()

            cell.border = self._create_border(
                self.display_config.header_border
            )

            if column == start_column:
                cell.value = title
                cell.font = Font(
                    name=self.display_config.header_font_name,
                    size=self.display_config.header_font_size,
                    bold=True,
                    color=self._to_excel_color(
                        self.display_config.header_font_color
                    ),
                )

            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
            )

        worksheet.merge_cells(
            start_row=row,
            start_column=start_column,
            end_row=row,
            end_column=end_column,
        )

    def _hour_row_count(self, slot: HourSlot) -> int:
        counts = [
            len(get_entry_layout(entry, self.display_config))
            for entry in (*slot.down_entries, *slot.up_entries)
        ]
        if counts:
            return max(counts)
        if (
            self.display_config.destination_position == "bottom"
            or self.display_config.train_type_position == "bottom"
        ):
            return 3
        return self._HOUR_ROWS

    def _write_hour_column(
        self,
        worksheet,
        row: int,
        column: int,
        hour: int | None,
        stripe_hour: int,
        row_count: int,
        direction: str = "up",
    ) -> None:
        config = self.display_config
        hour_fill = self._create_fill(config.hour_fill)
        hour_order = (
            (stripe_hour - 4) % 24
            if 0 <= stripe_hour < 24
            else stripe_hour
        )
        body_fill = self._create_fill(
            (
                config.get_up_timetable_fill(alternate=True)
                if config.striped_train_fill and hour_order % 2 == 0
                else config.get_up_timetable_fill()
            )
        )
        if direction == "down":
            body_fill = self._create_fill(
                config.down_timetable_alt_fill
                if config.striped_train_fill and hour_order % 2 == 0
                else config.down_timetable_fill
            )
        fill = hour_fill or body_fill or PatternFill()

        for row_offset in range(row_count):
            worksheet.cell(
                row=row + row_offset,
                column=column,
            ).fill = fill

        cell = worksheet.cell(row=row, column=column, value=hour)
        cell.font = Font(
            name=config.hour_font_name,
            size=config.hour_font_size,
            bold=True,
            color=self._to_excel_color(config.hour_font_color),
        )
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
        )
        cell.border = self._create_border(config.hour_border)
        worksheet.merge_cells(
            start_row=row,
            start_column=column,
            end_row=row + row_count - 1,
            end_column=column,
        )

    def _write_hour_entries(
        self,
        worksheet,
        row: int,
        start_column: int,
        entries: list[TimetableEntry],
        hour: int,
        row_count: int,
        direction: str = "up",
    ) -> None:
        for column, entry in enumerate(entries, start=start_column):
            entry_rows = get_entry_layout(entry, self.display_config)
            for row_offset in range(row_count):
                kinds = (
                    entry_rows[row_offset]
                    if row_offset < len(entry_rows)
                    else []
                )
                cell = worksheet.cell(
                    row=row + row_offset,
                    column=column,
                )

                has_metadata = any(
                    kind in ("destination", "train_type")
                    for kind in kinds
                )
                has_minute = "minute" in kinds

                fill_color = (
                    self.display_config.train_type_fills.get(
                        entry.train_type.index
                    )
                    if has_metadata
                    else None
                )

                minute_highlight_fill = (
                    self.display_config
                    .get_train_type_minute_highlight_fill(
                        entry.train_type.index
                    )
                    if has_minute
                    else None
                )

                config = self.display_config
                if (
                    has_metadata
                    and config.is_striped_train_fill_for_metadata()
                ):
                    # 行先・列車種別欄は時間帯別背景色を優先
                    fill = config.get_entry_fill(hour, direction)

                elif (
                    has_minute
                    and config.is_striped_train_fill_for_minute()
                ):
                    # 分欄は時間帯別背景色を優先
                    hour_order = (
                        (hour - 4) % 24
                        if 0 <= hour < 24
                        else hour
                    )
                    alternate = hour_order % 2 == 0

                    if direction == "down":
                        fill = (
                            config.down_timetable_alt_fill
                            if alternate
                            else config.down_timetable_fill
                        )
                    else:
                        fill = config.get_up_timetable_fill(
                            alternate=alternate
                        )

                else:
                    # 時間帯別背景色を使わない欄は個別設定を優先
                    fill = (
                        minute_highlight_fill
                        or fill_color
                        or config.get_entry_fill(hour, direction)
                    )

                cell.fill = self._create_fill(fill) or PatternFill()

                cell.alignment = Alignment(
                    horizontal="center",
                    vertical="center",
                    wrap_text=True,
                )
                cell.border = self._create_border(
                    self.display_config.train_border
                )

                if not kinds:
                    continue

                rendered = [
                    (
                        kind,
                        self._entry_item_value(entry, kind),
                        self.display_config.get_entry_font_settings(
                            kind,
                            entry.train_type.index,
                        ),
                    )
                    for kind in kinds
                ]
                cell_color = rendered[0][2][2]
                if len(rendered) > 1:
                    cell_color = (
                        self.display_config.get_train_type_color(
                            entry.train_type.index
                        )
                        or cell_color
                    )
                cell.font = Font(
                    name=rendered[0][2][0],
                    size=rendered[0][2][1],
                    color=self._to_excel_color(cell_color),
                    bold=rendered[0][0] == "minute",
                )
                if len(rendered) == 1:
                    cell.value = rendered[0][1]
                else:
                    rich_text = CellRichText()
                    for index, (_, text, style) in enumerate(rendered):
                        if index:
                            rich_text.append(
                                TextBlock(
                                    InlineFont(
                                        rFont=style[0],
                                        sz=style[1],
                                        color=self._to_excel_color(style[2]),
                                    ),
                                    " ",
                                )
                            )
                        rich_text.append(
                            TextBlock(
                                InlineFont(
                                    rFont=style[0],
                                    sz=style[1],
                                    color=self._to_excel_color(style[2]),
                                ),
                                str(text),
                            )
                        )
                    cell.value = rich_text

                if "minute" in kinds:
                    separator = self.display_config.train_separator
                    if separator.enabled:
                        cell.border = Border(
                            top=self._create_border_side(separator),
                        )

    def _entry_item_value(self, entry, kind: str):
        if kind == "destination":
            return entry.destination.display_name
        if kind == "train_type":
            return (
                entry.train_type.short_name
                if (
                    self.display_config.use_train_type_short_name
                    and entry.train_type.short_name
                )
                else entry.train_type.name
            )
        if kind == "minute":
            return entry.minute
        raise ValueError(f"不明な列車欄項目です: {kind}")

    def _set_hour_row_heights(
        self,
        worksheet,
        row: int,
        row_count: int,
    ) -> None:
        config = self.display_config

        if row_count == 2:
            heights = (
                config.train_upper_row_height,
                config.train_lower_row_height,
            )
        else:
            heights = (
                config.train_upper_row_height,
                18,
                config.train_lower_row_height,
            )

        for offset in range(row_count):
            worksheet.row_dimensions[row + offset].height = heights[
                min(offset, len(heights) - 1)
            ]

    @staticmethod
    def _apply_layout(
        worksheet,
        column_groups: tuple[tuple[int, int], ...],
        column_widths: dict[int, float],
        table_end_row: int,
    ) -> None:
        """時刻表全体のレイアウトを設定する。"""

        alignment = Alignment(
            horizontal="center",
            vertical="center",
        )

        for start_column, width in column_groups:
            end_column = start_column + width - 1

            for column in range(start_column, end_column + 1):
                worksheet.column_dimensions[
                    get_column_letter(column)
                ].width = column_widths[column]

            # ヘッダ
            for column in range(
                start_column,
                end_column + 1,
            ):
                cell = worksheet.cell(
                    row=3,
                    column=column,
                )
                cell.alignment = alignment

            # 時刻表本体
            for row in range(4, table_end_row):
                for column in range(
                    start_column,
                    end_column + 1,
                ):
                    cell = worksheet.cell(
                        row=row,
                        column=column,
                    )

                    cell.alignment = alignment

        worksheet.row_dimensions[1].height = 28
        worksheet.row_dimensions[3].height = 24


    def _format_entry_metadata(self, entry) -> str:
        """列車の行先・種別を駅時刻表用の文字列に変換する。"""
        return " ".join(
            self._entry_item_value(entry, kind)
            for row in get_entry_layout(entry, self.display_config)
            for kind in row
            if kind != "minute"
        )


    @staticmethod
    def _to_excel_color(
        color: str | None,
    ) -> str | None:
        """RGB色をExcel用ARGB色へ変換する。"""
        if color is None:
            return None

        if len(color) == 6:
            return f"FF{color}"

        if len(color) == 8:
            return color

        raise ValueError(
            f"色は6桁または8桁の16進数で指定してください: {color}"
        )


    @staticmethod
    def _create_fill(
        color: str | None,
    ) -> PatternFill | None:
        """塗りつぶし色からExcel用のFillを生成する。"""
        if color is None:
            return None

        return PatternFill(
            fill_type="solid",
            fgColor=ExcelWriter._to_excel_color(color),
        )


    def _write_legend(
        self,
        worksheet,
        row: int,
        down_start_column: int,
        up_start_column: int,
        timetable: StationTimetable,
    ) -> int:
        """下り・上りそれぞれの列車種別と行先凡例を書き込む。"""
        config = self.display_config
        if not config.show_legend:
            return row

        train_types = [
            train_type
            for train_type in timetable.train_types
            if config.train_type_visible.get(train_type.index, True)
            and config.show_train_type_legend
        ]

        def collect_station_items(
            hours: list[TimetableHour],
            direction: str,
        ) -> list[str]:
            items: list[str] = []
            seen: set[tuple[int, str]] = set()

            direction_visible = (
                config.show_down_destination_legend
                if direction == "down"
                else config.show_up_destination_legend
            )
            if (
                not config.show_destination_legend
                or not direction_visible
            ):
                return items

            for hour in hours:
                for entry in hour.entries:
                    station = entry.destination
                    key = (station.index, station.name)

                    if key in seen:
                        continue
                    seen.add(key)

                    if station.is_no_mark:
                        items.append(f"無印＝{station.name}")
                    elif station.short_name:
                        items.append(f"{station.short_name}＝{station.name}")

            return items

        down_items = collect_station_items(timetable.down, "down")
        up_items = collect_station_items(timetable.up, "up")

        if not train_types and not down_items and not up_items:
            return row

        label_fill = self._create_fill(config.legend_label_fill)
        legend_fill = self._create_fill(config.legend_fill)
        border = self._create_border(config.legend_border)

        slots = merge_timetable_hours(timetable.down, timetable.up)

        def available_columns(is_down: bool) -> int:
            width = max(
                max(
                    (
                        len(
                            slot.down_entries
                            if is_down
                            else slot.up_entries
                        )
                        for slot in slots
                    ),
                    default=0,
                ),
                1,
            )
            if config.hour_column_mode == "center":
                width -= 1
            return max(width, 0)

        def write_label(column: int, end_row: int) -> None:
            if end_row > row:
                worksheet.merge_cells(
                    start_row=row,
                    start_column=column,
                    end_row=end_row,
                    end_column=column,
                )
            cell = worksheet.cell(row=row, column=column, value="凡例")
            cell.font = Font(
                name=config.legend_label_font_name,
                size=config.legend_label_font_size,
                color=self._to_excel_color(config.legend_label_font_color),
            )
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
            )
            cell.fill = label_fill or PatternFill()
            cell.border = border

        def write_train_type(
            train_type: TrainType,
            row_number: int,
            column: int,
        ) -> None:
            name = (
                train_type.short_name
                if config.use_train_type_short_name and train_type.short_name
                else train_type.name
            )
            cell = worksheet.cell(
                row=row_number,
                column=column,
                value=name,
            )
            cell.font = Font(
                name=config.legend_font_name,
                size=config.legend_font_size,
                color=self._to_excel_color(
                    config.get_train_type_color(train_type.index)
                    or config.legend_font_color
                ),
            )
            cell.alignment = Alignment(
                horizontal="left",
                vertical="center",
                wrap_text=True,
            )
            cell.fill = legend_fill or PatternFill()
            cell.border = border

        def write_station_item(
            item: str,
            row_number: int,
            column: int,
        ) -> None:
            cell = worksheet.cell(
                row=row_number,
                column=column,
                value=item,
            )
            cell.font = Font(
                name=config.legend_font_name,
                size=config.legend_font_size,
                color=self._to_excel_color(config.legend_font_color),
            )
            cell.alignment = Alignment(
                horizontal="left",
                vertical="center",
                wrap_text=True,
            )
            cell.fill = legend_fill or PatternFill()
            cell.border = border

        def write_direction(
            column: int,
            capacity: int,
            station_items: list[str],
        ) -> int:
            if capacity == 0:
                row_count = 1 + len(train_types) + len(station_items)
                write_label(column, row)
                for index, train_type in enumerate(train_types):
                    write_train_type(train_type, row + 1 + index, column)
                for index, item in enumerate(station_items):
                    write_station_item(
                        item,
                        row + 1 + len(train_types) + index,
                        column,
                    )
                return row_count

            train_type_rows = (
                len(train_types) + capacity - 1
            ) // capacity
            station_rows = (
                len(station_items) + capacity - 1
            ) // capacity
            row_count = max(1, train_type_rows + station_rows)
            write_label(column, row + row_count - 1)

            for index, train_type in enumerate(train_types):
                write_train_type(
                    train_type,
                    row + index // capacity,
                    column + 1 + index % capacity,
                )
            for index, item in enumerate(station_items):
                write_station_item(
                    item,
                    row + train_type_rows + index // capacity,
                    column + 1 + index % capacity,
                )
            return row_count

        down_rows = write_direction(
            down_start_column,
            available_columns(is_down=True),
            down_items,
        )
        up_rows = write_direction(
            up_start_column,
            available_columns(is_down=False),
            up_items,
        )
        legend_rows = max(down_rows, up_rows)

        for current_row in range(row, row + legend_rows):
            worksheet.row_dimensions[current_row].height = (
                config.legend_row_height
            )

        return row + legend_rows


    @classmethod
    def _create_border_side(
        cls,
        config,
    ) -> Side | None:
        """罫線設定からExcel用の罫線を生成する。"""
        if not config.enabled:
            return None

        style_map = {
            "thin": "thin",
            "medium": "medium",
            "thick": "thick",
            "dashed": "dashed",
            "dotted": "dotted",
            "double": "double",
        }

        style = style_map.get(config.style, "thin")

        return Side(
            style=style,
            color=cls._to_excel_color(config.color),
        )


    @classmethod
    def _create_border(
        cls,
        config,
    ) -> Border:
        """BorderConfigからExcel用の罫線を生成する。"""
        return Border(
            top=cls._create_border_side(config.top),
            bottom=cls._create_border_side(config.bottom),
            left=cls._create_border_side(config.left),
            right=cls._create_border_side(config.right),
        )
