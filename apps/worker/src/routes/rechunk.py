import json
import logging
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException

from ..core.chunking import chunk_document, chunks_to_jsonl
from ..core.layout import LayoutDocument, TextBlock
from ..storage.job_store import JobStore, validate_job_id

logger = logging.getLogger(__name__)
router = APIRouter(tags=["rechunk"])
store = JobStore()


def _load_layout(job_id: str, page_count: int) -> LayoutDocument:
    layout_path = store.job_dir(job_id) / "layout.json"
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
        return LayoutDocument(blocks=blocks, page_count=page_count)

    chunks_path = store.job_dir(jobId) / "chunks.jsonl"  # typo fix below
    raise HTTPException(status_code=404, detail="404_JOB_NOT_FOUND")


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

    meta = store.load_job_meta(jobId)
    if not meta:
        raise HTTPException(status_code=404, detail="404_JOB_NOT_FOUND")

    if tokenBudget not in (256, 512, 1024, 2048):
        raise HTTPException(status_code=400, detail="400_PDF_INVALID")

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
            data = json.loads(line)
            blocks.append(
                TextBlock(
                    text=data["text"],
                    page=data["page"],
                    bbox=tuple(data["bbox"]),
                    kind=data.get("kind", "text"),
                    level=data.get("level"),
                    confidence=data.get("confidence", 0.9),
                )
            )
        layout = LayoutDocument(blocks=blocks, page_count=meta.page_count)

    chunks = chunk_document(layout, strategy=chunkStrategy, token_budget=tokenBudget)
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
