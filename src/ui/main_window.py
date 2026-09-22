from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from src.application.oud2_loader import load_oud2
from src.application.station_timetable import generate_station_timetable
from src.models.railway import Railway
from src.models.station import Station
from src.models.timetable import StationTimetable
from src.ui.timetable_view import TimetableView


class MainWindow:
    """OuDiaExcelのメインウィンドウ。"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("OuDiaExcel")
        self.root.geometry("800x700")

        self.file_path = tk.StringVar()
        self.railway: Railway | None = None
        self.selected_station: Station | None = None
        self.selected_station_text = tk.StringVar(value="未選択")

        self.station_timetable: StationTimetable | None = None

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

        browse_button = tk.Button(
            file_frame,
            text="参照...",
            command=self._select_file,
        )
        browse_button.pack(
            side=tk.LEFT,
            padx=(8, 0),
        )

        load_button = tk.Button(
            frame,
            text="読み込み",
            command=self._load_file,
        )
        load_button.pack(
            anchor=tk.E,
            pady=(15, 10),
        )

        station_label = tk.Label(
            frame,
            text="駅",
        )
        station_label.pack(anchor=tk.W)

        self.station_listbox = tk.Listbox(
            frame,
            height=8,
        )
        self.station_listbox.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self.station_listbox.bind(
            "<<ListboxSelect>>",
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

        generate_button = tk.Button(
            frame,
            text="時刻表生成",
            command=self._generate_timetable,
        )
        generate_button.pack(
            anchor=tk.E,
            pady=(10, 0),
        )

        self.timetable_view = TimetableView(frame)
        self.timetable_view.frame.pack(
            fill=tk.BOTH,
            expand=True,
            pady=(15, 0),
        )


    def _select_file(self) -> None:
        """OuDiaSecondファイルを選択する。"""
        selected_file = filedialog.askopenfilename(
            title="OuDiaSecondファイルを選択",
            filetypes=[
                ("OuDiaSecond files", "*.oud2"),
                ("All files", "*.*"),
            ],
        )

        if selected_file:
            self.file_path.set(str(Path(selected_file)))

    def _load_file(self) -> None:
        """選択されたOuDiaSecondファイルを読み込む。"""
        path = self.file_path.get()

        if not path:
            messagebox.showwarning(
                "ファイル未選択",
                "OuDiaSecondファイルを選択してください。",
            )
            return

        try:
            self.railway = load_oud2(Path(path))
        except Exception as exc:
            messagebox.showerror(
                "読み込みエラー",
                f"ファイルの読み込みに失敗しました。\n\n{exc}",
            )
            return

        self.selected_station = None
        self.station_timetable = None
        self.selected_station_text.set("未選択")
        self.timetable_view.clear()

        self._update_station_list()

        messagebox.showinfo(
            "読み込み完了",
            f"ファイルを読み込みました。\n\n"
            f"路線名: {self.railway.name}\n"
            f"駅数: {len(self.railway.stations)}\n"
            f"列車種別数: {len(self.railway.train_types)}\n"
            f"ダイヤ数: {len(self.railway.diagrams)}",
        )

    def _update_station_list(self) -> None:
        """駅一覧を更新する。"""
        self.station_listbox.delete(0, tk.END)

        if self.railway is None:
            return

        for station in self.railway.stations:
            self.station_listbox.insert(
                tk.END,
                station.name,
            )

    def _on_station_selected(self, _event: tk.Event) -> None:
        """駅一覧から駅が選択されたときの処理。"""
        if self.railway is None:
            return

        selection = self.station_listbox.curselection()

        if not selection:
            return

        index = selection[0]

        self.selected_station = self.railway.stations[index]
        self.selected_station_text.set(
            self.selected_station.name,
        )

    def _generate_timetable(self) -> None:
        """選択された駅の駅時刻表を生成する。"""
        if self.railway is None:
            messagebox.showwarning(
                "未読み込み",
                "OuDiaSecondファイルを読み込んでください。",
            )
            return

        if self.selected_station is None:
            messagebox.showwarning(
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
            messagebox.showerror(
                "時刻表生成エラー",
                f"時刻表の生成に失敗しました。\n\n{exc}",
            )
            return

        self.timetable_view.show(
            self.station_timetable,
        )

        messagebox.showinfo(
            "時刻表生成完了",
            f"時刻表を生成しました。\n\n"
            f"駅: {self.station_timetable.station_name}\n"
            f"下り: {len(self.station_timetable.down)}時間\n"
            f"上り: {len(self.station_timetable.up)}時間",
        )


def main() -> None:
    """アプリケーションを起動する。"""
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
