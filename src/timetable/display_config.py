from __future__ import annotations

from dataclasses import dataclass, field


STRIPED_TRAIN_FILL_NONE = "none"
STRIPED_TRAIN_FILL_BOTH = "both"
STRIPED_TRAIN_FILL_METADATA = "metadata"
STRIPED_TRAIN_FILL_MINUTE = "minute"


def normalize_striped_train_fill(value: object) -> object:
    """旧bool形式の時間帯別背景色設定を新文字列形式へ正規化する。"""
    if type(value) is bool:
        if value:
            return STRIPED_TRAIN_FILL_BOTH
        return STRIPED_TRAIN_FILL_NONE
    return value


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
    train_type_minute_highlight_enabled: dict[int, bool] = field(
        default_factory=dict
    )
    train_type_minute_highlight_fills: dict[int, str] = field(
        default_factory=dict
    )

    # 列車欄での列車種別ごとの表示有無
    train_type_column_visible: dict[int, bool] = field(
        default_factory=dict
    )

    destination_position: str = "top"
    train_type_position: str = "top"
    metadata_order: str = "destination_first"
    hour_column_mode: str = "separate"
    striped_train_fill: str = STRIPED_TRAIN_FILL_BOTH

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
    up_header_text: str = "上り"
    down_header_text: str = "下り"
    header_fill: str | None = None
    up_header_fill: str | None = None
    down_header_fill: str | None = None
    header_font_color: str = "FAFAFA"
    header_font_name: str = "源ノ角ゴシック JP Heavy"
    header_font_size: int = 12

    # 時刻表本体
    timetable_fill: str = "FAFAFA"
    timetable_alt_fill: str = "C8E6C9"
    up_timetable_fill: str = "FAFAFA"
    up_timetable_alt_fill: str = "C8E6C9"
    down_timetable_fill: str = "FAFAFA"
    down_timetable_alt_fill: str = "C8E6C9"
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
    show_legend: bool = True
    show_train_type_legend: bool = True
    show_up_destination_legend: bool = True
    show_down_destination_legend: bool = True
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

    def get_up_timetable_fill(self, alternate: bool = False) -> str:
        if alternate:
            if self.up_timetable_alt_fill != "C8E6C9":
                return self.up_timetable_alt_fill
            return self.timetable_alt_fill
        if self.up_timetable_fill != "FAFAFA":
            return self.up_timetable_fill
        return self.timetable_fill

    def is_striped_train_fill_for_metadata(self) -> bool:
        """行先・列車種別欄に時間帯別交互背景色を適用するかを返す。"""
        return self.striped_train_fill in (
            STRIPED_TRAIN_FILL_BOTH,
            STRIPED_TRAIN_FILL_METADATA,
        )

    def is_striped_train_fill_for_minute(self) -> bool:
        """分に時間帯別交互背景色を適用するかを返す。"""
        return self.striped_train_fill in (
            STRIPED_TRAIN_FILL_BOTH,
            STRIPED_TRAIN_FILL_MINUTE,
        )

    def get_entry_fill(
        self,
        hour: int,
        direction: str = "up",
    ) -> str:
        """列車欄の基本背景色を返す。種別色は呼び出し側で優先する。"""

        hour_order = (hour - 4) % 24 if 0 <= hour < 24 else hour
        apply_metadata_fill = self.is_striped_train_fill_for_metadata()

        if apply_metadata_fill:
            if direction == "down":
                return (
                    self.down_timetable_alt_fill
                    if hour_order % 2 == 0
                    else self.down_timetable_fill
                )

            return (
                self.get_up_timetable_fill(alternate=True)
                if hour_order % 2 == 0
                else self.get_up_timetable_fill()
            )

        if self.train_fill is not None:
            return self.train_fill

        if direction == "down":
            return self.down_timetable_fill

        return self.get_up_timetable_fill()


    def get_train_type_minute_highlight_fill(
        self,
        train_type_index: int,
    ) -> str | None:
        """分強調が有効な列車種別の背景色を返す。"""
        if not self.train_type_minute_highlight_enabled.get(
            train_type_index,
            False,
        ):
            return None
        return self.train_type_minute_highlight_fills.get(
            train_type_index
        )
