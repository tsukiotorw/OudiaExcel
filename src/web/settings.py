
from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


def _get_settings_path() -> Path:
    """Web版の設定ファイルパスを取得する。"""
    if os.name == "nt":
        base_dir = Path(
            os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
        )
    else:
        base_dir = Path(
            os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
        )

    return base_dir / "OuDiaExcelWeb" / "station_settings.json"


def _load_all_settings() -> dict:
    """設定ファイル全体を読み込む。"""
    path = _get_settings_path()

    if not path.exists():
        return {"sessions": {}}

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return {"sessions": {}}

    if not isinstance(data, dict):
        return {"sessions": {}}

    sessions = data.get("sessions")
    if not isinstance(sessions, dict):
        return {"sessions": {}}

    return data


def _save_all_settings(data: dict) -> None:
    """設定ファイル全体を保存する。"""
    path = _get_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = None

    try:
        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            suffix=".tmp",
            delete=False,
        ) as file:
            temp_path = Path(file.name)
            json.dump(data, file, ensure_ascii=False, indent=2)

        temp_path.replace(path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def load_station_settings(
    session_id: str,
    file_key: str,
) -> dict:
    """セッションとファイルに対応する設定を読み込む。"""
    data = _load_all_settings()

    session_settings = data["sessions"].get(session_id, {})
    settings = session_settings.get(file_key, {})

    if not isinstance(settings, dict):
        return {}

    return settings


def save_station_settings(
    session_id: str,
    file_key: str,
    station_aliases: dict[str, str],
    station_no_mark: dict[str, bool],
    train_type_colors: dict[int, str] | None = None,
) -> None:
    """駅設定と列車種別の色設定を保存する。"""
    data = _load_all_settings()

    sessions = data["sessions"]
    session_settings = sessions.setdefault(session_id, {})

    settings = session_settings.setdefault(file_key, {})

    settings["station_aliases"] = station_aliases
    settings["station_no_mark"] = station_no_mark

    # 色設定が渡された場合だけ更新する。
    # 省略された場合は既存の色設定を維持する。
    if train_type_colors is not None:
        settings["train_type_colors"] = {
            str(index): color
            for index, color in train_type_colors.items()
        }

    _save_all_settings(data)
