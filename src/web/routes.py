
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

    for station in railway.stations:
        alias = str(form_data.get(f"alias_{station.index}", "")).strip()
        no_mark = form_data.get(f"no_mark_{station.index}") == "true"

        if alias:
            station_aliases[station.name] = alias

        if no_mark:
            station_no_mark[station.name] = True

    # 既存の色設定を読み込み、フォームで指定された色を更新する。
    existing_settings = load_station_settings(session_id, file_key)
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

