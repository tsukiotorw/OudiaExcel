
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
        train_type_visible={0: True, 1: False},
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
    assert loaded.train_type_visible == {0: True, 1: False}

    assert isinstance(loaded.title_border, BorderConfig)
    assert isinstance(loaded.title_border.top, BorderSideConfig)
    assert loaded.title_border.top.enabled is True
    assert loaded.title_border.top.color == "FF0000"
    assert loaded.title_border.top.style == "medium"

    assert isinstance(loaded.train_separator, BorderSideConfig)
    assert loaded.train_separator.enabled is True
    assert loaded.train_separator.color == "0000FF"
    assert loaded.train_separator.style == "dashed"


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
