from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .api_models import (
    AnalysisReportModel,
    AnalyzeRequest,
    ErrorDetail,
    ErrorResponse,
)
from .utils.helpers import analyze_pipeline_log

app = FastAPI(title="CI/CD Pipeline Analyzer", version="0.1.0")


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        ErrorDetail(
            loc=[str(item) for item in err.get("loc", [])],
            msg=str(err.get("msg", "Invalid value")),
            type=str(err.get("type", "validation_error")),
        )
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(details=details).model_dump(),
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/sample-formats")
def sample_formats() -> dict[str, dict[str, str]]:
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


@app.post("/analyze", response_model=AnalysisReportModel, responses={400: {"model": ErrorResponse}})
def analyze(payload: AnalyzeRequest) -> AnalysisReportModel:
    report = analyze_pipeline_log(payload.source, payload.log_text)
    return AnalysisReportModel.model_validate(report.to_dict())
