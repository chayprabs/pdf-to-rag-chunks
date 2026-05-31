"""Golden-output regression tests with tolerance."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import app

SAMPLES = Path(__file__).resolve().parents[3] / "samples"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
client = TestClient(app)


def _ratio(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    from difflib import SequenceMatcher

    return SequenceMatcher(None, a, b).ratio()


@pytest.mark.parametrize(
    "filename,min_ratio",
    [
        ("minimal.pdf", 0.5),
        ("attention-is-all-you-need.pdf", 0.4),
        ("financial-report-sample.pdf", 0.35),
    ],
)
def test_parse_golden_markdown(filename: str, min_ratio: float):
    path = SAMPLES / filename
    if not path.exists():
        pytest.skip(f"missing {filename}")

    with path.open("rb") as f:
        r = client.post(
            "/v1/parse",
            files={"file": (filename, f, "application/pdf")},
            data={"ocr": "off", "chunkStrategy": "token_budget", "tokenBudget": "512"},
        )
    assert r.status_code == 200, r.text
    body = r.json()
    job_id = body["jobId"]
    md = client.get(f"/v1/jobs/{job_id}/artifacts/document.md")
    assert md.status_code == 200
    text = md.text

    golden = FIXTURES / f"{path.stem}.md"
    if golden.exists():
        expected = golden.read_text(encoding="utf-8")
        assert _ratio(text, expected) >= min_ratio, f"markdown drift for {filename}"

    assert body["stats"]["chunks"] >= 1
    chunks = client.get(f"/v1/jobs/{job_id}/artifacts/chunks.jsonl")
    assert chunks.status_code == 200
    lines = [ln for ln in chunks.text.splitlines() if ln.strip()]
    for ln in lines:
        row = json.loads(ln)
        assert "page" in row and "tokenCount" in row and "kind" in row


def test_samples_list():
    r = client.get("/v1/samples")
    assert r.status_code == 200
    data = r.json()
    assert "samples" in data
