
"""駅略称と時刻表表示設定の保存・読み込み。"""

import json
import os
from dataclasses import asdict, fields
from pathlib import Path
from typing import Any

from src.timetable.display_config import (
    BorderConfig,
    BorderSideConfig,
    TimetableDisplayConfig,
)


def _get_settings_path() -> Path:
    """ユーザー設定ファイルの保存先を返す。"""
    if os.name == "nt":
        base_dir = Path(
            os.environ.get(
                "APPDATA",
                str(Path.home() / "AppData" / "Roaming"),
            )
        )
    else:
        base_dir = Path(
            os.environ.get(
                "XDG_CONFIG_HOME",
                str(Path.home() / ".config"),
            )
        )

    return base_dir / "OuDiaExcel" / "station_aliases.json"


def _load_settings_file() -> dict[str, Any]:
    """設定ファイル全体を読み込む。"""
    settings_path = _get_settings_path()

    if not settings_path.exists():
        return {"railways": {}}

    try:
        with settings_path.open("r", encoding="utf-8") as file:
            settings = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"設定ファイルを読み込めません: {settings_path}"
        ) from exc

    if not isinstance(settings, dict):
        raise ValueError("設定ファイルの形式が正しくありません。")

    railways = settings.get("railways", {})

    if not isinstance(railways, dict):
        raise ValueError("設定ファイルの形式が正しくありません。")

    return settings


def _get_railway_settings(
    settings: dict[str, Any],
    oud2_path: Path,
) -> dict[str, Any]:
    """指定路線の設定を取得し、旧形式にも対応する。"""
    railway_key = str(oud2_path.resolve())
    railway_settings = settings.get("railways", {}).get(
        railway_key,
        {},
    )

    if not isinstance(railway_settings, dict):
        raise ValueError("路線設定の形式が正しくありません。")

    # 旧形式では、駅名と略称が直接格納されていた。
    if "station_aliases" not in railway_settings:
        if all(
            isinstance(name, str) and isinstance(alias, str)
            for name, alias in railway_settings.items()
        ):
            return {
                "station_aliases": railway_settings,
                "display_config": {},
            }

        raise ValueError("路線設定の形式が正しくありません。")

    return railway_settings


def _validate_station_no_mark(value: Any) -> dict[str, bool]:
    """駅ごとの無印設定を検証する。"""
    if not isinstance(value, dict):
        raise ValueError("駅の無印設定は辞書である必要があります。")

    if not all(
        isinstance(name, str) and isinstance(enabled, bool)
        for name, enabled in value.items()
    ):
        raise ValueError("駅の無印設定は駅名と真偽値の組み合わせである必要があります。")

    return value


def _validate_aliases(value: Any) -> dict[str, str]:
    """駅略称のデータ形式を検証する。"""
    if not isinstance(value, dict):
        raise ValueError("駅略称設定の形式が正しくありません。")

    if not all(
        isinstance(name, str) and isinstance(alias, str)
        for name, alias in value.items()
    ):
        raise ValueError("駅略称設定の形式が正しくありません。")

    return value


def load_station_no_mark(oud2_path: Path) -> dict[str, bool]:
    """駅ごとの無印設定を読み込む。"""
    settings = _load_settings_file()
    railway_settings = _get_railway_settings(settings, oud2_path)

    value = railway_settings.get("station_no_mark", {})
    return _validate_station_no_mark(value)


def load_station_aliases(oud2_path: Path) -> dict[str, str]:
    """指定されたOuDiaSecondファイルの駅略称を読み込む。"""
    settings = _load_settings_file()
    railway_settings = _get_railway_settings(settings, oud2_path)

    return _validate_aliases(
        railway_settings.get("station_aliases", {})
    ).copy()


def _border_config_from_dict(value: Any) -> BorderConfig:
    """辞書から罫線設定を復元する。"""
    if not isinstance(value, dict):
        raise ValueError("罫線設定の形式が正しくありません。")

    result = BorderConfig()

    for side in ("top", "bottom", "left", "right"):
        side_value = value.get(side)

        if side_value is None:
            continue

        if not isinstance(side_value, dict):
            raise ValueError("罫線設定の形式が正しくありません。")

        defaults = BorderSideConfig()
        allowed = {item.name for item in fields(BorderSideConfig)}
        values = {
            key: item
            for key, item in side_value.items()
            if key in allowed
        }

        try:
            side_config = BorderSideConfig(**values)
        except TypeError as exc:
            raise ValueError("罫線設定の形式が正しくありません。") from exc

        # JSONにない項目はデフォルト値を使う。
        for field in fields(BorderSideConfig):
            if field.name not in values:
                setattr(
                    side_config,
                    field.name,
                    getattr(defaults, field.name),
                )

        setattr(result, side, side_config)

    return result


def _display_config_from_dict(
    value: Any,
) -> TimetableDisplayConfig:
    """辞書から時刻表表示設定を復元する。"""
    if not isinstance(value, dict):
        raise ValueError("表示設定の形式が正しくありません。")

    config = TimetableDisplayConfig()

    # 設定ファイルに存在する、既知の項目だけを復元する。
    allowed_fields = {
        item.name for item in fields(TimetableDisplayConfig)
    }

    for name, item in value.items():
        if name not in allowed_fields:
            continue

        if name in {
            "title_border",
            "header_border",
            "hour_border",
            "train_border",
            "legend_border",
        }:
            setattr(config, name, _border_config_from_dict(item))
        elif name == "train_separator":
            if not isinstance(item, dict):
                raise ValueError("罫線設定の形式が正しくありません。")

            allowed = {
                field.name for field in fields(BorderSideConfig)
            }
            setattr(
                config,
                name,
                BorderSideConfig(
                    **{
                        key: val
                        for key, val in item.items()
                        if key in allowed
                    }
                ),
            )
        elif name in {
            "train_type_colors",
            "train_type_visible",
            "train_type_column_visible",
        }:
            if not isinstance(item, dict):
                raise ValueError("列車種別設定の形式が正しくありません。")

            try:
                converted = {
                    int(key): val for key, val in item.items()
                }
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "列車種別設定の形式が正しくありません。"
                ) from exc

            setattr(config, name, converted)
        else:
            setattr(config, name, item)

    return config


def load_display_config(oud2_path: Path) -> TimetableDisplayConfig:
    """指定されたOuDiaSecondファイルの表示設定を読み込む。"""
    settings = _load_settings_file()
    railway_settings = _get_railway_settings(settings, oud2_path)

    return _display_config_from_dict(
        railway_settings.get("display_config", {})
    )


def _save_railway_settings(
    oud2_path: Path,
    aliases: dict[str, str],
    display_config: TimetableDisplayConfig | None = None,
    station_no_mark: dict[str, bool] | None = None,
) -> None:
    """指定路線の設定を既存設定と合わせて保存する。"""
    aliases = _validate_aliases(aliases)

    settings = _load_settings_file()
    railway_key = str(oud2_path.resolve())

    railway_settings = _get_railway_settings(settings, oud2_path)

    if station_no_mark is not None:
        station_no_mark = _validate_station_no_mark(station_no_mark)

    # 旧形式から移行する場合も、既存の表示設定を維持する。
    current_config = railway_settings.get("display_config", {})

    current_station_no_mark = (
        station_no_mark
        if station_no_mark is not None
        else railway_settings.get("station_no_mark", {})
    )
    current_station_no_mark = _validate_station_no_mark(
        current_station_no_mark
    )

    if display_config is not None:
        current_config = asdict(display_config)

    settings["railways"][railway_key] = {
        "station_aliases": aliases,
        "display_config": current_config,
        "station_no_mark": current_station_no_mark,
    }

    settings_path = _get_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with settings_path.open("w", encoding="utf-8") as file:
            json.dump(
                settings,
                file,
                ensure_ascii=False,
                indent=2,
            )
            file.write("\n")
    except OSError as exc:
        raise ValueError(
            f"設定ファイルを保存できません: {settings_path}"
        ) from exc


def save_station_aliases(
    oud2_path: Path,
    aliases: dict[str, str],
) -> None:
    """指定されたOuDiaSecondファイルの駅略称を保存する。"""
    _save_railway_settings(oud2_path, aliases)


def save_station_settings(
    oud2_path: Path,
    aliases: dict[str, str],
    display_config: TimetableDisplayConfig,
    station_no_mark: dict[str, bool] | None = None,
) -> None:
    """駅略称・表示設定・無印設定を保存する。"""
    _save_railway_settings(
        oud2_path,
        aliases,
        display_config,
        station_no_mark,
    )
