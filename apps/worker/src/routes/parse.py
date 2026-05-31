import ipaddress
import logging
import socket
from typing import Annotated
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from ..config import settings
from ..core.pipeline import parse_pdf
from ..storage.job_store import JobStore, validate_job_id

logger = logging.getLogger(__name__)
router = APIRouter(tags=["parse"])
store = JobStore()

ERROR_MESSAGES = {
    "400_PDF_INVALID": "Invalid or missing PDF.",
    "413_PDF_TOO_LARGE": "PDF exceeds the maximum upload size.",
    "424_OCR_FAILED": "OCR processing failed.",
    "424_PARSE_TIMEOUT": "Parse timed out.",
    "404_NOT_FOUND": "Artifact not found.",
    "404_JOB_NOT_FOUND": "Job not found.",
}


def _block_private_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="400_PDF_INVALID")
    host = parsed.hostname
    if not host or host in ("localhost", "127.0.0.1", "0.0.0.0"):
        raise HTTPException(status_code=400, detail="400_PDF_INVALID")
    try:
        for info in socket.getaddrinfo(host, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                raise HTTPException(status_code=400, detail="400_PDF_INVALID")
    except socket.gaierror:
        raise HTTPException(status_code=400, detail="400_PDF_INVALID") from None


async def _fetch_pdf_url(url: str) -> bytes:
    _block_private_url(url)
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        async with client.stream("GET", url) as resp:
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail="400_PDF_INVALID")
            chunks: list[bytes] = []
            total = 0
            async for chunk in resp.aiter_bytes():
                total += len(chunk)
                if total > settings.max_upload_bytes:
                    raise HTTPException(status_code=413, detail="413_PDF_TOO_LARGE")
                chunks.append(chunk)
            return b"".join(chunks)


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
        pdf_bytes = await _fetch_pdf_url(url.strip())
    else:
        raise HTTPException(status_code=400, detail="400_PDF_INVALID")

    if not pdf_bytes or not pdf_bytes.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="400_PDF_INVALID")

    if len(pdf_bytes) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="413_PDF_TOO_LARGE")

    if tokenBudget not in (256, 512, 1024, 2048):
        raise HTTPException(status_code=400, detail="400_PDF_INVALID")

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
        result["engine"] = engine or settings.engine
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Parse failed job=%s", job_id)
        if "OCR" in str(exc).upper():
            raise HTTPException(status_code=424, detail="424_OCR_FAILED") from exc
        if "timeout" in str(exc).lower():
            raise HTTPException(status_code=424, detail="424_PARSE_TIMEOUT") from exc
        raise HTTPException(status_code=500, detail="500_PARSE_FAILED") from exc


@router.get("/jobs/{job_id}/artifacts/{artifact_path:path}")
async def download_artifact(job_id: str, artifact_path: str):
    try:
        validate_job_id(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="404_NOT_FOUND") from exc

    path = store.artifact_path(job_id, artifact_path)
    if not path:
        raise HTTPException(status_code=404, detail="404_NOT_FOUND")
    return FileResponse(path, filename=path.name)
