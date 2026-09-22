from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TimetableDisplayConfig:
    """駅時刻表の表示設定。"""

    # 列車種別ごとの文字色
    train_type_colors: dict[int, str] = field(default_factory=dict)

    # ヘッダー
    header_fill: str | None = None
    header_font_color: str = "FAFAFA"
    header_font_name: str = "源ノ角ゴシック JP Heavy"
    header_font_size: int = 12

    # 時刻表本体
    timetable_fill: str = "FAFAFA"
    timetable_alt_fill: str = "C8E6C9"
    timetable_border_color: str = "FAFAFA"
    timetable_border_width: str = "thin"

    # 時刻欄
    hour_fill: str | None = None
    hour_font_color: str = "000000"
    hour_font_name: str = "源ノ角ゴシック JP Heavy"
    hour_font_size: int = 10

    # 列車欄
    train_fill: str | None = None
    train_font_color: str = "000000"
    metadata_font_name: str = "源ノ角ゴシック JP"
    metadata_font_size: int = 6
    minute_font_name: str = "源ノ角ゴシック JP"
    minute_font_size: int = 10

    # 凡例
    legend_label_fill: str = "000000"
    legend_fill: str = "FAFAFA"
    legend_label_font_name: str = "源ノ角ゴシック JP Heavy"
    legend_font_name: str = "源ノ角ゴシック JP"
    legend_label_font_size: int = 8
    legend_font_size: int = 8
    legend_label_font_color: str = "FAFAFA"
    legend_row_height: float = 24.2

    def get_train_type_color(
        self,
        train_type_index: int,
    ) -> str | None:
        return self.train_type_colors.get(train_type_index)
