"""
調査用CLIツール: OudiaSecondファイルの内容を表示します。

責務:
  - .oud2ファイルを複数の文字コードで試行
  - 最初に成功した文字コードで内容を表示
  - 行番号を付与して全行表示
"""

import argparse
import logging
from pathlib import Path


ENCODINGS = ["utf-8", "utf-8-sig", "shift_jis", "cp932"]


def setup_logger() -> logging.Logger:
    """ロギングを設定します。"""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
    )
    return logging.getLogger(__name__)


def detect_encoding(file_path: Path) -> str | None:
    """
    ファイルの文字コードを判定します。

    試行順序: UTF-8, UTF-8-sig (BOM), Shift_JIS, CP932
    最初の数行を読み込んで判定効率を高めています。

    Args:
        file_path: 調査対象のファイルパス

    Returns:
        成功した文字コード、全て失敗した場合は None
    """
    for encoding in ENCODINGS:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                # 最初の数行を読み込んで判定
                for _ in range(100):
                    line = f.readline()
                    if not line:
                        break
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue

    return None


def main() -> None:
    """エントリーポイント。ファイルを読み込んで表示します。"""
    logger = setup_logger()

    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(
        description="OudiaSecondファイルを調査するCLIツール"
    )
    parser.add_argument(
        "file_path",
        type=Path,
        help="調査対象の.oud2ファイルパス",
    )
    args = parser.parse_args()

    file_path = args.file_path

    # ファイルの存在確認
    if not file_path.exists():
        logger.error(f"ファイルが見つかりません: {file_path}")
        return

    # 文字コード判定
    encoding = detect_encoding(file_path)
    if encoding is None:
        encodings_str = ", ".join(ENCODINGS)
        logger.error(
            f"文字コード判定に失敗しました: {file_path}\n"
            f"試行した文字コード: {encodings_str}"
        )
        return

    # 成功した文字コードを表示
    logger.info(f"文字コード: {encoding}")

    # ファイル内容を行番号付きで表示
    try:
        with open(file_path, "r", encoding=encoding) as f:
            lines = f.readlines()

        print()  # 空行を挿入
        for line_number, line in enumerate(lines, start=1):
            print(f"{line_number:4d}: {line.rstrip()}")

    except OSError as e:
        logger.error(f"ファイル読み込みエラー: {e}")


if __name__ == "__main__":
    main()
