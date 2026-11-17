"""OuDiaSecondファイルごとの表示設定プリセットを保存・読み込みする。"""

from __future__ import annotations

import json
import os

import secrets
import stat
import types
from dataclasses import asdict, dataclass, fields, is_dataclass
from pathlib import Path
from typing import Any, Union, get_args, get_origin, get_type_hints

from src.application.station_alias_settings import (
    _display_config_from_dict,
)
from src.timetable.display_config import TimetableDisplayConfig


_FILE_VERSION = 1
_TRAIN_TYPE_CONFIG_FIELDS = {
    "train_type_colors",
    "train_type_fills",
    "train_type_visible",
    "train_type_column_visible",
}


@dataclass
class Preset:
    """利用者作成の時刻表表示設定プリセット。"""

    id: str
    name: str
    base_preset_id: str | None
    config: TimetableDisplayConfig


def _get_presets_path(oud2_path: Path) -> Path:
    """対象ファイルの隣にあるプリセットファイルのパスを返す。"""
    return oud2_path.with_name(f"{oud2_path.name}.presets.json")


def _invalid_data(path: str) -> ValueError:
    return ValueError(f"プリセットデータの形式が正しくありません: {path}")


def _validate_typed_value(value: Any, expected_type: Any, path: str) -> None:
    """型注釈に従ってJSON値を再帰的に検証する。"""
    origin = get_origin(expected_type)

    if origin in (Union, types.UnionType):
        if not any(
            _matches_type(value, option, path)
            for option in get_args(expected_type)
        ):
            raise _invalid_data(path)
        return

    if origin is dict:
        if type(value) is not dict:
            raise _invalid_data(path)
        key_type, item_type = get_args(expected_type)
        for key, item in value.items():
            _validate_typed_value(key, key_type, f"{path} のキー")
            _validate_typed_value(item, item_type, path)
        return

    if isinstance(expected_type, type) and is_dataclass(expected_type):
        if type(value) is not dict:
            raise _invalid_data(path)

        dataclass_fields = fields(expected_type)
        hints = get_type_hints(expected_type)
        for item in dataclass_fields:
            if item.name in value:
                _validate_typed_value(
                    value[item.name],
                    hints[item.name],
                    f"{path}.{item.name}",
                )
        return

    if expected_type is Any:
        return

    if expected_type is float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise _invalid_data(path)
        return

    if expected_type is int:
        if type(value) is not int:
            raise _invalid_data(path)
        return

    if type(value) is not expected_type:
        raise _invalid_data(path)


def _matches_type(value: Any, expected_type: Any, path: str) -> bool:
    try:
        _validate_typed_value(value, expected_type, path)
    except ValueError:
        return False
    return True


def _validated_display_config(value: Any) -> TimetableDisplayConfig:
    """既知の表示設定を検証し、既存の復元処理でオブジェクト化する。"""
    if type(value) is not dict:
        raise _invalid_data("config")

    normalized = dict(value)

    # float型フィールドに整数が指定されていた場合はfloatに正規化する。
    config_hints = get_type_hints(TimetableDisplayConfig)
    for name, expected_type in config_hints.items():
        if name not in normalized or expected_type is not float:
            continue

        number = normalized[name]
        if isinstance(number, int) and not isinstance(number, bool):
            normalized[name] = float(number)

    for name in _TRAIN_TYPE_CONFIG_FIELDS:
        if name not in value:
            continue

        mapping = value[name]
        if type(mapping) is not dict:
            raise _invalid_data(f"config.{name}")

        converted: dict[int, Any] = {}
        for key, item in mapping.items():
            if not isinstance(key, str):
                raise _invalid_data(f"config.{name} のキー")
            try:
                index = int(key)
            except ValueError as exc:
                raise _invalid_data(f"config.{name} のキー") from exc
            if str(index) != key or index in converted:
                raise _invalid_data(f"config.{name} のキー")
            converted[index] = item
        normalized[name] = converted

    _validate_typed_value(
        normalized,
        TimetableDisplayConfig,
        "config",
    )
    return _display_config_from_dict(normalized)


def _validated_preset(
    value: Any,
    seen_ids: set[str],
    seen_names: set[str],
) -> Preset:
    if type(value) is not dict or set(value) != {
        "id",
        "name",
        "base_preset_id",
        "config",
    }:
        raise _invalid_data("presets の項目")

    preset_id = value["id"]
    name = value["name"]
    base_preset_id = value["base_preset_id"]

    if not isinstance(preset_id, str) or not preset_id.strip():
        raise _invalid_data("preset.id")
    if preset_id in seen_ids:
        raise ValueError(f"プリセットIDが重複しています: {preset_id}")
    if not isinstance(name, str) or not name.strip():
        raise _invalid_data("preset.name")

    normalized_name = name.strip()
    if normalized_name in seen_names:
        raise ValueError(f"プリセット名が重複しています: {name}")

    if base_preset_id is not None and (
        not isinstance(base_preset_id, str) or not base_preset_id.strip()
    ):
        raise _invalid_data("preset.base_preset_id")
    if not isinstance(value["config"], dict):
        raise _invalid_data("preset.config")

    config = _validated_display_config(value["config"])
    seen_ids.add(preset_id)
    seen_names.add(normalized_name)

    return Preset(
        id=preset_id,
        name=name,
        base_preset_id=base_preset_id,
        config=config,
    )


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"JSON定数は使用できません: {value}")


def _read_document(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file, parse_constant=_reject_json_constant)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(
            f"プリセットファイルを読み込めません: {path}"
        ) from exc


def _load_presets_file(path: Path) -> list[Preset]:
    if not path.exists():
        return []

    document = _read_document(path)
    if type(document) is not dict:
        raise _invalid_data("ファイル")

    if "version" not in document:
        raise _invalid_data("version")
    if type(document["version"]) is not int:
        raise _invalid_data("version")
    if document["version"] != _FILE_VERSION:
        raise ValueError(
            f"未対応のプリセットファイルバージョンです: "
            f"{document['version']}"
        )

    if set(document) != {"version", "presets"}:
        raise _invalid_data("ファイル")

    entries = document["presets"]
    if type(entries) is not list:
        raise _invalid_data("presets")

    seen_ids: set[str] = set()
    seen_names: set[str] = set()

    return [
        _validated_preset(entry, seen_ids, seen_names)
        for entry in entries
    ]


def load_presets(oud2_path: Path) -> list[Preset]:
    """指定されたOuDiaSecondファイルの利用者プリセットを読み込む。"""
    path = _get_presets_path(oud2_path)

    try:
        return _load_presets_file(path)
    except ValueError as exc:
        # エラーメッセージにファイルパスが含まれていなければ追加する。
        if str(path) in str(exc):
            raise

        raise ValueError(
            f"{exc} (ファイル: {path})"
        ) from exc


def _serialize_presets(presets: list[Preset]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_names: set[str] = set()

    for preset in presets:
        if not isinstance(preset, Preset):
            raise _invalid_data("presets の項目")
        if not isinstance(preset.config, TimetableDisplayConfig):
            raise _invalid_data("preset.config")

        config_data = asdict(preset.config)
        _validate_typed_value(
            config_data,
            TimetableDisplayConfig,
            "config",
        )

        # JSONでは辞書キーが文字列になるため、事前に変換する。
        for name in _TRAIN_TYPE_CONFIG_FIELDS:
            config_data[name] = {
                str(key): item
                for key, item in config_data[name].items()
            }

        entry = {
            "id": preset.id,
            "name": preset.name,
            "base_preset_id": preset.base_preset_id,
            "config": config_data,
        }

        # 読み込み時と同じ条件で検証する。
        validated = _validated_preset(
            entry,
            seen_ids,
            seen_names,
        )

        result.append(
            {
                "id": validated.id,
                "name": validated.name,
                "base_preset_id": validated.base_preset_id,
                "config": asdict(validated.config),
            }
        )

    return result


def save_presets(oud2_path: Path, presets: list[Preset]) -> None:
    """利用者プリセットを安全に保存する。"""
    if type(presets) is not list:
        raise _invalid_data("presets")

    serialized = _serialize_presets(presets)
    path = _get_presets_path(oud2_path)

    # 不正・未知バージョンの既存ファイルを黙って置き換えない。
    _load_presets_file(path)

    temp_path: Path | None = None
    temp_fd: int | None = None

    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        # 既存ファイルがあれば、そのアクセス権限を引き継ぐ。
        existing_mode = (
            stat.S_IMODE(path.stat().st_mode)
            if path.exists()
            else None
        )

        # 通常のファイル作成と同じく、umaskを考慮した権限で作成する。
        for _ in range(100):
            candidate = path.with_name(
                f".{path.name}.{secrets.token_hex(8)}.tmp"
            )
            try:
                temp_fd = os.open(
                    candidate,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o666,
                )
                temp_path = candidate
                break
            except FileExistsError:
                continue
        else:
            raise FileExistsError("一時ファイルを作成できません")

        with os.fdopen(temp_fd, "w", encoding="utf-8") as file:
            temp_fd = None

            if existing_mode is not None:
                os.chmod(temp_path, existing_mode)

            json.dump(
                {"version": _FILE_VERSION, "presets": serialized},
                file,
                ensure_ascii=False,
                indent=2,
                allow_nan=False,
            )
            file.write("\n")

        temp_path.replace(path)

    except (OSError, TypeError, ValueError) as exc:
        raise ValueError(
            f"プリセットファイルを保存できません: {path}"
        ) from exc

    finally:
        if temp_fd is not None:
            os.close(temp_fd)

        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass
