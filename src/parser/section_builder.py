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
    Token列からRosen Sectionのツリーを構築します。
    """

    stack: list[SectionNode] = []
    root: SectionNode | None = None
    ignored_depth = 0

    for token in tokens:

        if isinstance(token, SectionStartToken):

            if ignored_depth > 0:
                ignored_depth += 1
                continue

            if not stack and token.name != "Rosen":
                ignored_depth = 1
                continue

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

            if ignored_depth > 0:
                continue

            if not stack:
                continue

            stack[-1].key_values.append(token)

        elif isinstance(token, SectionEndToken):

            if ignored_depth > 0:
                ignored_depth -= 1
                continue

            if not stack:
                raise SectionBuilderError(
                    f"{token.line_number}行目: Section開始前に終了しました。"
                )

            stack.pop()

    if stack:
        raise SectionBuilderError("Sectionが閉じられていません。")

    if root is None:
        raise SectionBuilderError("Rosen Sectionが存在しません。")

    return root

