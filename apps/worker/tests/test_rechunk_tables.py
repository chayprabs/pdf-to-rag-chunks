import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.main import app

FINANCIAL = Path(__file__).resolve().parents[3] / "samples" / "financial-report-sample.pdf"
client = TestClient(app)


def test_rechunk_preserves_table_chunks():
    if not FINANCIAL.exists():
        import pytest

        pytest.skip("financial sample missing")

    with FINANCIAL.open("rb") as f:
        r = client.post(
            "/v1/parse",
            files={"file": ("financial-report-sample.pdf", f, "application/pdf")},
            data={"ocr": "off", "chunkStrategy": "token_budget", "tokenBudget": "512"},
        )
    assert r.status_code == 200
    job_id = r.json()["jobId"]

    before = client.get(f"/v1/jobs/{job_id}/artifacts/chunks.jsonl")
    kinds_before = [json.loads(ln)["kind"] for ln in before.text.splitlines() if ln.strip()]
    assert "table" in kinds_before

    rr = client.post(
        "/v1/rechunk",
        data={"jobId": job_id, "chunkStrategy": "token_budget", "tokenBudget": "512"},
    )
    assert rr.status_code == 200

    after = client.get(f"/v1/jobs/{job_id}/artifacts/chunks.jsonl")
    kinds_after = [json.loads(ln)["kind"] for ln in after.text.splitlines() if ln.strip()]
    assert "table" in kinds_after
