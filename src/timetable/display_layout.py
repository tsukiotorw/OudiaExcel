from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from types import MappingProxyType
from typing import Mapping, TypeAlias

from src.models.timetable import TimetableEntry, TimetableHour
from src.timetable.display_config import TimetableDisplayConfig


EntryRow = list[str]
EntryLayout = list[EntryRow]
EntryLayoutPattern: TypeAlias = tuple[tuple[str, ...], ...]
LayoutKey: TypeAlias = tuple[str, str, str, bool, bool]


COMMON_ENTRY_LAYOUT_PATTERNS: Mapping[str, EntryLayoutPattern] = (
    MappingProxyType({
        "P1": ((), ("minute",)),
        "P2": (("train_type",), ("minute",)),
        "P3": (("destination",), ("minute",)),
        "P4": (("destination", "train_type"), ("minute",)),
        "P5": (("train_type", "destination"), ("minute",)),
        "P6": ((), ("minute",), ("train_type",)),
        "P7": (("destination",), ("minute",), ("train_type",)),
        "P8": ((), ("minute",), ("destination",)),
        "P9": (("train_type",), ("minute",), ("destination",)),
        "P10": ((), ("destination", "train_type"), ("minute",)),
        "P11": ((), ("train_type", "destination"), ("minute",)),
    })
)


def _pattern_id_for_key(key: LayoutKey) -> str:
    (
        destination_position,
        train_type_position,
        metadata_order,
        show_destination,
        show_train_type,
    ) = key
    destination_position = (
        destination_position
        if destination_position in {"top", "bottom"}
        else "top"
    )
    train_type_position = (
        train_type_position
        if train_type_position in {"top", "bottom"}
        else "top"
    )
    if show_destination and show_train_type:
        if destination_position == train_type_position:
            order = (
                ("destination", "train_type")
                if metadata_order == "destination_first"
                else ("train_type", "destination")
            )
            if destination_position == "top":
                return "P4" if order[0] == "destination" else "P5"
            return "P10" if order[0] == "destination" else "P11"
        if destination_position == "top":
            return "P7"
        return "P9"
    if show_destination:
        return "P3" if destination_position == "top" else "P8"
    if show_train_type:
        return "P2" if train_type_position == "top" else "P6"
    return "P1"


ENTRY_LAYOUT_PATTERN_IDS: Mapping[LayoutKey, str] = MappingProxyType({
    (
        destination_position,
        train_type_position,
        metadata_order,
        show_destination,
        show_train_type,
    ): _pattern_id_for_key((
        destination_position,
        train_type_position,
        metadata_order,
        show_destination,
        show_train_type,
    ))
    for destination_position, train_type_position, metadata_order,
    show_destination, show_train_type in product(
        ("top", "bottom"),
        ("top", "bottom"),
        ("destination_first", "train_type_first"),
        (False, True),
        (False, True),
    )
})


def get_common_entry_layout(
    config: TimetableDisplayConfig,
    show_destination: bool,
    show_train_type: bool,
) -> tuple[str, EntryLayout]:
    """Return the shared pattern ID and a mutable layout copy."""
    key = (
        config.destination_position,
        config.train_type_position,
        config.metadata_order,
        show_destination,
        show_train_type,
    )
    normalized_key = (
        key[0] if key[0] in {"top", "bottom"} else "top",
        key[1] if key[1] in {"top", "bottom"} else "top",
        (
            key[2]
            if key[2] in {"destination_first", "train_type_first"}
            else "train_type_first"
        ),
        key[3],
        key[4],
    )
    pattern_id = ENTRY_LAYOUT_PATTERN_IDS[normalized_key]
    layout = [list(row) for row in COMMON_ENTRY_LAYOUT_PATTERNS[pattern_id]]
    return pattern_id, layout


@dataclass(frozen=True)
class HourSlot:
    hour: int
    down_entries: list[TimetableEntry]
    up_entries: list[TimetableEntry]
    down_present: bool
    up_present: bool


def get_entry_layout(
    entry: TimetableEntry,
    config: TimetableDisplayConfig,
) -> EntryLayout:
    """列車欄の項目名を表示行へ割り当てる。"""
    visible: dict[str, bool] = {
        "destination": (
            config.show_destination
            and not entry.destination.is_no_mark
            and bool(entry.destination.display_name)
        ),
        "train_type": (
            config.train_type_column_visible.get(
                entry.train_type.index,
                True,
            )
            and bool(
                entry.train_type.short_name
                if (
                    config.use_train_type_short_name
                    and entry.train_type.short_name
                )
                else entry.train_type.name
            )
        ),
    }

    fields = [name for name, is_visible in visible.items() if is_visible]
    if not fields:
        return [[], ["minute"]]

    positions = {
        "destination": (
            config.destination_position
            if config.destination_position in {"top", "bottom"}
            else "top"
        ),
        "train_type": (
            config.train_type_position
            if config.train_type_position in {"top", "bottom"}
            else "top"
        ),
    }

    if len(fields) == 1:
        field = fields[0]
        if positions[field] == "top":
            return [[field], ["minute"]]
        return [[], ["minute"], [field]]

    if positions["destination"] == positions["train_type"]:
        ordered = (
            ["destination", "train_type"]
            if config.metadata_order == "destination_first"
            else ["train_type", "destination"]
        )
        if positions["destination"] == "top":
            return [ordered, ["minute"]]
        return [[], ordered, ["minute"]]

    top_field = (
        "destination"
        if positions["destination"] == "top"
        else "train_type"
    )
    bottom_field = (
        "train_type"
        if top_field == "destination"
        else "destination"
    )
    return [[top_field], ["minute"], [bottom_field]]


def merge_timetable_hours(
    down: list[TimetableHour],
    up: list[TimetableHour],
) -> list[HourSlot]:
    """上下方向の時刻を重複なく統合し、同じ時刻の列車をまとめる。"""
    grouped: dict[
        int,
        tuple[
            list[TimetableEntry],
            list[TimetableEntry],
            bool,
            bool,
        ],
    ] = {}

    for direction_index, hours in enumerate((down, up)):
        for hour in hours:
            if hour.hour not in grouped:
                grouped[hour.hour] = ([], [], False, False)
            entries = grouped[hour.hour][direction_index]
            entries.extend(hour.entries)
            presence = list(grouped[hour.hour][2:])
            presence[direction_index] = True
            grouped[hour.hour] = (
                grouped[hour.hour][0],
                grouped[hour.hour][1],
                presence[0],
                presence[1],
            )

    ordered_hours = sorted(
        grouped,
        key=lambda hour: (hour - 4) % 24 if 0 <= hour < 24 else hour,
    )
    return [
        HourSlot(
            hour=hour,
            down_entries=grouped[hour][0],
            up_entries=grouped[hour][1],
            down_present=grouped[hour][2],
            up_present=grouped[hour][3],
        )
        for hour in ordered_hours
    ]
