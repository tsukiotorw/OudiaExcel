from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from src.models.timetable import (
    StationTimetable,
    TimetableHour,
)

from src.timetable.display_config import TimetableDisplayConfig

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


        down_width = self._max_entry_count(timetable.down) + 1
        up_width = self._max_entry_count(timetable.up) + 1

        down_start_column = 1

        up_start_column = (
            down_start_column
            + down_width
            + self._DIRECTION_GAP
        )

        start_row = 3

        self._write_title(
            worksheet=worksheet,
            station_name=timetable.station_name,
            title_column=up_start_column,
        )


        down_end_row = self._write_direction(
            worksheet=worksheet,
            row=start_row,
            start_column=down_start_column,
            title="下り",
            hours=timetable.down,
            width=down_width,
        )

        up_end_row = self._write_direction(
            worksheet=worksheet,
            row=start_row,
            start_column=up_start_column,
            title="上り",
            hours=timetable.up,
            width=up_width,
        )

        table_end_row = max(
            down_end_row,
            up_end_row,
        )

        self._apply_layout(
            worksheet=worksheet,
            down_start_column=down_start_column,
            down_width=down_width,
            up_start_column=up_start_column,
            up_width=up_width,
            table_end_row=table_end_row,
        )

        self._write_legend(
            worksheet=worksheet,
            row=table_end_row + 1,
            start_column=down_start_column,
            end_column=up_start_column + up_width - 1,
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


    def _write_direction(
        self,
        worksheet,
        row: int,
        start_column: int,
        title: str,
        hours: list[TimetableHour],
        width: int,
    ) -> int:
        end_column = start_column + width - 1

        # ヘッダ
        header_fill = self._create_fill(
            self.display_config.header_fill
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

        row += 1

        # 時刻表
        for hour_index, hour in enumerate(hours):
            metadata_row = row
            minute_row = row + 1

            timetable_fill = self._create_fill(
                self.display_config.timetable_alt_fill
                if hour_index % 2 == 0
                else self.display_config.timetable_fill
            )

            hour_fill = self._create_fill(
                self.display_config.hour_fill
            )

            train_fill = self._create_fill(
                self.display_config.train_fill
            )

            hour_cell_fill = hour_fill or timetable_fill
            train_cell_fill = train_fill or timetable_fill

            # 時刻欄
            hour_cell = worksheet.cell(
                row=metadata_row,
                column=start_column,
                value=hour.hour,
            )
            hour_cell.font = Font(
                name=self.display_config.hour_font_name,
                size=self.display_config.hour_font_size,
                bold=True,
                color=self._to_excel_color(
                    self.display_config.hour_font_color
                ),
            )
            hour_cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
            )
            hour_cell.fill = hour_cell_fill or PatternFill()

            hour_cell.border = self._create_border(
                self.display_config.hour_border
            )

            minute_hour_cell = worksheet.cell(
                row=minute_row,
                column=start_column,
            )
            minute_hour_cell.fill = hour_cell_fill or PatternFill()

            worksheet.merge_cells(
                start_row=metadata_row,
                start_column=start_column,
                end_row=minute_row,
                end_column=start_column,
            )

            # 列車
            for column, entry in enumerate(
                hour.entries,
                start=start_column + 1,
            ):
                metadata = self._format_entry_metadata(entry)

                train_type_color = self.display_config.get_train_type_color(
                    entry.train_type.index
                )

                metadata_font_color = (
                    train_type_color
                    if train_type_color is not None
                    else self.display_config.train_font_color
                )

                metadata_cell = worksheet.cell(
                    row=metadata_row,
                    column=column,
                    value=metadata,
                )

                metadata_cell.font = Font(
                    name=self.display_config.metadata_font_name,
                    size=self.display_config.metadata_font_size,
                    color=self._to_excel_color(metadata_font_color),
                )

                metadata_cell.alignment = Alignment(
                    horizontal="center",
                    vertical="center",
                    wrap_text=True,
                )

                metadata_cell.fill = train_cell_fill or PatternFill()

                metadata_cell.border = self._create_border(
                    self.display_config.train_border
                )

                minute_cell = worksheet.cell(
                    row=minute_row,
                    column=column,
                    value=entry.minute,
                )

                minute_cell.font = Font(
                    name=self.display_config.minute_font_name,
                    size=self.display_config.minute_font_size,
                    bold=True,
                    color=self._to_excel_color(
                        self.display_config.train_font_color
                    ),
                )

                minute_cell.alignment = Alignment(
                    horizontal="center",
                    vertical="center",
                )
                
                minute_cell.fill = train_cell_fill or PatternFill()

                separator = self.display_config.train_separator

                if separator.enabled:
                    minute_cell.border = Border(
                        top=self._create_border_side(separator),
                    )

            row += self._HOUR_ROWS

        return row

    @staticmethod
    def _apply_layout(
        worksheet,
        down_start_column: int,
        down_width: int,
        up_start_column: int,
        up_width: int,
        table_end_row: int,
    ) -> None:
        """時刻表全体のレイアウトを設定する。"""

        alignment = Alignment(
            horizontal="center",
            vertical="center",
        )

        border_side = Side(
            style="thin",
            color="FFFAFAFA",
        )

        for start_column, width in (
            (down_start_column, down_width),
            (up_start_column, up_width),
        ):
            end_column = start_column + width - 1

            # 時刻列
            worksheet.column_dimensions[
                get_column_letter(start_column)
            ].width = 4

            # 列車列
            for column in range(
                start_column + 1,
                end_column + 1,
            ):
                worksheet.column_dimensions[
                    get_column_letter(column)
                ].width = 7

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

        # 行高
        worksheet.row_dimensions[1].height = 28
        worksheet.row_dimensions[3].height = 24

        for row in range(4, table_end_row):
            if (row - 4) % 2 == 0:
                worksheet.row_dimensions[row].height = 18
            else:
                worksheet.row_dimensions[row].height = 20


    def _format_entry_metadata(self, entry) -> str:
        """列車の行先・種別を駅時刻表用の文字列に変換する。"""
        config = self.display_config

        parts = []

        if (
            config.show_destination
            and not entry.destination.is_no_mark
        ):
            parts.append(entry.destination.display_name)

        if config.train_type_column_visible.get(
            entry.train_type.index,
            True,
        ):
            train_type_name = (
                entry.train_type.short_name
                if (
                    config.use_train_type_short_name
                    and entry.train_type.short_name
                )
                else entry.train_type.name
            )

            if train_type_name:
                parts.append(train_type_name)

        return " ".join(parts)


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
        start_column: int,
        end_column: int,
        up_start_column: int,
        timetable: StationTimetable,
    ) -> int:
        """下り・上りそれぞれの列車種別と行先凡例を書き込む。"""
        config = self.display_config

        train_types = [
            train_type
            for train_type in timetable.train_types
            if config.train_type_visible.get(train_type.index, True)
        ]

        def collect_station_items(hours: list[TimetableHour]) -> list[str]:
            items: list[str] = []
            seen: set[tuple[int, str]] = set()

            if not config.show_destination_legend:
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

        down_items = collect_station_items(timetable.down)
        up_items = collect_station_items(timetable.up)

        if not train_types and not down_items and not up_items:
            return row

        has_station_items = bool(down_items or up_items)
        legend_rows = int(bool(train_types)) + int(has_station_items)
        legend_end_row = row + legend_rows - 1

        label_fill = self._create_fill(config.legend_label_fill)
        legend_fill = self._create_fill(config.legend_fill)
        border = self._create_border(config.legend_border)

        def write_label(column: int) -> None:
            worksheet.merge_cells(
                start_row=row,
                start_column=column,
                end_row=legend_end_row,
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

        def write_train_types(column: int) -> None:
            for index, train_type in enumerate(train_types):
                name = (
                    train_type.short_name
                    if config.use_train_type_short_name and train_type.short_name
                    else train_type.name
                )
                cell = worksheet.cell(
                    row=row,
                    column=column + 1 + index,
                    value=name,
                )
                cell.font = Font(
                    name=config.legend_font_name,
                    size=config.legend_font_size,
                    color=self._to_excel_color(
                        config.get_train_type_color(train_type.index)
                    ),
                )
                cell.alignment = Alignment(
                    horizontal="left",
                    vertical="center",
                    wrap_text=True,
                )
                cell.fill = legend_fill or PatternFill()
                cell.border = border

        def write_station_items(
            items: list[str],
            row_number: int,
            column: int,
        ) -> None:
            for index, item in enumerate(items):
                cell = worksheet.cell(
                    row=row_number,
                    column=column + 1 + index,
                    value=item,
                )
                cell.font = Font(
                    name=config.legend_font_name,
                    size=config.legend_font_size,
                )
                cell.alignment = Alignment(
                    horizontal="left",
                    vertical="center",
                    wrap_text=True,
                )
                cell.fill = legend_fill or PatternFill()
                cell.border = border

        # 下り側の凡例
        write_label(start_column)
        if train_types:
            write_train_types(start_column)
        if down_items:
            station_row = row + int(bool(train_types))
            write_station_items(down_items, station_row, start_column)

        # 上り側の凡例：上りの時刻列にラベル、その右から項目を配置
        write_label(up_start_column)
        if train_types:
            write_train_types(up_start_column)
        if up_items:
            station_row = row + int(bool(train_types))
            write_station_items(up_items, station_row, up_start_column)

        for current_row in range(row, legend_end_row + 1):
            worksheet.row_dimensions[current_row].height = (
                config.legend_row_height
            )

        return legend_end_row + 1


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
