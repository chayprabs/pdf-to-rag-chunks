import json
import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException

from ..core.chunking import chunk_document, chunks_from_tables, chunks_to_jsonl
from ..core.layout import LayoutDocument, TextBlock
from ..core.tables import extract_tables
from ..storage.job_store import JobStore, validate_job_id
from .validators import validate_chunk_strategy, validate_token_budget

logger = logging.getLogger(__name__)
router = APIRouter(tags=["rechunk"])
store = JobStore()


@router.post("/rechunk")
async def rechunk(
    jobId: Annotated[str, Form()],
    chunkStrategy: Annotated[str, Form()] = "token_budget",
    tokenBudget: Annotated[int, Form()] = 512,
) -> dict:
    try:
        validate_job_id(jobId)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="404_JOB_NOT_FOUND") from exc

    chunkStrategy = validate_chunk_strategy(chunkStrategy)
    tokenBudget = validate_token_budget(tokenBudget)

    meta = store.load_job_meta(jobId)
    if not meta:
        raise HTTPException(status_code=404, detail="404_JOB_NOT_FOUND")

    layout_path = store.job_dir(jobId) / "layout.json"
    if layout_path.exists():
        data = json.loads(layout_path.read_text(encoding="utf-8"))
        blocks = [
            TextBlock(
                text=item["text"],
                page=item["page"],
                bbox=tuple(item["bbox"]),
                kind=item.get("kind", "text"),
                level=item.get("level"),
                confidence=item.get("confidence", 0.9),
            )
            for item in data
        ]
        layout = LayoutDocument(blocks=blocks, page_count=meta.page_count)
    else:
        chunks_path = store.job_dir(jobId) / "chunks.jsonl"
        if not chunks_path.exists():
            raise HTTPException(status_code=404, detail="404_JOB_NOT_FOUND")
        blocks = []
        for line in chunks_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("kind") == "table":
                continue
            blocks.append(
                TextBlock(
                    text=row["text"],
                    page=row["page"],
                    bbox=tuple(row["bbox"]),
                    kind=row.get("kind", "text"),
                    level=row.get("level"),
                    confidence=row.get("confidence", 0.9),
                )
            )
        layout = LayoutDocument(blocks=blocks, page_count=meta.page_count)

    text_chunks = chunk_document(layout, strategy=chunkStrategy, token_budget=tokenBudget)

    pdf_path = store.job_dir(jobId) / "input.pdf"
    tables = extract_tables(pdf_path) if pdf_path.exists() else []
    chunks = text_chunks + chunks_from_tables(tables)

    out_path = store.job_dir(jobId) / "chunks.jsonl"
    out_path.write_text(chunks_to_jsonl(chunks), encoding="utf-8")

    return {
        "jobId": jobId,
        "chunksUrl": f"/v1/jobs/{jobId}/artifacts/chunks.jsonl",
        "stats": {
            "chunks": len(chunks),
            "tokens": sum(c.token_count for c in chunks),
        },
    }
