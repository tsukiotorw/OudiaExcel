from __future__ import annotations

from .section import SectionNode
from .tokens import (
    KeyValueToken,
    SectionEndToken,
    SectionStartToken,
    Token,
)


class SectionBuilderError(Exception):
    """SectionBuilder層の例外"""


def build_sections(tokens: list[Token]) -> SectionNode:
    """
    Token列からSectionツリーを構築します。
    """

    stack: list[SectionNode] = []

    root: SectionNode | None = None

    for token in tokens:

        if isinstance(token, SectionStartToken):

            node = SectionNode(
                line_number=token.line_number,
                name=token.name,
            )

            if stack:
                stack[-1].children.append(node)
            else:
                root = node

            stack.append(node)

        elif isinstance(token, KeyValueToken):

            if not stack:
                raise SectionBuilderError(
                    f"{token.line_number}行目: Section外にKeyValueがあります。"
                )

            stack[-1].key_values.append(token)

        elif isinstance(token, SectionEndToken):

            if not stack:
                raise SectionBuilderError(
                    f"{token.line_number}行目: Section開始前に終了しました。"
                )

            stack.pop()

    if stack:
        raise SectionBuilderError("Sectionが閉じられていません。")

    if root is None:
        raise SectionBuilderError("Sectionが存在しません。")

    return root
