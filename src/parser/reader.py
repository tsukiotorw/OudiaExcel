"""
Reader層: OudiaSecondファイルを読み込みます。

責務:
    - ファイルを読み込む
    - 文字コードを判定する
    - SourceFileを返す

このモジュールはファイルI/Oのみを担当します。
構文解析・意味解析は行いません。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# 将来的には exceptions.py へ移動予定
class ReaderError(Exception):
    """Reader層で発生する例外。"""


ENCODINGS: tuple[str, ...] = (
    "utf-8-sig",
    "utf-8",
    "cp932",
)


@dataclass(frozen=True)
class SourceFile:
    """
    Readerが返すファイル情報。

    Attributes:
        path:
            読み込んだファイルパス
        encoding:
            判定された文字コード
        lines:
            読み込んだ全行
    """

    path: Path
    encoding: str
    lines: list[str]


def read_file(file_path: Path) -> SourceFile:
    """
    OudiaSecondファイルを読み込みます。

    UTF-8 BOM付き、UTF-8、CP932 の順で文字コードを判定します。

    Args:
        file_path:
            読み込む .oud2 ファイル

    Returns:
        SourceFile

    Raises:
        ReaderError:
            ファイルが存在しない、
            読み込めない、
            または文字コード判定に失敗した場合。
    """

    if not file_path.exists():
        raise ReaderError(f"ファイルが見つかりません: {file_path}")

    if not file_path.is_file():
        raise ReaderError(f"ファイルではありません: {file_path}")

    for encoding in ENCODINGS:
        try:
            with file_path.open(
                mode="r",
                encoding=encoding,
            ) as file:
                lines = file.readlines()

            return SourceFile(
                path=file_path,
                encoding=encoding,
                lines=lines,
            )

        except UnicodeDecodeError:
            continue

        except OSError as exc:
            raise ReaderError(
                f"ファイルの読み込みに失敗しました: {file_path}"
            ) from exc

    raise ReaderError(
        "文字コードを判定できませんでした。"
        f" 対象ファイル: {file_path}"
        f" 試行した文字コード: {', '.join(ENCODINGS)}"
    )
