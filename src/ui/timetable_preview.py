import tkinter as tk
from tkinter import ttk

import tkinter.font as tkfont

from src.ui.display_config_dialog import DisplayConfigDialog
from src.ui.preview_item import PreviewItem

from src.timetable.display_config import (
    BorderConfig,
    TimetableDisplayConfig,
)
from src.timetable.display_layout import (
    HourSlot,
    get_entry_layout,
    merge_timetable_hours,
)

from src.models.timetable import (
    TimetableEntry,
    StationTimetable,
    TimetableHour,
)


class TimetablePreview(tk.Frame):
    """レイアウト設定用の駅時刻表プレビュー。"""

    _CELL_WIDTH = 72
    _HOUR_WIDTH = 45
    _CELL_HEIGHT = 24
    _HEADER_HEIGHT = 28
    _TITLE_HEIGHT = 40
    _DIRECTION_GAP = 16

    def __init__(
        self,
        master: tk.Misc,
        display_config: TimetableDisplayConfig | None = None,
        on_display_config_changed=None,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)

        self.display_config = (
            display_config
            if display_config is not None
            else TimetableDisplayConfig()
        )

        self.on_display_config_changed = on_display_config_changed

        container = ttk.Frame(self)
        container.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self.canvas = tk.Canvas(
            container,
            background="white",
            highlightthickness=0,
        )
        self.canvas.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        scrollbar = ttk.Scrollbar(
            container,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
        )
        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set,
        )

        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.bind(
            "<Configure>",
            self._on_configure,
        )

        self.canvas.bind(
            "<Button-1>", 
            self._on_click
        )

        self.timetable: StationTimetable | None = None


    def _on_configure(
        self,
        event: tk.Event,
    ) -> None:
        """ウィジェットサイズ変更時にプレビューを再描画する。"""
        self._draw()


    def _draw(self) -> None:
        """時刻表を描画する。"""

        self.canvas.delete("all")

        if self.timetable is None:
            """ダミーデータを表示する。"""
            title = "B駅 時刻表"

            down_hours = [
                TimetableHour(
                    hour=4,
                    entries=[],
                ),
            ]

            up_hours = [
                TimetableHour(
                    hour=4,
                    entries=[],
                ),
            ]

        else:
            """実際の時刻表データを表示する。"""
            title = f"{self.timetable.station_name}駅 時刻表"

            down_hours = self.timetable.down
            up_hours = self.timetable.up

        slots = merge_timetable_hours(down_hours, up_hours)
        down_train_count = max(
            (len(slot.down_entries) for slot in slots),
            default=0,
        )
        up_train_count = max(
            (len(slot.up_entries) for slot in slots),
            default=0,
        )
        central_hour_column = (
            self.display_config.hour_column_mode == "center"
        )
        down_train_width = self._CELL_WIDTH * max(down_train_count, 1)
        up_train_width = self._CELL_WIDTH * max(up_train_count, 1)
        if central_hour_column:
            down_width = down_train_width
            up_width = up_train_width
            total_width = down_width + self._HOUR_WIDTH + up_width
        else:
            down_width = self._HOUR_WIDTH + down_train_width
            up_width = self._HOUR_WIDTH + up_train_width
            total_width = down_width + up_width + self._DIRECTION_GAP

        row_counts = [
            self._hour_row_count(slot)
            for slot in slots
        ]

        # 凡例の高さを、下り・上りそれぞれの項目数から計算
        down_legend_rows, up_legend_rows, _, _ = (
            self._get_legend_layout(down_width, up_width)
        )
        legend_rows = max(
            len(down_legend_rows),
            len(up_legend_rows),
            1,
        )

        direction_height = (
            self._HEADER_HEIGHT
            + self._CELL_HEIGHT * sum(row_counts)
        )

        legend_height = (
            self.display_config.legend_row_height
            * legend_rows
        )

        total_height = (
            self._TITLE_HEIGHT
            + direction_height
            + 10
            + legend_height
        )

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        x0 = max(
            (canvas_width - total_width) / 2,
            10,
        )
        y0 = max(
            (canvas_height - total_height) / 2,
            10,
        )

        # タイトル
        self._draw_title(
            x=x0,
            y=y0,
            width=total_width,
            title=title,
        )

        direction_y = y0 + self._TITLE_HEIGHT

        # 上り
        self._draw_direction(
            x=x0,
            y=direction_y,
            width=up_width,
            title=self.display_config.up_header_text,
            slots=slots,
            direction="up",
            include_hour_column=not central_hour_column,
            row_counts=row_counts,
        )

        self._draw_direction(
            x=(
                x0 + up_width + self._HOUR_WIDTH
                if central_hour_column
                else x0 + up_width + self._DIRECTION_GAP
            ),
            y=direction_y,
            width=down_width,
            title=self.display_config.down_header_text,
            slots=slots,
            direction="down",
            include_hour_column=not central_hour_column,
            row_counts=row_counts,
        )
        if central_hour_column:
            self._draw_center_hour_column(
                x=x0 + up_width,
                y=direction_y,
                slots=slots,
                row_counts=row_counts,
            )

        # 凡例
        legend_y = (
            direction_y
            + direction_height
            + 10
        )

        self._draw_legend(
            x=x0,
            y=legend_y,
            down_width=down_width,
            up_width=up_width,
            central_hour_column=central_hour_column,
        )

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )


    def _draw_border(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        border: BorderConfig,
    ) -> None:
        """指定された範囲に罫線を描画する。"""

        if border.top.enabled:
            self.canvas.create_line(
                x1,
                y1,
                x2,
                y1,
                fill=self._to_tk_color(border.top.color),
                width=self._border_width(border.top.style),
            )

        if border.bottom.enabled:
            self.canvas.create_line(
                x1,
                y2,
                x2,
                y2,
                fill=self._to_tk_color(border.bottom.color),
                width=self._border_width(border.bottom.style),
            )

        if border.left.enabled:
            self.canvas.create_line(
                x1,
                y1,
                x1,
                y2,
                fill=self._to_tk_color(border.left.color),
                width=self._border_width(border.left.style),
            )

        if border.right.enabled:
            self.canvas.create_line(
                x2,
                y1,
                x2,
                y2,
                fill=self._to_tk_color(border.right.color),
                width=self._border_width(border.right.style),
            )

    @staticmethod
    def _border_width(style: str) -> int:
        """罫線種別をCanvasの線幅へ変換する。"""

        widths = {
            "thin": 1,
            "medium": 2,
            "thick": 3,
        }

        return widths.get(style, 1)


    def _draw_title(
        self,
        x: float,
        y: float,
        width: float,
        title: str,
    ) -> None:
        """タイトルを描画する。"""
        self.canvas.create_rectangle(
            x,
            y,
            x + width,
            y + self._TITLE_HEIGHT,
            fill=self._to_tk_color(
                self.display_config.title_fill
            ) or "#FFFFFF",
            outline="",
            tags=(PreviewItem.TITLE,),
        )

        self._draw_border(
            x,
            y,
            x + width,
            y + self._TITLE_HEIGHT,
            self.display_config.title_border,
        )

        self.canvas.create_text(
            x + width / 2,
            y + self._TITLE_HEIGHT / 2,
            text=title,
            font=(
                self.display_config.title_font_name,
                self.display_config.title_font_size,
                "bold",
            ),
            fill=self._to_tk_color(
                self.display_config.title_font_color
            ),
        )


    def _draw_direction(
        self,
        x: float,
        y: float,
        width: float,
        title: str,
        slots: list[HourSlot],
        direction: str,
        include_hour_column: bool,
        row_counts: list[int],
    ) -> None:
        """下り・上りの時刻表を描画する。"""
        config = self.display_config
        # ヘッダ
        self.canvas.create_rectangle(
            x,
            y,
            x + width,
            y + self._HEADER_HEIGHT,
            fill=self._to_tk_color(
                (
                    config.up_header_fill
                    if direction == "up"
                    else config.down_header_fill
                )
                or config.header_fill
            ) or "#D9EAD3",
            outline="",
            tags=(PreviewItem.HEADER,),
        )

        self._draw_border(
            x,
            y,
            x + width,
            y + self._HEADER_HEIGHT,
            self.display_config.header_border,
        )

        self.canvas.create_text(
            x + width / 2,
            y + self._HEADER_HEIGHT / 2,
            text=title,
            font=(
                self.display_config.header_font_name,
                self.display_config.header_font_size,
                "bold",
            ),
            fill=self._to_tk_color(
                self.display_config.header_font_color
            ),            
        )

        header_y = y + self._HEADER_HEIGHT

        entries_start_x = x + (
            self._HOUR_WIDTH if include_hour_column else 0
        )
        current_y = header_y
        for slot, row_count in zip(slots, row_counts):
            entries = (
                slot.down_entries
                if direction == "down"
                else slot.up_entries
            )
            has_hour = (
                slot.down_present
                if direction == "down"
                else slot.up_present
            )
            if include_hour_column:
                self._draw_hour_cell(
                    x=x,
                    y=current_y,
                    hour=slot.hour if has_hour else None,
                    row_count=row_count,
                    stripe_hour=slot.hour,
                )

            for entry_index, entry in enumerate(entries):
                entry_x = entries_start_x + entry_index * self._CELL_WIDTH
                entry_layout = get_entry_layout(entry, config)
                type_fill = config.train_type_fills.get(
                    entry.train_type.index
                )

                for row_index in range(row_count):
                    row_y = current_y + row_index * self._CELL_HEIGHT
                    kinds = (
                        entry_layout[row_index]
                        if row_index < len(entry_layout)
                        else []
                    )
                    fill = self._to_tk_color(
                        (type_fill if kinds else None)
                        or config.get_entry_fill(
                            slot.hour,
                        )
                    ) or "#FAFAFA"
                    self.canvas.create_rectangle(
                        entry_x,
                        row_y,
                        entry_x + self._CELL_WIDTH,
                        row_y + self._CELL_HEIGHT,
                        fill=fill,
                        outline="",
                        tags=(PreviewItem.TRAIN,),
                    )
                    if kinds:
                        self._draw_entry_text(
                            entry=entry,
                            kinds=kinds,
                            x=entry_x,
                            y=row_y,
                        )

                    if "minute" in kinds and row_index > 0:
                        separator = config.train_separator
                        if separator.enabled:
                            self.canvas.create_line(
                                entry_x,
                                row_y,
                                entry_x + self._CELL_WIDTH,
                                row_y,
                                fill=self._to_tk_color(separator.color),
                                width=self._border_width(separator.style),
                            )

                self._draw_border(
                    entry_x,
                    current_y,
                    entry_x + self._CELL_WIDTH,
                    current_y + row_count * self._CELL_HEIGHT,
                    config.train_border,
                )

            current_y += row_count * self._CELL_HEIGHT

    def _draw_hour_cell(
        self,
        x: float,
        y: float,
        hour: int | None,
        row_count: int,
        stripe_hour: int,
    ) -> None:
        config = self.display_config
        fill = self._to_tk_color(config.hour_fill)
        if fill is None:
            hour_order = (
                (stripe_hour - 4) % 24
                if 0 <= stripe_hour < 24
                else stripe_hour
            )
            fill = self._to_tk_color(
                config.timetable_alt_fill
                if hour_order % 2 == 0
                else config.timetable_fill
            ) or "#F2F2F2"
        self.canvas.create_rectangle(
            x,
            y,
            x + self._HOUR_WIDTH,
            y + row_count * self._CELL_HEIGHT,
            fill=fill,
            outline="",
            tags=(PreviewItem.HOUR,),
        )
        self._draw_border(
            x,
            y,
            x + self._HOUR_WIDTH,
            y + row_count * self._CELL_HEIGHT,
            config.hour_border,
        )
        if hour is not None:
            self.canvas.create_text(
                x + self._HOUR_WIDTH / 2,
                y + row_count * self._CELL_HEIGHT / 2,
                text=str(hour),
                font=(
                    config.hour_font_name,
                    config.hour_font_size,
                    "bold",
                ),
                fill=self._to_tk_color(config.hour_font_color),
            )

    def _draw_entry_text(
        self,
        entry: TimetableEntry,
        kinds: list[str],
        x: float,
        y: float,
    ) -> None:
        values = {
            "destination": entry.destination.display_name,
            "train_type": (
                entry.train_type.short_name
                if (
                    self.display_config.use_train_type_short_name
                    and entry.train_type.short_name
                )
                else entry.train_type.name
            ),
            "minute": f"{entry.minute:02d}",
        }
        rendered = []
        for kind in kinds:
            font_name, font_size, color = (
                self.display_config.get_entry_font_settings(
                    kind,
                    entry.train_type.index,
                )
            )
            font = tkfont.Font(
                family=font_name,
                size=font_size,
                weight="bold" if kind == "minute" else "normal",
            )
            rendered.append((values[kind], font, color))

        spacing = 4
        total_width = sum(font.measure(text) for text, font, _ in rendered)
        total_width += spacing * max(len(rendered) - 1, 0)
        current_x = x + (self._CELL_WIDTH - total_width) / 2
        for text, font, color in rendered:
            self.canvas.create_text(
                current_x,
                y + self._CELL_HEIGHT / 2,
                anchor=tk.W,
                text=text,
                font=font,
                fill=self._to_tk_color(color),
            )
            current_x += font.measure(text) + spacing

    def _draw_center_hour_column(
        self,
        x: float,
        y: float,
        slots: list[HourSlot],
        row_counts: list[int],
    ) -> None:
        current_y = y + self._HEADER_HEIGHT
        for slot, row_count in zip(slots, row_counts):
            self._draw_hour_cell(
                x=x,
                y=current_y,
                hour=slot.hour,
                row_count=row_count,
                stripe_hour=slot.hour,
            )
            current_y += row_count * self._CELL_HEIGHT

    def _hour_row_count(self, slot: HourSlot) -> int:
        counts = [
            len(get_entry_layout(entry, self.display_config))
            for entry in (*slot.down_entries, *slot.up_entries)
        ]
        if counts:
            return max(counts)
        if (
            self.display_config.destination_position == "bottom"
            or self.display_config.train_type_position == "bottom"
        ):
            return 3
        return 2


    def _get_destination_legend_items(
        self,
        hours: list[TimetableHour] | None = None,
    ) -> list[tuple[str, str]]:
        """指定された時刻表から行先凡例を取得する。"""
        if self.timetable is None or not self.display_config.show_destination_legend:
            return []

        if hours is None:
            hours = self.timetable.down + self.timetable.up

        stations = {}

        for hour in hours:
            for entry in hour.entries:
                station = entry.destination

                if station.is_no_mark or station.short_name:
                    stations[station.name] = station

        return [
            (
                "無印" if station.is_no_mark else station.short_name,
                station.name,
            )
            for station in stations.values()
        ]


    def _get_legend_layout(
        self,
        down_width: float,
        up_width: float,
    ):
        """下り・上り別に凡例項目を横並びに配置し、必要なら折り返す。"""
        config = self.display_config

        font = tkfont.Font(
            family=config.legend_font_name,
            size=config.legend_font_size,
        )

        def build_rows(
            width: float,
            station_items: list[tuple[str, str]],
        ) -> tuple[list[list[tuple[str, str]]], float]:
            label_width = min(60, width * 0.35)
            available_width = max(
                1,
                width - label_width - 16,
            )

            # 列車種別の項目
            items: list[tuple[str, str]] = []

            if self.timetable is not None:
                for train_type in self.timetable.train_types:
                    if not config.train_type_visible.get(
                        train_type.index, True
                    ):
                        continue

                    name = (
                        train_type.short_name
                        if (
                            config.use_train_type_short_name
                            and train_type.short_name
                        )
                        else train_type.name
                    )

                    if name:
                        color = (
                            config.get_train_type_color(train_type.index)
                            or config.train_font_color
                        )
                        items.append((name, color))

            rows: list[list[tuple[str, str]]] = []

            def append_wrapped(
                group: list[tuple[str, str]],
            ) -> None:
                current_row: list[tuple[str, str]] = []
                current_width = 0

                for text, color in group:
                    item_width = font.measure(text) + 16

                    if (
                        current_row
                        and current_width + item_width > available_width
                    ):
                        rows.append(current_row)
                        current_row = []
                        current_width = 0

                    current_row.append((text, color))
                    current_width += item_width

                if current_row:
                    rows.append(current_row)

            # 列車種別を横並びにし、幅を超えたら折り返す
            append_wrapped(items)

            # 行先の略称・無印も別の段で横並びにする
            destinations = [
                (
                    f"{short_name}＝{station_name}",
                    config.legend_font_color,
                )
                for short_name, station_name in station_items
            ]
            append_wrapped(destinations)

            return rows, label_width

        down_items = (
            self._get_destination_legend_items(self.timetable.down)
            if self.timetable is not None
            else []
        )
        up_items = (
            self._get_destination_legend_items(self.timetable.up)
            if self.timetable is not None
            else []
        )

        down_rows, down_label_width = build_rows(
            down_width, down_items
        )
        up_rows, up_label_width = build_rows(
            up_width, up_items
        )

        return (
            down_rows,
            up_rows,
            down_label_width,
            up_label_width,
        )


    def _draw_legend(
        self,
        x: float,
        y: float,
        down_width: float,
        up_width: float,
        central_hour_column: bool = False,
    ) -> None:
        """下り・上りそれぞれの時刻表位置に凡例を描画する。"""
        row_height = self.display_config.legend_row_height

        (
            down_rows,
            up_rows,
            down_label_width,
            up_label_width,
        ) = self._get_legend_layout(down_width, up_width)

        legend_rows = max(len(down_rows), len(up_rows), 1)
        legend_height = row_height * legend_rows

        directions = (
            (x, up_width, up_label_width, up_rows),
            (
                x
                + up_width
                + (
                    self._HOUR_WIDTH
                    if central_hour_column
                    else self._DIRECTION_GAP
                ),
                down_width,
                down_label_width,
                down_rows,
            ),
        )

        for direction_x, width, label_width, rows in directions:
            # 方向ごとの凡例背景と罫線
            self.canvas.create_rectangle(
                direction_x,
                y,
                direction_x + width,
                y + legend_height,
                fill=self._to_tk_color(
                    self.display_config.legend_fill
                ) or "#FFFFFF",
                outline="",
                tags=(PreviewItem.LEGEND,),
            )

            self._draw_border(
                direction_x,
                y,
                direction_x + width,
                y + legend_height,
                self.display_config.legend_border,
            )

            # 「凡例」ラベルは各方向の左端に配置
            self.canvas.create_rectangle(
                direction_x,
                y,
                direction_x + label_width,
                y + legend_height,
                fill=self._to_tk_color(
                    self.display_config.legend_label_fill
                ) or "#FFFFFF",
                outline="",
            )

            self.canvas.create_text(
                direction_x + label_width / 2,
                y + legend_height / 2,
                text="凡例",
                fill=self._to_tk_color(
                    self.display_config.legend_label_font_color
                ),
                font=(
                    self.display_config.legend_label_font_name,
                    self.display_config.legend_label_font_size,
                ),
            )

            # 各段の項目を横並びに描画
            content_x = direction_x + label_width + 8

            for row_index, items in enumerate(rows):
                text_x = content_x
                text_y = y + row_height * (row_index + 0.5)

                for text, color in items:
                    item_id = self.canvas.create_text(
                        text_x,
                        text_y,
                        anchor=tk.W,
                        text=text,
                        fill=self._to_tk_color(color),
                        font=(
                            self.display_config.legend_font_name,
                            self.display_config.legend_font_size,
                        ),
                    )

                    bbox = self.canvas.bbox(item_id)
                    if bbox is not None:
                        text_x = bbox[2] + 16


    def _on_click(self, event: tk.Event) -> None:
        """プレビュー上の設定対象をクリックしたときの処理。"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        items = self.canvas.find_overlapping(
            x,
            y,
            x,
            y,
        )

        if not items:
            return

        for item_id in reversed(items):
            tags = self.canvas.gettags(item_id)

            for tag in tags:
                try:
                    item = PreviewItem(tag)
                except ValueError:
                    continue

                dialog = DisplayConfigDialog(
                    self,
                    item,
                    self.display_config,
                    train_types=(
                        self.timetable.train_types
                        if self.timetable is not None
                        else None
                    ),
                )

                dialog.protocol(
                    "WM_DELETE_WINDOW",
                    dialog.destroy,
                )

                return


    @staticmethod
    def _to_tk_color(color: str | None) -> str | None:
        """6桁RGB色をTkinter用の色文字列へ変換する。"""
        if color is None:
            return None

        if len(color) == 6:
            return f"#{color}"

        if len(color) == 7 and color.startswith("#"):
            return color

        raise ValueError(
            f"色は6桁RGBで指定してください: {color}"
        )


    def redraw(self) -> None:
        """プレビューを再描画する。"""
        self._draw()


    def set_timetable(
        self,
        timetable: StationTimetable,
    ) -> None:
        """表示する時刻表を設定する。"""
        self.timetable = timetable
        self.redraw()


    def _create_preview_trains(
        self,
        hour: TimetableHour,
    ) -> list[tuple[str, int, str, str]]:
        """1時間分の列車情報をPreview表示用データへ変換する。"""

        return [
            (
                (
                    entry.destination.display_name
                    if (
                        self.display_config.show_destination
                        and not entry.destination.is_no_mark
                    )
                    else ""
                ),
                entry.train_type.index,
                (
                    entry.train_type.short_name
                    if (
                        self.display_config.use_train_type_short_name
                        and entry.train_type.short_name
                    )
                    else entry.train_type.name
                ),
                f"{entry.minute:02d}",
            )
            for entry in hour.entries
        ]


if __name__ == "__main__":
    root = tk.Tk()
    root.title("時刻表プレビュー")
    root.geometry("900x500")

    preview = TimetablePreview(root)
    preview.pack(
        fill=tk.BOTH,
        expand=True,
        padx=10,
        pady=10,
    )

    root.mainloop()
