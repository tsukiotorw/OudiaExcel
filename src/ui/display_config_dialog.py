import tkinter as tk
import tkinter.font as tkfont
from tkinter import colorchooser,ttk

from src.ui.preview_item import PreviewItem
from src.timetable.display_config import (
    TimetableDisplayConfig,
    STRIPED_TRAIN_FILL_NONE,
    STRIPED_TRAIN_FILL_BOTH,
    STRIPED_TRAIN_FILL_METADATA,
    STRIPED_TRAIN_FILL_MINUTE,
)
from src.models.train_type import TrainType

BORDER_STYLES = {
    "細線": "thin",
    "中線": "medium",
    "太線": "thick",
    "破線": "dashed",
    "点線": "dotted",
    "二重線": "double",
}


class DisplayConfigDialog(tk.Toplevel):
    """時刻表表示設定ダイアログ。"""

    _FONT_MODE_LABELS = {
        "independent": "個別設定",
        "destination": "行先に合わせる",
        "train_type": "列車種別に合わせる",
    }

    def __init__(
        self,
        parent: tk.Misc,
        item: PreviewItem,
        display_config: TimetableDisplayConfig,
        train_types: list[TrainType] | None = None,
    ) -> None:
        super().__init__(parent)

        self.item = item
        self.display_config = display_config
        self.train_types = train_types or []

        self.title(self._get_title())
        is_train_dialog = self.item == PreviewItem.TRAIN
        self.resizable(is_train_dialog, is_train_dialog)
        if is_train_dialog:
            self.minsize(760, 520)
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
            case PreviewItem.LEGEND:
                self._create_legend_variables()
            case _:
                pass
        self._create_border_variables()


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
        
        self.use_train_type_short_name = tk.BooleanVar(
            value=self.display_config.use_train_type_short_name,
        )

        self.show_destination = tk.BooleanVar(
            value=self.display_config.show_destination,
        )

        self.train_type_column_visible = {
            train_type.index: tk.BooleanVar(
                value=self.display_config.train_type_column_visible.get(
                    train_type.index,
                    True,
                )
            )
            for train_type in self.train_types
        }

        self.destination_position = tk.StringVar(
            value=(
                "下段"
                if self.display_config.destination_position == "bottom"
                else "上段"
            )
        )
        self.train_type_position = tk.StringVar(
            value=(
                "下段"
                if self.display_config.train_type_position == "bottom"
                else "上段"
            )
        )
        self.metadata_order = tk.StringVar(
            value=(
                "列車種別→行先"
                if self.display_config.metadata_order == "train_type_first"
                else "行先→列車種別"
            )
        )
        self.hour_column_mode = tk.StringVar(
            value=(
                "中央配置"
                if self.display_config.hour_column_mode == "center"
                else "上下線別"
            )
        )
        self.striped_train_fill = tk.StringVar(
            value=self.display_config.striped_train_fill,
        )
        self.up_timetable_fill = tk.StringVar(
            value=self.display_config.up_timetable_fill,
        )
        self.up_timetable_alt_fill = tk.StringVar(
            value=self.display_config.up_timetable_alt_fill,
        )
        self.down_timetable_fill = tk.StringVar(
            value=self.display_config.down_timetable_fill,
        )
        self.down_timetable_alt_fill = tk.StringVar(
            value=self.display_config.down_timetable_alt_fill,
        )
        self.entry_font_modes: dict[str, tk.StringVar] = {}
        self.entry_font_names: dict[str, tk.StringVar] = {}
        self.entry_font_mode_combos: dict[str, ttk.Combobox] = {}
        self.entry_font_sizes: dict[str, tk.IntVar] = {}
        self.entry_font_colors: dict[str, tk.StringVar] = {}
        legacy_font_settings = {
            "destination": (
                self.display_config.metadata_font_name,
                self.display_config.metadata_font_size,
                self.display_config.train_font_color,
            ),
            "train_type": (
                self.display_config.metadata_font_name,
                self.display_config.metadata_font_size,
                self.display_config.train_font_color,
            ),
            "minute": (
                self.display_config.minute_font_name,
                self.display_config.minute_font_size,
                self.display_config.minute_font_color
                or self.display_config.train_font_color,
            ),
        }
        for item, legacy in legacy_font_settings.items():
            mode = getattr(
                self.display_config,
                f"{item}_font_mode",
            )
            if mode not in self._FONT_MODE_LABELS:
                mode = "independent"
            self.entry_font_modes[item] = tk.StringVar(
                value=self._FONT_MODE_LABELS[mode],
            )
            self.entry_font_names[item] = tk.StringVar(
                value=(
                    getattr(self.display_config, f"{item}_font_name")
                    or legacy[0]
                ),
            )
            self.entry_font_sizes[item] = tk.IntVar(
                value=(
                    getattr(self.display_config, f"{item}_font_size")
                    or legacy[1]
                ),
            )
            self.entry_font_colors[item] = tk.StringVar(
                value=(
                    getattr(self.display_config, f"{item}_font_color")
                    or legacy[2]
                ),
            )

        self.train_type_fills = {
            train_type.index: tk.StringVar(
                value=self.display_config.train_type_fills.get(
                    train_type.index,
                    "",
                )
            )
            for train_type in self.train_types
        }
        self.train_type_minute_highlight_enabled = {
            train_type.index: tk.BooleanVar(
                value=self.display_config
                .train_type_minute_highlight_enabled.get(
                    train_type.index,
                    False,
                )
            )
            for train_type in self.train_types
        }
        self.train_type_minute_highlight_fills = {
            train_type.index: tk.StringVar(
                value=self.display_config
                .train_type_minute_highlight_fills.get(
                    train_type.index,
                    "",
                )
            )
            for train_type in self.train_types
        }


    def _create_header_variables(self) -> None:
        """ヘッダ情報の設定値を保持するTk変数を作成する。"""
        self.up_header_text = tk.StringVar(
            value=self.display_config.up_header_text,
        )
        self.down_header_text = tk.StringVar(
            value=self.display_config.down_header_text,
        )
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
        self.up_header_fill = tk.StringVar(
            value=self.display_config.up_header_fill or "",
        )
        self.down_header_fill = tk.StringVar(
            value=self.display_config.down_header_fill or "",
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


    def _create_legend_variables(self) -> None:
        """凡例の設定値を保持するTk変数を作成する。"""
        self.show_destination_legend = tk.BooleanVar(
            value=self.display_config.show_destination_legend,
        )

        self.legend_label_font_name = tk.StringVar(
            value=self.display_config.legend_label_font_name,
        )
        self.legend_label_font_size = tk.IntVar(
            value=self.display_config.legend_label_font_size,
        )
        self.legend_label_font_color = tk.StringVar(
            value=self.display_config.legend_label_font_color,
        )
        self.legend_label_fill = tk.StringVar(
            value=self.display_config.legend_label_fill,
        )

        self.legend_font_name = tk.StringVar(
            value=self.display_config.legend_font_name,
        )
        self.legend_font_size = tk.IntVar(
            value=self.display_config.legend_font_size,
        )
        self.legend_font_color = tk.StringVar(
            value=self.display_config.legend_font_color,
        )
        self.legend_fill = tk.StringVar(
            value=self.display_config.legend_fill,
        )
        self.legend_row_height = tk.DoubleVar(
            value=self.display_config.legend_row_height,
        )

        self.train_type_colors = {}
        self.train_type_visible = {}

        for train_type in self.train_types:
            color = self.display_config.get_train_type_color(
                train_type.index
            )

            if color is None:
                color = self.display_config.train_font_color

            self.train_type_colors[train_type.index] = tk.StringVar(
                value=color
            )

            visible = self.display_config.train_type_visible.get(
                train_type.index,
                True,
            )

            self.train_type_visible[train_type.index] = tk.BooleanVar(
                value=visible
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
            case PreviewItem.LEGEND:
                self._create_legend_widgets(frame)
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

        border_row = self._create_border_widgets(
            frame,
            start_row=5,
        )

        button_frame = ttk.Frame(frame)
        button_frame.grid(
            row=border_row,
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


    def _update_font_mode_options(
        self,
        changed_item: str | None = None,
    ) -> None:
        """行先と列車種別のフォント連動が循環しないよう選択肢を更新する。"""

        independent = self._FONT_MODE_LABELS["independent"]
        destination = self._FONT_MODE_LABELS["destination"]
        train_type = self._FONT_MODE_LABELS["train_type"]

        destination_mode = self.entry_font_modes["destination"].get()
        train_type_mode = self.entry_font_modes["train_type"].get()

        # 相互循環が発生した場合、変更されていない側を個別設定に戻す。
        if (
            destination_mode == train_type
            and train_type_mode == destination
        ):
            if changed_item == "destination":
                self.entry_font_modes["train_type"].set(independent)
            else:
                self.entry_font_modes["destination"].set(independent)

        destination_mode = self.entry_font_modes["destination"].get()
        train_type_mode = self.entry_font_modes["train_type"].get()

        destination_options = [independent]
        if train_type_mode != destination:
            destination_options.append(train_type)

        train_type_options = [independent]
        if destination_mode != train_type:
            train_type_options.append(destination)

        minute_options = [
            independent,
            destination,
            train_type,
        ]

        options = {
            "destination": destination_options,
            "train_type": train_type_options,
            "minute": minute_options,
        }

        for item, modes in options.items():
            combo = self.entry_font_mode_combos[item]
            combo["values"] = tuple(modes)

            if self.entry_font_modes[item].get() not in modes:
                self.entry_font_modes[item].set(independent)


    def _create_train_widgets(self, frame: ttk.Frame) -> None:
        """列車情報のウィジェットを作成する。"""
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        layout_frame = ttk.Frame(notebook, padding=10)
        font_frame = ttk.Frame(notebook, padding=10)
        color_frame = ttk.Frame(notebook, padding=10)
        border_frame = ttk.Frame(notebook, padding=10)
        notebook.add(layout_frame, text="配置")
        notebook.add(font_frame, text="フォント")
        notebook.add(color_frame, text="背景色")
        notebook.add(border_frame, text="罫線")

        ttk.Label(layout_frame, text="行先の位置").grid(
            row=0, column=0, sticky=tk.W, padx=4, pady=4
        )
        ttk.Combobox(
            layout_frame,
            textvariable=self.destination_position,
            values=("上段", "下段"),
            state="readonly",
            width=12,
        ).grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        ttk.Label(layout_frame, text="列車種別の位置").grid(
            row=1, column=0, sticky=tk.W, padx=4, pady=4
        )
        ttk.Combobox(
            layout_frame,
            textvariable=self.train_type_position,
            values=("上段", "下段"),
            state="readonly",
            width=12,
        ).grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
        ttk.Label(layout_frame, text="同じ段の順序").grid(
            row=2, column=0, sticky=tk.W, padx=4, pady=4
        )
        ttk.Combobox(
            layout_frame,
            textvariable=self.metadata_order,
            values=("行先→列車種別", "列車種別→行先"),
            state="readonly",
            width=20,
        ).grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
        ttk.Label(layout_frame, text="時刻欄の位置").grid(
            row=3, column=0, sticky=tk.W, padx=4, pady=4
        )
        ttk.Combobox(
            layout_frame,
            textvariable=self.hour_column_mode,
            values=("上下線別", "中央配置"),
            state="readonly",
            width=20,
        ).grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)
        ttk.Checkbutton(
            layout_frame,
            text="列車種別に略称を使用",
            variable=self.use_train_type_short_name,
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=4)
        ttk.Checkbutton(
            layout_frame,
            text="行先を表示する",
            variable=self.show_destination,
        ).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=4)
        ttk.Label(
            layout_frame,
            text="列車欄に表示する列車種別",
        ).grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=(8, 4))
        for index, train_type in enumerate(self.train_types):
            ttk.Checkbutton(
                layout_frame,
                text=train_type.name,
                variable=self.train_type_column_visible[train_type.index],
            ).grid(
                row=7 + index // 3,
                column=index % 3,
                sticky=tk.W,
                padx=4,
                pady=2,
            )

        available_fonts = self._get_available_fonts()
        for column, heading in enumerate(
            ("項目", "設定方式", "フォント", "サイズ", "文字色")
        ):
            ttk.Label(font_frame, text=heading).grid(
                row=0, column=column, padx=4, pady=(0, 6), sticky=tk.W
            )
        item_labels = {
            "destination": "行先",
            "train_type": "列車種別",
            "minute": "分",
        }
        for row, item in enumerate(item_labels, start=1):
            ttk.Label(font_frame, text=item_labels[item]).grid(
                row=row, column=0, sticky=tk.W, padx=4, pady=4
            )
            mode_combo = ttk.Combobox(
                font_frame,
                textvariable=self.entry_font_modes[item],
                values=(),
                state="readonly",
                width=22,
            )
            mode_combo.grid(
                row=row,
                column=1,
                padx=4,
                pady=4,
            )

            self.entry_font_mode_combos[item] = mode_combo

            mode_combo.bind(
                "<<ComboboxSelected>>",
                lambda event, selected_item=item:
                    self._update_font_mode_options(selected_item),
            )
            ttk.Spinbox(
                font_frame,
                from_=6,
                to=72,
                textvariable=self.entry_font_sizes[item],
                width=6,
            ).grid(row=row, column=3, padx=4, pady=4)
            ttk.Entry(
                font_frame,
                textvariable=self.entry_font_colors[item],
                width=9,
            ).grid(row=row, column=4, padx=4, pady=4)
            ttk.Button(
                font_frame,
                text="選択",
                command=lambda current=item: self._choose_entry_font_color(
                    current
                ),
            ).grid(row=row, column=5, padx=4, pady=4)

        self._update_font_mode_options()

        ttk.Label(
            font_frame,
            text="旧設定の共通フォント・色は、個別設定の既定値として保持されます。",
        ).grid(row=4, column=0, columnspan=6, sticky=tk.W, pady=(8, 0))

        ttk.Label(color_frame, text="旧設定の共通文字色").grid(
            row=0, column=0, sticky=tk.W, padx=4, pady=4
        )
        ttk.Entry(
            color_frame,
            textvariable=self.font_color,
            width=12,
        ).grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(
            color_frame,
            text="選択...",
            command=self._choose_font_color,
        ).grid(row=0, column=2, padx=4, pady=4)
        ttk.Label(
            color_frame,
            text="共通背景色（指定時は時間帯色より優先）",
        ).grid(
            row=1, column=0, sticky=tk.W, padx=4, pady=4
        )
        ttk.Entry(
            color_frame,
            textvariable=self.fill_color,
            width=12,
        ).grid(row=1, column=1, padx=4, pady=4)
        ttk.Button(
            color_frame,
            text="選択...",
            command=self._choose_fill_color,
        ).grid(row=1, column=2, padx=4, pady=4)
        ttk.Label(
            color_frame,
            text="時間帯別背景色",
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
            padx=4,
            pady=4,
        )

        ttk.Combobox(
            color_frame,
            textvariable=self.striped_train_fill,
            values=(
                STRIPED_TRAIN_FILL_NONE,
                STRIPED_TRAIN_FILL_BOTH,
                STRIPED_TRAIN_FILL_METADATA,
                STRIPED_TRAIN_FILL_MINUTE,
            ),
            state="readonly",
            width=16,
        ).grid(
            row=2,
            column=1,
            sticky=tk.W,
            padx=4,
            pady=4,
        )

        direction_fill_fields = (
            ("上り基本", self.up_timetable_fill, "up"),
            ("上り交互", self.up_timetable_alt_fill, "up_alt"),
            ("下り基本", self.down_timetable_fill, "down"),
            ("下り交互", self.down_timetable_alt_fill, "down_alt"),
        )
        for offset, (label, variable, color_type) in enumerate(
            direction_fill_fields
        ):
            row = 3 + offset // 2
            column = (offset % 2) * 3
            ttk.Label(color_frame, text=label).grid(
                row=row,
                column=column,
                sticky=tk.W,
                padx=4,
                pady=2,
            )
            ttk.Entry(
                color_frame,
                textvariable=variable,
                width=12,
            ).grid(
                row=row,
                column=column + 1,
                padx=4,
                pady=2,
            )
            ttk.Button(
                color_frame,
                text="選択...",
                command=lambda current=color_type: (
                    self._choose_timetable_fill(current)
                ),
            ).grid(
                row=row,
                column=column + 2,
                padx=4,
                pady=2,
            )

        ttk.Label(color_frame, text="列車種別ごとの背景色").grid(
            row=5, column=0, columnspan=3, sticky=tk.W, pady=(10, 4)
        )
        ttk.Label(
            color_frame,
            text="分強調",
        ).grid(row=5, column=3, sticky=tk.W, pady=(10, 4))
        ttk.Label(
            color_frame,
            text="分強調背景色",
        ).grid(row=5, column=4, columnspan=2, sticky=tk.W, pady=(10, 4))
        for row, train_type in enumerate(self.train_types, start=6):
            ttk.Label(color_frame, text=train_type.name).grid(
                row=row, column=0, sticky=tk.W, padx=4, pady=2
            )
            ttk.Entry(
                color_frame,
                textvariable=self.train_type_fills[train_type.index],
                width=12,
            ).grid(row=row, column=1, padx=4, pady=2)
            ttk.Button(
                color_frame,
                text="選択...",
                command=lambda index=train_type.index: self._choose_train_type_fill(
                    index
                ),
            ).grid(row=row, column=2, padx=4, pady=2)
            ttk.Checkbutton(
                color_frame,
                variable=self.train_type_minute_highlight_enabled[
                    train_type.index
                ],
            ).grid(row=row, column=3, padx=4, pady=2)
            ttk.Entry(
                color_frame,
                textvariable=(
                    self.train_type_minute_highlight_fills[train_type.index]
                ),
                width=12,
            ).grid(row=row, column=4, padx=4, pady=2)
            ttk.Button(
                color_frame,
                text="選択...",
                command=lambda index=train_type.index: (
                    self._choose_train_type_minute_highlight_fill(index)
                ),
            ).grid(row=row, column=5, padx=4, pady=2)

        border_row = self._create_border_widgets(
            border_frame,
            start_row=0,
        )
        self._create_train_separator_widgets(border_frame, border_row)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

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

        ttk.Label(frame, text="上りヘッダ文字列").grid(
            row=1,
            column=0,
            sticky=tk.W,
        )
        ttk.Entry(
            frame,
            textvariable=self.up_header_text,
            width=28,
        ).grid(
            row=1,
            column=1,
            columnspan=2,
            padx=(10, 0),
            pady=4,
            sticky=tk.W,
        )

        ttk.Label(frame, text="下りヘッダ文字列").grid(
            row=2,
            column=0,
            sticky=tk.W,
        )
        ttk.Entry(
            frame,
            textvariable=self.down_header_text,
            width=28,
        ).grid(
            row=2,
            column=1,
            columnspan=2,
            padx=(10, 0),
            pady=4,
            sticky=tk.W,
        )

        ttk.Label(
            frame,
            text="フォント",
        ).grid(
            row=3,
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
            row=3,
            column=1,
            columnspan=2,
            padx=(10, 0),
            pady=4,
        )

        ttk.Label(
            frame,
            text="サイズ",
        ).grid(
            row=4,
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
            row=4,
            column=1,
            sticky=tk.W,
            padx=(10, 0),
            pady=4,
        )

        ttk.Label(
            frame,
            text="文字色",
        ).grid(
            row=5,
            column=0,
            sticky=tk.W,
        )

        ttk.Entry(
            frame,
            textvariable=self.header_font_color,
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
            command=self._choose_header_font_color,
        ).grid(
            row=5,
            column=2,
            padx=(5, 0),
        )

        ttk.Label(
            frame,
            text="共通ヘッダ背景色",
        ).grid(
            row=6,
            column=0,
            sticky=tk.W,
        )

        ttk.Entry(
            frame,
            textvariable=self.header_fill,
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
            command=self._choose_header_fill,
        ).grid(
            row=6,
            column=2,
            padx=(5, 0),
        )

        ttk.Label(frame, text="上りヘッダ背景色").grid(
            row=7,
            column=0,
            sticky=tk.W,
        )
        ttk.Entry(
            frame,
            textvariable=self.up_header_fill,
            width=12,
        ).grid(
            row=7,
            column=1,
            padx=(10, 0),
            pady=4,
        )
        ttk.Button(
            frame,
            text="選択...",
            command=self._choose_up_header_fill,
        ).grid(
            row=7,
            column=2,
            padx=(5, 0),
        )

        ttk.Label(frame, text="下りヘッダ背景色").grid(
            row=8,
            column=0,
            sticky=tk.W,
        )
        ttk.Entry(
            frame,
            textvariable=self.down_header_fill,
            width=12,
        ).grid(
            row=8,
            column=1,
            padx=(10, 0),
            pady=4,
        )
        ttk.Button(
            frame,
            text="選択...",
            command=self._choose_down_header_fill,
        ).grid(
            row=8,
            column=2,
            padx=(5, 0),
        )

        border_row = self._create_border_widgets(
            frame,
            start_row=9,
        )

        button_frame = ttk.Frame(frame)
        button_frame.grid(
            row=border_row,
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

        border_row = self._create_border_widgets(
            frame,
            start_row=5,
        )

        button_frame = ttk.Frame(frame)
        button_frame.grid(
            row=border_row,
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


    def _create_legend_widgets(self, frame: ttk.Frame) -> None:
        """凡例設定用ウィジェットを作成する。"""
        ttk.Label(frame, text="ラベルフォント").grid(
            row=0,
            column=0,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Combobox(
            frame,
            textvariable=self.legend_label_font_name,
            values=self._get_available_fonts(),
            state="readonly",
            width=30,
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=5,
            pady=5,
        )

        ttk.Label(frame, text="ラベルサイズ").grid(
            row=1,
            column=0,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Spinbox(
            frame,
            from_=6,
            to=72,
            textvariable=self.legend_label_font_size,
            width=8,
        ).grid(
            row=1,
            column=1,
            sticky="w",
            padx=5,
            pady=5,
        )

        ttk.Label(frame, text="ラベル文字色").grid(
            row=2,
            column=0,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Entry(
            frame,
            textvariable=self.legend_label_font_color,
            width=12,
        ).grid(
            row=2,
            column=1,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Button(
            frame,
            text="選択",
            command=self._choose_legend_label_font_color,
        ).grid(
            row=2,
            column=2,
            padx=5,
            pady=5,
        )

        ttk.Label(frame, text="ラベル背景色").grid(
            row=3,
            column=0,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Entry(
            frame,
            textvariable=self.legend_label_fill,
            width=12,
        ).grid(
            row=3,
            column=1,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Button(
            frame,
            text="選択",
            command=self._choose_legend_label_fill,
        ).grid(
            row=3,
            column=2,
            padx=5,
            pady=5,
        )

        ttk.Label(frame, text="凡例フォント").grid(
            row=4,
            column=0,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Combobox(
            frame,
            textvariable=self.legend_font_name,
            values=self._get_available_fonts(),
            state="readonly",
            width=30,
        ).grid(
            row=4,
            column=1,
            sticky="ew",
            padx=5,
            pady=5,
        )

        ttk.Label(frame, text="凡例サイズ").grid(
            row=5,
            column=0,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Spinbox(
            frame,
            from_=6,
            to=72,
            textvariable=self.legend_font_size,
            width=8,
        ).grid(
            row=5,
            column=1,
            sticky="w",
            padx=5,
            pady=5,
        )

        ttk.Label(frame, text="凡例項目文字色").grid(
            row=6,
            column=0,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Entry(
            frame,
            textvariable=self.legend_font_color,
            width=12,
        ).grid(
            row=6,
            column=1,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Button(
            frame,
            text="選択",
            command=self._choose_legend_font_color,
        ).grid(
            row=6,
            column=2,
            padx=5,
            pady=5,
        )

        ttk.Label(frame, text="凡例背景色").grid(
            row=7,
            column=0,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Entry(
            frame,
            textvariable=self.legend_fill,
            width=12,
        ).grid(
            row=7,
            column=1,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Button(
            frame,
            text="選択",
            command=self._choose_legend_fill,
        ).grid(
            row=7,
            column=2,
            padx=5,
            pady=5,
        )

        ttk.Label(frame, text="行の高さ").grid(
            row=8,
            column=0,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Spinbox(
            frame,
            from_=10.0,
            to=100.0,
            increment=0.1,
            textvariable=self.legend_row_height,
            width=8,
        ).grid(
            row=8,
            column=1,
            sticky="w",
            padx=5,
            pady=5,
        )

        ttk.Checkbutton(
            frame,
            text="駅略称の行先凡例を表示する",
            variable=self.show_destination_legend,
        ).grid(
            row=9,
            column=0,
            columnspan=3,
            sticky=tk.W,
            padx=5,
            pady=(6, 4),
        )

        row = 10

        ttk.Label(
            frame,
            text="列車種別色",
        ).grid(
            row=row,
            column=0,
            sticky=tk.W,
            pady=(10, 4),
        )

        row += 1

        for train_type in self.train_types:
            ttk.Checkbutton(
                frame,
                text=(
                    f"{train_type.name}（{train_type.short_name}）"
                    if train_type.short_name
                    else train_type.name
                ),
                variable=self.train_type_visible[train_type.index],
            ).grid(
                row=row,
                column=0,
                sticky=tk.W,
                padx=(10, 0),
                pady=2,
            )

            ttk.Button(
                frame,
                text="色を選択",
                command=lambda index=train_type.index: self._choose_train_type_color(
                    index
                ),
            ).grid(
                row=row,
                column=1,
                sticky=tk.W,
                padx=(8, 0),
                pady=2,
            )

            ttk.Entry(
                frame,
                textvariable=self.train_type_colors[train_type.index],
                width=8,
            ).grid(
                row=row,
                column=2,
                sticky=tk.W,
                padx=(8, 0),
                pady=2,
            )

            row += 1

        border_row = self._create_border_widgets(
            frame,
            start_row=row,
        )

        button_frame = ttk.Frame(frame)
        button_frame.grid(
            row=border_row,
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


    def _create_border_widgets(
        self,
        frame: ttk.Frame,
        start_row: int,
    ) -> int:
        """罫線設定用ウィジェットを作成する。"""
        border_frame = ttk.LabelFrame(
            frame,
            text="罫線",
            padding=10,
        )
        border_frame.grid(
            row=start_row,
            column=0,
            columnspan=3,
            sticky=tk.EW,
            pady=(15, 0),
        )

        ttk.Label(
            border_frame,
            text="",
        ).grid(row=0, column=0, padx=5)

        ttk.Label(
            border_frame,
            text="設定",
        ).grid(row=0, column=1, padx=5)

        ttk.Label(
            border_frame,
            text="色",
        ).grid(row=0, column=2, padx=5)

        ttk.Label(
            border_frame,
            text="",
        ).grid(row=0, column=3, padx=5)

        ttk.Label(
            border_frame,
            text="線種",
        ).grid(row=0, column=4, padx=5)

        side_names = {
            "top": "上",
            "bottom": "下",
            "left": "左",
            "right": "右",
        }

        for row, side in enumerate(
            ("top", "bottom", "left", "right"),
            start=1,
        ):
            ttk.Label(
                border_frame,
                text=side_names[side],
            ).grid(
                row=row,
                column=0,
                sticky=tk.W,
                padx=5,
                pady=2,
            )

            ttk.Checkbutton(
                border_frame,
                variable=self.border_enabled[side],
            ).grid(
                row=row,
                column=1,
                padx=5,
                pady=2,
            )

            ttk.Entry(
                border_frame,
                textvariable=self.border_colors[side],
                width=10,
            ).grid(
                row=row,
                column=2,
                padx=5,
                pady=2,
            )

            ttk.Button(
                border_frame,
                text="選択...",
                command=lambda s=side: self._choose_border_color(s),
            ).grid(
                row=row,
                column=3,
                padx=5,
                pady=2,
            )

            ttk.Combobox(
                border_frame,
                textvariable=self.border_styles[side],
                values=list(BORDER_STYLES.keys()),
                state="readonly",
                width=10,
            ).grid(
                row=row,
                column=4,
                padx=5,
                pady=2,
            )

        return start_row + 1


    def _create_train_separator_widgets(
        self,
        parent: tk.Misc,
        row: int,
    ) -> int:
        """列車欄の上下段の境界線設定を作成する。"""

        frame = ttk.LabelFrame(
            parent,
            text="行先・列車種別と分の境界",
            padding=10,
        )
        frame.grid(
            row=row,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(10, 0),
        )

        ttk.Checkbutton(
            frame,
            text="設定",
            variable=self.train_separator_enabled,
        ).grid(
            row=0,
            column=0,
            padx=(0, 10),
        )

        ttk.Label(
            frame,
            text="色",
        ).grid(
            row=0,
            column=1,
            padx=(0, 5),
        )

        ttk.Entry(
            frame,
            textvariable=self.train_separator_color,
            width=10,
        ).grid(
            row=0,
            column=2,
            padx=(0, 5),
        )
        
        ttk.Button(
            frame,
            text="選択...",
            command=self._choose_train_separator_color,
        ).grid(
            row=0,
            column=3,
            padx=(0, 10),
        )

        ttk.Label(
            frame,
            text="線種",
        ).grid(
            row=0,
            column=4,
            padx=(0, 5),
        )

        ttk.Combobox(
            frame,
            textvariable=self.train_separator_style,
            values=list(BORDER_STYLES.keys()),
            state="readonly",
            width=10,
        ).grid(
            row=0,
            column=5,
        )

        return row + 1


    def _get_border_config(self):
        """現在の設定対象に対応する罫線設定を返す。"""
        border_configs = {
            PreviewItem.TITLE: self.display_config.title_border,
            PreviewItem.HEADER: self.display_config.header_border,
            PreviewItem.HOUR: self.display_config.hour_border,
            PreviewItem.TRAIN: self.display_config.train_border,
            PreviewItem.LEGEND: self.display_config.legend_border,
        }

        return border_configs[self.item]
    

    def _create_border_variables(self) -> None:
        """罫線設定用のTk変数を作成する。"""
        border_config = self._get_border_config()

        self.border_enabled: dict[str, tk.BooleanVar] = {}
        self.border_colors: dict[str, tk.StringVar] = {}
        self.border_styles: dict[str, tk.StringVar] = {}

        for side in ("top", "bottom", "left", "right"):
            side_config = getattr(border_config, side)

            self.border_enabled[side] = tk.BooleanVar(
                value=side_config.enabled,
            )
            self.border_colors[side] = tk.StringVar(
                value=side_config.color,
            )
            self.border_styles[side] = tk.StringVar(
                value=side_config.style,
            )

        self.train_separator_enabled = tk.BooleanVar(
            value=False
        )
        self.train_separator_color = tk.StringVar(
            value="000000"
        )
        self.train_separator_style = tk.StringVar(
            value=self._style_to_label("thin")
        )

        if self.item == PreviewItem.TRAIN:
            separator = self.display_config.train_separator

            self.train_separator_enabled.set(
                separator.enabled
            )
            self.train_separator_color.set(
                separator.color
            )
            self.train_separator_style.set(
                self._style_to_label(separator.style)
            )


    def _choose_border_color(self, side: str) -> None:
        """指定した辺の罫線色を選択する。"""
        current_color = self.border_colors[side].get().strip()

        if current_color:
            current_color = f"#{current_color.lstrip('#')}"

        color = colorchooser.askcolor(
            initialcolor=current_color or "#000000",
            parent=self,
        )

        if color[1] is not None:
            self.border_colors[side].set(
                color[1].lstrip("#").upper()
            )


    def _choose_train_separator_color(self) -> None:
        """列車欄の上下段境界線の色を選択する。"""

        color = colorchooser.askcolor(
            initialcolor=f"#{self.train_separator_color.get()}",
            parent=self,
        )

        if color[1]:
            self.train_separator_color.set(
                color[1].lstrip("#").upper()
            )


    def _choose_train_type_color(
        self,
        train_type_index: int,
    ) -> None:
        color = colorchooser.askcolor(
            title="列車種別の色を選択",
            initialcolor=f"#{self.train_type_colors[train_type_index].get()}",
            parent=self,
        )

        if color[1] is None:
            return

        self.train_type_colors[train_type_index].set(
            color[1].lstrip("#").upper()
        )


    def _choose_timetable_fill(self, color_type: str) -> None:
        """時間帯別背景色を選択する。"""
        variables = {
            "up": self.up_timetable_fill,
            "up_alt": self.up_timetable_alt_fill,
            "down": self.down_timetable_fill,
            "down_alt": self.down_timetable_alt_fill,
        }

        variable = variables[color_type]
        current = variable.get().strip()

        color = colorchooser.askcolor(
            title="時間帯別背景色を選択",
            initialcolor=(
                f"#{current.lstrip('#')}"
                if current
                else "#FFFFFF"
            ),
            parent=self,
        )

        if color[1] is not None:
            variable.set(
                color[1].lstrip("#").upper()
            )


    def _choose_train_type_fill(
        self,
        train_type_index: int,
    ) -> None:
        current = self.train_type_fills[train_type_index].get().strip()
        color = colorchooser.askcolor(
            title="列車種別の背景色を選択",
            initialcolor=f"#{current.lstrip('#')}" if current else "#FFFFFF",
            parent=self,
        )
        if color[1] is not None:
            self.train_type_fills[train_type_index].set(
                color[1].lstrip("#").upper()
            )

    def _choose_train_type_minute_highlight_fill(
        self,
        train_type_index: int,
    ) -> None:
        current = (
            self.train_type_minute_highlight_fills[
                train_type_index
            ].get().strip()
        )
        color = colorchooser.askcolor(
            title="列車種別の分強調背景色を選択",
            initialcolor=f"#{current.lstrip('#')}" if current else "#FFF2CC",
            parent=self,
        )
        if color[1] is not None:
            self.train_type_minute_highlight_fills[
                train_type_index
            ].set(
                color[1].lstrip("#").upper()
            )

    def _choose_entry_font_color(self, item: str) -> None:
        current = self.entry_font_colors[item].get().strip()
        color = colorchooser.askcolor(
            title=f"{item}の文字色を選択",
            initialcolor=f"#{current.lstrip('#')}" if current else "#000000",
            parent=self,
        )
        if color[1] is not None:
            self.entry_font_colors[item].set(
                color[1].lstrip("#").upper()
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


    def _choose_legend_label_font_color(self) -> None:
        current_color = self.legend_label_font_color.get().strip()
        if current_color:
            current_color = f"#{current_color.lstrip('#')}"

        color = colorchooser.askcolor(
            initialcolor=current_color or "#000000",
            parent=self,
        )
        if color[1] is not None:
            self.legend_label_font_color.set(
                color[1].lstrip("#").upper()
            )


    def _choose_legend_font_color(self) -> None:
        """凡例項目の文字色を選択する。"""
        current_color = self.legend_font_color.get().strip()

        if current_color:
            current_color = f"#{current_color.lstrip('#')}"

        color = colorchooser.askcolor(
            initialcolor=current_color or "#000000",
            parent=self,
        )

        if color[1] is not None:
            self.legend_font_color.set(
                color[1].lstrip("#").upper()
            )


    def _choose_legend_label_fill(self) -> None:
        current_color = self.legend_label_fill.get().strip()
        if current_color:
            current_color = f"#{current_color.lstrip('#')}"

        color = colorchooser.askcolor(
            initialcolor=current_color or "#000000",
            parent=self,
        )
        if color[1] is not None:
            self.legend_label_fill.set(
                color[1].lstrip("#").upper()
            )


    def _choose_legend_fill(self) -> None:
        current_color = self.legend_fill.get().strip()
        if current_color:
            current_color = f"#{current_color.lstrip('#')}"

        color = colorchooser.askcolor(
            initialcolor=current_color or "#FFFFFF",
            parent=self,
        )
        if color[1] is not None:
            self.legend_fill.set(
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

    def _choose_up_header_fill(self) -> None:
        """上りヘッダの塗りつぶし色を選択する。"""
        current_color = self.up_header_fill.get().strip()
        color = colorchooser.askcolor(
            initialcolor=(
                f"#{current_color.lstrip('#')}"
                if current_color
                else "#FFFFFF"
            ),
            parent=self,
        )
        if color[1] is not None:
            self.up_header_fill.set(
                color[1].lstrip("#").upper()
            )

    def _choose_down_header_fill(self) -> None:
        """下りヘッダの塗りつぶし色を選択する。"""
        current_color = self.down_header_fill.get().strip()
        color = colorchooser.askcolor(
            initialcolor=(
                f"#{current_color.lstrip('#')}"
                if current_color
                else "#FFFFFF"
            ),
            parent=self,
        )
        if color[1] is not None:
            self.down_header_fill.set(
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
            case PreviewItem.LEGEND:
                self._apply_legend()
            case _:
                pass

        self._apply_border()
        self._apply_train_separator()

        parent = self.master

        if hasattr(parent, "redraw"):
            parent.redraw()

        if hasattr(parent, "on_display_config_changed"):
            callback = parent.on_display_config_changed
            if callback is not None:
                callback()

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
        self.display_config.train_font_color = (
            self.font_color.get()
        )

        fill_color = self.fill_color.get().strip()
        self.display_config.train_fill = (
            fill_color if fill_color else None
        )

        self.display_config.use_train_type_short_name = (
            self.use_train_type_short_name.get()
        )

        self.display_config.show_destination = (
            self.show_destination.get()
        )

        self.display_config.train_type_column_visible = {
            index: variable.get()
            for index, variable in self.train_type_column_visible.items()
        }
        self.display_config.destination_position = (
            "bottom" if self.destination_position.get() == "下段" else "top"
        )
        self.display_config.train_type_position = (
            "bottom" if self.train_type_position.get() == "下段" else "top"
        )
        self.display_config.metadata_order = (
            "train_type_first"
            if self.metadata_order.get() == "列車種別→行先"
            else "destination_first"
        )
        self.display_config.hour_column_mode = (
            "center"
            if self.hour_column_mode.get() == "中央配置"
            else "separate"
        )
        self.display_config.striped_train_fill = (
            self.striped_train_fill.get()
        )
        self.display_config.up_timetable_fill = (
            self.up_timetable_fill.get().strip().lstrip("#").upper()
            or "FAFAFA"
        )
        self.display_config.up_timetable_alt_fill = (
            self.up_timetable_alt_fill.get().strip().lstrip("#").upper()
            or "C8E6C9"
        )
        self.display_config.down_timetable_fill = (
            self.down_timetable_fill.get().strip().lstrip("#").upper()
            or "FAFAFA"
        )
        self.display_config.down_timetable_alt_fill = (
            self.down_timetable_alt_fill.get().strip().lstrip("#").upper()
            or "C8E6C9"
        )

        font_mode_keys = {
            label: mode
            for mode, label in self._FONT_MODE_LABELS.items()
        }
        for item in ("destination", "train_type", "minute"):
            setattr(
                self.display_config,
                f"{item}_font_mode",
                font_mode_keys[self.entry_font_modes[item].get()],
            )
            font_name = self.entry_font_names[item].get().strip()
            font_color = (
                self.entry_font_colors[item]
                .get()
                .strip()
                .lstrip("#")
                .upper()
            )
            setattr(
                self.display_config,
                f"{item}_font_name",
                font_name or None,
            )
            setattr(
                self.display_config,
                f"{item}_font_size",
                self.entry_font_sizes[item].get(),
            )
            setattr(
                self.display_config,
                f"{item}_font_color",
                font_color or None,
            )

        self.display_config.minute_font_name = (
            self.entry_font_names["minute"].get().strip()
            or self.display_config.minute_font_name
        )
        self.display_config.minute_font_size = (
            self.entry_font_sizes["minute"].get()
        )
        self.display_config.minute_font_color = (
            self.entry_font_colors["minute"].get().strip().lstrip("#").upper()
            or None
        )
        self.display_config.train_type_fills = {
            index: variable.get().strip().lstrip("#").upper()
            for index, variable in self.train_type_fills.items()
            if variable.get().strip().lstrip("#")
        }
        self.display_config.train_type_minute_highlight_enabled = {
            index: variable.get()
            for index, variable
            in self.train_type_minute_highlight_enabled.items()
        }
        self.display_config.train_type_minute_highlight_fills = {
            index: variable.get().strip().lstrip("#").upper()
            for index, variable
            in self.train_type_minute_highlight_fills.items()
            if variable.get().strip().lstrip("#")
        }


    def _apply_header(self) -> None:
        """ヘッダの表示設定を適用する。"""
        self.display_config.up_header_text = self.up_header_text.get()
        self.display_config.down_header_text = self.down_header_text.get()
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

        up_fill_color = self.up_header_fill.get().strip()
        self.display_config.up_header_fill = (
            up_fill_color if up_fill_color else None
        )
        down_fill_color = self.down_header_fill.get().strip()
        self.display_config.down_header_fill = (
            down_fill_color if down_fill_color else None
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


    def _apply_legend(self) -> None:
        """凡例の設定を表示設定へ反映する。"""
        self.display_config.legend_label_font_name = (
            self.legend_label_font_name.get()
        )
        self.display_config.legend_label_font_size = (
            self.legend_label_font_size.get()
        )
        self.display_config.legend_label_font_color = (
            self.legend_label_font_color.get().strip().lstrip("#").upper()
        )
        self.display_config.legend_label_fill = (
            self.legend_label_fill.get().strip().lstrip("#").upper()
        )

        self.display_config.legend_font_name = (
            self.legend_font_name.get()
        )
        self.display_config.legend_font_size = (
            self.legend_font_size.get()
        )
        self.display_config.legend_font_color = (
            self.legend_font_color.get().strip().lstrip("#").upper()
        )
        self.display_config.legend_fill = (
            self.legend_fill.get().strip().lstrip("#").upper()
        )
        self.display_config.legend_row_height = (
            self.legend_row_height.get()
        )

        for train_type_index, color_var in self.train_type_colors.items():
            self.display_config.train_type_colors[train_type_index] = (
                color_var.get().strip().lstrip("#").upper()
            )

        for train_type_index, visible_var in self.train_type_visible.items():
            self.display_config.train_type_visible[train_type_index] = (
                visible_var.get()
            )

        self.display_config.show_destination_legend = (
            self.show_destination_legend.get()
        )


    def _apply_border(self) -> None:
        """罫線設定を表示設定へ反映する。"""
        border_config = self._get_border_config()

        for side in ("top", "bottom", "left", "right"):
            side_config = getattr(border_config, side)

            side_config.enabled = (
                self.border_enabled[side].get()
            )
            side_config.color = (
                self.border_colors[side].get()
                .strip()
                .lstrip("#")
                .upper()
            )
            side_config.style = self._label_to_style(
                self.border_styles[side].get()
            )


    def _apply_train_separator(self) -> None:
        """列車欄の上下段境界線設定を保存する。"""

        if self.item != PreviewItem.TRAIN:
            return

        separator = self.display_config.train_separator

        separator.enabled = self.train_separator_enabled.get()
        separator.color = self.train_separator_color.get()
        separator.style = self._label_to_style(
            self.train_separator_style.get()
        )


    def _style_to_label(self, style: str) -> str:
        """OpenPyXLの線種を表示名へ変換する。"""
        for label, value in BORDER_STYLES.items():
            if value == style:
                return label

        return "細線"


    def _label_to_style(self, label: str) -> str:
        """表示名をOpenPyXLの線種へ変換する。"""
        return BORDER_STYLES.get(label, "thin")

