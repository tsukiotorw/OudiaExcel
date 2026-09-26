import tkinter as tk
from tkinter import ttk

from src.ui.display_config_dialog import DisplayConfigDialog
from src.ui.preview_item import PreviewItem

from src.timetable.display_config import TimetableDisplayConfig
from src.models.timetable import (
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
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)

        self.display_config = (
            display_config
            if display_config is not None
            else TimetableDisplayConfig()
        )

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

        down_train_count = max(
            (
                len(hour.entries)
                for hour in down_hours
            ),
            default=0,
        )

        up_train_count = max(
            (
                len(hour.entries)
                for hour in up_hours
            ),
            default=0,
        )

        # 2方向の幅
        down_width = (
            self._HOUR_WIDTH
            + self._CELL_WIDTH * max(down_train_count, 1)
        )

        up_width = (
            self._HOUR_WIDTH
            + self._CELL_WIDTH * max(up_train_count, 1)
        )

        total_width = (
            down_width
            + up_width
            + self._DIRECTION_GAP
        )

        # 凡例の高さ
        if self.timetable is not None:
            visible_train_types = [
                train_type
                for train_type in self.timetable.train_types
                if self.display_config.train_type_visible.get(
                    train_type.index,
                    True,
                )
            ]
            legend_rows = max(len(visible_train_types), 1)
        else:
            legend_rows = 1

        max_hours = max(
            len(down_hours),
            len(up_hours),
            1,
        )

        direction_height = (
            self._HEADER_HEIGHT
            + self._CELL_HEIGHT * 2 * max_hours
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

        # 下り
        self._draw_direction(
            x=x0,
            y=direction_y,
            width=down_width,
            title="下り",
            hours=down_hours,
        )

        # 上り
        self._draw_direction(
            x=x0 + down_width + self._DIRECTION_GAP,
            y=direction_y,
            width=up_width,
            title="上り",
            hours=up_hours,
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
            width=total_width,
        )

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )


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
            outline="black",
            tags=(PreviewItem.TITLE,),
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
        hours: list[TimetableHour],
    ) -> None:
        """下り・上りの時刻表を描画する。"""
        # ヘッダ
        self.canvas.create_rectangle(
            x,
            y,
            x + width,
            y + self._HEADER_HEIGHT,
            fill=self._to_tk_color(
                self.display_config.header_fill
            ) or "#D9EAD3",
            outline="black",
            tags=(PreviewItem.HEADER,),
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

        for hour_index, hour in enumerate(hours):

            hour_y = (
                header_y
                + hour_index * self._CELL_HEIGHT * 2
            )

            trains = self._create_preview_trains(hour)

            # 時刻列
            self.canvas.create_rectangle(
                x,
                hour_y,
                x + self._HOUR_WIDTH,
                hour_y + self._CELL_HEIGHT * 2,
                fill=self._to_tk_color(
                    self.display_config.hour_fill
                ) or "#F2F2F2",
                outline="black",
                tags=(PreviewItem.HOUR,),
            )

            self.canvas.create_text(
                x + self._HOUR_WIDTH / 2,
                hour_y + self._CELL_HEIGHT,
                text=str(hour.hour),
                font=(
                    self.display_config.hour_font_name,
                    self.display_config.hour_font_size,
                    "bold",
                ),
                fill=self._to_tk_color(
                    self.display_config.hour_font_color
                ),
            )

            # 列車列
            for index, (
                destination,
                train_type_index,
                train_type,
                minute,
            ) in enumerate(trains):

                train_x = (
                    x
                    + self._HOUR_WIDTH
                    + index * self._CELL_WIDTH
                )

                # 列車情報
                self.canvas.create_rectangle(
                    train_x,
                    hour_y,
                    train_x + self._CELL_WIDTH,
                    hour_y + self._CELL_HEIGHT,
                    fill=self._to_tk_color(
                        self.display_config.train_fill
                    ) or "#FAFAFA",
                    outline="black",
                    tags=(PreviewItem.TRAIN,),
                )

                train_type_color = (
                    self.display_config.get_train_type_color(
                        train_type_index
                    )
                    or self.display_config.train_font_color
                )

                self.canvas.create_text(
                    train_x + self._CELL_WIDTH / 2,
                    hour_y + self._CELL_HEIGHT / 2,
                    text=f"{destination} {train_type}",
                    font=(
                        self.display_config.metadata_font_name,
                        self.display_config.metadata_font_size,
                    ),
                    fill=self._to_tk_color(train_type_color),
                )

                # 分
                self.canvas.create_rectangle(
                    train_x,
                    hour_y + self._CELL_HEIGHT,
                    train_x + self._CELL_WIDTH,
                    hour_y + self._CELL_HEIGHT * 2,
                    fill="white",
                    outline="black",
                )

                self.canvas.create_text(
                    train_x + self._CELL_WIDTH / 2,
                    hour_y + self._CELL_HEIGHT * 1.5,
                    text=minute,
                    font=(
                        self.display_config.minute_font_name,
                        self.display_config.minute_font_size,
                    ),
                    fill=self._to_tk_color(
                        self.display_config.train_font_color
                    ),
                )


    def _draw_legend(
        self,
        x: float,
        y: float,
        width: float,
    ) -> None:
        """凡例を描画する。"""
        label_width = 60
        row_height = self.display_config.legend_row_height

        visible_train_types = []

        if self.timetable is not None:
            visible_train_types = [
                train_type
                for train_type in self.timetable.train_types
                if self.display_config.train_type_visible.get(
                    train_type.index,
                    True,
                )
            ]

        legend_height = max(
            row_height * len(visible_train_types),
            row_height,
        )

        # 背景
        self.canvas.create_rectangle(
            x,
            y,
            x + width,
            y + legend_height,
            fill=self._to_tk_color(
                self.display_config.legend_fill
            ),
            outline="black",
            tags=(PreviewItem.LEGEND,),
        )

        # ラベル部分
        self.canvas.create_rectangle(
            x,
            y,
            x + label_width,
            y + legend_height,
            fill=self._to_tk_color(
                self.display_config.legend_label_fill
            ),
            outline="black",
        )

        self.canvas.create_text(
            x + label_width / 2,
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

        # 列車種別
        if self.timetable is not None:
            display_index = 0

            for train_type in self.timetable.train_types:
                if not self.display_config.train_type_visible.get(
                    train_type.index,
                    True,
                ):
                    continue

                color = (
                    self.display_config.get_train_type_color(
                        train_type.index,
                    )
                    or self.display_config.train_font_color
                )

                self.canvas.create_text(
                    x + label_width + 60,
                    y + row_height / 2 + display_index * row_height,
                    text=train_type.name,
                    fill=self._to_tk_color(color),
                    font=(
                        self.display_config.legend_font_name,
                        self.display_config.legend_font_size,
                    ),
                )

                display_index += 1


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

                DisplayConfigDialog(
                    self,
                    item,
                    self.display_config,
                    train_types=(
                        self.timetable.train_types
                        if self.timetable is not None
                        else None
                    ),
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
        """1時間分の列車情報をPreview表示用データへ変換する."""

        return [
            (
                entry.destination,
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
