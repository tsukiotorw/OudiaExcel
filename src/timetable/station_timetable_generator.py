from __future__ import annotations

from src.models.railway import Direction, Railway
from src.models.station import Station
from src.models.stop_time import StopTime
from src.models.timetable import (
    StationTimetable,
    TimetableEntry,
    TimetableHour,
)
from src.models.train import Train


class StationTimetableGenerator:
    """Railwayから指定駅の駅時刻表を生成する。"""

    def __init__(self, railway: Railway) -> None:
        self.railway = railway

    def generate(self, station: Station) -> StationTimetable:
        """
        指定駅の駅時刻表を生成する。

        Args:
            station:
                時刻表を作成する駅。

        Returns:
            指定駅の駅時刻表。
        """
        down = self._generate_direction(
            station=station,
            direction=Direction.DOWN,
        )
        up = self._generate_direction(
            station=station,
            direction=Direction.UP,
        )

        return StationTimetable(
            station_name=station.name,
            down=down,
            up=up,
            train_types=list(self.railway.train_types),
        )


    def _generate_direction(
        self,
        station: Station,
        direction: Direction,
    ) -> list[TimetableHour]:
        """
        指定方向の駅時刻表を生成する。
        """
        entries: list[tuple[int, TimetableEntry]] = []

        for diagram in self.railway.diagrams:
            if diagram.direction != direction:
                continue

            for train in diagram.trains:
                stop_time = self._find_stop_time(
                    train=train,
                    station=station,
                )

                if stop_time is None:
                    continue

                # 通過列車は駅時刻表に掲載しない。
                if stop_time.is_pass:
                    continue

                # 時刻表なので出発時刻を使用する。
                if stop_time.departure_time is None:
                    continue

                hour, minute = self._parse_time(
                    stop_time.departure_time
                )

                destination = self._find_destination(train)

                if destination is None:
                    continue

                train_type = self.railway.train_types[
                    train.train_type_index
                ]

                entries.append(
                    (
                        hour,
                        TimetableEntry(
                            minute=minute,
                            destination=destination.name,
                            train_type=train_type,
                            train_number=train.number,
                        ),
                    )
                )

        entries.sort(
            key=lambda item: (
                self._timetable_order(item[0]),
                item[1].minute,
            )
        )

        return self._group_by_hour(entries)

    @staticmethod
    def _find_stop_time(
        train: Train,
        station: Station,
    ) -> StopTime | None:
        """
        列車の指定駅に対応するStopTimeを取得する。
        """
        for stop_time in train.stop_times:
            if stop_time.station.index == station.index:
                return stop_time

        return None

    @staticmethod
    def _find_destination(
        train: Train,
    ) -> Station | None:
        """
        最後に到着時刻が存在する駅を行先として取得する。

        StopTimeのorderを基準として、arrival_timeが存在する
        最後の駅を行先とする。
        """
        arrival_stops = [
            stop_time
            for stop_time in train.stop_times
            if stop_time.arrival_time is not None
        ]

        if not arrival_stops:
            return None

        return max(
            arrival_stops,
            key=lambda stop_time: stop_time.order,
        ).station

    @staticmethod
    def _parse_time(
        value: str,
    ) -> tuple[int, int]:
        """
        OuDiaSecondの時刻文字列を時・分に変換する。

        Examples:
            "005"  -> (0, 5)
            "023"  -> (0, 23)
            "100"  -> (1, 0)
            "1234" -> (12, 34)
        """
        numeric_value = int(value)

        return (
            numeric_value // 100,
            numeric_value % 100,
        )

    @staticmethod
    def _timetable_order(
        hour: int,
    ) -> int:
        """
        04時始発～03時終電の時刻表上の並び順を返す。

        Examples:
            04時 -> 0
            05時 -> 1
            ...
            23時 -> 19
            00時 -> 20
            01時 -> 21
            02時 -> 22
            03時 -> 23
        """
        return (hour - 4) % 24

    @classmethod
    def _group_by_hour(
        cls,
        entries: list[tuple[int, TimetableEntry]],
    ) -> list[TimetableHour]:
        """時刻表エントリを04時始発～03時終電の24時間にまとめる。"""
        hours: dict[int, list[TimetableEntry]] = {
            hour: []
            for hour in range(24)
        }

        for hour, entry in entries:
            hours[hour].append(entry)

        return [
            TimetableHour(
                hour=hour,
                entries=hours[hour],
            )
            for hour in sorted(
                hours,
                key=cls._timetable_order,
            )
        ]

