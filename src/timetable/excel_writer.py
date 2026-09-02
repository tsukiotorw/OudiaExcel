from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Side

from src.models.timetable import (
    StationTimetable,
    TimetableHour,
)


class ExcelWriter:
    """StationTimetableをExcelファイルへ出力する。"""

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

        self._write_title(
            worksheet=worksheet,
            station_name=timetable.station_name,
        )

        row = 3

        row = self._write_direction(
            worksheet=worksheet,
            row=row,
            title="下り",
            hours=timetable.down,
        )

        row += 2

        self._write_direction(
            worksheet=worksheet,
            row=row,
            title="上り",
            hours=timetable.up,
        )

        self._apply_layout(worksheet)

        workbook.save(output_path)

    @staticmethod
    def _write_title(
        worksheet,
        station_name: str,
    ) -> None:
        """駅名タイトルを書き込む。"""
        worksheet.cell(
            row=1,
            column=1,
            value=f"{station_name} 時刻表",
        )

    @staticmethod
    def _write_direction(
        worksheet,
        row: int,
        title: str,
        hours: list[TimetableHour],
    ) -> int:
        """指定方向の駅時刻表を書き込む。"""
        worksheet.cell(
            row=row,
            column=1,
            value=title,
        )
        row += 1

        for hour in hours:
            worksheet.cell(
                row=row,
                column=1,
                value=hour.hour,
            )

            for column, entry in enumerate(
                hour.entries,
                start=2,
            ):
                worksheet.cell(
                    row=row,
                    column=column,
                    value=entry.minute,
                )

                worksheet.cell(
                    row=row + 1,
                    column=column,
                    value=entry.destination,
                )

                worksheet.cell(
                    row=row + 2,
                    column=column,
                    value=entry.train_type.short_name,
                )

            row += 3

        return row

    @staticmethod
    def _apply_layout(worksheet) -> None:
        """ワークシートの基本レイアウトを設定する。"""
        alignment = Alignment(
            horizontal="center",
            vertical="center",
        )

        thin = Side(style="thin")

        border = Border(
            left=thin,
            right=thin,
            top=thin,
            bottom=thin,
        )

        # 時刻列
        worksheet.column_dimensions["A"].width = 6

        # 列車列
        for column in range(2, worksheet.max_column + 1):
            column_letter = worksheet.cell(
                row=1,
                column=column,
            ).column_letter

            worksheet.column_dimensions[
                column_letter
            ].width = 10

        # 使用セルの書式
        for row in worksheet.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue

                cell.alignment = alignment
                cell.border = border

        # 行高
        for row in range(1, worksheet.max_row + 1):
            worksheet.row_dimensions[row].height = 20

        # タイトル
        worksheet.row_dimensions[1].height = 28
    