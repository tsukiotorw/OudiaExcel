from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from src.application.oud2_loader import load_oud2
from src.models.railway import Railway


class MainWindow:
    """OuDiaExcelのメインウィンドウ。"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("OuDiaExcel")
        self.root.geometry("600x350")

        self.file_path = tk.StringVar()
        self.railway: Railway | None = None

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


def main() -> None:
    """アプリケーションを起動する。"""
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
