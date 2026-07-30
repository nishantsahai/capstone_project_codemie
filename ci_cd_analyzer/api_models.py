from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

PipelineSource = Literal["jenkins", "github"]
StageStatus = Literal["SUCCESS", "FAILED", "SKIPPED", "UNSTABLE", "UNKNOWN"]


LOG_TEXT_MAX_CHARS_DEFAULT = 1_000_000


class AnalyzeRequest(BaseModel):
    source: PipelineSource = Field(default="jenkins")
    log_text: str = Field(..., min_length=1, description="Raw pipeline log text")

    @field_validator("log_text")
    @classmethod
    def log_text_must_be_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("log_text is required.")
        if len(value) > LOG_TEXT_MAX_CHARS_DEFAULT:
            raise ValueError(
                f"log_text exceeds maximum size of {LOG_TEXT_MAX_CHARS_DEFAULT} characters."
            )
        return value


class ErrorDetail(BaseModel):
    loc: list[str] = Field(default_factory=list)
    msg: str
    type: str = "validation_error"


class ErrorResponse(BaseModel):
    error: str = "Invalid request"
    details: list[ErrorDetail]


class StageEventModel(BaseModel):
    stage: str
    status: StageStatus
    duration_seconds: float | None = None
    error_message: str | None = None
    raw_line: str | None = None
    run_id: str | None = None


class PipelineSummaryModel(BaseModel):
    total_runs: int
    success_runs: int
    failure_runs: int
    success_rate: float
    average_execution_time_seconds: float


class StageMetricsModel(BaseModel):
    stage: str
    average_duration_seconds: float
    failure_count: int
    total_runs: int
    failure_rate: float
    flaky: bool


class BottleneckInsightModel(BaseModel):
    stage: str
    average_duration_seconds: float
    multiplier_vs_average: float
    insight: str


class FailurePatternModel(BaseModel):
    stage: str
    failure_count: int
    share_of_failures: float
    common_errors: list[str] = Field(default_factory=list)


class FlakyStageInsightModel(BaseModel):
    stage: str
    pattern: list[str]
    insight: str


class ActionableSuggestionModel(BaseModel):
    area: str
    suggestion: str
    reason: str


class AnalysisReportModel(BaseModel):
    summary: PipelineSummaryModel
    stage_metrics: list[StageMetricsModel] = Field(default_factory=list)
    bottlenecks: list[BottleneckInsightModel] = Field(default_factory=list)
    failure_patterns: list[FailurePatternModel] = Field(default_factory=list)
    flaky_stages: list[FlakyStageInsightModel] = Field(default_factory=list)
    suggestions: list[ActionableSuggestionModel] = Field(default_factory=list)
