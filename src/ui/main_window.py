from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk

from src.application.oud2_loader import load_oud2
from src.application.station_timetable import generate_station_timetable
from src.application.excel_export import export_station_timetable
from src.models.railway import Railway
from src.models.station import Station
from src.models.timetable import StationTimetable
from src.ui.timetable_view import TimetableView
from src.ui.timetable_preview import TimetablePreview
from src.timetable.display_config import TimetableDisplayConfig

class MainWindow:
    """OuDiaExcelのメインウィンドウ。"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("OuDiaExcel")
        self.root.geometry("1100x750")

        self.file_path = tk.StringVar()
        self.railway: Railway | None = None
        self.selected_station: Station | None = None
        self.selected_station_text = tk.StringVar(value="未選択")

        self.station_timetable: StationTimetable | None = None
        self.display_config = TimetableDisplayConfig()

        self._create_widgets()


    def _create_widgets(self) -> None:
        """画面のウィジェットを作成する。"""
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        label = tk.Label(
            frame,
            text="OuDiaSecondファイル",
        )
        label.pack(anchor=tk.W)

        file_frame = tk.Frame(frame)
        file_frame.pack(fill=tk.X, pady=(8, 0))

        entry = tk.Entry(
            file_frame,
            textvariable=self.file_path,
        )
        entry.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
        )

        open_button = tk.Button(
            file_frame,
            text="ファイルを開く",
            command=self._open_file,
        )
        open_button.pack(
            side=tk.LEFT,
            padx=(8, 0),
        )

        station_label = tk.Label(
            frame,
            text="駅",
        )
        station_label.pack(anchor=tk.W)

        self.station_combo = ttk.Combobox(
            frame,
            textvariable=self.selected_station_text,
            state="readonly",
        )
        self.station_combo.pack(
            fill=tk.X,
            pady=(8, 0),
        )

        self.station_combo.bind(
            "<<ComboboxSelected>>",
            self._on_station_selected,
        )
 
        selected_frame = tk.Frame(frame)
        selected_frame.pack(
            fill=tk.X,
            pady=(10, 0),
        )

        selected_label = tk.Label(
            selected_frame,
            text="選択駅:",
        )
        selected_label.pack(side=tk.LEFT)

        selected_value = tk.Label(
            selected_frame,
            textvariable=self.selected_station_text,
        )
        selected_value.pack(side=tk.LEFT, padx=(8, 0))

        button_frame = tk.Frame(frame)
        button_frame.pack(
            anchor=tk.E,
            pady=(10, 0),
        )

        button_frame = tk.Frame(frame)
        button_frame.pack(
            anchor=tk.E,
            pady=(10, 0),
        )

        export_button = tk.Button(
            button_frame,
            text="Excel出力",
            command=self._export_excel,
        )
        export_button.pack()

        self.timetable_preview = TimetablePreview(
            frame,
            display_config=self.display_config,
        )
        self.timetable_preview.pack(
            fill=tk.BOTH,
            expand=True,
            pady=(15, 0),
        )

        self.timetable_view = TimetableView(frame)
        self.timetable_view.frame.pack(
            fill=tk.BOTH,
            expand=True,
            pady=(15, 0),
        )


    def _open_file(self) -> None:
        """OuDiaSecondファイルを選択して読み込む。"""
        selected_file = filedialog.askopenfilename(
            title="OuDiaSecondファイルを選択",
            filetypes=[
                ("OuDiaSecond files", "*.oud2"),
                ("All files", "*.*"),
            ],
        )

        if not selected_file:
            return

        self.file_path.set(str(Path(selected_file)))

        try:
            self.railway = load_oud2(Path(selected_file))
        except Exception as exc:
            self._show_message(
                "読み込みエラー",
                f"ファイルの読み込みに失敗しました。\n\n{exc}",
            )
            return

        self.selected_station = None
        self.station_timetable = None
        self.selected_station_text.set("未選択")
        self.timetable_view.clear()

        self._update_station_list()

        if self.railway.stations:
            self.station_combo.current(0)
            self._on_station_selected()


    def _update_station_list(self) -> None:
        """駅一覧を更新する。"""
        if self.railway is None:
            self.station_combo["values"] = ()
            return

        self.station_combo["values"] = [
            station.name
            for station in self.railway.stations
        ]


    def _on_station_selected(
        self,
        _event: tk.Event | None = None,
    ) -> None:
        """駅が選択されたときに時刻表を生成する。"""
        if self.railway is None:
            return

        station_name = self.selected_station_text.get()

        self.selected_station = next(
            (
                station
                for station in self.railway.stations
                if station.name == station_name
            ),
            None,
        )

        if self.selected_station is None:
            return

        self._generate_timetable()


    def _generate_timetable(self) -> None:
        """選択された駅の駅時刻表を生成する。"""
        if self.railway is None:
            self._show_message(
                "未読み込み",
                "OuDiaSecondファイルを読み込んでください。",
            )
            return

        if self.selected_station is None:
            self._show_message(
                "駅未選択",
                "駅を選択してください。",
            )
            return

        try:
            self.station_timetable = generate_station_timetable(
                self.railway,
                self.selected_station,
            )
        except Exception as exc:
            self._show_message(
                "時刻表生成エラー",
                f"時刻表の生成に失敗しました。\n\n{exc}"
            )
            return

        self.timetable_view.show(
            self.station_timetable,
        )

        self.timetable_preview.set_timetable(
            self.station_timetable,
        )


    def _export_excel(self) -> None:
        """生成済みの駅時刻表をExcelファイルへ出力する。"""
        if self.station_timetable is None:
            self._show_message(
                "時刻表未生成",
                "先に時刻表を生成してください。",
            )
            return

        output_path = filedialog.asksaveasfilename(
            title="Excelファイルを保存",
            defaultextension=".xlsx",
            filetypes=[
                ("Excelファイル", "*.xlsx"),
                ("すべてのファイル", "*.*"),
            ],
        )

        if not output_path:
            return

        try:
            export_station_timetable(
                self.station_timetable,
                Path(output_path),
            )
        except Exception as exc:
            self._show_message(
                "Excel出力エラー",
                f"Excelファイルの出力に失敗しました。\n\n{exc}",
            )
            return

        self._show_message(
            "Excel出力完了",
            f"Excelファイルを出力しました。\n\n{output_path}",
        )


    def _show_message(
        self,
        title: str,
        message: str,
    ) -> None:
        """メインウィンドウの近くにメッセージを表示する。"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.transient(self.root)
        dialog.resizable(False, False)

        label = tk.Label(
            dialog,
            text=message,
            justify=tk.LEFT,
            padx=20,
            pady=20,
        )
        label.pack()

        button = tk.Button(
            dialog,
            text="OK",
            width=10,
            command=dialog.destroy,
        )
        button.pack(pady=(0, 15))

        dialog.update_idletasks()

        x = (
            self.root.winfo_x()
            + (self.root.winfo_width() - dialog.winfo_width()) // 2
        )
        y = (
            self.root.winfo_y()
            + (self.root.winfo_height() - dialog.winfo_height()) // 2
        )

        dialog.geometry(f"+{x}+{y}")

        dialog.grab_set()
        button.focus_set()
        dialog.bind("<Return>", lambda _event: dialog.destroy())


def main() -> None:
    """アプリケーションを起動する。"""
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
