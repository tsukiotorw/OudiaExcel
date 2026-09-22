from pathlib import Path

from src.models.railway import Railway
from src.parser.parser import Parser
from src.parser.reader import read_file
from src.parser.section_builder import build_sections
from src.parser.tokenizer import tokenize


def load_oud2(path: Path) -> Railway:
    """OuDiaSecondファイルを読み込み、Railwayを返す。"""
    source = read_file(path)
    tokens = tokenize(source)
    root = build_sections(tokens)

    return Parser().parse(root)
