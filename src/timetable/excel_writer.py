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

        max_column = (
            max(
                self._max_entry_count(timetable.down),
                self._max_entry_count(timetable.up),
            )
            + 1
        )

        row = 3

        row = self._write_direction(
            worksheet=worksheet,
            row=row,
            title="下り",
            hours=timetable.down,
            max_column=max_column,
        )

        row += 2

        end_row = self._write_direction(
            worksheet=worksheet,
            row=row,
            title="上り",
            hours=timetable.up,
            max_column=max_column,
        )

        self._apply_layout(
            worksheet,
            max_column=max_column,
            table_end_row=end_row,
        )

        workbook.save(output_path)


    @staticmethod
    def _max_entry_count(hours: list[TimetableHour]) -> int:
        """1時間あたりの最大列車本数を求める(見出し・列幅の基準)。"""
        if not hours:
            return 0
        return max(len(hour.entries) for hour in hours)


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
        max_column: int,
    ) -> int:
        """指定方向の駅時刻表を書き込む。"""
        title_row = row

        worksheet.cell(
            row=title_row,
            column=1,
            value=title,
        )

        # 「下り」「上り」見出しを表全体の幅まで横結合
        worksheet.merge_cells(
            start_row=title_row,
            start_column=1,
            end_row=title_row,
            end_column=max_column,
        )

        row += 1

        for hour in hours:
            worksheet.cell(
                row=row,
                column=1,
                value=hour.hour,
            )

            # 時刻(A列)を3行分縦結合
            worksheet.merge_cells(
                start_row=row,
                start_column=1,
                end_row=row + 2,
                end_column=1,
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
    def _apply_layout(
        worksheet,
        max_column: int,
        table_end_row: int,
    ) -> None:
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
        for column in range(2, max_column + 1):
            column_letter = worksheet.cell(
                row=1,
                column=column,
            ).column_letter

            worksheet.column_dimensions[
                column_letter
            ].width = 10


        # 表全体(空欄セルも含む)に罫線・中央揃えを適用
        for row in worksheet.iter_rows(
            min_row=3,
            max_row=table_end_row - 1,
            min_col=1,
            max_col=max_column,
        ):
            for cell in row:
                cell.alignment = alignment
                cell.border = border

        # 行高
        for row in range(1, worksheet.max_row + 1):
            worksheet.row_dimensions[row].height = 20

        # タイトル
        worksheet.row_dimensions[1].height = 28

    