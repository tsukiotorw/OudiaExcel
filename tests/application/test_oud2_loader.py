from pathlib import Path

from src.application.oud2_loader import load_oud2
from src.models.railway import Railway


EXAMPLE_FILE = Path("examples/解析用.oud2")


def test_load_oud2() -> None:
    railway = load_oud2(EXAMPLE_FILE)

    assert isinstance(railway, Railway)
