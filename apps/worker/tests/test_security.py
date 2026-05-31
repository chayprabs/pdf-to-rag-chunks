from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_artifact_path_traversal_blocked():
    r = client.get("/v1/jobs/not-a-uuid/artifacts/chunks.jsonl")
    assert r.status_code == 404

    # Create a real job first via parse would be better; test invalid IDs
    r2 = client.get(
        "/v1/jobs/00000000-0000-0000-0000-000000000000/artifacts/../../../etc/passwd"
    )
    assert r2.status_code in (404, 422)


def test_rechunk_invalid_job_id():
    r = client.post(
        "/v1/rechunk",
        data={"jobId": "../../../tmp/evil", "chunkStrategy": "token_budget", "tokenBudget": "512"},
    )
    assert r.status_code == 404
