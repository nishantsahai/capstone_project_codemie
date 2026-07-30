from __future__ import annotations

from fastapi.testclient import TestClient

from ci_cd_analyzer.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_sample_formats() -> None:
    response = client.get("/sample-formats")
    assert response.status_code == 200
    payload = response.json()
    assert "jenkins" in payload
    assert "github" in payload


def test_analyze_valid_payload() -> None:
    log_text = "Stage: Build - SUCCESS - 2 sec\nStage: Test - SUCCESS - 1 sec\n"
    response = client.post("/analyze", json={"source": "jenkins", "log_text": log_text})
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "stage_metrics" in data


def test_analyze_invalid_source_returns_consistent_error_shape() -> None:
    response = client.post(
        "/analyze",
        json={"source": "nope", "log_text": "Stage: Build - SUCCESS - 1 sec"},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "Invalid request"
    assert isinstance(body["details"], list)
    assert body["details"], "expected at least one error detail"


def test_analyze_empty_log_text_returns_consistent_error_shape() -> None:
    response = client.post("/analyze", json={"source": "jenkins", "log_text": "   "})
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "Invalid request"
    assert isinstance(body["details"], list)
    assert body["details"], "expected at least one error detail"
