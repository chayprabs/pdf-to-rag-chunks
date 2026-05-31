from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..config import settings

router = APIRouter(tags=["samples"])

SAMPLES_DIR = settings.samples_dir.resolve()

SAMPLE_META = [
    {
        "id": "minimal",
        "filename": "minimal.pdf",
        "title": "Minimal demo",
        "description": "Single-page smoke test PDF.",
    },
    {
        "id": "attention",
        "filename": "attention-is-all-you-need.pdf",
        "title": "Research paper",
        "description": "Headings, lists, and code block sample.",
    },
    {
        "id": "financial",
        "filename": "financial-report-sample.pdf",
        "title": "Financial report",
        "description": "Table-heavy quarterly report sample.",
    },
    {
        "id": "scanned",
        "filename": "scanned-manual.pdf",
        "title": "Scanned manual",
        "description": "Manual-style text for OCR workflows.",
    },
    {
        "id": "magazine",
        "filename": "multi-column-magazine.pdf",
        "title": "Multi-column magazine",
        "description": "Multi-column layout sample.",
    },
]


@router.get("/samples")
async def list_samples() -> dict:
    available = []
    for meta in SAMPLE_META:
        path = SAMPLES_DIR / meta["filename"]
        if path.exists():
            available.append({**meta, "url": f"/v1/samples/{meta['filename']}"})
    return {"samples": available}


@router.get("/samples/{filename}")
async def get_sample(filename: str):
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=404, detail="404_NOT_FOUND")
    path = (SAMPLES_DIR / filename).resolve()
    if not path.exists() or not str(path).startswith(str(SAMPLES_DIR.resolve())):
        raise HTTPException(status_code=404, detail="404_NOT_FOUND")
    return FileResponse(path, filename=filename, media_type="application/pdf")
