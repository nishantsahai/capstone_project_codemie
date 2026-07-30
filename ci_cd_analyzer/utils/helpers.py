from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from statistics import mean

from ..analyzer.failure_analysis import analyze_failures
from ..analyzer.flaky_detector import detect_flaky_stages
from ..analyzer.stage_analysis import analyze_stages
from ..models.schema import (
    ActionableSuggestion,
    AnalysisReport,
    BottleneckInsight,
    PipelineSource,
    PipelineSummary,
    StageEvent,
    StageMetrics,
)
from ..parser.github_parser import parse_github_log
from ..parser.jenkins_parser import parse_jenkins_log


def parse_pipeline_log(source: PipelineSource, log_text: str) -> list[StageEvent]:
    source_name = source.lower().strip()
    if source_name == "jenkins":
        return parse_jenkins_log(log_text)
    if source_name == "github":
        return parse_github_log(log_text)
    raise ValueError(f"Unsupported log source: {source}")


def load_log_text(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8")


def summarize_pipeline(events: Iterable[StageEvent]) -> PipelineSummary:
    event_list = list(events)
    durations = [
        event.duration_seconds for event in event_list if event.duration_seconds is not None
    ]
    total_runs = 1 if event_list else 0
    success_runs = 1 if event_list and all(event.status != "FAILED" for event in event_list) else 0
    failure_runs = total_runs - success_runs
    success_rate = success_runs / total_runs if total_runs else 0.0
    average_execution_time_seconds = mean(durations) if durations else 0.0

    return PipelineSummary(
        total_runs=total_runs,
        success_runs=success_runs,
        failure_runs=failure_runs,
        success_rate=success_rate,
        average_execution_time_seconds=average_execution_time_seconds,
    )


def identify_bottlenecks(stage_metrics: Iterable[StageMetrics]) -> list[BottleneckInsight]:
    metric_list = list(stage_metrics)
    durations = [
        metric.average_duration_seconds
        for metric in metric_list
        if metric.average_duration_seconds > 0
    ]
    if not durations:
        return []

    overall_average = mean(durations)
    bottlenecks: list[BottleneckInsight] = []
    for metric in sorted(metric_list, key=lambda item: item.average_duration_seconds, reverse=True):
        if metric.average_duration_seconds <= overall_average * 1.2:
            continue
        multiplier = metric.average_duration_seconds / overall_average if overall_average else 0.0
        bottlenecks.append(
            BottleneckInsight(
                stage=metric.stage,
                average_duration_seconds=metric.average_duration_seconds,
                multiplier_vs_average=multiplier,
                insight=f"{metric.stage} is {multiplier:.1f}x slower than the average stage time.",
            )
        )

    return bottlenecks[:3]


def generate_suggestions(
    bottlenecks: Iterable[BottleneckInsight],
    failure_patterns: Iterable,
    flaky_stages: Iterable,
) -> list[ActionableSuggestion]:
    suggestions: list[ActionableSuggestion] = []

    bottleneck_list = list(bottlenecks)
    if bottleneck_list:
        slowest = bottleneck_list[0]
        suggestions.append(
            ActionableSuggestion(
                area="Bottlenecks",
                suggestion=f"Break {slowest.stage} into smaller steps or parallelize expensive work.",
                reason=slowest.insight,
            )
        )

    failure_list = list(failure_patterns)
    for pattern in failure_list[:1]:
        if any("timeout" in error.lower() for error in pattern.common_errors):
            suggestions.append(
                ActionableSuggestion(
                    area="Failures",
                    suggestion="Increase timeouts or improve infrastructure capacity for the failing stage.",
                    reason=f"Repeated timeout errors in {pattern.stage}.",
                )
            )
            break

    flaky_list = list(flaky_stages)
    if flaky_list:
        suggestions.append(
            ActionableSuggestion(
                area="Flaky stages",
                suggestion="Add retries and stabilize the test environment for the flaky stage.",
                reason=f"{flaky_list[0].stage} shows repeated pass/fail alternation.",
            )
        )

    return suggestions


def analyze_pipeline_log(source: PipelineSource, log_text: str) -> AnalysisReport:
    events = parse_pipeline_log(source, log_text)
    if not events:
        raise ValueError("No stage events were found in the provided log text.")

    summary = summarize_pipeline(events)
    stage_metrics = analyze_stages(events)
    bottlenecks = identify_bottlenecks(stage_metrics)
    failure_patterns = analyze_failures(events)
    flaky_stages = detect_flaky_stages(events)
    suggestions = generate_suggestions(bottlenecks, failure_patterns, flaky_stages)

    return AnalysisReport(
        summary=summary,
        stage_metrics=stage_metrics,
        bottlenecks=bottlenecks,
        failure_patterns=failure_patterns,
        flaky_stages=flaky_stages,
        suggestions=suggestions,
    )
