import tkinter as tk
import tkinter.font as tkfont
from tkinter import colorchooser,ttk

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

        self._create_variables()
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


    def _get_available_fonts(self) -> list[str]:
        """インストール済みフォント名の一覧を取得する。"""
        families = {
            name
            for name in tkfont.families()
            if not name.startswith("@")
        }

        return sorted(families, key=str.lower)


    def _create_variables(self) -> None:
        """設定値を保持するTk変数を作成する。"""
        match self.item:
            case PreviewItem.TITLE:
                self._create_title_variables()
            case PreviewItem.TRAIN:
                self._create_train_variables()
            case PreviewItem.HEADER:
                self._create_header_variables()
            case PreviewItem.HOUR:
                self._create_hour_variables() 
            case _:
                pass


    def _create_title_variables(self) -> None:
        """タイトルの設定値を保持するTk変数を作成する。"""
        self.title_font_name = tk.StringVar(
            value=self.display_config.title_font_name,
        )
        self.title_font_size = tk.IntVar(
            value=self.display_config.title_font_size,
        )
        self.title_font_color = tk.StringVar(
            value=self.display_config.title_font_color,
        )
        self.title_fill = tk.StringVar(
            value=self.display_config.title_fill or "",
        )


    def _create_train_variables(self) -> None:
        """列車情報の設定値を保持するTk変数を作成する。"""
        self.metadata_font_name = tk.StringVar(
            value=self.display_config.metadata_font_name,
        )
        self.metadata_font_size = tk.IntVar(
            value=self.display_config.metadata_font_size,
        )

        self.minute_font_name = tk.StringVar(
            value=self.display_config.minute_font_name,
        )
        self.minute_font_size = tk.IntVar(
            value=self.display_config.minute_font_size,
        )

        self.font_color = tk.StringVar(
            value=self.display_config.train_font_color,
        )
        self.fill_color = tk.StringVar(
            value=self.display_config.train_fill or "",
        )


    def _create_header_variables(self) -> None:
        """ヘッダ情報の設定値を保持するTk変数を作成する。"""
        self.header_font_name = tk.StringVar(
            value=self.display_config.header_font_name,
        )
        self.header_font_size = tk.IntVar(
            value=self.display_config.header_font_size,
        )

        self.header_font_color = tk.StringVar(
            value=self.display_config.header_font_color,
        )
        self.header_fill = tk.StringVar(
            value=self.display_config.header_fill or "",
        )


    def _create_hour_variables(self) -> None:
        """時刻情報の設定値を保持するTk変数を作成する。"""
        self.hour_font_name = tk.StringVar(
            value=self.display_config.hour_font_name,
        )
        self.hour_font_size = tk.IntVar(
            value=self.display_config.hour_font_size,
        )
        self.hour_font_color = tk.StringVar(
            value=self.display_config.hour_font_color,
        )
        self.hour_fill = tk.StringVar(
            value=self.display_config.hour_fill or "",
        )


    def _create_widgets(self) -> None:
        """ダイアログのウィジェットを作成する。"""
        frame = ttk.Frame(
            self,
            padding=20,
        )
        frame.pack()

        match self.item:
            case PreviewItem.TITLE:
                self._create_title_widgets(frame)
            case PreviewItem.TRAIN:
                self._create_train_widgets(frame)
            case PreviewItem.HEADER:
                self._create_header_widgets(frame)
            case PreviewItem.HOUR:
                self._create_hour_widgets(frame)
            case _:
                ttk.Label(
                    frame,
                    text=f"設定対象: {self._get_item_name()}",
                ).pack(pady=(0, 15))

                ttk.Button(
                    frame,
                    text="閉じる",
                    command=self.destroy,
                ).pack()


    def _create_title_widgets(self, frame: ttk.Frame) -> None:
        """タイトルの表示設定ウィジェットを作成する。"""
        available_fonts = self._get_available_fonts()

        ttk.Label(
            frame,
            text="タイトルの表示設定",
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky=tk.W,
            pady=(0, 15),
        )

        ttk.Label(
            frame,
            text="フォント",
        ).grid(
            row=1,
            column=0,
            sticky=tk.W,
        )

        ttk.Combobox(
            frame,
            textvariable=self.title_font_name,
            values=available_fonts,
            state="readonly",
            width=28,
        ).grid(
            row=1,
            column=1,
            columnspan=2,
            padx=(10, 0),
            pady=4,
        )

        ttk.Label(
            frame,
            text="サイズ",
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
        )

        ttk.Spinbox(
            frame,
            from_=6,
            to=72,
            textvariable=self.title_font_size,
            width=8,
        ).grid(
            row=2,
            column=1,
            sticky=tk.W,
            padx=(10, 0),
            pady=4,
        )

        ttk.Label(
            frame,
            text="文字色",
        ).grid(
            row=3,
            column=0,
            sticky=tk.W,
        )

        ttk.Entry(
            frame,
            textvariable=self.title_font_color,
            width=12,
        ).grid(
            row=3,
            column=1,
            padx=(10, 0),
            pady=4,
        )

        ttk.Button(
            frame,
            text="選択...",
            command=self._choose_title_font_color,
        ).grid(
            row=3,
            column=2,
            padx=(5, 0),
        )

        ttk.Label(
            frame,
            text="塗りつぶし色",
        ).grid(
            row=4,
            column=0,
            sticky=tk.W,
        )

        ttk.Entry(
            frame,
            textvariable=self.title_fill,
            width=12,
        ).grid(
            row=4,
            column=1,
            padx=(10, 0),
            pady=4,
        )

        ttk.Button(
            frame,
            text="選択...",
            command=self._choose_title_fill,
        ).grid(
            row=4,
            column=2,
            padx=(5, 0),
        )

        button_frame = ttk.Frame(frame)
        button_frame.grid(
            row=5,
            column=0,
            columnspan=3,
            sticky=tk.E,
            pady=(20, 0),
        )

        ttk.Button(
            button_frame,
            text="適用",
            command=self._apply,
        ).pack(side=tk.LEFT)

        ttk.Button(
            button_frame,
            text="キャンセル",
            command=self.destroy,
        ).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )


    def _create_train_widgets(self, frame: ttk.Frame) -> None:
        """列車情報のウィジェットを作成する。"""

        available_fonts = self._get_available_fonts()

        ttk.Label(
            frame,
            text="列車の表示設定",
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky=tk.W,
            pady=(0, 15),
        )

        ttk.Label(
            frame,
            text="行先・種別フォント",
        ).grid(row=1, column=0, sticky=tk.W)

        ttk.Combobox(
            frame,
            textvariable=self.metadata_font_name,
            values=available_fonts,
            state="readonly",
            width=28,
        ).grid(
            row=1,
            column=1,
            columnspan=2,
            padx=(10, 0),
            pady=4,
        )

        ttk.Label(
            frame,
            text="行先・種別サイズ",
        ).grid(row=2, column=0, sticky=tk.W)

        ttk.Spinbox(
            frame,
            from_=6,
            to=72,
            textvariable=self.metadata_font_size,
            width=8,
        ).grid(
            row=2,
            column=1,
            sticky=tk.W,
            padx=(10, 0),
            pady=4,
        )

        ttk.Label(
            frame,
            text="時刻フォント",
        ).grid(row=3, column=0, sticky=tk.W)

        ttk.Combobox(
            frame,
            textvariable=self.minute_font_name,
            values=available_fonts,
            state="readonly",
            width=28,
        ).grid(
            row=3,
            column=1,
            columnspan=2,
            padx=(10, 0),
            pady=4,
        )
        
        ttk.Label(
            frame,
            text="時刻サイズ",
        ).grid(row=4, column=0, sticky=tk.W)

        ttk.Spinbox(
            frame,
            from_=6,
            to=72,
            textvariable=self.minute_font_size,
            width=8,
        ).grid(
            row=4,
            column=1,
            sticky=tk.W,
            padx=(10, 0),
            pady=4,
        )

        ttk.Label(
            frame,
            text="文字色",
        ).grid(row=5, column=0, sticky=tk.W)

        ttk.Entry(
            frame,
            textvariable=self.font_color,
            width=12,
        ).grid(
            row=5,
            column=1,
            padx=(10, 0),
            pady=4,
        )

        ttk.Button(
            frame,
            text="選択...",
            command=self._choose_font_color,
        ).grid(row=5, column=2, padx=(5, 0))

        ttk.Label(
            frame,
            text="塗りつぶし色",
        ).grid(row=6, column=0, sticky=tk.W)

        ttk.Entry(
            frame,
            textvariable=self.fill_color,
            width=12,
        ).grid(
            row=6,
            column=1,
            padx=(10, 0),
            pady=4,
        )

        ttk.Button(
            frame,
            text="選択...",
            command=self._choose_fill_color,
        ).grid(row=6, column=2, padx=(5, 0))

        button_frame = ttk.Frame(frame)
        button_frame.grid(
            row=7,
            column=0,
            columnspan=3,
            sticky=tk.E,
            pady=(20, 0),
        )

        ttk.Button(
            button_frame,
            text="適用",
            command=self._apply,
        ).pack(side=tk.LEFT)

        ttk.Button(
            button_frame,
            text="キャンセル",
            command=self.destroy,
        ).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )


    def _create_header_widgets(self, frame: ttk.Frame) -> None:
        """ヘッダの表示設定ウィジェットを作成する。"""
        available_fonts = self._get_available_fonts()

        ttk.Label(
            frame,
            text="ヘッダの表示設定",
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky=tk.W,
            pady=(0, 15),
        )

        ttk.Label(
            frame,
            text="フォント",
        ).grid(
            row=1,
            column=0,
            sticky=tk.W,
        )

        ttk.Combobox(
            frame,
            textvariable=self.header_font_name,
            values=available_fonts,
            state="readonly",
            width=28,
        ).grid(
            row=1,
            column=1,
            columnspan=2,
            padx=(10, 0),
            pady=4,
        )

        ttk.Label(
            frame,
            text="サイズ",
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
        )

        ttk.Spinbox(
            frame,
            from_=6,
            to=72,
            textvariable=self.header_font_size,
            width=8,
        ).grid(
            row=2,
            column=1,
            sticky=tk.W,
            padx=(10, 0),
            pady=4,
        )

        ttk.Label(
            frame,
            text="文字色",
        ).grid(
            row=3,
            column=0,
            sticky=tk.W,
        )

        ttk.Entry(
            frame,
            textvariable=self.header_font_color,
            width=12,
        ).grid(
            row=3,
            column=1,
            padx=(10, 0),
            pady=4,
        )

        ttk.Button(
            frame,
            text="選択...",
            command=self._choose_header_font_color,
        ).grid(
            row=3,
            column=2,
            padx=(5, 0),
        )

        ttk.Label(
            frame,
            text="塗りつぶし色",
        ).grid(
            row=4,
            column=0,
            sticky=tk.W,
        )

        ttk.Entry(
            frame,
            textvariable=self.header_fill,
            width=12,
        ).grid(
            row=4,
            column=1,
            padx=(10, 0),
            pady=4,
        )

        ttk.Button(
            frame,
            text="選択...",
            command=self._choose_header_fill,
        ).grid(
            row=4,
            column=2,
            padx=(5, 0),
        )

        button_frame = ttk.Frame(frame)
        button_frame.grid(
            row=5,
            column=0,
            columnspan=3,
            sticky=tk.E,
            pady=(20, 0),
        )

        ttk.Button(
            button_frame,
            text="適用",
            command=self._apply,
        ).pack(side=tk.LEFT)

        ttk.Button(
            button_frame,
            text="キャンセル",
            command=self.destroy,
        ).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )        


    def _create_hour_widgets(self, frame: ttk.Frame) -> None:
        """時刻欄の表示設定ウィジェットを作成する。"""
        available_fonts = self._get_available_fonts()

        ttk.Label(
            frame,
            text="時刻の表示設定",
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky=tk.W,
            pady=(0, 15),
        )

        ttk.Label(
            frame,
            text="フォント",
        ).grid(
            row=1,
            column=0,
            sticky=tk.W,
        )

        ttk.Combobox(
            frame,
            textvariable=self.hour_font_name,
            values=available_fonts,
            state="readonly",
            width=28,
        ).grid(
            row=1,
            column=1,
            columnspan=2,
            padx=(10, 0),
            pady=4,
        )

        ttk.Label(
            frame,
            text="サイズ",
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
        )

        ttk.Spinbox(
            frame,
            from_=6,
            to=72,
            textvariable=self.hour_font_size,
            width=8,
        ).grid(
            row=2,
            column=1,
            sticky=tk.W,
            padx=(10, 0),
            pady=4,
        )

        ttk.Label(
            frame,
            text="文字色",
        ).grid(
            row=3,
            column=0,
            sticky=tk.W,
        )

        ttk.Entry(
            frame,
            textvariable=self.hour_font_color,
            width=12,
        ).grid(
            row=3,
            column=1,
            padx=(10, 0),
            pady=4,
        )

        ttk.Button(
            frame,
            text="選択...",
            command=self._choose_hour_font_color,
        ).grid(
            row=3,
            column=2,
            padx=(5, 0),
        )

        ttk.Label(
            frame,
            text="塗りつぶし色",
        ).grid(
            row=4,
            column=0,
            sticky=tk.W,
        )

        ttk.Entry(
            frame,
            textvariable=self.hour_fill,
            width=12,
        ).grid(
            row=4,
            column=1,
            padx=(10, 0),
            pady=4,
        )

        ttk.Button(
            frame,
            text="選択...",
            command=self._choose_hour_fill,
        ).grid(
            row=4,
            column=2,
            padx=(5, 0),
        )

        button_frame = ttk.Frame(frame)
        button_frame.grid(
            row=5,
            column=0,
            columnspan=3,
            sticky=tk.E,
            pady=(20, 0),
        )

        ttk.Button(
            button_frame,
            text="適用",
            command=self._apply,
        ).pack(side=tk.LEFT)

        ttk.Button(
            button_frame,
            text="キャンセル",
            command=self.destroy,
        ).pack(
            side=tk.LEFT,
            padx=(8, 0),
        )


    def _choose_font_color(self) -> None:
        """文字色を選択する。"""
        current_color = self.font_color.get().strip()

        if current_color:
            current_color = f"#{current_color.lstrip('#')}"

        color = colorchooser.askcolor(
            initialcolor=current_color or "#000000",
            parent=self,
        )

        if color[1] is not None:
            self.font_color.set(
                color[1].lstrip("#").upper()
            )


    def _choose_title_font_color(self) -> None:
        """タイトルの文字色を選択する。"""
        current_color = self.title_font_color.get().strip()

        if current_color:
            current_color = f"#{current_color.lstrip('#')}"

        color = colorchooser.askcolor(
            initialcolor=current_color or "#000000",
            parent=self,
        )

        if color[1] is not None:
            self.title_font_color.set(
                color[1].lstrip("#").upper()
            )

    def _choose_header_font_color(self) -> None:
        """ヘッダの文字色を選択する。"""
        current_color = self.header_font_color.get().strip()

        if current_color:
            current_color = f"#{current_color.lstrip('#')}"

        color = colorchooser.askcolor(
            initialcolor=current_color or "#000000",
            parent=self,
        )

        if color[1] is not None:
            self.header_font_color.set(
                color[1].lstrip("#").upper()
            )


    def _choose_hour_font_color(self) -> None:
        """時刻欄の文字色を選択する。"""
        current_color = self.hour_font_color.get().strip()

        if current_color:
            current_color = f"#{current_color.lstrip('#')}"

        color = colorchooser.askcolor(
            initialcolor=current_color or "#000000",
            parent=self,
        )

        if color[1] is not None:
            self.hour_font_color.set(
                color[1].lstrip("#").upper()
            )


    def _choose_fill_color(self) -> None:
        """塗りつぶし色を選択する。"""
        current_color = self.fill_color.get().strip()

        if current_color:
            current_color = f"#{current_color.lstrip('#')}"

        color = colorchooser.askcolor(
            initialcolor=current_color or "#FFFFFF",
            parent=self,
        )

        if color[1] is not None:
            self.fill_color.set(
                color[1].lstrip("#").upper()
            )


    def _choose_title_fill(self) -> None:
        """タイトルの塗りつぶし色を選択する。"""
        current_color = self.title_fill.get().strip()

        if current_color:
            current_color = f"#{current_color.lstrip('#')}"

        color = colorchooser.askcolor(
            initialcolor=current_color or "#FFFFFF",
            parent=self,
        )

        if color[1] is not None:
            self.title_fill.set(
                color[1].lstrip("#").upper()
            )


    def _choose_header_fill(self) -> None:
        """ヘッダの塗りつぶし色を選択する。"""
        current_color = self.header_fill.get().strip()

        if current_color:
            current_color = f"#{current_color.lstrip('#')}"

        color = colorchooser.askcolor(
            initialcolor=current_color or "#FFFFFF",
            parent=self,
        )

        if color[1] is not None:
            self.header_fill.set(
                color[1].lstrip("#").upper()
            )


    def _choose_hour_fill(self) -> None:
        """時刻欄の塗りつぶし色を選択する。"""
        current_color = self.hour_fill.get().strip()

        if current_color:
            current_color = f"#{current_color.lstrip('#')}"

        color = colorchooser.askcolor(
            initialcolor=current_color or "#FFFFFF",
            parent=self,
        )

        if color[1] is not None:
            self.hour_fill.set(
                color[1].lstrip("#").upper()
            )


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


    def _apply(self) -> None:
        """設定を適用する。"""
        match self.item:
            case PreviewItem.TITLE:
                self._apply_title()
            case PreviewItem.TRAIN:
                self._apply_train()
            case PreviewItem.HEADER:
                self._apply_header()
            case PreviewItem.HOUR:
                self._apply_hour()
            case _:
                pass

        parent = self.master

        if hasattr(parent, "redraw"):
            parent.redraw()

        self.destroy()


    def _apply_title(self) -> None:
        """タイトルの表示設定を適用する。"""
        self.display_config.title_font_name = (
            self.title_font_name.get()
        )
        self.display_config.title_font_size = (
            self.title_font_size.get()
        )
        self.display_config.title_font_color = (
            self.title_font_color.get()
        )

        fill_color = self.title_fill.get().strip()
        self.display_config.title_fill = (
            fill_color if fill_color else None
        )


    def _apply_train(self) -> None:
        """列車の表示設定を適用する。"""
        self.display_config.metadata_font_name = (
            self.metadata_font_name.get()
        )
        self.display_config.metadata_font_size = (
            self.metadata_font_size.get()
        )
        self.display_config.minute_font_name = (
            self.minute_font_name.get()
        )
        self.display_config.minute_font_size = (
            self.minute_font_size.get()
        )
        self.display_config.train_font_color = (
            self.font_color.get()
        )

        fill_color = self.fill_color.get().strip()
        self.display_config.train_fill = (
            fill_color if fill_color else None
        )


    def _apply_header(self) -> None:
        """ヘッダの表示設定を適用する。"""
        self.display_config.header_font_name = (
            self.header_font_name.get()
        )
        self.display_config.header_font_size = (
            self.header_font_size.get()
        )
        self.display_config.header_font_color = (
            self.header_font_color.get()
        )

        fill_color = self.header_fill.get().strip()
        self.display_config.header_fill = (
            fill_color if fill_color else None
        )


    def _apply_hour(self) -> None:
        """時刻欄の表示設定を適用する。"""
        self.display_config.hour_font_name = (
            self.hour_font_name.get()
        )
        self.display_config.hour_font_size = (
            self.hour_font_size.get()
        )
        self.display_config.hour_font_color = (
            self.hour_font_color.get()
        )

        fill_color = self.hour_fill.get().strip()
        self.display_config.hour_fill = (
            fill_color if fill_color else None
        )

