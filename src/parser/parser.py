from __future__ import annotations

from src.models.railway import (
    Diagram,
    Direction,
    Railway,
    Station,
    Train,
)
from src.parser.section import SectionNode


class ParserError(Exception):
    """Parser層の例外"""

    pass


class Parser:
    """
    SectionNodeをドメインモデルへ変換する。
    """

    def parse(self, root: SectionNode) -> Railway:
        """
        SectionNodeからRailwayを生成する。
        """

        if root.name != "Rosen":
            raise ParserError(
                f"{root.line_number}行目: ルートSectionは 'Rosen' である必要があります。"
            )

        return self._parse_railway(root)


    def _parse_railway(self, section: SectionNode) -> Railway:
        """
        Railwayを生成する。
        """

        railway = Railway(
            name = self._get_required_value(section, "Name"),
        )

        for index, child in enumerate(section.children):
            match child.name:
                case "Eki":
                    railway.stations.append(
                        self._parse_station(child, index)
                    )

                case "Dia":
                    railway.diagrams.extend(
                        self._parse_dia(child)
                    )

                case _:
                    raise ParserError(
                        f"{child.line_number}行目: 未対応のSection '{child.name}'"
            )

        return railway

    def _parse_station(
        self,
        section: SectionNode,
        index: int,
    ) -> Station:
        """
        Eki SectionからStationを生成する。
        """

        return Station(
            index=index,
            name=self._get_required_value(section, "Ekimei"),
        )

    def _parse_diagram(
        self,
        section: SectionNode,
    ) -> Diagram:
        """
        Dia SectionからDiagramを生成する。
        """

        return Diagram(
            name=self._get_required_value(section, "Name"),
            direction=Direction(
                self._get_required_value(section, "Direction")
            ),
        )

    def _parse_dia(
        self,
        section: SectionNode,
    ) -> list[Diagram]:
        """
        Diaセクションを解析しDiagram一覧を生成する。
        """

        diagrams: list[Diagram] = []

        name = self._get_required_value(section, "DiaName")

        for child in section.children:
            match child.name:
                case "Kudari":
                    diagram = Diagram(
                        name=name,
                        direction=Direction.DOWN,
                    )

                    self._parse_direction(
                        child,
                        diagram,
                    )

                    diagrams.append(diagram)

                case "Nobori":
                    diagram = Diagram(
                        name=name,
                        direction=Direction.UP,
                    )

                    self._parse_direction(
                        child,
                        diagram,
                    )

                    diagrams.append(diagram)

                case _:
                    raise ParserError(
                        f"{child.line_number}行目: Dia配下に未対応のSection '{child.name}' があります。"
                    )

        return diagrams

    def _parse_direction(
        self,
        section: SectionNode,
        diagram: Diagram,
    ) -> None:
        """
        Kudari/Noboriセクションを解析する。
        """

        for child in section.children:

            match child.name:

                case "Ressya":
                    diagram.trains.append(
                        self._parse_train(child)
                    )

                case _:
                    raise ParserError(
                        f"{child.line_number}行目: "
                        f"未対応のSection '{child.name}'"
                    )

    def _parse_train(
        self,
        section: SectionNode,
    ) -> Train:
        """
        Ressyaセクションを解析しTrainを生成する。
        """

        return Train(
            number="",
            train_type=self._get_required_value(
                section,
                "Syubetsu",
            ),
            stop_times=[],
        )

    def _get_required_value(
        self,
        section: SectionNode,
        key: str,
    ) -> str:
        """
        必須キーを取得する。
        """

        for kv in section.key_values:
            if kv.key == key:
                return kv.value

        raise ParserError(
            f"{section.line_number}行目: 必須キー '{key}' が見つかりません。"
        )

    def _get_optional_value(
        self,
        section: SectionNode,
        key: str,
    ) -> str | None:
        """
        任意キーを取得する。
        """

        for kv in section.key_values:
            if kv.key == key:
                return kv.value

        return None
