from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

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

        row = 1

        row = self._write_direction(
            worksheet=worksheet,
            row=row,
            title="下り",
            hours=timetable.down,
        )

        row += 1

        self._write_direction(
            worksheet=worksheet,
            row=row,
            title="上り",
            hours=timetable.up,
        )

        workbook.save(output_path)

    @staticmethod
    def _write_direction(
        worksheet,
        row: int,
        title: str,
        hours: list[TimetableHour],
    ) -> int:
        """指定方向の時刻表を書き込む。"""
        worksheet.cell(row=row, column=1, value=title)
        row += 1

        worksheet.cell(row=row, column=1, value="時")
        worksheet.cell(row=row, column=2, value="分")
        worksheet.cell(row=row, column=3, value="行先")
        worksheet.cell(row=row, column=4, value="種別")
        row += 1

        for hour in hours:
            for entry in hour.entries:
                worksheet.cell(
                    row=row,
                    column=1,
                    value=hour.hour,
                )
                worksheet.cell(
                    row=row,
                    column=2,
                    value=entry.minute,
                )
                worksheet.cell(
                    row=row,
                    column=3,
                    value=entry.destination,
                )
                worksheet.cell(
                    row=row,
                    column=4,
                    value=entry.train_type.name,
                )

                row += 1

        return row
