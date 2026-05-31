"""Layout-aware PDF text extraction with reading order."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber

HEADER_FOOTER_MARGIN = 0.08
HEADING_SIZE_RATIO = 1.15


@dataclass
class TextBlock:
    text: str
    page: int
    bbox: tuple[float, float, float, float]
    kind: str = "text"
    level: int | None = None
    confidence: float = 0.9


@dataclass
class LayoutDocument:
    blocks: list[TextBlock] = field(default_factory=list)
    page_count: int = 0
    ocr_pages: list[int] = field(default_factory=list)


def _is_header_footer(block: TextBlock, page_height: float) -> bool:
    _, y0, _, y1 = block.bbox
    top = page_height * HEADER_FOOTER_MARGIN
    bottom = page_height * (1 - HEADER_FOOTER_MARGIN)
    center_y = (y0 + y1) / 2
    if center_y < top or center_y > bottom:
        if re.match(r"^\s*\d+\s*$", block.text.strip()):
            return True
        if len(block.text.strip()) < 80 and re.search(
            r"(page|chapter|©|copyright|\d{4})", block.text, re.I
        ):
            return True
    return False


def _detect_heading(block: TextBlock, median_size: float) -> TextBlock:
    text = block.text.strip()
    if not text or len(text) > 200:
        return block
    if re.match(r"^#{1,6}\s", text):
        level = len(re.match(r"^(#+)", text).group(1))  # type: ignore[union-attr]
        block.kind = "heading"
        block.level = level
        block.text = re.sub(r"^#+\s*", "", text)
        return block
    if text.isupper() and len(text.split()) <= 12:
        block.kind = "heading"
        block.level = 2
        return block
  # Heuristic: short lines at larger font (approximated by bbox height)
    height = block.bbox[3] - block.bbox[1]
    if height > median_size * HEADING_SIZE_RATIO and len(text.split()) <= 14:
        block.kind = "heading"
        block.level = min(3, max(1, int(height / max(median_size, 1))))
    return block


def _detect_code_block(block: TextBlock) -> TextBlock:
    lines = block.text.split("\n")
    if len(lines) >= 2:
        indented = sum(1 for ln in lines if ln.startswith("    ") or ln.startswith("\t"))
        if indented / len(lines) > 0.6:
            block.kind = "code"
            block.confidence = 0.75
    if re.match(r"^(def |class |import |function |const |let |var )", block.text):
        block.kind = "code"
    return block


def extract_layout(pdf_path: Path, ocr_text_by_page: dict[int, str] | None = None) -> LayoutDocument:
    doc = LayoutDocument()
    ocr_text_by_page = ocr_text_by_page or {}

    with pdfplumber.open(pdf_path) as pdf:
        doc.page_count = len(pdf.pages)
        for page_idx, page in enumerate(pdf.pages, start=1):
            page_height = float(page.height or 792)
            if page_idx in ocr_text_by_page:
                doc.ocr_pages.append(page_idx)
                for para in ocr_text_by_page[page_idx].split("\n\n"):
                    para = para.strip()
                    if para:
                        doc.blocks.append(
                            TextBlock(
                                text=para,
                                page=page_idx,
                                bbox=(0, 0, float(page.width or 612), page_height),
                                confidence=0.85,
                            )
                        )
                continue

            words = page.extract_words(use_text_flow=True, keep_blank_chars=False)
            if not words:
                chars = page.chars
                if not chars:
                    continue
                median_size = sorted(
                    (c.get("size") or 10 for c in chars), key=lambda x: x
                )[len(chars) // 2]
            else:
                median_size = 10

            lines: list[TextBlock] = []
            if words:
                current_line: list[dict] = []
                last_top = None
                for w in sorted(words, key=lambda x: (round(x["top"], 1), x["x0"])):
                    if last_top is not None and abs(w["top"] - last_top) > 4:
                        if current_line:
                            text = " ".join(x["text"] for x in current_line)
                            x0 = min(x["x0"] for x in current_line)
                            x1 = max(x["x1"] for x in current_line)
                            top = min(x["top"] for x in current_line)
                            bottom = max(x["bottom"] for x in current_line)
                            lines.append(
                                TextBlock(
                                    text=text,
                                    page=page_idx,
                                    bbox=(x0, top, x1, bottom),
                                )
                            )
                            current_line = []
                    current_line.append(w)
                    last_top = w["top"]
                if current_line:
                    text = " ".join(x["text"] for x in current_line)
                    x0 = min(x["x0"] for x in current_line)
                    x1 = max(x["x1"] for x in current_line)
                    top = min(x["top"] for x in current_line)
                    bottom = max(x["bottom"] for x in current_line)
                    lines.append(
                        TextBlock(text=text, page=page_idx, bbox=(x0, top, x1, bottom))
                    )
            else:
                text = page.extract_text() or ""
                for line in text.split("\n"):
                    line = line.strip()
                    if line:
                        lines.append(
                            TextBlock(
                                text=line,
                                page=page_idx,
                                bbox=(0, 0, float(page.width or 612), page_height),
                            )
                        )

            if chars := page.chars:
                median_size = sorted((c.get("size") or 10 for c in chars), key=lambda x: x)[
                    len(chars) // 2
                ]

            for block in lines:
                if _is_header_footer(block, page_height):
                    continue
                block = _detect_heading(block, median_size)
                block = _detect_code_block(block)
                doc.blocks.append(block)

    doc.blocks.sort(key=lambda b: (b.page, b.bbox[1], b.bbox[0]))
    return doc
