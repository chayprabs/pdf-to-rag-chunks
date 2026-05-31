import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.main import app

FINANCIAL = Path(__file__).resolve().parents[3] / "samples" / "financial-report-sample.pdf"
client = TestClient(app)


def test_financial_no_duplicate_table_in_heading_chunk():
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
    chunks = client.get(f"/v1/jobs/{job_id}/artifacts/chunks.jsonl")
    kinds = [json.loads(ln)["kind"] for ln in chunks.text.splitlines() if ln.strip()]
    heading_with_table_cells = 0
    for ln in chunks.text.splitlines():
        if not ln.strip():
            continue
        row = json.loads(ln)
        if row["kind"] == "heading" and "|" in row["text"] and "Revenue" in row["text"]:
            heading_with_table_cells += 1
    assert heading_with_table_cells == 0
    assert "table" in kinds
