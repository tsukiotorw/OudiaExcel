from enum import StrEnum


class PreviewItem(StrEnum):
    """時刻表プレビュー上の設定対象。"""

    TITLE = "title"
    HEADER = "header"
    HOUR = "hour"
    TRAIN = "train"
    LEGEND = "legend"

