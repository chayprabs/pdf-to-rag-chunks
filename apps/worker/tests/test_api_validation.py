"""API validation edge cases discovered during worker verification."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import app

SAMPLE = Path(__file__).resolve().parents[3] / "samples" / "minimal.pdf"
client = TestClient(app)

VALID_STRATEGIES = {
    "by_heading",
    "token_budget",
    "semantic_block",
    "by_page",
    "citation_aware",
    "hybrid",
}
VALID_OCR = {"auto", "force", "off"}


def _parse(**data: str):
    with SAMPLE.open("rb") as f:
        return client.post(
            "/v1/parse",
            files={"file": ("minimal.pdf", f, "application/pdf")},
            data=data,
        )


@pytest.mark.parametrize("chunk_strategy", sorted(VALID_STRATEGIES))
def test_valid_chunk_strategy_accepted(chunk_strategy: str):
    r = _parse(ocr="off", chunkStrategy=chunk_strategy, tokenBudget="512")
    assert r.status_code == 200, r.text


def test_invalid_chunk_strategy_rejected():
    """chunkStrategy should be validated; unknown values must not silently default."""
    r = _parse(ocr="off", chunkStrategy="not_a_strategy", tokenBudget="512")
    assert r.status_code == 400
    assert r.json()["detail"] == "400_PDF_INVALID"


@pytest.mark.parametrize("ocr", sorted(VALID_OCR))
def test_valid_ocr_mode_accepted(ocr: str):
    if ocr == "force" and not shutil.which("pdfinfo"):
        pytest.skip("poppler required for ocr=force")
    r = _parse(ocr=ocr, chunkStrategy="token_budget", tokenBudget="512")
    assert r.status_code == 200, r.text


def test_invalid_ocr_mode_rejected():
    r = _parse(ocr="bogus", chunkStrategy="token_budget", tokenBudget="512")
    assert r.status_code == 400
    assert r.json()["detail"] == "400_PDF_INVALID"


@pytest.mark.parametrize("budget", ("256", "512", "1024", "2048"))
def test_valid_token_budget_accepted(budget: str):
    r = _parse(ocr="off", chunkStrategy="token_budget", tokenBudget=budget)
    assert r.status_code == 200


def test_invalid_token_budget_rejected():
    r = _parse(ocr="off", chunkStrategy="token_budget", tokenBudget="999")
    assert r.status_code == 400
    assert r.json()["detail"] == "400_PDF_INVALID"


def test_ocr_runtime_failure_returns_424_not_500(monkeypatch):
    """When OCR pipeline fails with an explicit OCR error, return 424."""

    def _fail_ocr(*_a, **_k):
        raise RuntimeError("OCR failed: poppler not available")

    monkeypatch.setattr("src.core.pipeline.run_ocr", _fail_ocr)
    r = _parse(ocr="force", chunkStrategy="token_budget", tokenBudget="512")
    assert r.status_code == 424
    assert r.json()["detail"] == "424_OCR_FAILED"


def test_poppler_missing_maps_to_424_not_500(monkeypatch):
    """pdf2image/poppler failures should surface as 424_OCR_FAILED, not 500."""

    from pdf2image.exceptions import PDFInfoNotInstalledError

    def _no_poppler(*_a, **_k):
        raise PDFInfoNotInstalledError(
            "Unable to get page count. Is poppler installed and in PATH?"
        )

    monkeypatch.setattr("pdf2image.convert_from_path", _no_poppler)
    r = _parse(ocr="force", chunkStrategy="token_budget", tokenBudget="512")
    assert r.status_code == 424
    assert r.json()["detail"] == "424_OCR_FAILED"
