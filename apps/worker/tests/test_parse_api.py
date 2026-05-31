from pathlib import Path

from fastapi.testclient import TestClient

from src.main import app

SAMPLE = Path(__file__).resolve().parents[3] / "samples" / "minimal.pdf"


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_parse_minimal_pdf():
    if not SAMPLE.exists():
        return
    client = TestClient(app)
    with SAMPLE.open("rb") as f:
        r = client.post(
            "/v1/parse",
            files={"file": ("minimal.pdf", f, "application/pdf")},
            data={"ocr": "off", "chunkStrategy": "token_budget", "tokenBudget": "512"},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["stats"]["chunks"] >= 1
    assert "chunks.jsonl" in body["chunksUrl"]
