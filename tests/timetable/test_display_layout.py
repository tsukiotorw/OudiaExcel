from dataclasses import replace
from itertools import product

from src.application.station_timetable import generate_station_timetable
from src.models.station import Station
from src.models.train_type import TrainType
from src.models.timetable import TimetableHour
from src.timetable.display_config import TimetableDisplayConfig
from src.timetable.display_layout import (
    COMMON_ENTRY_LAYOUT_PATTERNS,
    ENTRY_LAYOUT_PATTERN_IDS,
    get_common_entry_layout,
    get_entry_layout,
    merge_timetable_hours,
)


def test_common_layout_mapping_covers_all_32_combinations(
    parsed_railway,
) -> None:
    timetable = generate_station_timetable(
        parsed_railway,
        parsed_railway.stations[1],
    )
    source = timetable.down[0].entries[0]
    combinations = product(
        ("top", "bottom"),
        ("top", "bottom"),
        ("destination_first", "train_type_first"),
        (False, True),
        (False, True),
    )
    for (
        destination_position,
        train_type_position,
        metadata_order,
        show_dest,
        show_type,
    ) in combinations:
        entry = replace(
            source,
            destination=Station(index=source.destination.index, name="行先"),
            train_type=TrainType(
                index=source.train_type.index,
                name="種別",
                short_name="略",
            ),
        )
        config = TimetableDisplayConfig(
            destination_position=destination_position,
            train_type_position=train_type_position,
            metadata_order=metadata_order,
            show_destination=show_dest,
            use_train_type_short_name=True,
            train_type_column_visible={source.train_type.index: show_type},
        )
        key = (
            destination_position,
            train_type_position,
            metadata_order,
            show_dest,
            show_type,
        )
        pattern_id, layout = get_common_entry_layout(config, show_dest, show_type)

        assert len(ENTRY_LAYOUT_PATTERN_IDS) == 32
        assert pattern_id == ENTRY_LAYOUT_PATTERN_IDS[key]
        expected_pattern = [
            list(row) for row in COMMON_ENTRY_LAYOUT_PATTERNS[pattern_id]
        ]
        assert layout == expected_pattern
        assert layout == get_entry_layout(entry, config)


def test_common_layout_preserves_entry_visibility_rules(parsed_railway) -> None:
    timetable = generate_station_timetable(
        parsed_railway,
        parsed_railway.stations[1],
    )
    source = timetable.down[0].entries[0]
    config = TimetableDisplayConfig(use_train_type_short_name=True)

    cases = [
        (
            Station(source.destination.index, "行先", is_no_mark=True),
            TrainType(source.train_type.index, "種別"),
            False,
            True,
        ),
        (
            Station(source.destination.index, "", short_name=""),
            TrainType(source.train_type.index, "種別"),
            False,
            True,
        ),
        (
            Station(source.destination.index, "行先"),
            TrainType(source.train_type.index, "", short_name=""),
            True,
            False,
        ),
        (
            Station(source.destination.index, "行先"),
            TrainType(source.train_type.index, "正式", short_name="略"),
            True,
            True,
        ),
        (
            Station(source.destination.index, "行先"),
            TrainType(source.train_type.index, "正式", short_name=""),
            True,
            True,
        ),
    ]
    for destination, train_type, expected_destination, expected_type in cases:
        entry = replace(source, destination=destination, train_type=train_type)
        config.show_destination = True
        config.train_type_column_visible = {train_type.index: True}
        config.use_train_type_short_name = True
        pattern_id, layout = get_common_entry_layout(
            config,
            expected_destination,
            expected_type,
        )
        assert layout == get_entry_layout(entry, config)
        assert pattern_id in COMMON_ENTRY_LAYOUT_PATTERNS


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
