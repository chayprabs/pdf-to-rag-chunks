"""End-to-end PDF parse pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

from .chunking import chunk_document
from .images import extract_images
from .layout import extract_layout
from .markdown import blocks_to_markdown
from .ocr import run_ocr
from .tables import extract_tables
from ..storage.job_store import JobStore

logger = logging.getLogger(__name__)


def parse_pdf(
    pdf_path: Path,
    job_id: str,
    sha256: str,
    store: JobStore,
    *,
    ocr_mode: str = "auto",
    ocr_language: str = "eng",
    chunk_strategy: str = "token_budget",
    token_budget: int = 512,
) -> dict:
    ocr_text = run_ocr(pdf_path, language=ocr_language, mode=ocr_mode)
    layout = extract_layout(pdf_path, ocr_text_by_page=ocr_text)
    tables = extract_tables(pdf_path)
    images = extract_images(pdf_path, store.job_dir(job_id))

    markdown = blocks_to_markdown(layout)
    for table in tables:
        from .tables import table_to_markdown

        markdown += f"\n\n## Table on page {table.page}\n\n"
        markdown += table_to_markdown(table) + "\n"

    chunks = chunk_document(layout, strategy=chunk_strategy, token_budget=token_budget)

    headings = sum(1 for b in layout.blocks if b.kind == "heading")
    stats = {
        "headings": headings,
        "tables": len(tables),
        "figures": len(images),
        "chunks": len(chunks),
        "tokens": sum(c.token_count for c in chunks),
        "toc": [
            {"title": b.text[:80], "page": b.page, "level": b.level}
            for b in layout.blocks
            if b.kind == "heading"
        ],
    }

    artifacts = store.save_artifacts(
        job_id=job_id,
        sha256=sha256,
        markdown=markdown,
        chunks=chunks,
        tables=tables,
        page_count=layout.page_count,
        ocr_pages=layout.ocr_pages,
        images=images,
        stats=stats,
    )

    return {
        "jobId": job_id,
        "document": {
            "sha256": sha256,
            "pageCount": layout.page_count,
            "ocrPages": layout.ocr_pages,
        },
        "markdownUrl": f"/v1/jobs/{job_id}/artifacts/document.md",
        "chunksUrl": f"/v1/jobs/{job_id}/artifacts/chunks.jsonl",
        "tables": artifacts.tables,
        "images": artifacts.images,
        "stats": artifacts.stats,
    }
