from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

PipelineSource = Literal["jenkins", "github"]
StageStatus = Literal["SUCCESS", "FAILED", "SKIPPED", "UNSTABLE", "UNKNOWN"]


@dataclass(frozen=True)
class StageEvent:
    stage: str
    status: StageStatus
    duration_seconds: float | None = None
    error_message: str | None = None
    raw_line: str | None = None
    run_id: str | None = None


@dataclass(frozen=True)
class PipelineSummary:
    total_runs: int
    success_runs: int
    failure_runs: int
    success_rate: float
    average_execution_time_seconds: float


@dataclass(frozen=True)
class StageMetrics:
    stage: str
    average_duration_seconds: float
    failure_count: int
    total_runs: int
    failure_rate: float
    flaky: bool


@dataclass(frozen=True)
class BottleneckInsight:
    stage: str
    average_duration_seconds: float
    multiplier_vs_average: float
    insight: str


@dataclass(frozen=True)
class FailurePattern:
    stage: str
    failure_count: int
    share_of_failures: float
    common_errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FlakyStageInsight:
    stage: str
    pattern: list[str]
    insight: str


@dataclass(frozen=True)
class ActionableSuggestion:
    area: str
    suggestion: str
    reason: str


@dataclass(frozen=True)
class AnalysisReport:
    summary: PipelineSummary
    stage_metrics: list[StageMetrics] = field(default_factory=list)
    bottlenecks: list[BottleneckInsight] = field(default_factory=list)
    failure_patterns: list[FailurePattern] = field(default_factory=list)
    flaky_stages: list[FlakyStageInsight] = field(default_factory=list)
    suggestions: list[ActionableSuggestion] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
