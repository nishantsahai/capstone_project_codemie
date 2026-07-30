from __future__ import annotations

from fastapi.testclient import TestClient

from ci_cd_analyzer.main import app

client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_sample_formats() -> None:
    resp = client.get("/sample-formats")
    assert resp.status_code == 200
    data = resp.json()
    assert "jenkins" in data
    assert "github" in data


def test_analyze_valid_jenkins() -> None:
    log_text = "\n".join(
        [
            "Stage: Build - SUCCESS - 12 sec",
            "Stage: Test - FAILED - 7 sec - Error: test failure",
        ]
    )
    resp = client.post("/analyze", json={"source": "jenkins", "log_text": log_text})
    assert resp.status_code == 200
    body = resp.json()

    # API contract returns the AnalysisReport structure (summary + insights)
    assert body["summary"]["total_runs"] == 1
    assert body["summary"]["failure_runs"] == 1
    assert body["summary"]["success_runs"] == 0
    assert body["summary"]["success_rate"] == 0.0


def test_analyze_invalid_source_returns_consistent_error_envelope() -> None:
    resp = client.post(
        "/analyze", json={"source": "nope", "log_text": "Stage: X - SUCCESS - 1 sec"}
    )
    assert resp.status_code == 400
    body = resp.json()
    assert "details" in body
    assert isinstance(body["details"], list)


def test_analyze_empty_log_returns_consistent_error_envelope() -> None:
    resp = client.post("/analyze", json={"source": "jenkins", "log_text": ""})
    assert resp.status_code == 400
    body = resp.json()
    assert "details" in body


def test_analyze_no_stage_events_returns_consistent_error_envelope() -> None:
    # Well-formed request that cannot be parsed into stage events.
    resp = client.post(
        "/analyze", json={"source": "jenkins", "log_text": "this is not a stage line"}
    )
    assert resp.status_code == 400
    body = resp.json()
    assert "details" in body
    assert body["details"][0]["type"] in {"value_error", "http_error"}
