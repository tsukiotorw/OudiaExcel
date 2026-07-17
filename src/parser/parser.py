from __future__ import annotations

from src.models.railway import Railway
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

        return Railway(
            name = self._get_required_value(section, "Name"),
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
