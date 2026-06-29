from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Iterable, List

from ..models.schema import StageEvent, StageMetrics
from .flaky_detector import detect_flaky


def analyze_stages(events: Iterable[StageEvent]) -> List[StageMetrics]:
    stage_history = defaultdict(list)
    for event in events:
        stage_history[event.stage].append(event)

    metrics: List[StageMetrics] = []
    for stage, stage_events in stage_history.items():
        durations = [event.duration_seconds for event in stage_events if event.duration_seconds is not None]
        average_duration = mean(durations) if durations else 0.0
        failure_count = sum(1 for event in stage_events if event.status == "FAILED")
        failure_rate = failure_count / len(stage_events) if stage_events else 0.0
        metrics.append(
            StageMetrics(
                stage=stage,
                average_duration_seconds=average_duration,
                failure_count=failure_count,
                total_runs=len(stage_events),
                failure_rate=failure_rate,
                flaky=detect_flaky([event.status for event in stage_events]),
            )
        )

    return sorted(metrics, key=lambda item: item.average_duration_seconds, reverse=True)
