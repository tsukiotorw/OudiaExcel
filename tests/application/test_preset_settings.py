import json
import os
import stat
from dataclasses import asdict
from pathlib import Path

import pytest

from src.application.preset_settings import (
    Preset,
    load_official_presets,
    load_presets,
    save_presets,
)
from src.application import preset_settings
from src.timetable.display_config import (
    BorderConfig,
    BorderSideConfig,
    TimetableDisplayConfig,
)


@pytest.fixture
def oud2_path(tmp_path: Path) -> Path:
    path = tmp_path / "路線データ.oud2"
    path.touch()
    return path


def _write_single_preset(oud2_path: Path, config: dict) -> Path:
    path = oud2_path.with_name(f"{oud2_path.name}.presets.json")
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "presets": [
                    {
                        "id": "test-preset",
                        "name": "テスト",
                        "base_preset_id": None,
                        "config": config,
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def _official_preset(preset_id: str, name: str) -> dict:
    return {
        "id": preset_id,
        "name": name,
        "base_preset_id": None,
        "config": {},
    }


def _write_official_file(
    directory: Path,
    filename: str,
    document: dict,
) -> Path:
    path = directory / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def test_save_and_load_preset(oud2_path: Path) -> None:
    config = TimetableDisplayConfig(
        show_destination=False,
        train_type_colors={0: "008000", 2: "0000FF"},
        train_type_fills={0: "FFFF00"},
        train_type_visible={0: True, 2: False},
        train_type_column_visible={2: True},
    )
    config.title_border = BorderConfig(
        top=BorderSideConfig(True, "FF0000", "medium"),
        bottom=BorderSideConfig(False, "000000", "thin"),
        left=BorderSideConfig(True, "00FF00", "dashed"),
        right=BorderSideConfig(True, "0000FF", "double"),
    )
    config.train_separator = BorderSideConfig(True, "AABBCC", "dotted")
    preset = Preset("user-1", "見やすい表示", "official-1", config)

    save_presets(oud2_path, [preset])
    loaded = load_presets(oud2_path)

    assert loaded == [preset]
    assert loaded[0].config == config
    assert isinstance(loaded[0].config.title_border, BorderConfig)
    assert isinstance(
        loaded[0].config.title_border.top,
        BorderSideConfig,
    )
    assert loaded[0].config.train_separator == config.train_separator
    assert loaded[0].config.train_type_colors == {0: "008000", 2: "0000FF"}
    assert loaded[0].config.train_type_column_visible == {2: True}


def test_load_official_presets_from_one_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(preset_settings, "_OFFICIAL_PRESETS_DIR", tmp_path)
    _write_official_file(
        tmp_path,
        "keio.json",
        {
            "version": 1,
            "presets": [_official_preset("keio-standard", "京王標準")],
        },
    )

    loaded = load_official_presets()

    assert isinstance(loaded, list)
    assert loaded == [
        Preset("keio-standard", "京王標準", None, TimetableDisplayConfig())
    ]
    assert all(isinstance(preset, Preset) for preset in loaded)


def test_load_official_presets_from_multiple_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(preset_settings, "_OFFICIAL_PRESETS_DIR", tmp_path)
    _write_official_file(
        tmp_path,
        "keio.json",
        {
            "version": 1,
            "presets": [_official_preset("keio-standard", "京王標準")],
        },
    )
    _write_official_file(
        tmp_path,
        "jr_east.json",
        {
            "version": 1,
            "presets": [_official_preset("jr-east-standard", "JR東日本標準")],
        },
    )

    loaded = load_official_presets()

    assert [preset.id for preset in loaded] == [
        "jr-east-standard",
        "keio-standard",
    ]


def test_load_official_presets_uses_filename_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(preset_settings, "_OFFICIAL_PRESETS_DIR", tmp_path)
    _write_official_file(
        tmp_path,
        "z-last.json",
        {
            "version": 1,
            "presets": [_official_preset("last", "最後")],
        },
    )
    _write_official_file(
        tmp_path,
        "a-first.json",
        {
            "version": 1,
            "presets": [_official_preset("first", "最初")],
        },
    )

    assert [preset.id for preset in load_official_presets()] == [
        "first",
        "last",
    ]


def test_load_official_presets_rejects_invalid_json_format(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(preset_settings, "_OFFICIAL_PRESETS_DIR", tmp_path)
    _write_official_file(
        tmp_path,
        "invalid.json",
        {"version": 1, "presets": "invalid"},
    )

    with pytest.raises(ValueError):
        load_official_presets()


def test_load_official_presets_rejects_unsupported_version(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(preset_settings, "_OFFICIAL_PRESETS_DIR", tmp_path)
    _write_official_file(
        tmp_path,
        "future.json",
        {"version": 999, "presets": []},
    )

    with pytest.raises(ValueError, match="未対応"):
        load_official_presets()


def test_load_official_presets_rejects_duplicate_ids_across_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(preset_settings, "_OFFICIAL_PRESETS_DIR", tmp_path)
    for filename, name in (("a.json", "一つ目"), ("b.json", "二つ目")):
        _write_official_file(
            tmp_path,
            filename,
            {
                "version": 1,
                "presets": [_official_preset("duplicate", name)],
            },
        )

    with pytest.raises(ValueError, match="IDが重複"):
        load_official_presets()


def test_load_official_presets_rejects_duplicate_names_across_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(preset_settings, "_OFFICIAL_PRESETS_DIR", tmp_path)
    for filename, preset_id in (("a.json", "first"), ("b.json", "second")):
        _write_official_file(
            tmp_path,
            filename,
            {
                "version": 1,
                "presets": [_official_preset(preset_id, "同じ名前")],
            },
        )

    with pytest.raises(ValueError, match="名が重複"):
        load_official_presets()


def test_load_official_presets_error_includes_invalid_file_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(preset_settings, "_OFFICIAL_PRESETS_DIR", tmp_path)
    invalid_path = _write_official_file(
        tmp_path,
        "invalid.json",
        {"version": 1, "presets": "invalid"},
    )

    with pytest.raises(ValueError) as exc_info:
        load_official_presets()

    assert str(invalid_path) in str(exc_info.value)


def test_save_and_load_multiple_presets(oud2_path: Path) -> None:
    presets = [
        Preset("first", "標準", None, TimetableDisplayConfig()),
        Preset(
            "second",
            "行先非表示",
            "first",
            TimetableDisplayConfig(show_destination=False),
        ),
    ]

    save_presets(oud2_path, presets)

    assert load_presets(oud2_path) == presets


def test_presets_are_separated_by_oud2_path(tmp_path: Path) -> None:
    first_path = tmp_path / "first.oud2"
    second_path = tmp_path / "second.oud2"
    first_path.touch()
    second_path.touch()

    save_presets(
        first_path,
        [Preset("one", "一つ目", None, TimetableDisplayConfig())],
    )
    save_presets(
        second_path,
        [Preset("two", "二つ目", None, TimetableDisplayConfig())],
    )

    assert load_presets(first_path)[0].id == "one"
    assert load_presets(second_path)[0].id == "two"
    assert (tmp_path / "first.oud2.presets.json").exists()
    assert (tmp_path / "second.oud2.presets.json").exists()


def test_load_returns_empty_when_file_does_not_exist(
    oud2_path: Path,
) -> None:
    assert load_presets(oud2_path) == []


def test_invalid_json_is_rejected_and_not_overwritten(
    oud2_path: Path,
) -> None:
    path = oud2_path.with_name(f"{oud2_path.name}.presets.json")
    path.write_text("{invalid", encoding="utf-8")

    with pytest.raises(ValueError, match="読み込めません"):
        load_presets(oud2_path)
    with pytest.raises(ValueError, match="読み込めません"):
        save_presets(oud2_path, [])

    assert path.read_text(encoding="utf-8") == "{invalid"


def test_unsupported_version_is_rejected(oud2_path: Path) -> None:
    path = oud2_path.with_name(f"{oud2_path.name}.presets.json")
    path.write_text(
        json.dumps({"version": 999, "presets": []}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="未対応"):
        load_presets(oud2_path)
    with pytest.raises(ValueError, match="未対応"):
        save_presets(oud2_path, [])


@pytest.mark.parametrize(
    "entries",
    [
        [
            {
                "id": "duplicate",
                "name": "一つ目",
                "base_preset_id": None,
                "config": asdict(TimetableDisplayConfig()),
            },
            {
                "id": "duplicate",
                "name": "二つ目",
                "base_preset_id": None,
                "config": asdict(TimetableDisplayConfig()),
            },
        ],
        [
            {
                "id": "incomplete",
                "name": "不完全",
                "base_preset_id": None,
                "config": [],
            }
        ],
    ],
)
def test_invalid_preset_data_is_rejected(
    oud2_path: Path,
    entries: list[dict],
) -> None:
    path = oud2_path.with_name(f"{oud2_path.name}.presets.json")
    path.write_text(
        json.dumps({"version": 1, "presets": entries}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_presets(oud2_path)


def test_missing_display_config_field_uses_default(
    oud2_path: Path,
) -> None:
    config = asdict(TimetableDisplayConfig(show_destination=False))
    del config["title_font_size"]
    _write_single_preset(oud2_path, config)

    loaded = load_presets(oud2_path)[0].config

    assert loaded.title_font_size == TimetableDisplayConfig().title_font_size
    assert loaded.show_destination is False


def test_unknown_display_config_field_is_ignored(
    oud2_path: Path,
) -> None:
    config = asdict(TimetableDisplayConfig(show_destination=False))
    config["future_display_option"] = "unused"
    _write_single_preset(oud2_path, config)

    loaded = load_presets(oud2_path)[0].config

    assert loaded.show_destination is False


def test_missing_nested_border_fields_use_defaults(
    oud2_path: Path,
) -> None:
    config = asdict(TimetableDisplayConfig())
    config["title_border"] = {"top": {"enabled": True}}
    _write_single_preset(oud2_path, config)

    loaded = load_presets(oud2_path)[0].config

    assert loaded.title_border.top.enabled is True
    assert loaded.title_border.top.color == "000000"
    assert loaded.title_border.top.style == "thin"
    assert loaded.title_border.bottom == BorderSideConfig()


def test_unknown_nested_border_fields_are_ignored(
    oud2_path: Path,
) -> None:
    config = asdict(TimetableDisplayConfig())
    config["title_border"]["top"]["future_side_option"] = "unused"
    config["title_border"]["future_border_side"] = {}
    _write_single_preset(oud2_path, config)

    loaded = load_presets(oud2_path)[0].config

    assert loaded.title_border == TimetableDisplayConfig().title_border


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title_font_size", "14"),
        ("title_border", {"top": {"enabled": "true"}}),
    ],
)
def test_known_display_config_type_mismatch_is_rejected(
    oud2_path: Path,
    field: str,
    value: object,
) -> None:
    config = asdict(TimetableDisplayConfig())
    config[field] = value
    _write_single_preset(oud2_path, config)

    with pytest.raises(ValueError):
        load_presets(oud2_path)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (24, 24.0),
        (24.2, 24.2),
    ],
)
def test_float_config_accepts_integer_and_float(
    oud2_path: Path,
    value: int | float,
    expected: float,
) -> None:
    config = asdict(TimetableDisplayConfig())
    config["legend_row_height"] = value
    _write_single_preset(oud2_path, config)

    loaded = load_presets(oud2_path)[0].config

    assert loaded.legend_row_height == expected
    assert type(loaded.legend_row_height) is float


@pytest.mark.parametrize(
    "value",
    [
        True,
        "24",
    ],
)
def test_float_config_rejects_invalid_value(
    oud2_path: Path,
    value: object,
) -> None:
    config = asdict(TimetableDisplayConfig())
    config["legend_row_height"] = value
    _write_single_preset(oud2_path, config)

    with pytest.raises(ValueError):
        load_presets(oud2_path)


def test_int_config_rejects_float_value(oud2_path: Path) -> None:
    config = asdict(TimetableDisplayConfig())
    config["title_font_size"] = 14.5
    _write_single_preset(oud2_path, config)

    with pytest.raises(ValueError):
        load_presets(oud2_path)


def test_empty_display_config_loads_defaults(oud2_path: Path) -> None:
    _write_single_preset(oud2_path, {})

    assert load_presets(oud2_path)[0].config == TimetableDisplayConfig()


def test_save_accepts_existing_preset_with_missing_and_unknown_fields(
    oud2_path: Path,
) -> None:
    existing_config = asdict(TimetableDisplayConfig(show_destination=False))
    del existing_config["title_font_size"]
    existing_config["future_display_option"] = True
    _write_single_preset(oud2_path, existing_config)

    presets = load_presets(oud2_path)
    presets.append(
        Preset("new-preset", "新規", None, TimetableDisplayConfig())
    )

    save_presets(oud2_path, presets)
    loaded = load_presets(oud2_path)

    assert [preset.id for preset in loaded] == [
        "test-preset",
        "new-preset",
    ]
    assert loaded[0].config.title_font_size == 14
    assert loaded[0].config.show_destination is False


def test_invalid_data_is_rejected_before_save(oud2_path: Path) -> None:
    path = oud2_path.with_name(f"{oud2_path.name}.presets.json")
    original = {
        "version": 1,
        "presets": [
            {
                "id": "existing",
                "name": "既存",
                "base_preset_id": None,
                "config": asdict(TimetableDisplayConfig()),
            }
        ],
    }
    original_text = json.dumps(original, ensure_ascii=False)
    path.write_text(original_text, encoding="utf-8")

    duplicate_presets = [
        Preset("duplicate", "一つ目", None, TimetableDisplayConfig()),
        Preset("duplicate", "二つ目", None, TimetableDisplayConfig()),
    ]
    with pytest.raises(ValueError, match="重複"):
        save_presets(oud2_path, duplicate_presets)

    assert path.read_text(encoding="utf-8") == original_text


def test_presets_do_not_change_station_settings(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.application import station_alias_settings

    station_settings_path = tmp_path / "settings" / "station_aliases.json"
    monkeypatch.setattr(
        station_alias_settings,
        "_get_settings_path",
        lambda: station_settings_path,
    )
    oud2_path = tmp_path / "railway.oud2"
    oud2_path.touch()

    station_alias_settings.save_station_settings(
        oud2_path,
        {"仙台": "仙"},
        TimetableDisplayConfig(show_destination=False),
    )
    save_presets(
        oud2_path,
        [Preset("preset-1", "設定", None, TimetableDisplayConfig())],
    )

    assert station_alias_settings.load_station_aliases(oud2_path) == {
        "仙台": "仙"
    }
    assert (
        station_alias_settings.load_display_config(oud2_path).show_destination
        is False
    )

def test_save_fails_when_parent_directory_creation_fails(
    oud2_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_mkdir(*args: object, **kwargs: object) -> None:
        raise OSError("directory creation failed")

    monkeypatch.setattr(Path, "mkdir", fail_mkdir)

    with pytest.raises(ValueError, match="保存できません"):
        save_presets(
            oud2_path,
            [Preset("test", "テスト", None, TimetableDisplayConfig())],
        )

def test_save_fails_when_replace_fails_and_preserves_original(
    oud2_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = oud2_path.with_name(f"{oud2_path.name}.presets.json")
    original_text = json.dumps(
        {
            "version": 1,
            "presets": [],
        }
    )
    path.write_text(original_text, encoding="utf-8")

    def fail_replace(self: Path, target: Path) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(Path, "replace", fail_replace)

    with pytest.raises(ValueError, match="保存できません"):
        save_presets(
            oud2_path,
            [Preset("test", "テスト", None, TimetableDisplayConfig())],
        )

    assert path.read_text(encoding="utf-8") == original_text
    assert list(path.parent.glob(f".{path.name}.*.tmp")) == []


def test_save_fails_when_json_write_fails(
    oud2_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = oud2_path.with_name(f"{oud2_path.name}.presets.json")
    original_text = json.dumps(
        {"version": 1, "presets": []}
    )
    path.write_text(original_text, encoding="utf-8")

    def fail_dump(*args: object, **kwargs: object) -> None:
        raise OSError("write failed")

    monkeypatch.setattr(json, "dump", fail_dump)

    with pytest.raises(ValueError, match="保存できません"):
        save_presets(
            oud2_path,
            [Preset("test", "テスト", None, TimetableDisplayConfig())],
        )

    assert path.read_text(encoding="utf-8") == original_text
    assert list(path.parent.glob(f".{path.name}.*.tmp")) == []


def test_load_presets_error_includes_file_path(tmp_path):
    oud2_path = tmp_path / "test.oud2"
    presets_path = oud2_path.with_name(
        f"{oud2_path.name}.presets.json"
    )

    presets_path.write_text(
        '{"version": 1, "presets": "invalid"}',
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as exc_info:
        load_presets(oud2_path)

    assert str(presets_path) in str(exc_info.value)


def test_load_presets_does_not_duplicate_file_path_in_error(
    tmp_path,
    monkeypatch,
):
    oud2_path = tmp_path / "test.oud2"
    presets_path = oud2_path.with_name(
        f"{oud2_path.name}.presets.json"
    )

    presets_path.write_text("{}", encoding="utf-8")

    original_open = Path.open

    def fail_open(self, *args, **kwargs):
        if self == presets_path:
            raise OSError("テスト用の読み込みエラー")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_open)

    with pytest.raises(ValueError) as exc_info:
        load_presets(oud2_path)

    message = str(exc_info.value)

    assert str(presets_path) in message
    assert message.count(str(presets_path)) == 1


@pytest.mark.skipif(os.name != "posix", reason="POSIX環境限定")
def test_new_preset_file_uses_normal_creation_permissions(
    oud2_path: Path,
) -> None:
    # umaskを一時的に027に設定する。
    original_umask = os.umask(0o027)

    try:
        save_presets(
            oud2_path,
            [Preset("test", "テスト", None, TimetableDisplayConfig())],
        )
    finally:
        os.umask(original_umask)

    path = oud2_path.with_name(f"{oud2_path.name}.presets.json")

    assert stat.S_IMODE(path.stat().st_mode) == 0o640


@pytest.mark.skipif(os.name != "posix", reason="POSIX環境限定")
def test_save_preserves_existing_preset_file_permissions(
    oud2_path: Path,
) -> None:
    path = oud2_path.with_name(f"{oud2_path.name}.presets.json")

    save_presets(
        oud2_path,
        [Preset("first", "最初", None, TimetableDisplayConfig())],
    )

    # 既存ファイルの権限を640に設定する。
    path.chmod(0o640)

    save_presets(
        oud2_path,
        [
            Preset(
                "second",
                "更新後",
                None,
                TimetableDisplayConfig(),
            )
        ],
    )

    assert stat.S_IMODE(path.stat().st_mode) == 0o640
    assert load_presets(oud2_path)[0].id == "second"
