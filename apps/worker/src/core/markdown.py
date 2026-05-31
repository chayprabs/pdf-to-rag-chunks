"""Convert layout blocks to Markdown."""

from __future__ import annotations

from .layout import LayoutDocument, TextBlock


def _format_list_item(text: str) -> str:
    text = text.strip()
    if re_match := __import__("re").match(r"^([\u2022\-\*•]|\d+[\.\)])\s*(.+)", text):
        marker, body = re_match.groups()
        if marker[0].isdigit():
            return f"1. {body}"
        return f"- {body}"
    return text


def blocks_to_markdown(doc: LayoutDocument) -> str:
    import re

    parts: list[str] = []
    in_code = False
    code_lines: list[str] = []

    for block in doc.blocks:
        if block.kind == "code":
            if not in_code:
                in_code = True
                code_lines = []
            code_lines.append(block.text)
            continue
        if in_code:
            parts.append("```\n" + "\n".join(code_lines) + "\n```\n")
            in_code = False
            code_lines = []

        text = block.text.strip()
        if not text:
            continue

        if block.kind == "heading" and block.level:
            parts.append("#" * block.level + " " + text + "\n")
        elif re.match(r"^([\u2022\-\*•]|\d+[\.\)])\s", text):
            parts.append(_format_list_item(text) + "\n")
        else:
            parts.append(text + "\n\n")

    if in_code and code_lines:
        parts.append("```\n" + "\n".join(code_lines) + "\n```\n")

    return "\n".join(parts).strip() + "\n"


def block_section_path(blocks: list[TextBlock], index: int) -> list[str]:
    path: list[str] = []
    for i in range(index):
        b = blocks[i]
        if b.kind == "heading" and b.level:
            while path and len(path) >= b.level:
                path.pop()
            if len(path) < b.level:
                path.append(b.text[:80])
            else:
                path[-1] = b.text[:80]
    if blocks[index].kind == "heading":
        return path
    return path or ["Document"]
