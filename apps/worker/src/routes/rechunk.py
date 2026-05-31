import json
import logging
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException

from ..core.chunking import ChunkRecord, chunk_document, chunks_to_jsonl, count_tokens
from ..core.layout import LayoutDocument, TextBlock
from ..storage.job_store import JobStore

logger = logging.getLogger(__name__)
router = APIRouter(tags=["rechunk"])
store = JobStore()


@router.post("/rechunk")
async def rechunk(
    jobId: Annotated[str, Form()],
    chunkStrategy: Annotated[str, Form()] = "token_budget",
    tokenBudget: Annotated[int, Form()] = 512,
) -> dict:
    meta = store.load_job_meta(jobId)
    if not meta:
        raise HTTPException(status_code=404, detail="404_JOB_NOT_FOUND")

    chunks_path = store.job_dir(jobId) / "chunks.jsonl"
    if not chunks_path.exists():
        raise HTTPException(status_code=404, detail="404_JOB_NOT_FOUND")

    blocks: list[TextBlock] = []
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
