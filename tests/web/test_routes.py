import re
from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from openpyxl import load_workbook
import pytest

from src.application.station_timetable import generate_station_timetable
from src.web import routes
from src.web.main import app


def test_display_config_includes_web_display_options() -> None:
    config = routes._display_config_from_settings(
        {
            "train_type_colors": {"2": "A1B2C3"},
            "display_settings": {
                "header": {
                    "font_name": "Header Font",
                    "font_size": 14,
                    "font_color": "123456",
                    "fill": "654321",
                    "up_header_text": "北行",
                    "down_header_text": "南行",
                    "up_fill": "CFE2F3",
                    "down_fill": "FCE5CD",
                },
                "hour": {
                    "font_name": "Hour Font",
                    "font_size": 11,
                    "font_color": "ABCDEF",
                    "fill": "FEDCBA",
                },
                "legend": {
                    "label_font_name": "Label Font",
                    "label_font_size": 10,
                    "label_font_color": "111111",
                    "label_fill": "222222",
                    "font_name": "Legend Font",
                    "font_size": 9,
                    "fill": "333333",
                    "row_height": 30,
                    "show_destination_legend": False,
                },
                "legend_border": {
                    "bottom": {
                        "enabled": True,
                        "color": "445566",
                        "style": "double",
                    }
                },
                "train_type_legend_visible": {"2": False},
            },
        }
    )

    assert (config.header_font_name, config.header_font_size) == (
        "Header Font",
        14,
    )
    assert (config.header_font_color, config.header_fill) == (
        "123456",
        "654321",
    )
    assert config.up_header_text == "北行"
    assert config.down_header_text == "南行"
    assert config.up_header_fill == "CFE2F3"
    assert config.down_header_fill == "FCE5CD"
    assert (config.hour_font_name, config.hour_fill) == (
        "Hour Font",
        "FEDCBA",
    )
    assert config.legend_label_font_name == "Label Font"
    assert config.legend_font_name == "Legend Font"
    assert config.legend_row_height == 30
    assert config.show_destination_legend is False
    assert config.legend_border.bottom.enabled is True
    assert config.legend_border.bottom.style == "double"
    assert config.train_type_colors[2] == "A1B2C3"
    assert config.train_type_visible[2] is False


def test_display_config_uses_default_header_fill_and_legacy_settings() -> None:
    config = routes._display_config_from_settings(
        {
            "display_settings": {
                "header": {
                    "fill": "D9EAD3",
                }
            }
        }
    )

    assert config.header_fill == "D9EAD3"
    assert config.up_header_text == "上り"
    assert config.down_header_text == "下り"
    assert config.up_header_fill is None
    assert config.down_header_fill is None

    default_config = routes._display_config_from_settings({})
    assert default_config.header_fill == "D9EAD3"
    assert default_config.header_font_color == "FAFAFA"
    assert default_config.up_header_fill is None
    assert default_config.down_header_fill is None


def test_display_config_preserves_empty_direction_header_text() -> None:
    config = routes._display_config_from_settings(
        {
            "display_settings": {
                "header": {
                    "up_header_text": "",
                    "down_header_text": "南行",
                }
            }
        }
    )

    assert config.up_header_text == ""
    assert config.down_header_text == "南行"


def test_display_config_preserves_disabled_common_header_fill() -> None:
    config = routes._display_config_from_settings(
        {
            "display_settings": {
                "header": {
                    "fill": None,
                }
            }
        }
    )

    assert config.header_fill is None


@pytest.mark.parametrize(
    ("up_fill", "down_fill", "common_fill", "expected_up", "expected_down"),
    [
        ("A1B2C3", "D4E5F6", "102030", "A1B2C3", "D4E5F6"),
        ("A1B2C3", None, "102030", "A1B2C3", "102030"),
        (None, "D4E5F6", "102030", "102030", "D4E5F6"),
        (None, None, "102030", "102030", "102030"),
    ],
)
def test_settings_render_direction_header_fills(
    parsed_railway,
    monkeypatch,
    up_fill: str | None,
    down_fill: str | None,
    common_fill: str,
    expected_up: str,
    expected_down: str,
) -> None:
    railway_id = "header-fill-test"
    file_key = "header-fill-file"
    saved_settings = {
        "display_settings": {
            "header": {
                "fill": common_fill,
                "up_fill": up_fill,
                "down_fill": down_fill,
            }
        }
    }
    monkeypatch.setitem(routes._loaded_railways, railway_id, parsed_railway)
    monkeypatch.setitem(routes._railway_file_keys, railway_id, file_key)
    monkeypatch.setattr(
        routes,
        "load_station_settings",
        lambda *_args: saved_settings,
    )

    def save_settings(**kwargs) -> None:
        saved_settings.update(kwargs)

    monkeypatch.setattr(routes, "save_station_settings", save_settings)
    form_data = {
        "railway_id": railway_id,
        "station_index": str(parsed_railway.stations[0].index),
        "up_header_fill": f"#{up_fill or common_fill or 'D9EAD3'}",
        "down_header_fill": f"#{down_fill or common_fill or 'D9EAD3'}",
    }
    if common_fill:
        form_data["header_fill_enabled"] = "true"
        form_data["header_fill"] = f"#{common_fill}"
    if up_fill:
        form_data["up_header_fill_enabled"] = "true"
    if down_fill:
        form_data["down_header_fill_enabled"] = "true"

    response = TestClient(app).post("/settings", data=form_data)

    assert response.status_code == 200
    for direction, expected_fill in (
        ("up", expected_up),
        ("down", expected_down),
    ):
        match = re.search(
            rf'<h3\b(?=[^>]*data-direction="{direction}")[^>]*>.*?</h3>',
            response.text,
            re.DOTALL,
        )
        assert match is not None
        assert f"background-color: #{expected_fill};" in match.group()


def test_excel_export_downloads_selected_station(
    parsed_railway,
    monkeypatch,
) -> None:
    railway_id = "export-test"
    file_key = "export-test-file"
    saved_settings = {
        "display_settings": {
            "header": {
                "up_header_text": "北行",
                "down_header_text": "南行",
            }
        }
    }
    monkeypatch.setitem(routes._loaded_railways, railway_id, parsed_railway)
    monkeypatch.setitem(routes._railway_file_keys, railway_id, file_key)
    monkeypatch.setattr(
        routes,
        "load_station_settings",
        lambda *_args: saved_settings,
    )
    monkeypatch.setattr(
        routes,
        "save_station_settings",
        lambda **_kwargs: None,
    )

    response = TestClient(app).post(
        "/export/excel",
        data={
            "railway_id": railway_id,
            "station_index": str(parsed_railway.stations[0].index),
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument"
    )
    workbook = load_workbook(BytesIO(response.content))
    assert workbook.active.title == parsed_railway.stations[0].name
    header_values = [
        cell.value
        for cell in workbook.active[3]
    ]
    assert "北行" in header_values
    assert "南行" in header_values
    assert (
        f"{parsed_railway.stations[0].name}駅 時刻表"
        in [cell.value for row in workbook.active for cell in row]
    )


def test_upload_selects_first_station_and_renders_web_controls() -> None:
    sample_path = (
        Path(__file__).resolve().parents[2]
        / "examples"
        / "解析用.oud2"
    )
    with sample_path.open("rb") as sample_file:
        response = TestClient(app).post(
            "/",
            files={
                "file": (
                    sample_path.name,
                    sample_file,
                    "application/octet-stream",
                )
            },
        )

    assert response.status_code == 200
    assert "timetable-panel" in response.text
    assert "A駅 時刻表" in response.text
    assert 'id="export-png"' in response.text
    assert 'name="header_font_name"' in response.text
    assert 'value="#FAFAFA"' in response.text
    assert 'name="up_header_fill"' in response.text
    assert 'name="down_header_fill"' in response.text
    assert 'name="up_header_text"' in response.text
    assert 'name="down_header_text"' in response.text
    assert 'value="上り"' in response.text
    assert 'value="下り"' in response.text
    assert 'value="#D9EAD3"' in response.text
    assert 'name="hour_font_name"' in response.text
    assert 'name="show_destination_legend"' in response.text


def test_web_preview_places_up_left_and_down_right_with_matching_data(
    parsed_railway,
) -> None:
    sample_path = (
        Path(__file__).resolve().parents[2]
        / "examples"
        / "解析用.oud2"
    )
    expected_timetable = generate_station_timetable(
        parsed_railway,
        parsed_railway.stations[0],
    )

    with sample_path.open("rb") as sample_file:
        response = TestClient(app).post(
            "/",
            files={
                "file": (
                    sample_path.name,
                    sample_file,
                    "application/octet-stream",
                )
            },
        )

    assert response.status_code == 200
    direction_sections = re.findall(
        r'<section class="direction">(.*?)</section>',
        response.text,
        re.DOTALL,
    )
    assert [
        re.search(r'data-direction="([^"]+)"', section).group(1)
        for section in direction_sections
    ] == ["up", "down"]

    for direction, hours in (
        ("up", expected_timetable.up),
        ("down", expected_timetable.down),
    ):
        section = next(
            section
            for section in direction_sections
            if f'data-direction="{direction}"' in section
        )
        assert hours
        for hour in hours:
            assert str(hour.hour) in section
            for entry in hour.entries:
                assert f"{entry.minute:02d}" in section
                assert entry.train_type.name in section
                if not entry.destination.is_no_mark:
                    assert entry.destination.display_name in section


def test_settings_save_new_display_controls(
    parsed_railway,
    monkeypatch,
) -> None:
    railway_id = "settings-test"
    file_key = "settings-test-file"
    saved_settings = {}
    train_type_index = parsed_railway.train_types[0].index
    monkeypatch.setitem(routes._loaded_railways, railway_id, parsed_railway)
    monkeypatch.setitem(routes._railway_file_keys, railway_id, file_key)
    monkeypatch.setattr(
        routes,
        "load_station_settings",
        lambda _session_id, _file_key: saved_settings,
    )

    def save_settings(**kwargs) -> None:
        saved_settings.update(kwargs)

    monkeypatch.setattr(routes, "save_station_settings", save_settings)
    response = TestClient(app).post(
        "/settings",
        data={
            "railway_id": railway_id,
            "station_index": str(parsed_railway.stations[0].index),
            "header_font_name": "Web Header",
            "header_font_size": "15",
            "header_font_color": "#102030",
            "header_fill_enabled": "true",
            "header_fill": "#405060",
            "up_header_text": "仙台方面",
            "down_header_text": "",
            "up_header_fill_enabled": "true",
            "up_header_fill": "#A1B2C3",
            "hour_font_name": "Web Hour",
            "hour_font_size": "13",
            "hour_font_color": "#607080",
            "hour_fill_enabled": "true",
            "hour_fill": "#90A0B0",
            "label_font_name": "Legend Label",
            "label_font_size": "11",
            "label_font_color": "#112233",
            "label_fill": "#223344",
            "font_name": "Legend Items",
            "font_size": "12",
            "fill": "#334455",
            "legend_row_height": "31.5",
            "show_destination_legend": "true",
            f"train_type_legend_visible_{train_type_index}": "true",
            "legend_border_bottom_enabled": "true",
            "legend_border_bottom_color": "#445566",
            "legend_border_bottom_style": "double",
        },
    )

    assert response.status_code == 200
    display_settings = saved_settings["display_settings"]
    assert display_settings["header"]["font_name"] == "Web Header"
    assert display_settings["header"]["font_color"] == "102030"
    assert display_settings["header"]["fill"] == "405060"
    assert display_settings["header"]["up_header_text"] == "仙台方面"
    assert display_settings["header"]["down_header_text"] == ""
    assert display_settings["header"]["up_fill"] == "A1B2C3"
    assert display_settings["header"]["down_fill"] is None
    up_checkbox = response.text.split(
        'id="up_header_fill_enabled"',
        1,
    )[1].split(">", 1)[0]
    down_checkbox = response.text.split(
        'id="down_header_fill_enabled"',
        1,
    )[1].split(">", 1)[0]
    assert "checked" in up_checkbox
    assert "checked" not in down_checkbox
    assert 'value="#A1B2C3"' in response.text
    assert re.search(r'name="up_header_text"[^>]*value="仙台方面"', response.text)
    assert re.search(r'name="down_header_text"[^>]*value=""', response.text)
    assert ">仙台方面</h3>" in response.text
    assert re.search(
        r'<h3\b(?=[^>]*data-direction="down")[^>]*></h3>',
        response.text,
    )
    assert display_settings["hour"]["font_size"] == 13
    assert display_settings["hour"]["fill"] == "90A0B0"
    assert display_settings["legend"]["label_font_name"] == "Legend Label"
    assert display_settings["legend"]["font_name"] == "Legend Items"
    assert display_settings["legend"]["row_height"] == 31.5
    assert display_settings["legend"]["show_destination_legend"] is True
    assert (
        display_settings["train_type_legend_visible"][
            str(train_type_index)
        ]
        is True
    )
    assert (
        display_settings["legend_border"]["bottom"]["style"]
        == "double"
    )
