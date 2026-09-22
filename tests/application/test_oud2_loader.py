from pathlib import Path

from src.application.oud2_loader import load_oud2
from src.models.railway import Railway
from src.models.railway import Direction


EXAMPLE_FILE = Path("examples/解析用.oud2")


def test_load_oud2() -> None:
    railway = load_oud2(EXAMPLE_FILE)

    assert isinstance(railway, Railway)

    assert len(railway.stations) == 4
    assert len(railway.train_types) == 2
    assert len(railway.diagrams) == 2

    assert [station.name for station in railway.stations] == [
        "A",
        "B",
        "C",
        "D",
    ]

    assert [
        (train_type.index, train_type.name, train_type.short_name)
        for train_type in railway.train_types
    ] == [
        (0, "普通", ""),
        (1, "快速", "快"),
    ]

    assert railway.diagrams[0].direction == Direction.DOWN
    assert railway.diagrams[1].direction == Direction.UP

    assert len(railway.diagrams[0].trains) == 10
    assert len(railway.diagrams[1].trains) == 6
