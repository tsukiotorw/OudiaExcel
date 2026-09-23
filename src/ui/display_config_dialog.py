import tkinter as tk
from tkinter import ttk

from src.ui.preview_item import PreviewItem
from src.timetable.display_config import TimetableDisplayConfig

class DisplayConfigDialog(tk.Toplevel):
    """時刻表表示設定ダイアログ。"""

    def __init__(
        self,
        parent: tk.Misc,
        item: PreviewItem,
        display_config: TimetableDisplayConfig,
    ) -> None:
        super().__init__(parent)

        self.item = item
        self.display_config = display_config

        self.title(self._get_title())
        self.resizable(False, False)
        self.transient(parent)

        self._create_widgets()

        self.update_idletasks()

        x = (
            parent.winfo_rootx()
            + (parent.winfo_width() - self.winfo_width()) // 2
        )
        y = (
            parent.winfo_rooty()
            + (parent.winfo_height() - self.winfo_height()) // 2
        )

        self.geometry(f"+{x}+{y}")

        self.grab_set()
        self.focus_set()


    def _get_title(self) -> str:
        """設定対象に応じたダイアログタイトルを返す。"""
        titles = {
            PreviewItem.TITLE: "タイトルの表示設定",
            PreviewItem.HEADER: "ヘッダの表示設定",
            PreviewItem.HOUR: "時刻の表示設定",
            PreviewItem.TRAIN: "列車の表示設定",
            PreviewItem.LEGEND: "凡例の表示設定",
        }

        return titles[self.item]


    def _create_widgets(self) -> None:
        """ダイアログのウィジェットを作成する。"""
        frame = ttk.Frame(
            self,
            padding=20,
        )
        frame.pack()

        label = ttk.Label(
            frame,
            text=f"設定対象: {self._get_item_name()}",
        )
        label.pack(pady=(0, 15))

        ttk.Label(
            frame,
            text="ここに表示設定を追加します。",
        ).pack()

        button = ttk.Button(
            frame,
            text="閉じる",
            command=self.destroy,
        )
        button.pack(pady=(20, 0))


    def _get_item_name(self) -> str:
        """設定対象の表示名を返す。"""
        names = {
            PreviewItem.TITLE: "タイトル",
            PreviewItem.HEADER: "ヘッダ",
            PreviewItem.HOUR: "時刻",
            PreviewItem.TRAIN: "列車",
            PreviewItem.LEGEND: "凡例",
        }

        return names[self.item]
