from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, HTTPException

from .utils.helpers import analyze_pipeline_log

app = FastAPI(title="CI/CD Pipeline Analyzer", version="0.1.0")


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/sample-formats")
def sample_formats() -> Dict[str, Dict[str, str]]:
    return {
        "jenkins": {
            "example": "Stage: Build - SUCCESS - 120 sec",
            "description": "Jenkins console-style stage lines.",
        },
        "github": {
            "example": "::group::Test | FAILED | 220 sec | Error: AssertionError",
            "description": "GitHub Actions stage lines.",
        },
    }


@app.post("/analyze")
def analyze(payload: Dict[str, Any]) -> Dict[str, Any]:
    source = str(payload.get("source", "jenkins"))
    log_text = str(payload.get("log_text", ""))

    if not log_text.strip():
        raise HTTPException(status_code=400, detail="log_text is required.")

    try:
        report = analyze_pipeline_log(source, log_text)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return report.to_dict()
