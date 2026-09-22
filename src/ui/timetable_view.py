import tkinter as tk

from src.models.timetable import StationTimetable, TimetableHour


class TimetableView:
    """駅時刻表を表示するUI部品。"""

    def __init__(self, parent: tk.Misc) -> None:
        self.frame = tk.Frame(parent)

        self.text = tk.Text(
            self.frame,
            height=20,
            width=60,
            state=tk.DISABLED,
        )
        self.text.pack(
            fill=tk.BOTH,
            expand=True,
        )

    def show(self, timetable: StationTimetable) -> None:
        """駅時刻表を表示する。"""
        lines: list[str] = []

        lines.append(f"【{timetable.station_name}駅】")
        lines.append("")
        lines.append("【下り】")
        lines.extend(self._format_direction(timetable.down))

        lines.append("")
        lines.append("【上り】")
        lines.extend(self._format_direction(timetable.up))

        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", "\n".join(lines))
        self.text.config(state=tk.DISABLED)

    @staticmethod
    def _format_direction(
        hours: list[TimetableHour],
    ) -> list[str]:
        """方向別の時刻表を表示用文字列に変換する。"""
        lines: list[str] = []

        for hour in hours:
            if not hour.entries:
                continue

            for entry in hour.entries:
                lines.append(
                    f"{hour.hour:02d}:{entry.minute:02d} "
                    f"{entry.train_type.name} "
                    f"{entry.destination}"
                )

        return lines

    def clear(self) -> None:
        """時刻表表示をクリアする。"""
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.config(state=tk.DISABLED)
