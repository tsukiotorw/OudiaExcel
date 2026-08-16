import re

from src.models.operation import (
    ConnectDetail,
    JunctionDetail,
    NumberChangeDetail,
    Operation,
    OperationDetail,
    OperationRecord,
    OperationType,
    OuterDetail,
    OutInDetail,
    ReleaseDetail,
    ShuntDetail,
)

_OPERATION_KEY_PATTERN = re.compile(
    r"^Operation(?P<order>\d+)(?P<position>[BA])(?P<path>(?:\.\d+[BA])+)?$"
)
_PATH_STEP_PATTERN = re.compile(r"\.(?P<index>\d+)(?P<position>[BA])")


class OperationParserError(Exception):
    """OperationParser層の例外"""


class OperationParser:
    """
    Ressyaセクションの Operation キー群を解析する。
    """

    def parse(
        self,
        tokens: list[tuple[str, str]],
    ) -> list[OperationRecord]:
        """
        Operationキーのトークン列からOperationRecordのリストを生成する。

        Args:
            tokens:
                (key, value) のタプルのリスト。
                例: [("Operation41B", "2/1$1/618"), ("Operation41B.0A", "5/$0")]

        Returns:
            order, is_before順にソートされたOperationRecordのリスト

        Raises:
            OperationParserError:
                不正なフォーマットの場合
        """
        roots: dict[tuple[int, str], list[Operation]] = {}
        nested: list[tuple[int, str, str, list[Operation]]] = []

        for key, value in tokens:
            match = _OPERATION_KEY_PATTERN.match(key)

            if match is None:
                raise OperationParserError(
                    f"不正なOperationキー形式です: {key}"
                )

            order = int(match.group("order"))
            position = match.group("position")
            path = match.group("path") or ""

            operations = self._parse_operation_list(value)

            if path == "":
                roots[(order, position)] = operations
            else:
                nested.append((order, position, path, operations))

        # パスが浅い順(親→子)に処理し、常に親が先に構築された状態にする。
        nested.sort(key=lambda item: item[2].count("."))

        for order, position, path, operations in nested:
            root = roots.get((order, position))

            if root is None:
                raise OperationParserError(
                    f"Operation{order}{position} が見つかりません"
                    f"(ネストキー: Operation{order}{position}{path})"
                )

            self._attach(root, path, operations)

        records = [
            OperationRecord(
                order=order,
                is_before=(position == "B"),
                operations=operations,
            )
            for (order, position), operations in roots.items()
        ]

        return sorted(
            records,
            key=lambda record: (record.order, not record.is_before),
        )

    def _attach(
        self,
        current: list[Operation],
        path: str,
        operations: list[Operation],
    ) -> None:
        """
        パスに従って階層をたどり、末端の作業に子作業列をセットする。
        """
        steps = _PATH_STEP_PATTERN.findall(path)
        target = current

        for index_str, position in steps[:-1]:
            index = int(index_str)

            if index >= len(target):
                raise OperationParserError(
                    f"ネストキーのIndexが不正です: .{index_str}{position}"
                )

            operation = target[index]
            target = (
                operation.before_children
                if position == "B"
                else operation.after_children
            )

        last_index_str, last_position = steps[-1]
        last_index = int(last_index_str)

        if last_index >= len(target):
            raise OperationParserError(
                f"ネストキーのIndexが不正です: .{last_index_str}{last_position}"
            )

        operation = target[last_index]

        if last_position == "B":
            operation.before_children = operations
        else:
            operation.after_children = operations

    def _parse_operation_list(self, value: str) -> list[Operation]:
        """
        カンマ区切りの作業列を解析する。
        """
        return [self._parse_operation(raw) for raw in value.split(",")]

    def _parse_operation(self, raw: str) -> Operation:
        """
        1件分の作業文字列を解析する。
        """
        type_str, _, rest = raw.partition("/")

        try:
            operation_type = OperationType(int(type_str))
        except ValueError as error:
            raise OperationParserError(
                f"不正な作業種別です: {raw}"
            ) from error

        param1, has_dollar, sub_params = rest.partition("$")

        detail = self._parse_detail(
            operation_type,
            param1,
            sub_params if has_dollar else None,
        )

        return Operation(type=operation_type, detail=detail)

    def _parse_detail(
        self,
        operation_type: OperationType,
        param1: str,
        sub_params: str | None,
    ) -> OperationDetail:
        """
        作業種別ごとに詳細情報を解析する。
        """
        match operation_type:

            case OperationType.SHUNT:
                departure, arrival, flag = self._split_shunt(sub_params)
                return ShuntDetail(
                    linked_track_index=int(param1),
                    departure_time=departure,
                    arrival_time=arrival,
                    show_arrival=(flag == "1"),
                )

            case OperationType.CONNECT:
                return ConnectDetail(
                    connect_position=int(param1),
                    connect_time=sub_params or None,
                )

            case OperationType.RELEASE:
                count, time = self._split_release(sub_params)
                return ReleaseDetail(
                    release_position=int(param1),
                    release_count=int(count),
                    release_time=time,
                )

            case OperationType.OUT_IN:
                return OutInDetail(
                    time=param1 or None,
                    train_number=self._split_out_in(sub_params),
                )

            case OperationType.OUTER:
                (
                    departure,
                    arrival,
                    train_number,
                ) = self._split_outer(sub_params)
                return OuterDetail(
                    outer_station_index=int(param1),
                    departure_time=departure,
                    arrival_time=arrival,
                    train_number=train_number,
                )

            case OperationType.JUNCTION:
                return JunctionDetail(
                    time=param1 or None,
                    value=sub_params or None,
                )

            case OperationType.NUMBER_CHANGE:
                return NumberChangeDetail(train_number=param1)

            case _:
                raise OperationParserError(
                    f"未対応の作業種別です: {operation_type}"
                )

    @staticmethod
    def _split_shunt(
        sub_params: str | None,
    ) -> tuple[str | None, str | None, str | None]:
        """
        入換のSubParamsを分解する。
        形式:
            {発時刻}/{着時刻}${着時刻表示フラグ}
        例:
            531/540$0
        """
        if sub_params is None:
            return (None, None, None)

        time_part, _, flag = sub_params.partition("$")
        departure, _, arrival = time_part.partition("/")

        return (departure or None, arrival or None, flag or None)

    @staticmethod
    def _split_release(
        sub_params: str | None,
    ) -> tuple[str, str | None]:
        """
        解結のSubParamsを分解する。
        形式:
            {編成数}/{解結時刻}
        """
        if sub_params is None:
            return ("0", None)

        count, _, time = sub_params.partition("/")

        return (count, time or None)

    @staticmethod
    def _split_out_in(
        sub_params: str | None,
    ) -> str | None:
        """
        出区/入区のSubParamsから運用番号を取り出す。
        形式:
            {連携コード}/{運用番号}
        """
        if sub_params is None:
            return None

        _, _, train_number = sub_params.partition("/")

        return train_number or None

    @staticmethod
    def _split_outer(
        sub_params: str | None,
    ) -> tuple[str | None, str | None, str | None]:
        """
        路線外始発/終着のSubParamsを分解する。
        形式:
            {発車時刻}/{当駅着時刻}${連携コード}/{運用番号}
        """
        if sub_params is None:
            return (None, None, None)

        time_part, _, code_part = sub_params.partition("$")
        departure, _, arrival = time_part.partition("/")
        _, _, train_number = code_part.partition("/")

        return (departure or None, arrival or None, train_number or None)
