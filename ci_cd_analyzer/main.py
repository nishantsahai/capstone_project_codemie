from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from .api_models import (
    AnalysisReportModel,
    AnalyzeRequest,
    ErrorDetail,
    ErrorResponse,
)
from .utils.helpers import analyze_pipeline_log

app = FastAPI(title="CI/CD Pipeline Analyzer", version="0.1.0")


def _error_response(details: list[ErrorDetail]) -> JSONResponse:
    return JSONResponse(status_code=400, content=ErrorResponse(details=details).model_dump())


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
    return _error_response(details)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    # Normalize all 400s into our error envelope.
    if exc.status_code == 400:
        if isinstance(exc.detail, dict) and "details" in exc.detail:
            return JSONResponse(status_code=400, content=exc.detail)
        return _error_response(
            [ErrorDetail(loc=["body"], msg=str(exc.detail), type="http_error")]
        )

    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


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


@app.post(
    "/analyze", response_model=AnalysisReportModel, responses={400: {"model": ErrorResponse}}
)
def analyze(payload: AnalyzeRequest) -> AnalysisReportModel:
    try:
        report = analyze_pipeline_log(payload.source, payload.log_text)
    except ValueError as exc:
        # Treat domain errors as client errors and keep a consistent envelope.
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                details=[ErrorDetail(loc=["body"], msg=str(exc), type="value_error")]
            ).model_dump(),
        ) from exc

    return AnalysisReportModel.model_validate(report.to_dict())
