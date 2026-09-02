from pathlib import Path

import pytest

from src.parser.parser import Parser
from src.parser.reader import read_file
from src.parser.tokenizer import tokenize
from src.parser.section_builder import build_sections
from src.models.railway import Railway


EXAMPLE_FILE = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "解析用.oud2"
)


@pytest.fixture
def parsed_railway() -> Railway:
    """実データの.oud2ファイルを解析したRailwayを返す。"""
    source = read_file(EXAMPLE_FILE)
    tokens = tokenize(source)
    root = build_sections(tokens)

    return Parser().parse(root)
