
import json
from pathlib import Path

import pytest

from src.application import station_alias_settings as settings_module
from src.application.station_alias_settings import (
    load_display_config,
    load_station_aliases,
    save_station_aliases,
    save_station_settings,
    load_station_no_mark,
)
from src.timetable.display_config import (
    BorderConfig,
    BorderSideConfig,
    TimetableDisplayConfig,
)


@pytest.fixture
def settings_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Path:
    """設定ファイルの保存先をテスト用ディレクトリに変更する。"""
    path = tmp_path / "OuDiaExcel" / "station_aliases.json"
    monkeypatch.setattr(
        settings_module,
        "_get_settings_path",
        lambda: path,
    )
    return path


@pytest.fixture
def oud2_path(tmp_path: Path) -> Path:
    """テスト用のOuDiaSecondファイルパスを返す。"""
    path = tmp_path / "test.oud2"
    path.touch()
    return path


def test_load_station_aliases_returns_empty_when_no_settings(
    settings_path: Path,
    oud2_path: Path,
) -> None:
    assert load_station_aliases(oud2_path) == {}


def test_display_config_direction_header_defaults() -> None:
    config = TimetableDisplayConfig()

    assert config.up_header_text == "上り"
    assert config.down_header_text == "下り"


def test_save_and_load_station_aliases(
    settings_path: Path,
    oud2_path: Path,
) -> None:
    aliases = {
        "仙台": "無印",
        "長町": "長",
        "南仙台": "南仙",
        "名取": "",
    }

    save_station_aliases(oud2_path, aliases)

    assert load_station_aliases(oud2_path) == aliases


def test_save_and_load_display_config(
    settings_path: Path,
    oud2_path: Path,
) -> None:
    config = TimetableDisplayConfig(
        train_type_colors={0: "008000", 1: "0000FF"},
        train_type_fills={0: "FFFF00", 1: "00FFFF"},
        header_fill="D9EAD3",
        up_header_fill="CFE2F3",
        down_header_fill="FCE5CD",
        train_type_visible={0: True, 1: False},
        destination_position="bottom",
        train_type_position="top",
        metadata_order="train_type_first",
        hour_column_mode="center",
        striped_train_fill=False,
        destination_font_name="ＭＳ ゴシック",
        destination_font_size=9,
        destination_font_color="112233",
        destination_font_mode="train_type",
        train_type_font_name="Arial",
        train_type_font_size=11,
        train_type_font_color="445566",
        train_type_font_mode="destination",
        minute_font_mode="train_type",
        show_destination=False,
        show_destination_legend=False,
        use_train_type_short_name=True,
    )
    config.title_border.top = BorderSideConfig(
        enabled=True,
        color="FF0000",
        style="medium",
    )
    config.train_separator = BorderSideConfig(
        enabled=True,
        color="0000FF",
        style="dashed",
    )

    save_station_settings(oud2_path, {"仙台": "無印"}, config)

    loaded = load_display_config(oud2_path)

    assert loaded.show_destination is False
    assert loaded.show_destination_legend is False
    assert loaded.use_train_type_short_name is True
    assert loaded.train_type_colors == {0: "008000", 1: "0000FF"}
    assert loaded.train_type_fills == {0: "FFFF00", 1: "00FFFF"}
    assert loaded.header_fill == "D9EAD3"
    assert loaded.up_header_fill == "CFE2F3"
    assert loaded.down_header_fill == "FCE5CD"
    assert loaded.train_type_visible == {0: True, 1: False}
    assert loaded.destination_position == "bottom"
    assert loaded.train_type_position == "top"
    assert loaded.metadata_order == "train_type_first"
    assert loaded.hour_column_mode == "center"
    assert loaded.striped_train_fill is False
    assert loaded.destination_font_name == "ＭＳ ゴシック"
    assert loaded.destination_font_size == 9
    assert loaded.destination_font_color == "112233"
    assert loaded.destination_font_mode == "train_type"
    assert loaded.train_type_font_name == "Arial"
    assert loaded.train_type_font_size == 11
    assert loaded.train_type_font_color == "445566"
    assert loaded.train_type_font_mode == "destination"
    assert loaded.minute_font_mode == "train_type"
    assert loaded.up_header_text == "上り"
    assert loaded.down_header_text == "下り"

    assert isinstance(loaded.title_border, BorderConfig)
    assert isinstance(loaded.title_border.top, BorderSideConfig)
    assert loaded.title_border.top.enabled is True
    assert loaded.title_border.top.color == "FF0000"
    assert loaded.title_border.top.style == "medium"

    assert isinstance(loaded.train_separator, BorderSideConfig)
    assert loaded.train_separator.enabled is True
    assert loaded.train_separator.color == "0000FF"
    assert loaded.train_separator.style == "dashed"


def test_display_config_header_text_round_trip(
    settings_path: Path,
    oud2_path: Path,
) -> None:
    config = TimetableDisplayConfig(
        up_header_text="仙台方面",
        down_header_text="東京方面",
    )

    save_station_settings(oud2_path, {}, config)

    loaded = load_display_config(oud2_path)

    assert loaded.up_header_text == "仙台方面"
    assert loaded.down_header_text == "東京方面"


def test_old_display_config_uses_direction_header_defaults(
    settings_path: Path,
    oud2_path: Path,
) -> None:
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(
            {
                "railways": {
                    str(oud2_path.resolve()): {
                        "station_aliases": {},
                        "display_config": {
                            "header_font_size": 14,
                        },
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    loaded = load_display_config(oud2_path)

    assert loaded.header_font_size == 14
    assert loaded.up_header_text == "上り"
    assert loaded.down_header_text == "下り"


def test_old_display_config_keeps_common_header_fill(
    settings_path: Path,
    oud2_path: Path,
) -> None:
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(
            {
                "railways": {
                    str(oud2_path.resolve()): {
                        "station_aliases": {},
                        "display_config": {
                            "header_fill": "D9EAD3",
                        },
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    loaded = load_display_config(oud2_path)

    assert loaded.header_fill == "D9EAD3"
    assert loaded.up_header_fill is None
    assert loaded.down_header_fill is None


def test_save_station_aliases_preserves_display_config(
    settings_path: Path,
    oud2_path: Path,
) -> None:
    config = TimetableDisplayConfig(show_destination=False)
    save_station_settings(oud2_path, {"仙台": "無印"}, config)

    save_station_aliases(oud2_path, {"仙台": "仙"})

    assert load_station_aliases(oud2_path) == {"仙台": "仙"}
    assert load_display_config(oud2_path).show_destination is False


def test_load_legacy_alias_settings(
    settings_path: Path,
    oud2_path: Path,
) -> None:
    """従来形式の設定ファイルから駅略称を読み込める。"""
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    settings_path.write_text(
        json.dumps(
            {
                "railways": {
                    str(oud2_path.resolve()): {
                        "仙台": "無印",
                        "長町": "長",
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert load_station_aliases(oud2_path) == {
        "仙台": "無印",
        "長町": "長",
    }

    # 表示設定がない旧形式では、デフォルト設定を返す。
    loaded = load_display_config(oud2_path)
    assert loaded.show_destination is True
    assert loaded.show_destination_legend is True


def test_settings_are_separated_by_oud2_path(
    settings_path: Path,
    tmp_path: Path,
) -> None:
    first_path = tmp_path / "first.oud2"
    second_path = tmp_path / "second.oud2"
    first_path.touch()
    second_path.touch()

    save_station_aliases(first_path, {"仙台": "無印"})
    save_station_aliases(second_path, {"仙台": "仙"})

    assert load_station_aliases(first_path) == {"仙台": "無印"}
    assert load_station_aliases(second_path) == {"仙台": "仙"}



def test_save_and_load_station_no_mark(
    settings_path: Path,
    oud2_path: Path,
) -> None:
    """駅ごとの無印設定を保存・復元できる。"""
    config = TimetableDisplayConfig()

    save_station_settings(
        oud2_path,
        {"仙台": "", "長町": "長"},
        config,
        station_no_mark={"仙台": True, "長町": False},
    )

    assert load_station_no_mark(oud2_path) == {
        "仙台": True,
        "長町": False,
    }


def test_load_station_no_mark_returns_empty_when_unset(
    settings_path: Path,
    oud2_path: Path,
) -> None:
    """無印設定がない既存ファイルでは空の辞書を返す。"""
    save_station_aliases(oud2_path, {"仙台": "仙"})

    assert load_station_no_mark(oud2_path) == {}
