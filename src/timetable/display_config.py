from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TimetableDisplayConfig:
    """駅時刻表の表示設定。"""

    train_type_colors: dict[int, str] = field(default_factory=dict)
    train_type_fills: dict[int, str] = field(default_factory=dict)

    header_fill: str | None = None
    hour_fill: str | None = None

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

    def get_train_type_fill(
        self,
        train_type_index: int,
    ) -> str | None:
        return self.train_type_fills.get(train_type_index)
