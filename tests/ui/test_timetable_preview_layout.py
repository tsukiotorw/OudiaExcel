from types import SimpleNamespace

import pytest

from src.models.station import Station
from src.models.timetable import (
    StationTimetable,
    TimetableEntry,
    TimetableHour,
)
from src.models.train_type import TrainType
from src.timetable.display_config import TimetableDisplayConfig
from src.ui.display_config_dialog import DisplayConfigDialog
from src.ui.timetable_preview import TimetablePreview


class _Canvas:
    def __init__(self) -> None:
        self.text_items: list[tuple[int, float, str]] = []
        self.rectangle_items: list[dict] = []
        self._next_item_id = 0

    def delete(self, _tag: str) -> None:
        pass

    def winfo_width(self) -> int:
        return 1000

    def winfo_height(self) -> int:
        return 1000

    def configure(self, **_kwargs) -> None:
        pass

    def bbox(self, _tag: str):
        return (0, 0, 1, 1)

    def create_rectangle(self, *_args, **kwargs) -> int:
        self._next_item_id += 1
        self.rectangle_items.append(kwargs)
        return self._next_item_id

    def create_text(self, x, _y, **kwargs) -> int:
        self._next_item_id += 1
        self.text_items.append(
            (self._next_item_id, x, kwargs["text"])
        )
        return self._next_item_id


def _timetable() -> StationTimetable:
    train_type = TrainType(0, "快速")

    def entry(direction: str, index: int) -> TimetableEntry:
        return TimetableEntry(
            minute=10 + index,
            destination=Station(
                index=index,
                name=f"{direction} station",
                short_name=direction,
            ),
            train_type=train_type,
            train_number=f"{direction}{index}",
        )

    return StationTimetable(
        station_name="Test",
        down=[TimetableHour(4, [entry("DOWN", 0)])],
        up=[TimetableHour(4, [entry("UP", 0), entry("UP", 1)])],
        train_types=[train_type],
    )


@pytest.mark.parametrize(
    "hour_column_mode",
    ["separate", "center"],
)
def test_draw_places_up_left_and_down_right(
    hour_column_mode: str,
) -> None:
    canvas = _Canvas()
    direction_calls = []
    center_hour_calls = []
    legend_calls = []

    def capture_direction(**kwargs) -> None:
        direction_calls.append(kwargs)

    preview = SimpleNamespace(
        canvas=canvas,
        timetable=_timetable(),
        display_config=TimetableDisplayConfig(
            hour_column_mode=hour_column_mode,
            up_header_text="北行",
            down_header_text="南行",
        ),
        _CELL_WIDTH=TimetablePreview._CELL_WIDTH,
        _HOUR_WIDTH=TimetablePreview._HOUR_WIDTH,
        _CELL_HEIGHT=TimetablePreview._CELL_HEIGHT,
        _HEADER_HEIGHT=TimetablePreview._HEADER_HEIGHT,
        _TITLE_HEIGHT=TimetablePreview._TITLE_HEIGHT,
        _DIRECTION_GAP=TimetablePreview._DIRECTION_GAP,
        _draw_title=lambda **_kwargs: None,
        _draw_direction=capture_direction,
        _draw_center_hour_column=lambda **kwargs: (
            center_hour_calls.append(kwargs)
        ),
        _hour_row_count=lambda _slot: 2,
        _get_legend_layout=lambda down_width, up_width: (
            [["down"]],
            [["up"]],
            20,
            20,
        ),
        _draw_legend=lambda **kwargs: legend_calls.append(kwargs),
    )

    TimetablePreview._draw(preview)

    up_call, down_call = direction_calls
    up_left_width = 2 * TimetablePreview._CELL_WIDTH
    down_width = TimetablePreview._CELL_WIDTH
    up_direction_width = up_left_width + (
        TimetablePreview._HOUR_WIDTH
        if hour_column_mode == "separate"
        else 0
    )
    down_direction_width = down_width + (
        TimetablePreview._HOUR_WIDTH
        if hour_column_mode == "separate"
        else 0
    )
    total_width = up_direction_width + down_direction_width + (
        TimetablePreview._HOUR_WIDTH
        if hour_column_mode == "center"
        else TimetablePreview._DIRECTION_GAP
    )
    x0 = (1000 - total_width) / 2
    expected_down_x = up_direction_width + (
        TimetablePreview._HOUR_WIDTH
        if hour_column_mode == "center"
        else TimetablePreview._DIRECTION_GAP
    )

    assert (up_call["direction"], up_call["x"]) == ("up", x0)
    assert up_call["title"] == "北行"
    assert up_call["width"] == up_direction_width
    assert down_call["direction"] == "down"
    assert down_call["x"] == x0 + expected_down_x
    assert down_call["title"] == "南行"
    assert down_call["width"] == down_direction_width
    assert up_call["slots"][0].up_entries == preview.timetable.up[0].entries
    assert down_call["slots"][0].down_entries == preview.timetable.down[0].entries

    if hour_column_mode == "separate":
        assert center_hour_calls == []
    else:
        assert center_hour_calls[0]["x"] == x0 + up_left_width

    assert legend_calls[0]["up_width"] == up_call["width"]
    assert legend_calls[0]["down_width"] == down_call["width"]


@pytest.mark.parametrize("central_hour_column", [False, True])
def test_draw_legend_places_up_items_left_and_down_items_right(
    central_hour_column: bool,
) -> None:
    canvas = _Canvas()
    preview = SimpleNamespace(
        canvas=canvas,
        display_config=TimetableDisplayConfig(),
        _HOUR_WIDTH=TimetablePreview._HOUR_WIDTH,
        _DIRECTION_GAP=TimetablePreview._DIRECTION_GAP,
        _get_legend_layout=lambda _down_width, _up_width: (
            [[("DOWN_ITEM", "000000")]],
            [[("UP_ITEM", "000000")]],
            20,
            20,
        ),
        _draw_border=lambda *_args: None,
        _to_tk_color=lambda color: color,
    )

    TimetablePreview._draw_legend(
        preview,
        x=100,
        y=200,
        down_width=80,
        up_width=120,
        central_hour_column=central_hour_column,
    )

    text_positions = {
        text: x
        for _, x, text in canvas.text_items
        if text in {"UP_ITEM", "DOWN_ITEM"}
    }

    assert text_positions["UP_ITEM"] < text_positions["DOWN_ITEM"]
    assert text_positions["UP_ITEM"] == 128
    assert text_positions["DOWN_ITEM"] == 100 + 120 + (
        TimetablePreview._HOUR_WIDTH
        if central_hour_column
        else TimetablePreview._DIRECTION_GAP
    ) + 28


def test_apply_header_settings_saves_custom_text_and_allows_blank() -> None:
    config = TimetableDisplayConfig()
    dialog = SimpleNamespace(
        display_config=config,
        up_header_text=SimpleNamespace(get=lambda: "北行"),
        down_header_text=SimpleNamespace(get=lambda: ""),
        header_font_name=SimpleNamespace(get=lambda: config.header_font_name),
        header_font_size=SimpleNamespace(get=lambda: config.header_font_size),
        header_font_color=SimpleNamespace(get=lambda: config.header_font_color),
        header_fill=SimpleNamespace(get=lambda: "D9EAD3"),
        up_header_fill=SimpleNamespace(get=lambda: "CFE2F3"),
        down_header_fill=SimpleNamespace(get=lambda: "FCE5CD"),
    )

    DisplayConfigDialog._apply_header(dialog)

    assert config.up_header_text == "北行"
    assert config.down_header_text == ""
    assert config.header_fill == "D9EAD3"
    assert config.up_header_fill == "CFE2F3"
    assert config.down_header_fill == "FCE5CD"


@pytest.mark.parametrize(
    ("direction", "up_fill", "down_fill", "expected"),
    [
        ("up", "CFE2F3", "FCE5CD", "CFE2F3"),
        ("down", "CFE2F3", "FCE5CD", "FCE5CD"),
        ("up", None, "FCE5CD", "D9EAD3"),
        ("down", "CFE2F3", None, "D9EAD3"),
    ],
)
def test_draw_direction_uses_direction_header_fill(
    direction: str,
    up_fill: str | None,
    down_fill: str | None,
    expected: str,
) -> None:
    canvas = _Canvas()
    preview = SimpleNamespace(
        canvas=canvas,
        display_config=TimetableDisplayConfig(
            header_fill="D9EAD3",
            up_header_fill=up_fill,
            down_header_fill=down_fill,
        ),
        _HEADER_HEIGHT=TimetablePreview._HEADER_HEIGHT,
        _to_tk_color=lambda color: color,
        _draw_border=lambda *_args: None,
    )

    TimetablePreview._draw_direction(
        preview,
        x=0,
        y=0,
        width=100,
        title="direction",
        slots=[],
        direction=direction,
        include_hour_column=False,
        row_counts=[],
    )

    assert canvas.rectangle_items[0]["fill"] == expected
