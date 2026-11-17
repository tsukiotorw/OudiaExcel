from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BorderSideConfig:
    """罫線の片側に対する表示設定。"""

    enabled: bool = False
    color: str = "000000"
    style: str = "thin"


@dataclass
class BorderConfig:
    """罫線の上下左右に対する設定。"""

    top: BorderSideConfig = field(
        default_factory=BorderSideConfig,
    )
    bottom: BorderSideConfig = field(
        default_factory=BorderSideConfig,
    )
    left: BorderSideConfig = field(
        default_factory=BorderSideConfig,
    )
    right: BorderSideConfig = field(
        default_factory=BorderSideConfig,
    )


@dataclass
class TimetableDisplayConfig:
    """駅時刻表の表示設定。"""

    # 列車種別ごとの文字色・背景色・表示有無
    train_type_colors: dict[int, str] = field(default_factory=dict)
    train_type_fills: dict[int, str] = field(default_factory=dict)
    train_type_visible: dict[int, bool] = field(default_factory=dict)

    # 列車欄での列車種別ごとの表示有無
    train_type_column_visible: dict[int, bool] = field(
        default_factory=dict
    )

    destination_position: str = "top"
    train_type_position: str = "top"
    metadata_order: str = "destination_first"
    hour_column_mode: str = "separate"
    striped_train_fill: bool = True

    # 罫線
    title_border: BorderConfig = field(
        default_factory=BorderConfig,
    )
    header_border: BorderConfig = field(
        default_factory=BorderConfig,
    )
    hour_border: BorderConfig = field(
        default_factory=BorderConfig,
    )
    train_border: BorderConfig = field(
        default_factory=BorderConfig,
    )
    train_separator: BorderSideConfig = field(
        default_factory=BorderSideConfig
    )
    legend_border: BorderConfig = field(
        default_factory=BorderConfig,
    )

    # タイトル
    title_fill: str | None = None
    title_font_color: str = "000000"
    title_font_name: str = "源ノ角ゴシック JP"
    title_font_size: int = 14

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

    # 分の文字色（Noneの場合は列車欄の文字色を使用）
    minute_font_color: str | None = None

    # 時刻表の列車種別に略称を使用する
    use_train_type_short_name: bool = False

    # 列車欄に行先を表示するか
    show_destination: bool = True

    # 行先凡例を表示するか
    show_destination_legend: bool = True

    metadata_font_name: str = "源ノ角ゴシック JP"
    metadata_font_size: int = 6
    minute_font_name: str = "源ノ角ゴシック JP"
    minute_font_size: int = 10
    destination_font_name: str | None = None
    destination_font_size: int | None = None
    destination_font_color: str | None = None
    destination_font_mode: str = "independent"
    train_type_font_name: str | None = None
    train_type_font_size: int | None = None
    train_type_font_color: str | None = None
    train_type_font_mode: str = "independent"
    minute_font_mode: str = "independent"

    # 凡例
    legend_label_fill: str = "000000"
    legend_fill: str = "FAFAFA"
    legend_font_color: str = "000000"
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

    def get_entry_font_settings(
        self,
        item: str,
        train_type_index: int,
    ) -> tuple[str, int, str]:
        """列車欄の項目に適用するフォント名・サイズ・色を返す。"""
        legacy_settings = {
            "destination": (
                self.metadata_font_name,
                self.metadata_font_size,
                self.train_font_color,
            ),
            "train_type": (
                self.metadata_font_name,
                self.metadata_font_size,
                self.train_font_color,
            ),
            "minute": (
                self.minute_font_name,
                self.minute_font_size,
                self.minute_font_color or self.train_font_color,
            ),
        }
        if item not in legacy_settings:
            raise ValueError(f"不明な列車欄項目です: {item}")

        allowed_modes = {
            "destination": {"independent", "train_type"},
            "train_type": {"independent", "destination"},
            "minute": {"independent", "destination", "train_type"},
        }

        def resolve(
            current: str,
            path: tuple[str, ...],
        ) -> tuple[str, int, str]:
            mode = getattr(self, f"{current}_font_mode")
            if (
                mode in allowed_modes[current]
                and mode != "independent"
            ):
                if mode in path:
                    return independent_settings(mode)
                return resolve(mode, (*path, current))

            return independent_settings(current)

        def independent_settings(current: str) -> tuple[str, int, str]:
            legacy = legacy_settings[current]
            return (
                getattr(self, f"{current}_font_name", None) or legacy[0],
                getattr(self, f"{current}_font_size", None) or legacy[1],
                getattr(self, f"{current}_font_color", None) or legacy[2],
            )

        values = resolve(item, ())

        train_type_color = self.get_train_type_color(train_type_index)
        if train_type_color is not None:
            values = (
                values[0],
                values[1],
                train_type_color,
            )

        return values

    def get_entry_fill(
        self,
        hour: int,
    ) -> str:
        """列車欄の基本背景色を返す。種別色は呼び出し側で優先する。"""
        if self.train_fill is not None:
            return self.train_fill
        hour_order = (hour - 4) % 24 if 0 <= hour < 24 else hour
        if self.striped_train_fill and hour_order % 2 == 0:
            return self.timetable_alt_fill
        return self.timetable_fill
