import difflib
import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..config import settings
from ..core.pipeline import parse_pdf
from ..storage.job_store import JobStore

logger = logging.getLogger(__name__)
router = APIRouter(tags=["compare"])
store = JobStore()


@router.post("/compare")
async def compare(
    file: Annotated[UploadFile, File()],
    engineA: Annotated[str, Form()] = "pdfplumber",
    engineB: Annotated[str, Form()] = "pdfplumber",
    chunkStrategy: Annotated[str, Form()] = "token_budget",
    tokenBudget: Annotated[int, Form()] = 512,
) -> dict:
    pdf_bytes = await file.read()
    if not pdf_bytes.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="400_PDF_INVALID")
    if len(pdf_bytes) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="413_PDF_TOO_LARGE")

    job_a, sha_a = store.create_job(pdf_bytes)
    job_b, sha_b = store.create_job(pdf_bytes)
    path = store.job_dir(job_a) / "input.pdf"

    try:
        result_a = parse_pdf(
            path,
            job_a,
            sha_a,
            store,
            chunk_strategy=chunkStrategy,
            token_budget=tokenBudget,
        )
        result_b = parse_pdf(
            path,
            job_b,
            sha_b,
            store,
            chunk_strategy=chunkStrategy,
            token_budget=tokenBudget,
        )
    except Exception as exc:
        logger.exception("Compare parse failed")
        raise HTTPException(status_code=400, detail="400_PDF_INVALID") from exc

    md_a = (store.job_dir(job_a) / "document.md").read_text(encoding="utf-8")
    md_b = (store.job_dir(job_b) / "document.md").read_text(encoding="utf-8")
    diff = list(
        difflib.unified_diff(
            md_a.splitlines(),
            md_b.splitlines(),
            fromfile=engineA,
            tofile=engineB,
            lineterm="",
        )
    )

    return {
        "resultA": result_a,
        "resultB": result_b,
        "diff": diff,
        "engines": {"a": engineA, "b": engineB},
        "note": "Both runs currently use pdfplumber; engine labels are for future multi-engine support.",
    }
