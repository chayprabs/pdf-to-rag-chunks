"""Exhaustive worker API matrix — parse, rechunk, compare, samples, artifacts."""

from __future__ import annotations

import json
import shutil
import zipfile
from io import BytesIO
from pathlib import Path

import pytest

pytestmark = pytest.mark.slow

from fastapi.testclient import TestClient

from src.main import app

SAMPLES = Path(__file__).resolve().parents[3] / "samples"
CHUNK_STRATEGIES = (
    "by_heading",
    "token_budget",
    "semantic_block",
    "by_page",
    "citation_aware",
    "hybrid",
)
OCR_MODES = ("auto", "force", "off")
TOKEN_BUDGETS = (256, 512, 1024, 2048)
CHUNK_REQUIRED = ("page", "bbox", "sectionPath", "tokenCount", "kind", "confidence")
PARSE_TOP_KEYS = (
    "jobId",
    "document",
    "markdownUrl",
    "chunksUrl",
    "manifestUrl",
    "tablesZipUrl",
    "imagesZipUrl",
    "tables",
    "images",
    "stats",
    "engine",
)
DOCUMENT_KEYS = ("sha256", "pageCount", "ocrPages")
STATS_KEYS = ("headings", "tables", "figures", "chunks", "tokens", "toc", "ocrConfidence")

client = TestClient(app)


def _sample_pdfs() -> list[Path]:
    return sorted(SAMPLES.glob("*.pdf"))


def _validate_chunk_line(row: dict) -> None:
    for key in CHUNK_REQUIRED:
        assert key in row, f"missing {key}"
    assert isinstance(row["page"], int)
    assert isinstance(row["bbox"], list) and len(row["bbox"]) == 4
    assert isinstance(row["sectionPath"], list)
    assert isinstance(row["tokenCount"], int)
    assert isinstance(row["kind"], str)
    assert isinstance(row["confidence"], (int, float))


def _validate_parse_body(body: dict, *, expect_tables: bool = False) -> str:
    for key in PARSE_TOP_KEYS:
        assert key in body, f"missing top-level {key}"
    for key in DOCUMENT_KEYS:
        assert key in body["document"], f"missing document.{key}"
    for key in STATS_KEYS:
        assert key in body["stats"], f"missing stats.{key}"
    job_id = body["jobId"]
    assert body["markdownUrl"] == f"/v1/jobs/{job_id}/artifacts/document.md"
    assert body["chunksUrl"] == f"/v1/jobs/{job_id}/artifacts/chunks.jsonl"
    assert body["manifestUrl"] == f"/v1/jobs/{job_id}/artifacts/manifest.json"
    assert body["tablesZipUrl"] == f"/v1/jobs/{job_id}/artifacts/tables.zip"
    if expect_tables:
        assert body["stats"]["tables"] >= 1
        assert len(body["tables"]) >= 1
    return job_id


@pytest.fixture(scope="module")
def health_body():
    r = client.get("/health")
    assert r.status_code == 200
    return r.json()


def test_health_schema(health_body):
    assert health_body["status"] == "ok"
    assert "engine" in health_body
    assert "engineVersion" in health_body


@pytest.mark.parametrize("pdf_path", _sample_pdfs(), ids=lambda p: p.name)
@pytest.mark.parametrize("ocr", OCR_MODES)
@pytest.mark.parametrize("chunk_strategy", CHUNK_STRATEGIES)
@pytest.mark.parametrize("token_budget", TOKEN_BUDGETS)
def test_parse_matrix(pdf_path: Path, ocr: str, chunk_strategy: str, token_budget: int):
    if ocr == "force" and not shutil.which("pdfinfo"):
        pytest.skip("poppler (pdfinfo) required for ocr=force")
    with pdf_path.open("rb") as f:
        r = client.post(
            "/v1/parse",
            files={"file": (pdf_path.name, f, "application/pdf")},
            data={
                "ocr": ocr,
                "chunkStrategy": chunk_strategy,
                "tokenBudget": str(token_budget),
            },
        )
    assert r.status_code == 200, r.text
    body = r.json()
    expect_tables = pdf_path.name == "financial-report-sample.pdf"
    job_id = _validate_parse_body(body, expect_tables=expect_tables)

    md = client.get(f"/v1/jobs/{job_id}/artifacts/document.md")
    assert md.status_code == 200
    if pdf_path.name != "scanned-manual.pdf" or ocr in ("force", "auto"):
        # text-layer PDFs must have markdown; scanned may be thin with ocr off
        if ocr != "off" or pdf_path.name != "scanned-manual.pdf":
            assert len(md.text.strip()) > 0, "document.md empty"

    chunks = client.get(f"/v1/jobs/{job_id}/artifacts/chunks.jsonl")
    assert chunks.status_code == 200
    lines = [ln for ln in chunks.text.splitlines() if ln.strip()]
    assert lines, "chunks.jsonl empty"
    for ln in lines:
        _validate_chunk_line(json.loads(ln))

    manifest = client.get(f"/v1/jobs/{job_id}/artifacts/manifest.json")
    assert manifest.status_code == 200
    m = manifest.json()
    assert m["jobId"] == job_id
    assert "sha256" in m and "pageCount" in m

    tz = client.get(f"/v1/jobs/{job_id}/artifacts/tables.zip")
    assert tz.status_code == 200
    if expect_tables:
        with zipfile.ZipFile(BytesIO(tz.content)) as zf:
            names = zf.namelist()
            assert any(n.endswith("table.csv") for n in names)
        for tbl in body["tables"]:
            for fmt in ("table.md", "table.csv", "table.json", "table.html"):
                sub = f"tables/{tbl['id']}/{fmt}"
                ar = client.get(f"/v1/jobs/{job_id}/artifacts/{sub}")
                assert ar.status_code == 200, sub


@pytest.mark.parametrize("chunk_strategy", CHUNK_STRATEGIES)
@pytest.mark.parametrize("token_budget", TOKEN_BUDGETS)
def test_rechunk_after_parse(chunk_strategy: str, token_budget: int):
    sample = SAMPLES / "minimal.pdf"
    with sample.open("rb") as f:
        pr = client.post(
            "/v1/parse",
            files={"file": ("minimal.pdf", f, "application/pdf")},
            data={"ocr": "off", "chunkStrategy": "token_budget", "tokenBudget": "512"},
        )
    assert pr.status_code == 200
    job_id = pr.json()["jobId"]
    rr = client.post(
        "/v1/rechunk",
        data={
            "jobId": job_id,
            "chunkStrategy": chunk_strategy,
            "tokenBudget": str(token_budget),
        },
    )
    assert rr.status_code == 200, rr.text
    rb = rr.json()
    assert rb["jobId"] == job_id
    assert rb["chunksUrl"] == f"/v1/jobs/{job_id}/artifacts/chunks.jsonl"
    assert rb["stats"]["chunks"] >= 1

    chunks = client.get(rb["chunksUrl"])
    assert chunks.status_code == 200
    for ln in chunks.text.splitlines():
        if ln.strip():
            _validate_chunk_line(json.loads(ln))


def test_compare_endpoint():
    sample = SAMPLES / "financial-report-sample.pdf"
    with sample.open("rb") as f:
        r = client.post(
            "/v1/compare",
            files={"file": ("financial-report-sample.pdf", f, "application/pdf")},
            data={
                "engineA": "pdfplumber",
                "engineB": "pdfplumber",
                "chunkStrategy": "by_heading",
                "tokenBudget": "1024",
            },
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "resultA" in body and "resultB" in body
    assert "diff" in body and isinstance(body["diff"], list)
    _validate_parse_body(body["resultA"], expect_tables=True)
    _validate_parse_body(body["resultB"], expect_tables=True)


def test_samples_list_and_download():
    r = client.get("/v1/samples")
    assert r.status_code == 200
    samples = r.json()["samples"]
    assert samples
    filenames = {s["filename"] for s in samples}
    for pdf in _sample_pdfs():
        assert pdf.name in filenames
    for meta in samples:
        dl = client.get(meta["url"])
        assert dl.status_code == 200
        assert dl.headers["content-type"].startswith("application/pdf")
        assert dl.content[:4] == b"%PDF"
