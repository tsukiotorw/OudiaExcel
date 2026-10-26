from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk

from src.application.oud2_loader import load_oud2
from src.application.station_timetable import generate_station_timetable
from src.application.station_alias_settings import (
    load_station_aliases,
    load_display_config,
    save_station_settings,
    load_station_no_mark
)
from src.application.excel_export import export_station_timetable
from src.models.railway import Railway
from src.models.station import Station
from src.models.timetable import StationTimetable
from src.ui.timetable_preview import TimetablePreview
from src.timetable.display_config import TimetableDisplayConfig


class MainWindow:
    """OuDiaExcelのメインウィンドウ。"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("OuDiaExcel")
        self.root.geometry("1200x750")

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

        alias_button = tk.Button(
            button_frame,
            text="駅略称設定",
            command=self._open_station_alias_editor,
        )
        alias_button.pack(side=tk.LEFT, padx=(0, 8))

        export_button = tk.Button(
            button_frame,
            text="Excel出力",
            command=self._export_excel,
        )
        export_button.pack(side=tk.LEFT)

        self.timetable_preview = TimetablePreview(
            frame,
            display_config=self.display_config,
            on_display_config_changed=self._save_display_config,
        )
        self.timetable_preview.pack(
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

        # OuDiaSecondファイルを読み込む
        try:
            self.railway = load_oud2(Path(selected_file))
        except Exception as exc:
            self._show_message(
                "読み込みエラー",
                f"ファイルの読み込みに失敗しました。\n\n{exc}",
            )
            return

        # 駅略称設定を復元する
        try:
            aliases = load_station_aliases(Path(selected_file))
        except ValueError as exc:
            self._show_message(
                "駅略称設定エラー",
                f"駅略称設定を読み込めませんでした。\n\n{exc}",
            )
            aliases = {}

        for station in self.railway.stations:
            station.short_name = aliases.get(station.name, "")

        # 無印設定を復元する
        try:
            station_no_mark = load_station_no_mark(
                Path(selected_file)
            )
        except (OSError, ValueError) as exc:
            self._show_message(
                "無印設定エラー",
                f"無印設定を読み込めませんでした。\n\n{exc}",
            )
            station_no_mark = {}

        for station in self.railway.stations:
            station.is_no_mark = station_no_mark.get(
                station.name,
                False,
            )

        # 表示設定を復元する
        try:
            self.display_config = load_display_config(
                Path(selected_file)
            )
        except (OSError, ValueError) as exc:
            self._show_message(
                "表示設定エラー",
                f"表示設定を読み込めませんでした。\n\n{exc}",
            )
            self.display_config = TimetableDisplayConfig()

        # プレビューにも復元した設定を反映する
        self.timetable_preview.display_config = self.display_config

        self.selected_station = None
        self.station_timetable = None
        self.selected_station_text.set("未選択")

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

        station_index = self.station_combo.current()

        if not 0 <= station_index < len(self.railway.stations):
            return

        self.selected_station = self.railway.stations[station_index]
        self.selected_station_text.set(
            self.selected_station.name
        )

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
                self.display_config,
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


    def _open_station_alias_editor(self) -> None:
        """駅略称の編集ウィンドウを開く。"""
        if self.railway is None:
            self._show_message(
                "未読み込み",
                "先にOuDiaSecondファイルを読み込んでください。",
            )
            return

        try:
            station_no_mark_settings = load_station_no_mark(
                Path(self.file_path.get())
            )
        except (OSError, ValueError) as exc:
            self._show_message(
                "設定読み込みエラー",
                f"無印設定を読み込めませんでした。\n\n{exc}",
            )
            return

        dialog = tk.Toplevel(self.root)
        dialog.withdraw()
        dialog.title("駅略称設定")
        dialog.transient(self.root)

        container = ttk.Frame(dialog, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="略称を空欄にすると、正式駅名が使用されます。",
        ).pack(anchor=tk.W, pady=(0, 8))

        # 駅数が多い場合に備えてスクロール可能にする
        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            container,
            orient=tk.VERTICAL,
            command=canvas.yview,
        )
        rows_frame = ttk.Frame(canvas)

        rows_frame.bind(
            "<Configure>",
            lambda _event: canvas.configure(
                scrollregion=canvas.bbox("all")
            ),
        )

        canvas_window = canvas.create_window(
            (0, 0),
            window=rows_frame,
            anchor=tk.NW,
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(
                canvas_window,
                width=event.width,
            ),
        )

        entries: list[
            tuple[Station, tk.Entry, tk.BooleanVar]
        ] = []

        # 同名駅は同じ略称を共有する。
        alias_vars: dict[str, tk.StringVar] = {}
        dialog._alias_vars = alias_vars  # StringVarがGCされないよう保持する

        for row, station in enumerate(self.railway.stations):
            ttk.Label(
                rows_frame,
                text=station.name,
                width=20,
            ).grid(
                row=row,
                column=0,
                sticky=tk.W,
                padx=(0, 8),
                pady=3,
            )

            # 最初に出現した駅の略称を初期値として採用する。
            if station.name not in alias_vars:
                alias_vars[station.name] = tk.StringVar(
                    value=station.short_name
                )

            # 同名駅では同じStringVarを共有する。
            entry = ttk.Entry(
                rows_frame,
                textvariable=alias_vars[station.name],
            )
            entry.grid(
                row=row,
                column=1,
                sticky=tk.EW,
                pady=3,
            )

            no_mark_var = tk.BooleanVar(
                value=station_no_mark_settings.get(
                    station.name,
                    station.is_no_mark,
                )
            )
            ttk.Checkbutton(
                rows_frame,
                text="無印",
                variable=no_mark_var,
            ).grid(
                row=row,
                column=2,
                sticky=tk.W,
                padx=(8, 0),
                pady=3,
            )

            entries.append((station, entry, no_mark_var))

        rows_frame.columnconfigure(1, weight=1)

        button_frame = ttk.Frame(container)
        button_frame.pack(
            fill=tk.X,
            pady=(10, 0),
        )

        def save() -> None:
            aliases = {
                station.name: entry.get().strip()
                for station, entry, _no_mark_var in entries
            }

            station_no_mark = {
                station.name: no_mark_var.get()
                for station, _entry, no_mark_var in entries
            }

            try:
                save_station_settings(
                    Path(self.file_path.get()),
                    aliases,
                    self.display_config,
                    station_no_mark=station_no_mark,
                )
            except (OSError, ValueError) as exc:
                self._show_message(
                    "保存エラー",
                    f"駅設定を保存できませんでした。\n\n{exc}",
                )
                return

            for station, entry, no_mark_var in entries:
                station.short_name = entry.get().strip()
                station.is_no_mark = no_mark_var.get()

            selected_index = self.station_combo.current()
            self._update_station_list()

            if (
                0 <= selected_index < len(self.railway.stations)
            ):
                self.station_combo.current(selected_index)
                self.selected_station = (
                    self.railway.stations[selected_index]
                )
                self.selected_station_text.set(
                    self.selected_station.name
                )
                self._generate_timetable()

            dialog.destroy()

        ttk.Button(
            button_frame,
            text="保存",
            command=save,
        ).pack(side=tk.RIGHT)

        ttk.Button(
            button_frame,
            text="キャンセル",
            command=dialog.destroy,
        ).pack(side=tk.RIGHT, padx=(0, 8))

        dialog.update_idletasks()

        # メインウィンドウの位置・サイズを基準に配置する
        self.root.update_idletasks()

        dialog_width = dialog.winfo_reqwidth()
        dialog_height = dialog.winfo_reqheight()

        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        x = root_x + (root_width - dialog_width) // 2
        y = root_y + (root_height - dialog_height) // 2

        # 画面の表示範囲からはみ出さないように調整する
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()

        x = max(0, min(x, screen_width - dialog_width))
        y = max(0, min(y, screen_height - dialog_height))

        dialog.geometry(
            f"{dialog_width}x{dialog_height}+{x}+{y}"
        )

        dialog.deiconify()
        dialog.update()

        dialog.grab_set()


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


    def _save_display_config(self) -> None:
        """表示設定を設定ファイルへ保存する。"""
        if self.railway is None:
            return

        try:
            aliases = {
                station.name: station.short_name
                for station in self.railway.stations
                if station.short_name
            }

            save_station_settings(
                Path(self.file_path.get()),
                aliases,
                self.display_config,
            )
        except (OSError, ValueError) as exc:
            self._show_message(
                "表示設定保存エラー",
                f"表示設定を保存できませんでした。\n\n{exc}",
            )


def main() -> None:
    """アプリケーションを起動する。"""
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
