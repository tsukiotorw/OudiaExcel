from __future__ import annotations

from src.models.railway import (
    Diagram,
    Direction,
    Railway,
    Station,
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
                    diagrams.append(
                        Diagram(
                            name=name,
                            direction=Direction.DOWN,
                        )
                    )

                case "Nobori":
                    diagrams.append(
                        Diagram(
                            name=name,
                            direction=Direction.UP,
                        )
                    )

                case _:
                    raise ParserError(
                        f"{child.line_number}行目: Dia配下に未対応のSection '{child.name}' があります。"
                    )

        return diagrams


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
