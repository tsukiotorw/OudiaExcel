from src.application.station_timetable import generate_station_timetable
from src.models.timetable import TimetableHour
from src.timetable.display_config import TimetableDisplayConfig
from src.timetable.display_layout import (
    get_entry_layout,
    merge_timetable_hours,
)


def test_entry_layout_supports_independent_positions_and_order(
    parsed_railway,
) -> None:
    timetable = generate_station_timetable(
        parsed_railway,
        parsed_railway.stations[1],
    )
    entry = timetable.down[0].entries[0]

    config = TimetableDisplayConfig()
    assert get_entry_layout(entry, config) == [
        ["destination", "train_type"],
        ["minute"],
    ]

    config.metadata_order = "train_type_first"
    assert get_entry_layout(entry, config) == [
        ["train_type", "destination"],
        ["minute"],
    ]

    config.destination_position = "top"
    config.train_type_position = "bottom"
    assert get_entry_layout(entry, config) == [
        ["destination"],
        ["minute"],
        ["train_type"],
    ]


def test_entry_layout_places_both_bottom_items_on_middle_row(
    parsed_railway,
) -> None:
    timetable = generate_station_timetable(
        parsed_railway,
        parsed_railway.stations[1],
    )
    entry = timetable.down[0].entries[0]
    config = TimetableDisplayConfig(
        destination_position="bottom",
        train_type_position="bottom",
        metadata_order="train_type_first",
    )

    assert get_entry_layout(entry, config) == [
        [],
        ["train_type", "destination"],
        ["minute"],
    ]


def test_entry_layout_keeps_remaining_visible_item_in_configured_position(
    parsed_railway,
) -> None:
    timetable = generate_station_timetable(
        parsed_railway,
        parsed_railway.stations[1],
    )
    entry = timetable.down[0].entries[0]
    config = TimetableDisplayConfig(
        show_destination=False,
        train_type_position="bottom",
    )

    assert get_entry_layout(entry, config) == [
        [],
        ["minute"],
        ["train_type"],
    ]

    config.train_type_column_visible[entry.train_type.index] = False
    config.show_destination = True
    config.destination_position = "top"
    assert get_entry_layout(entry, config) == [
        ["destination"],
        ["minute"],
    ]


def test_entry_font_modes_resolve_independent_and_linked_styles() -> None:
    config = TimetableDisplayConfig(
        destination_font_name="Arial",
        destination_font_size=9,
        destination_font_color="112233",
        train_type_font_name="ＭＳ ゴシック",
        train_type_font_size=11,
        train_type_font_color="445566",
        minute_font_name="Calibri",
        minute_font_size=12,
        minute_font_color="778899",
    )
    index = 3

    assert config.get_entry_font_settings("destination", index) == (
        "Arial",
        9,
        "112233",
    )
    assert config.get_entry_font_settings("train_type", index) == (
        "ＭＳ ゴシック",
        11,
        "445566",
    )
    assert config.get_entry_font_settings("minute", index) == (
        "Calibri",
        12,
        "778899",
    )

    config.destination_font_mode = "train_type"
    config.minute_font_mode = "destination"
    assert config.get_entry_font_settings("destination", index) == (
        "ＭＳ ゴシック",
        11,
        "445566",
    )
    config.destination_font_mode = "independent"
    config.train_type_font_mode = "destination"
    assert config.get_entry_font_settings("train_type", index) == (
        "Arial",
        9,
        "112233",
    )
    assert config.get_entry_font_settings("minute", index) == (
        "Arial",
        9,
        "112233",
    )

    config.train_type_font_mode = "independent"
    config.minute_font_mode = "train_type"
    config.train_type_colors[index] = "00AA00"
    assert config.get_entry_font_settings("minute", index) == (
        "ＭＳ ゴシック",
        11,
        "00AA00",
    )
    assert config.get_entry_font_settings("train_type", index) == (
        "ＭＳ ゴシック",
        11,
        "00AA00",
    )


def test_merge_timetable_hours_unifies_and_orders_asymmetric_hours(
    parsed_railway,
) -> None:
    timetable = generate_station_timetable(
        parsed_railway,
        parsed_railway.stations[1],
    )
    down_entry = timetable.down[0].entries[0]
    up_entry = down_entry

    slots = merge_timetable_hours(
        [
            TimetableHour(hour=4, entries=[down_entry]),
            TimetableHour(hour=7, entries=[]),
        ],
        [
            TimetableHour(hour=5, entries=[up_entry]),
            TimetableHour(hour=7, entries=[up_entry]),
        ],
    )

    assert [slot.hour for slot in slots] == [4, 5, 7]
    assert [slot.down_present for slot in slots] == [True, False, True]
    assert [slot.up_present for slot in slots] == [False, True, True]
    assert slots[0].down_entries == [down_entry]
    assert slots[1].up_entries == [up_entry]
