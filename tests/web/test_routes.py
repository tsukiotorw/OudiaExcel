from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from openpyxl import load_workbook

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


def test_excel_export_downloads_selected_station(
    parsed_railway,
    monkeypatch,
) -> None:
    railway_id = "export-test"
    file_key = "export-test-file"
    monkeypatch.setitem(routes._loaded_railways, railway_id, parsed_railway)
    monkeypatch.setitem(routes._railway_file_keys, railway_id, file_key)
    monkeypatch.setattr(routes, "load_station_settings", lambda *_args: {})
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
    assert 'id="export-png"' in response.text
    assert 'name="header_font_name"' in response.text
    assert 'name="hour_font_name"' in response.text
    assert 'name="show_destination_legend"' in response.text


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
    assert display_settings["header"]["fill"] == "405060"
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
