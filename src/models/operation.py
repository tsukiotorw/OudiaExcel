from dataclasses import dataclass, field
from enum import IntEnum


class OperationType(IntEnum):
    """作業種別(EBOperation/EAOperation 共通)。"""

    SHUNT = 0
    """入換。番線間の移動を伴う作業。"""

    CONNECT = 1
    """増結。他編成と連結する作業。"""

    RELEASE = 2
    """解結。編成の一部を切り離す作業。"""

    OUT_IN = 3
    """出区/入区。Before側では出区、After側では入区を表す。"""

    OUTER = 4
    """路線外始発/終着。Before側では路線外始発、After側では路線外終着を表す。"""

    JUNCTION = 5
    """前列車接続/後続列車接続。前後の列車情報を引き継ぐ作業。"""

    NUMBER_CHANGE = 6
    """運用番号変更。編成はそのままに、運用番号のみを変更する作業。"""


@dataclass(slots=True)
class ShuntDetail:
    """
    入換の詳細情報。

    linked_track_index:
        Operationの Param1 に記録されている番線Index。
        この値単独では「入換前番線」「入換後番線」は確定しない。
        OperationRecord.is_before との組み合わせでは、
        - Before側 (is_before=True):
            linked_track_index = 入換前番線(移動元)
        - After側 (is_before=False):
            linked_track_index = 入換後番線(移動先)
        実際の入換前番線・入換後番線を確定する場合は、
        対応する EkiJikoku の番線Indexと組み合わせて解釈する。
    """

    linked_track_index: int
    departure_time: str | None
    arrival_time: str | None
    show_arrival: bool


@dataclass(slots=True)
class ConnectDetail:
    """増結の詳細情報。"""

    connect_position: int
    connect_time: str | None


@dataclass(slots=True)
class ReleaseDetail:
    """解結の詳細情報。"""

    release_position: int
    release_count: int
    release_time: str | None


@dataclass(slots=True)
class OutInDetail:
    """出区/入区の詳細情報。"""

    time: str | None
    train_number: str | None


@dataclass(slots=True)
class OuterDetail:
    """路線外始発/終着の詳細情報。"""

    outer_station_index: int
    departure_time: str | None
    arrival_time: str | None
    train_number: str | None


@dataclass(slots=True)
class JunctionDetail:
    """前後列車接続の詳細情報。"""

    time: str | None
    value: str | None


@dataclass(slots=True)
class NumberChangeDetail:
    """運用番号変更の詳細情報。"""

    train_number: str


OperationDetail = (
    ShuntDetail
    | ConnectDetail
    | ReleaseDetail
    | OutInDetail
    | OuterDetail
    | JunctionDetail
    | NumberChangeDetail
)


@dataclass(slots=True)
class Operation:
    """1件の作業。増解結時は再帰的に子作業列を持つ。"""

    type: OperationType
    detail: OperationDetail
    before_children: list["Operation"] = field(default_factory=list)
    after_children: list["Operation"] = field(default_factory=list)


@dataclass(slots=True)
class OperationRecord:
    """特定の駅Order・Before/Afterに紐づく作業列。"""

    order: int
    is_before: bool
    operations: list[Operation]
