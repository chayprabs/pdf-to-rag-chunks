import logging
from typing import Annotated
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from ..config import settings
from ..core.pipeline import parse_pdf
from ..storage.job_store import JobStore

logger = logging.getLogger(__name__)
router = APIRouter(tags=["parse"])
store = JobStore()


@router.post("/parse")
async def parse_endpoint(
    file: Annotated[UploadFile | None, File()] = None,
    url: Annotated[str | None, Form()] = None,
    ocr: Annotated[str, Form()] = "auto",
    engine: Annotated[str, Form()] = "pdfplumber",
    chunkStrategy: Annotated[str, Form()] = "token_budget",
    tokenBudget: Annotated[int, Form()] = 512,
    ocrLanguage: Annotated[str, Form()] = "eng",
) -> dict:
    pdf_bytes: bytes | None = None

    if file and file.filename:
        pdf_bytes = await file.read()
    elif url:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise HTTPException(status_code=400, detail="400_PDF_INVALID")
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail="400_PDF_INVALID")
            pdf_bytes = resp.content
    else:
        raise HTTPException(status_code=400, detail="400_PDF_INVALID")

    if not pdf_bytes or not pdf_bytes.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="400_PDF_INVALID")

    if len(pdf_bytes) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="413_PDF_TOO_LARGE")

    if tokenBudget not in (256, 512, 1024, 2048):
        tokenBudget = 512

    job_id, sha256 = store.create_job(pdf_bytes)
    pdf_path = store.job_dir(job_id) / "input.pdf"

    try:
        result = parse_pdf(
            pdf_path,
            job_id,
            sha256,
            store,
            ocr_mode=ocr,
            ocr_language=ocrLanguage,
            chunk_strategy=chunkStrategy,
            token_budget=tokenBudget,
        )
        return result
    except Exception as exc:
        logger.exception("Parse failed job=%s", job_id)
        if "OCR" in str(exc).upper():
            raise HTTPException(status_code=424, detail="424_OCR_FAILED") from exc
        if "timeout" in str(exc).lower():
            raise HTTPException(status_code=424, detail="424_PARSE_TIMEOUT") from exc
        raise HTTPException(status_code=500, detail="500_PARSE_FAILED") from exc


@router.get("/jobs/{job_id}/artifacts/{artifact_path:path}")
async def download_artifact(job_id: str, artifact_path: str):
    path = store.artifact_path(job_id, artifact_path)
    if not path:
        raise HTTPException(status_code=404, detail="404_NOT_FOUND")
    return FileResponse(path, filename=path.name)
