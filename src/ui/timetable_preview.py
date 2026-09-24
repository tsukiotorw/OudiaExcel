import tkinter as tk

from src.ui.display_config_dialog import DisplayConfigDialog
from src.ui.preview_item import PreviewItem

from src.timetable.display_config import TimetableDisplayConfig


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

        self.canvas = tk.Canvas(
            self,
            background="white",
            highlightthickness=0,
        )
        self.canvas.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self.bind(
            "<Configure>",
            self._on_configure,
        )

        self.canvas.bind(
            "<Button-1>", 
            self._on_click
        )


    def _on_configure(
        self,
        event: tk.Event,
    ) -> None:
        """ウィジェットサイズ変更時にプレビューを再描画する。"""
        self._draw()


    def _draw(self) -> None:
        """サンプル時刻表を描画する。"""
        self.canvas.delete("all")

        # サンプルの列車
        down_trains = [
            ("仙台", 0, "普通", "05"),
            ("仙台", 1, "快速", "15"),
            ("松島", 0, "普通", "25"),
        ]

        up_trains = [
            ("石巻", 0, "普通", "10"),
            ("石巻", 1, "快速", "20"),
            ("塩釜", 0, "普通", "30"),
        ]

        title = "B駅 時刻表"

        # 2方向の幅
        direction_width = (
            self._HOUR_WIDTH
            + self._CELL_WIDTH * 3
        )

        total_width = (
            direction_width * 2
            + self._DIRECTION_GAP
        )

        total_height = (
            self._TITLE_HEIGHT
            + self._HEADER_HEIGHT
            + self._CELL_HEIGHT * 4
            + 45
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
            width=direction_width,
            title="下り",
            trains=down_trains,
        )

        # 上り
        self._draw_direction(
            x=x0 + direction_width + self._DIRECTION_GAP,
            y=direction_y,
            width=direction_width,
            title="上り",
            trains=up_trains,
        )

        # 凡例
        legend_y = (
            direction_y
            + self._HEADER_HEIGHT
            + self._CELL_HEIGHT * 4
            + 10
        )

        self._draw_legend(
            x=x0,
            y=legend_y,
            width=total_width,
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
        trains: list[tuple[str, str, str]],
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

        # 時刻列
        self.canvas.create_rectangle(
            x,
            header_y,
            x + self._HOUR_WIDTH,
            header_y + self._CELL_HEIGHT * 2,
            fill=self._to_tk_color(
                self.display_config.hour_fill
            ) or "#F2F2F2",
            outline="black",
            tags=(PreviewItem.HOUR,),
        )

        self.canvas.create_text(
            x + self._HOUR_WIDTH / 2,
            header_y + self._CELL_HEIGHT,
            text="4",
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
                header_y,
                train_x + self._CELL_WIDTH,
                header_y + self._CELL_HEIGHT,
                fill=self._to_tk_color(
                    self.display_config.train_fill
                ) or "#FAFAFA",
                outline="black",
                tags=(PreviewItem.TRAIN,),
            )

            train_type_color = (
                self.display_config.get_train_type_color(train_type_index)
                or self.display_config.train_font_color
            )

            self.canvas.create_text(
                train_x + self._CELL_WIDTH / 2,
                header_y + self._CELL_HEIGHT / 2,
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
                header_y + self._CELL_HEIGHT,
                train_x + self._CELL_WIDTH,
                header_y + self._CELL_HEIGHT * 2,
                fill="white",
                outline="black",
            )

            self.canvas.create_text(
                train_x + self._CELL_WIDTH / 2,
                header_y + self._CELL_HEIGHT * 1.5,
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

        self.canvas.create_rectangle(
            x,
            y,
            x + width,
            y + 30,
            fill="black",
            outline="black",
            tags=(PreviewItem.LEGEND,),
        )

        self.canvas.create_text(
            x + label_width / 2,
            y + 15,
            text="凡例",
            fill="white",
            font=("源ノ角ゴシック JP", 9, "bold"),
        )

        self.canvas.create_text(
            x + label_width + 60,
            y + 15,
            text="普通",
            fill="#008000",
            font=("源ノ角ゴシック JP", 9),
        )

        self.canvas.create_text(
            x + label_width + 140,
            y + 15,
            text="快速",
            fill="#0000FF",
            font=("源ノ角ゴシック JP", 9),
        )


    def _on_click(self, event: tk.Event) -> None:
        """プレビュー上の設定対象をクリックしたときの処理。"""
        items = self.canvas.find_overlapping(
            event.x,
            event.y,
            event.x,
            event.y,
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
