"""End-to-end PDF parse pipeline."""

from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .chunking import ChunkRecord, chunk_document, chunks_from_tables
from .images import extract_images
from .layout import extract_layout
from .markdown import blocks_to_markdown
from .ocr import ocr_confidence_by_page, run_ocr
from .tables import extract_tables, table_to_markdown
from ..config import settings
from ..storage.job_store import JobStore

logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=2)


def _parse_sync(
    pdf_path: Path,
    job_id: str,
    sha256: str,
    store: JobStore,
    *,
    ocr_mode: str,
    ocr_language: str,
    chunk_strategy: str,
    token_budget: int,
) -> dict:
    ocr_text = run_ocr(pdf_path, language=ocr_language, mode=ocr_mode)
    ocr_conf = ocr_confidence_by_page(ocr_text)
    layout = extract_layout(pdf_path, ocr_text_by_page=ocr_text)
    tables = extract_tables(pdf_path)
    images = extract_images(pdf_path, store.job_dir(job_id))

    markdown = blocks_to_markdown(layout)
    for table in tables:
        markdown += f"\n\n## Table on page {table.page}\n\n"
        markdown += table_to_markdown(table) + "\n"

    text_chunks = chunk_document(layout, strategy=chunk_strategy, token_budget=token_budget)
    chunks = text_chunks + chunks_from_tables(tables)

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
        "ocrConfidence": ocr_conf,
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
        layout_blocks=layout.blocks,
    )

    base = f"/v1/jobs/{job_id}/artifacts"
    return {
        "jobId": job_id,
        "document": {
            "sha256": sha256,
            "pageCount": layout.page_count,
            "ocrPages": layout.ocr_pages,
        },
        "markdownUrl": f"{base}/document.md",
        "chunksUrl": f"{base}/chunks.jsonl",
        "manifestUrl": f"{base}/manifest.json",
        "tablesZipUrl": f"{base}/tables.zip",
        "imagesZipUrl": f"{base}/images.zip",
        "tables": artifacts.tables,
        "images": [
            {
                "id": img["id"],
                "page": img["page"],
                "url": img.get("url", ""),
                "caption": img.get("caption"),
                "altText": img.get("altText"),
            }
            for img in artifacts.images
        ],
        "stats": artifacts.stats,
        "engine": settings.engine,
    }


async def parse_pdf(
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
    loop = asyncio.get_event_loop()
    return await asyncio.wait_for(
        loop.run_in_executor(
            _executor,
            lambda: _parse_sync(
                pdf_path,
                job_id,
                sha256,
                store,
                ocr_mode=ocr_mode,
                ocr_language=ocr_language,
                chunk_strategy=chunk_strategy,
                token_budget=token_budget,
            ),
        ),
        timeout=settings.parse_timeout_seconds,
    )
