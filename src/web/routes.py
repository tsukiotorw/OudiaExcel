
import hashlib
import secrets
import re

from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.application.oud2_loader import load_oud2
from src.application.station_timetable import generate_station_timetable
from src.models.railway import Railway
from src.web.settings import (
    load_station_settings,
    save_station_settings,
)

WEB_DIR = Path(__file__).resolve().parent

router = APIRouter()
templates = Jinja2Templates(directory=WEB_DIR / "templates")

# ローカルWeb版の路線データとファイル識別キーを一時的に保持する。
_loaded_railways: dict[str, Railway] = {}
_railway_file_keys: dict[str, str] = {}


def _get_session_id(request: Request) -> tuple[str, bool]:
    """CookieからセッションIDを取得し、なければ新規発行する。"""
    session_id = request.cookies.get("session_id")

    if session_id:
        return session_id, False

    return secrets.token_urlsafe(32), True


def _set_session_cookie(
    response: HTMLResponse,
    session_id: str,
    is_new_session: bool,
) -> HTMLResponse:
    """新規セッションの場合にCookieを設定する。"""
    if is_new_session:
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=60 * 60 * 24 * 30,
        )

    return response


def _apply_station_settings(
    railway: Railway,
    settings: dict,
) -> None:
    """保存済みの駅略称・無印設定を路線データに反映する。"""
    aliases = settings.get("station_aliases", {})
    no_mark = settings.get("station_no_mark", {})

    if not isinstance(aliases, dict):
        aliases = {}

    if not isinstance(no_mark, dict):
        no_mark = {}

    for station in railway.stations:
        station.short_name = aliases.get(station.name, "")
        station.is_no_mark = no_mark.get(station.name, False)


def _render_page(
    request: Request,
    session_id: str,
    railway_id: str | None = None,
    error: str | None = None,
    station_index: int | None = None,
    message: str | None = None,
):
    railway = _loaded_railways.get(railway_id) if railway_id else None
    timetable = None
    settings = {}

    if railway is not None:
        file_key = _railway_file_keys.get(railway_id)

        if file_key is not None:
            settings = load_station_settings(session_id, file_key)
            _apply_station_settings(railway, settings)

    legend_settings = settings.get("legend_settings", {})

    if not isinstance(legend_settings, dict):
        legend_settings = {}

    show_legend = legend_settings.get("show_legend", True)
    show_train_type_legend = legend_settings.get(
        "show_train_type_legend",
        True,
    )
    show_station_legend = legend_settings.get(
        "show_station_legend",
        True,
    )

    # 時刻表の表示設定
    display_settings = settings.get("display_settings", {})
    if not isinstance(display_settings, dict):
        display_settings = {}

    # 列車欄の表示設定
    train_display_defaults = {
        "metadata_font_name": "源ノ角ゴシック JP",
        "metadata_font_size": 9,
        "minute_font_name": "源ノ角ゴシック JP",
        "minute_font_size": 9,
        "train_font_color": "000000",
        "train_fill": "FAFAFA",
        "use_train_type_short_name": False,
        "show_destination": True,
    }

    train_display_settings = {}

    saved_train_display = display_settings.get("train", {})
    if not isinstance(saved_train_display, dict):
        saved_train_display = {}

    train_display_settings.update(train_display_defaults)
    train_display_settings.update(saved_train_display)

    # フォントサイズを検証
    for key in ("metadata_font_size", "minute_font_size"):
        try:
            size = int(train_display_settings[key])
        except (TypeError, ValueError):
            size = train_display_defaults[key]

        if not 6 <= size <= 72:
            size = train_display_defaults[key]

        train_display_settings[key] = size

    # 色を検証
    for key in ("train_font_color", "train_fill"):
        color = str(train_display_settings.get(key, ""))

        if not re.fullmatch(r"[0-9A-Fa-f]{6}", color):
            train_display_settings[key] = train_display_defaults[key]
        else:
            train_display_settings[key] = color.upper()

    # 真偽値を検証
    for key in ("use_train_type_short_name", "show_destination"):
        if not isinstance(train_display_settings[key], bool):
            train_display_settings[key] = train_display_defaults[key]

    # 列車種別ごとの表示・非表示
    saved_column_visibility = display_settings.get(
        "train_type_column_visible", {}
    )
    if not isinstance(saved_column_visibility, dict):
        saved_column_visibility = {}

    train_type_column_visible = {}

    if railway is not None:
        for train_type in railway.train_types:
            value = saved_column_visibility.get(
                str(train_type.index),
                saved_column_visibility.get(train_type.index, True),
            )
            train_type_column_visible[train_type.index] = (
                value if isinstance(value, bool) else True
            )

    # タイトルの表示設定（未設定の場合は既定値を使用）
    title_settings = {
        "fill": None,
        "font_color": "000000",
        "font_name": "源ノ角ゴシック JP",
        "font_size": 14,
        "borders": {
            "top": {
                "enabled": False,
                "color": "000000",
                "style": "thin",
            },
            "bottom": {
                "enabled": False,
                "color": "000000",
                "style": "thin",
            },
            "left": {
                "enabled": False,
                "color": "000000",
                "style": "thin",
            },
            "right": {
                "enabled": False,
                "color": "000000",
                "style": "thin",
            },
        },
    }

    saved_title_settings = display_settings.get("title", {})
    if isinstance(saved_title_settings, dict):
        title_settings.update(saved_title_settings)

    # ヘッダ（下り・上り）の罫線設定
    default_border_side = {
        "enabled": False,
        "color": "000000",
        "style": "thin",
    }

    header_border = {
        side: default_border_side.copy()
        for side in ("top", "bottom", "left", "right")
    }

    saved_header_border = display_settings.get("header_border", {})

    if isinstance(saved_header_border, dict):
        for side in ("top", "bottom", "left", "right"):
            saved_side = saved_header_border.get(side, {})

            if isinstance(saved_side, dict):
                header_border[side].update(saved_side)

    # 保存値の形式を検証し、不正な値は既定値に戻す
    valid_border_styles = {
        "thin",
        "medium",
        "thick",
        "dashed",
        "dotted",
        "double",
    }

    for side in ("top", "bottom", "left", "right"):
        border = header_border[side]

        if not isinstance(border.get("enabled"), bool):
            border["enabled"] = False

        if not re.fullmatch(
            r"[0-9A-Fa-f]{6}",
            str(border.get("color", "")),
        ):
            border["color"] = "000000"
        else:
            border["color"] = border["color"].upper()

        if border.get("style") not in valid_border_styles:
            border["style"] = "thin"

    # 時刻欄の罫線設定
    hour_border = {
        side: default_border_side.copy()
        for side in ("top", "bottom", "left", "right")
    }

    saved_hour_border = display_settings.get("hour_border", {})

    if isinstance(saved_hour_border, dict):
        for side in ("top", "bottom", "left", "right"):
            saved_side = saved_hour_border.get(side, {})

            if isinstance(saved_side, dict):
                hour_border[side].update(saved_side)

    # 保存値の形式を検証し、不正な値は既定値に戻す
    for side in ("top", "bottom", "left", "right"):
        border = hour_border[side]

        if not isinstance(border.get("enabled"), bool):
            border["enabled"] = False

        if not re.fullmatch(
            r"[0-9A-Fa-f]{6}",
            str(border.get("color", "")),
        ):
            border["color"] = "000000"
        else:
            border["color"] = border["color"].upper()

        if border.get("style") not in valid_border_styles:
            border["style"] = "thin"

    # 列車欄の罫線設定
    train_border = {
        side: default_border_side.copy()
        for side in ("top", "bottom", "left", "right")
    }

    saved_train_border = display_settings.get("train_border", {})

    if isinstance(saved_train_border, dict):
        for side in ("top", "bottom", "left", "right"):
            saved_side = saved_train_border.get(side, {})

            if isinstance(saved_side, dict):
                train_border[side].update(saved_side)

    # 保存値の形式を検証し、不正な値は既定値に戻す
    for side in ("top", "bottom", "left", "right"):
        border = train_border[side]

        if not isinstance(border.get("enabled"), bool):
            border["enabled"] = False

        if not re.fullmatch(
            r"[0-9A-Fa-f]{6}",
            str(border.get("color", "")),
        ):
            border["color"] = "000000"
        else:
            border["color"] = border["color"].upper()

        if border.get("style") not in valid_border_styles:
            border["style"] = "thin"

    # 列車情報と分の間の罫線設定
    train_minute_border = default_border_side.copy()

    saved_train_minute_border = display_settings.get(
        "train_minute_border",
        {},
    )

    if isinstance(saved_train_minute_border, dict):
        train_minute_border.update(saved_train_minute_border)

    # 保存値の形式を検証し、不正な値は既定値に戻す
    if not isinstance(train_minute_border.get("enabled"), bool):
        train_minute_border["enabled"] = False

    if not re.fullmatch(
        r"[0-9A-Fa-f]{6}",
        str(train_minute_border.get("color", "")),
    ):
        train_minute_border["color"] = "000000"
    else:
        train_minute_border["color"] = train_minute_border["color"].upper()

    if train_minute_border.get("style") not in valid_border_styles:
        train_minute_border["style"] = "thin"

    saved_colors = settings.get("train_type_colors", {})
    train_type_colors: dict[int, str] = {}

    if isinstance(saved_colors, dict):
        for index, color in saved_colors.items():
            if (
                str(index).isdigit()
                and isinstance(color, str)
                and re.fullmatch(r"[0-9A-Fa-f]{6}", color)
            ):
                train_type_colors[int(index)] = color.upper()

    if railway is not None and station_index is not None:
        station = next(
            (
                item
                for item in railway.stations
                if item.index == station_index
            ),
            None,
        )

        if station is not None:
            timetable = generate_station_timetable(railway, station)
        else:
            error = "選択された駅が見つかりません。"

    train_type_legend = []
    station_legend = []

    if railway is not None:
        # 列車種別の凡例
        train_type_legend = [
            {
                "index": train_type.index,
                "name": train_type.short_name or train_type.name,
                "color": train_type_colors.get(
                    train_type.index,
                    "000000",
                ),
            }
            for train_type in railway.train_types
        ]

        # 略称または無印が設定された駅だけを凡例に表示する
        for station in railway.stations:
            if station.is_no_mark:
                station_legend.append(f"無印＝{station.name}")
            elif station.short_name:
                station_legend.append(
                    f"{station.short_name}＝{station.name}"
                )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "railway": railway,
            "railway_id": railway_id,
            "error": error,
            "station_index": station_index,
            "timetable": timetable,
            "message": message,
            "train_type_legend": train_type_legend,
            "station_legend": station_legend,
            "train_type_colors": train_type_colors,
            "show_legend": show_legend,
            "show_train_type_legend": show_train_type_legend,
            "show_station_legend": show_station_legend,
            "display_settings": display_settings,
            "title_settings": title_settings,
            "header_border": header_border,
            "hour_border": hour_border,
            "train_border": train_border,
            "train_minute_border": train_minute_border,
            "train_display_settings": train_display_settings,
            "train_type_column_visible": train_type_column_visible,
        },
    )


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    session_id, is_new_session = _get_session_id(request)

    response = _render_page(
        request,
        session_id=session_id,
    )

    return _set_session_cookie(response, session_id, is_new_session)


@router.post("/", response_class=HTMLResponse)
async def upload_oud2(
    request: Request,
    file: UploadFile = File(...),
):
    session_id, is_new_session = _get_session_id(request)
    temp_path = None

    try:
        if not file.filename or not file.filename.lower().endswith(".oud2"):
            raise ValueError("拡張子が .oud2 のファイルを選択してください。")

        with NamedTemporaryFile(suffix=".oud2", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

            while chunk := await file.read(1024 * 1024):
                temp_file.write(chunk)

        # ファイル内容から識別キーを作成する。
        file_key = hashlib.sha256(temp_path.read_bytes()).hexdigest()

        railway = load_oud2(temp_path)
        railway_id = uuid4().hex

        _loaded_railways[railway_id] = railway
        _railway_file_keys[railway_id] = file_key

        response = _render_page(
            request,
            session_id=session_id,
            railway_id=railway_id,
        )

    except Exception as exc:
        response = _render_page(
            request,
            session_id=session_id,
            error=f"ファイルを読み込めませんでした: {exc}",
        )

    finally:
        await file.close()

        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    return _set_session_cookie(response, session_id, is_new_session)


@router.post("/station", response_class=HTMLResponse)
async def select_station(
    request: Request,
    railway_id: str = Form(...),
    station_index: int = Form(...),
):
    session_id, is_new_session = _get_session_id(request)

    if railway_id not in _loaded_railways:
        response = _render_page(
            request,
            session_id=session_id,
            error="路線データが見つかりません。ファイルを再読み込みしてください。",
        )
    else:
        response = _render_page(
            request,
            session_id=session_id,
            railway_id=railway_id,
            station_index=station_index,
        )

    return _set_session_cookie(response, session_id, is_new_session)


@router.post("/settings", response_class=HTMLResponse)
async def save_settings(
    request: Request,
    railway_id: str = Form(...),
    station_index: str = Form(""),
):
    session_id, is_new_session = _get_session_id(request)

    railway = _loaded_railways.get(railway_id)

    if railway is None:
        response = _render_page(
            request,
            session_id=session_id,
            error="路線データが見つかりません。ファイルを再読み込みしてください。",
        )
        return _set_session_cookie(response, session_id, is_new_session)

    file_key = _railway_file_keys.get(railway_id)

    if file_key is None:
        response = _render_page(
            request,
            session_id=session_id,
            error="ファイル識別情報が見つかりません。再読み込みしてください。",
        )
        return _set_session_cookie(response, session_id, is_new_session)

    form_data = await request.form()

    station_aliases: dict[str, str] = {}
    station_no_mark: dict[str, bool] = {}

    legend_settings = {
        "show_legend": form_data.get("show_legend") == "true",
        "show_train_type_legend": (
            form_data.get("show_train_type_legend") == "true"
        ),
        "show_station_legend": (
            form_data.get("show_station_legend") == "true"
        ),
    }

    for station in railway.stations:
        alias = str(form_data.get(f"alias_{station.index}", "")).strip()
        no_mark = form_data.get(f"no_mark_{station.index}") == "true"

        if alias:
            station_aliases[station.name] = alias

        if no_mark:
            station_no_mark[station.name] = True

    # 既存の表示設定を読み込む
    existing_settings = load_station_settings(session_id, file_key)
    display_settings = existing_settings.get("display_settings", {})

    if not isinstance(display_settings, dict):
        display_settings = {}

    # 列車欄の表示設定を取得・保存する
    saved_train_display = display_settings.get("train", {})
    if not isinstance(saved_train_display, dict):
        saved_train_display = {}

    train_display_settings = {}

    for key, default in (
        ("metadata_font_name", "源ノ角ゴシック JP"),
        ("minute_font_name", "源ノ角ゴシック JP"),
    ):
        submitted = str(form_data.get(key, "")).strip()
        train_display_settings[key] = (
            submitted[:100]
            if submitted
            else saved_train_display.get(key, default)
        )

    for key, default in (
        ("metadata_font_size", 9),
        ("minute_font_size", 9),
    ):
        try:
            size = int(form_data.get(key, default))
        except (TypeError, ValueError):
            size = saved_train_display.get(key, default)

        if not 6 <= size <= 72:
            size = saved_train_display.get(key, default)

        train_display_settings[key] = size

    for key, default in (
        ("train_font_color", "000000"),
        ("train_fill", "FAFAFA"),
    ):
        submitted = str(form_data.get(key, "")).strip()

        if re.fullmatch(r"#[0-9A-Fa-f]{6}", submitted):
            train_display_settings[key] = submitted[1:].upper()
        else:
            train_display_settings[key] = saved_train_display.get(
                key, default
            )

    train_display_settings["use_train_type_short_name"] = (
        form_data.get("use_train_type_short_name") == "true"
    )
    train_display_settings["show_destination"] = (
        form_data.get("show_destination") == "true"
    )

    display_settings["train"] = train_display_settings

    # 列車種別ごとの表示・非表示
    train_type_column_visible = {}

    for train_type in railway.train_types:
        train_type_column_visible[str(train_type.index)] = (
            form_data.get(
                f"train_type_column_visible_{train_type.index}"
            ) == "true"
        )

    display_settings["train_type_column_visible"] = (
        train_type_column_visible
    )

    # タイトル設定を取得する
    title_settings = display_settings.get("title", {})
    if not isinstance(title_settings, dict):
        title_settings = {}

    # タイトルの背景色を取得する
    title_fill = None

    if form_data.get("title_fill_enabled") == "true":
        submitted_fill = str(form_data.get("title_fill", "")).strip()

        if re.fullmatch(r"#[0-9A-Fa-f]{6}", submitted_fill):
            title_fill = submitted_fill[1:].upper()
        else:
            title_fill = title_settings.get("fill")

    # タイトルの文字色を取得する
    submitted_font_color = str(
        form_data.get("title_font_color", "")
    ).strip()

    if re.fullmatch(r"#[0-9A-Fa-f]{6}", submitted_font_color):
        title_font_color = submitted_font_color[1:].upper()
    else:
        title_font_color = title_settings.get("font_color", "000000")

    # タイトルのフォント名を取得する
    submitted_font_name = str(
        form_data.get("title_font_name", "")
    ).strip()

    title_font_name = (
        submitted_font_name[:100]
        if submitted_font_name
        else title_settings.get("font_name", "源ノ角ゴシック JP")
    )

    # タイトルのフォントサイズを取得する
    try:
        title_font_size = int(form_data.get("title_font_size", "14"))
    except (TypeError, ValueError):
        title_font_size = title_settings.get("font_size", 14)

    if not 6 <= title_font_size <= 72:
        title_font_size = title_settings.get("font_size", 14)

    # タイトルの罫線設定を取得する
    saved_borders = title_settings.get("borders", {})

    if not isinstance(saved_borders, dict):
        saved_borders = {}

    title_borders = {}

    valid_border_styles = {
        "thin",
        "medium",
        "thick",
        "dashed",
        "dotted",
        "double",
    }

    for side in ("top", "bottom", "left", "right"):
        saved_border = saved_borders.get(side, {})

        if not isinstance(saved_border, dict):
            saved_border = {}

        # 罫線の有効・無効
        border_enabled = (
            form_data.get(f"title_border_{side}_enabled") == "true"
        )

        # 罫線の色
        submitted_border_color = str(
            form_data.get(f"title_border_{side}_color", "")
        ).strip()

        if re.fullmatch(r"#[0-9A-Fa-f]{6}", submitted_border_color):
            border_color = submitted_border_color[1:].upper()
        else:
            border_color = saved_border.get("color", "000000")

        # 罫線の線種
        submitted_border_style = str(
            form_data.get(f"title_border_{side}_style", "")
        ).strip()

        if submitted_border_style in valid_border_styles:
            border_style = submitted_border_style
        else:
            border_style = saved_border.get("style", "thin")

        title_borders[side] = {
            "enabled": border_enabled,
            "color": border_color,
            "style": border_style,
        }

    # タイトル設定を保存用の辞書にまとめる
    title_settings = {
        "fill": title_fill,
        "font_color": title_font_color,
        "font_name": title_font_name,
        "font_size": title_font_size,
        "borders": title_borders,
    }

    display_settings["title"] = title_settings

    # ヘッダ（下り・上り）の罫線設定を取得する
    saved_header_border = display_settings.get("header_border", {})

    if not isinstance(saved_header_border, dict):
        saved_header_border = {}

    header_border = {}

    for side in ("top", "bottom", "left", "right"):
        saved_border = saved_header_border.get(side, {})

        if not isinstance(saved_border, dict):
            saved_border = {}

        # 罫線の有効・無効
        border_enabled = (
            form_data.get(f"header_border_{side}_enabled") == "true"
        )

        # 罫線の色
        submitted_border_color = str(
            form_data.get(f"header_border_{side}_color", "")
        ).strip()

        if re.fullmatch(r"#[0-9A-Fa-f]{6}", submitted_border_color):
            border_color = submitted_border_color[1:].upper()
        else:
            border_color = saved_border.get("color", "000000")

        # 罫線の線種
        submitted_border_style = str(
            form_data.get(f"header_border_{side}_style", "")
        ).strip()

        if submitted_border_style in valid_border_styles:
            border_style = submitted_border_style
        else:
            border_style = saved_border.get("style", "thin")

        header_border[side] = {
            "enabled": border_enabled,
            "color": border_color,
            "style": border_style,
        }

    display_settings["header_border"] = header_border

    # 時刻欄の罫線設定を取得する
    saved_hour_border = display_settings.get("hour_border", {})

    if not isinstance(saved_hour_border, dict):
        saved_hour_border = {}

    hour_border = {}

    for side in ("top", "bottom", "left", "right"):
        saved_border = saved_hour_border.get(side, {})

        if not isinstance(saved_border, dict):
            saved_border = {}

        # 罫線の有効・無効
        border_enabled = (
            form_data.get(f"hour_border_{side}_enabled") == "true"
        )

        # 罫線の色
        submitted_border_color = str(
            form_data.get(f"hour_border_{side}_color", "")
        ).strip()

        if re.fullmatch(r"#[0-9A-Fa-f]{6}", submitted_border_color):
            border_color = submitted_border_color[1:].upper()
        else:
            border_color = saved_border.get("color", "000000")

        # 罫線の線種
        submitted_border_style = str(
            form_data.get(f"hour_border_{side}_style", "")
        ).strip()

        if submitted_border_style in valid_border_styles:
            border_style = submitted_border_style
        else:
            border_style = saved_border.get("style", "thin")

        hour_border[side] = {
            "enabled": border_enabled,
            "color": border_color,
            "style": border_style,
        }

    display_settings["hour_border"] = hour_border

    # 列車欄の罫線設定を取得・保存する
    saved_train_border = display_settings.get("train_border", {})

    if not isinstance(saved_train_border, dict):
        saved_train_border = {}

    train_border = {}

    for side in ("top", "bottom", "left", "right"):
        saved_border = saved_train_border.get(side, {})

        if not isinstance(saved_border, dict):
            saved_border = {}

        # 罫線の有効・無効
        border_enabled = (
            form_data.get(f"train_border_{side}_enabled") == "true"
        )

        # 罫線の色
        submitted_border_color = str(
            form_data.get(f"train_border_{side}_color", "")
        ).strip()

        if re.fullmatch(r"#[0-9A-Fa-f]{6}", submitted_border_color):
            border_color = submitted_border_color[1:].upper()
        else:
            border_color = saved_border.get("color", "000000")

        # 罫線の線種
        submitted_border_style = str(
            form_data.get(f"train_border_{side}_style", "")
        ).strip()

        if submitted_border_style in valid_border_styles:
            border_style = submitted_border_style
        else:
            border_style = saved_border.get("style", "thin")

        train_border[side] = {
            "enabled": border_enabled,
            "color": border_color,
            "style": border_style,
        }

    display_settings["train_border"] = train_border

    # 列車情報と分の間の罫線設定を取得・保存する
    saved_train_minute_border = display_settings.get(
        "train_minute_border",
        {},
    )

    if not isinstance(saved_train_minute_border, dict):
        saved_train_minute_border = {}

    # 罫線の有効・無効
    train_minute_border_enabled = (
        form_data.get("train_minute_border_enabled") == "true"
    )

    # 罫線の色
    submitted_train_minute_color = str(
        form_data.get("train_minute_border_color", "")
    ).strip()

    if re.fullmatch(r"#[0-9A-Fa-f]{6}", submitted_train_minute_color):
        train_minute_border_color = submitted_train_minute_color[1:].upper()
    else:
        train_minute_border_color = saved_train_minute_border.get(
            "color",
            "000000",
        )

    # 罫線の線種
    submitted_train_minute_style = str(
        form_data.get("train_minute_border_style", "")
    ).strip()

    if submitted_train_minute_style in valid_border_styles:
        train_minute_border_style = submitted_train_minute_style
    else:
        train_minute_border_style = saved_train_minute_border.get(
            "style",
            "thin",
        )

    display_settings["train_minute_border"] = {
        "enabled": train_minute_border_enabled,
        "color": train_minute_border_color,
        "style": train_minute_border_style,
    }

    # 既存の列車種別の色設定を読み込む
    saved_colors = existing_settings.get("train_type_colors", {})

    train_type_colors: dict[int, str] = {}

    if isinstance(saved_colors, dict):
        for index, color in saved_colors.items():
            if (
                str(index).isdigit()
                and isinstance(color, str)
                and re.fullmatch(r"[0-9A-Fa-f]{6}", color)
            ):
                train_type_colors[int(index)] = color.upper()

    for train_type in railway.train_types:
        field_name = f"train_type_color_{train_type.index}"
        submitted_color = str(form_data.get(field_name, "")).strip()

        if re.fullmatch(r"#[0-9A-Fa-f]{6}", submitted_color):
            train_type_colors[train_type.index] = submitted_color[1:].upper()

    save_station_settings(
        session_id=session_id,
        file_key=file_key,
        station_aliases=station_aliases,
        station_no_mark=station_no_mark,
        train_type_colors=train_type_colors,
        legend_settings=legend_settings,
        display_settings=display_settings,
    )

    # 保存した設定を路線データに反映する。
    settings = load_station_settings(session_id, file_key)
    _apply_station_settings(railway, settings)

    selected_index = None
    if station_index.strip():
        try:
            selected_index = int(station_index)
        except ValueError:
            selected_index = None

    response = _render_page(
        request,
        session_id=session_id,
        railway_id=railway_id,
        station_index=selected_index,
        message="駅設定・列車種別の色設定を保存しました。",
    )

    return _set_session_cookie(response, session_id, is_new_session)

