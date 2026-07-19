from src.models.railway import (
    Station,
    StopTime,
)

from enum import StrEnum

class RecordType(StrEnum):
    """EkiJikokuレコードの種類。"""
    EMPTY = "empty"
    TIME = "time"


def parse_stop_times(
    value: str,
    stations: list[Station],
) -> list[StopTime]:
    """
    EkiJikoku文字列を解析する。

    Args:
        value:
            EkiJikokuの値

        stations:
            Railwayが保持する駅一覧

    Returns:
        StopTimeのリスト

    Raises:
        TimeParserError:
            不正なフォーマットの場合
    """
    records = value.split(",")

    return [
        TimeParser.parse(
            record,
            stations[order],
            order,
        )
        for order, record in enumerate(records)
    ]

class TimeParser:

    @staticmethod
    def parse(
        record: str,
        station: Station,
        order: int,
    ) -> StopTime:
        """
        EkiJikoku の1レコードを解析する。
        """
        return TimeParser._parse_record(
            record=record,
            station=station,
            order=order,
        )


    @staticmethod
    def _detect_record_type(
        record: str,
    ) -> RecordType:
        """
        レコード種別を判定する。
        """

        if record == "":
            return RecordType.EMPTY

        return RecordType.TIME


    @staticmethod
    def _parse_record(
        record: str,
        station: Station,
        order: int,
    ) -> StopTime:
        """
        駅ごとの時刻情報を解析してStopTimeを生成する。
        """
        record_type = TimeParser._detect_record_type(record)

        match record_type:

            case RecordType.EMPTY:
                raise TimeParserError(
                    f"未対応のレコード形式: {record}"
                )

            case RecordType.TIME:
                return TimeParser._parse_time_record(
                    record=record,
                    station=station,
                    order=order,
                )


    @staticmethod
    def _parse_time_record(
        record: str,
        station: Station,
        order: int,
    ) -> StopTime:
        """
        TIME レコードを解析して StopTime を生成する。
        """
        if ";" in record :

            stop_flag, time_info = record.split(";", maxsplit=1)

            is_pass = (stop_flag == "2")

            time_value, track = time_info.split("$", maxsplit=1)

            arrival_time, departure_time = TimeParser._parse_time(time_value)

            if is_pass and arrival_time is None:

                arrival_time = departure_time
                departure_time = None

            return StopTime(
                station=station,
                order=order,
                arrival_time=arrival_time,
                departure_time=departure_time,
                is_pass=is_pass,
                track_index=int(track) if track else None,
            )

        else :
            stop_flag, track = record.split("$", maxsplit=1)

            return StopTime(
                station=station,
                order=order,
                arrival_time=None,
                departure_time=None,
                is_pass=True,
                track_index=int(track)
            )


    @staticmethod
    def _parse_time(
        value: str,
    ) -> tuple[str | None, str | None]:
        """
        OudiaSecondの時刻表現を
        (着時刻, 発時刻)へ変換する。
        """
        if "/" in value:
            arrival, departure = value.split("/", maxsplit=1)
            return (
                arrival or None,
                departure or None,
            )

        return (None, value)


class TimeParserError(Exception):
    """TimeParser層の例外"""

    pass
