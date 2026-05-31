"""Chunking strategies with tiktoken metadata."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass

import tiktoken

from .layout import LayoutDocument, TextBlock
from .markdown import block_section_path

ENCODING = tiktoken.get_encoding("cl100k_base")


@dataclass
class ChunkRecord:
    id: str
    text: str
    kind: str
    level: int | None
    page: int
    bbox: list[float]
    section_path: list[str]
    token_count: int
    language: str | None
    confidence: float


def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))


def make_chunk_id(text: str, page: int) -> str:
    h = hashlib.sha256(f"{page}:{text[:64]}".encode()).hexdigest()[:12]
    return f"chunk-{h}"


def _chunk_id(text: str, page: int) -> str:
    return make_chunk_id(text, page)


def chunk_document(
    doc: LayoutDocument,
    strategy: str = "token_budget",
    token_budget: int = 512,
) -> list[ChunkRecord]:
    blocks = doc.blocks
    if not blocks:
        return []

    if strategy == "by_page":
        return _chunk_by_page(blocks)
    if strategy == "by_heading":
        return _chunk_by_heading(blocks)
    if strategy == "semantic_block":
        return _chunk_semantic(blocks, token_budget)
    if strategy == "citation_aware":
        return _chunk_citation_aware(blocks, token_budget)
    if strategy == "hybrid":
        return _chunk_hybrid(blocks, token_budget)
    return _chunk_token_budget(blocks, token_budget)


def _to_record(
    text: str,
    block: TextBlock,
    section_path: list[str],
    kind: str | None = None,
) -> ChunkRecord:
    return ChunkRecord(
        id=_chunk_id(text, block.page),
        text=text.strip(),
        kind=kind or block.kind,
        level=block.level,
        page=block.page,
        bbox=list(block.bbox),
        section_path=section_path,
        token_count=count_tokens(text),
        language="python" if block.kind == "code" else None,
        confidence=block.confidence,
    )


def _chunk_by_page(blocks: list[TextBlock]) -> list[ChunkRecord]:
    by_page: dict[int, list[TextBlock]] = {}
    for b in blocks:
        by_page.setdefault(b.page, []).append(b)
    chunks: list[ChunkRecord] = []
    for page, page_blocks in sorted(by_page.items()):
        text = "\n\n".join(b.text for b in page_blocks)
        path = block_section_path(blocks, blocks.index(page_blocks[0]))
        chunks.append(_to_record(text, page_blocks[0], path))
    return chunks


def _chunk_by_heading(blocks: list[TextBlock]) -> list[ChunkRecord]:
    chunks: list[ChunkRecord] = []
    current: list[TextBlock] = []
    for i, block in enumerate(blocks):
        if block.kind == "heading" and current:
            text = "\n\n".join(b.text for b in current)
            chunks.append(_to_record(text, current[0], block_section_path(blocks, i - 1)))
            current = [block]
        else:
            current.append(block)
    if current:
        text = "\n\n".join(b.text for b in current)
        chunks.append(
            _to_record(text, current[0], block_section_path(blocks, len(blocks) - 1))
        )
    return chunks


def _chunk_semantic(blocks: list[TextBlock], budget: int) -> list[ChunkRecord]:
    return _chunk_token_budget(blocks, budget, respect_paragraphs=True)


def _chunk_citation_aware(blocks: list[TextBlock], budget: int) -> list[ChunkRecord]:
    import re

    chunks: list[ChunkRecord] = []
    buffer = ""
    anchor = blocks[0] if blocks else None
    for i, block in enumerate(blocks):
        piece = block.text
        if re.search(r"\[\d+\]|\(\w+,\s*\d{4}\)", piece):
            candidate = (buffer + "\n\n" + piece).strip() if buffer else piece
            if count_tokens(candidate) <= budget:
                buffer = candidate
                if not anchor:
                    anchor = block
                continue
        if buffer and anchor:
            chunks.append(_to_record(buffer, anchor, block_section_path(blocks, i)))
        buffer = piece
        anchor = block
    if buffer and anchor:
        chunks.append(_to_record(buffer, anchor, block_section_path(blocks, len(blocks) - 1)))
    return chunks or _chunk_token_budget(blocks, budget)


def _chunk_hybrid(blocks: list[TextBlock], budget: int) -> list[ChunkRecord]:
    heading_chunks = _chunk_by_heading(blocks)
    final: list[ChunkRecord] = []
    for ch in heading_chunks:
        if ch.token_count <= budget:
            final.append(ch)
        else:
            sub_blocks = [
                TextBlock(
                    text=p,
                    page=ch.page,
                    bbox=tuple(ch.bbox),  # type: ignore[arg-type]
                    kind=ch.kind,
                )
                for p in ch.text.split("\n\n")
                if p.strip()
            ]
            final.extend(_chunk_token_budget(sub_blocks, budget))
    return final


def _chunk_token_budget(
    blocks: list[TextBlock],
    budget: int,
    respect_paragraphs: bool = False,
) -> list[ChunkRecord]:
    chunks: list[ChunkRecord] = []
    buffer = ""
    anchor: TextBlock | None = None

    for i, block in enumerate(blocks):
        piece = block.text
        candidate = (buffer + "\n\n" + piece).strip() if buffer else piece
        tokens = count_tokens(candidate)

        if tokens > budget and buffer and anchor:
            chunks.append(_to_record(buffer, anchor, block_section_path(blocks, i)))
            buffer = piece
            anchor = block
        elif tokens > budget:
            words = piece.split()
            sub = ""
            for word in words:
                test = (sub + " " + word).strip()
                if count_tokens(test) > budget and sub:
                    chunks.append(
                        _to_record(sub, block, block_section_path(blocks, i))
                    )
                    sub = word
                else:
                    sub = test
                while sub and count_tokens(sub) > budget:
                    mid = max(1, len(sub) // 2)
                    chunks.append(
                        _to_record(sub[:mid], block, block_section_path(blocks, i))
                    )
                    sub = sub[mid:]
            buffer = sub
            anchor = block
        else:
            buffer = candidate
            anchor = anchor or block

    if buffer and anchor:
        chunks.append(_to_record(buffer, anchor, block_section_path(blocks, len(blocks) - 1)))
    return chunks


def chunks_to_jsonl(chunks: list[ChunkRecord]) -> str:
    lines = []
    for c in chunks:
        lines.append(
            json.dumps(
                {
                    "id": c.id,
                    "text": c.text,
                    "kind": c.kind,
                    "level": c.level,
                    "page": c.page,
                    "bbox": c.bbox,
                    "sectionPath": c.section_path,
                    "tokenCount": c.token_count,
                    "language": c.language,
                    "confidence": c.confidence,
                },
                ensure_ascii=False,
            )
        )
    return "\n".join(lines) + ("\n" if lines else "")
