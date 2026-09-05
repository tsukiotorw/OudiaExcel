from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TimetableDisplayConfig:
    """駅時刻表の表示設定。"""

    train_type_colors: dict[int, str] = field(
        default_factory=dict
    )

    train_type_fills: dict[int, str] = field(
        default_factory=dict
    )

    header_fill: str | None = None

    hour_fill: str | None = None

    def get_train_type_color(
        self,
        train_type_index: int,
    ) -> str | None:
        """列車種別に対応する文字色を取得する。"""
        return self.train_type_colors.get(train_type_index)

    def get_train_type_fill(
        self,
        train_type_index: int,
    ) -> str | None:
        """列車種別に対応する塗りつぶし色を取得する。"""
        return self.train_type_fills.get(train_type_index)
