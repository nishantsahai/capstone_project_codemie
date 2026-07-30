from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable

from ..models.schema import FailurePattern, StageEvent


def analyze_failures(events: Iterable[StageEvent]) -> list[FailurePattern]:
    failed_events = [event for event in events if event.status == "FAILED"]
    total_failures = len(failed_events)
    if total_failures == 0:
        return []

    errors_by_stage = defaultdict(Counter)
    failures_by_stage = Counter()

    for event in failed_events:
        failures_by_stage[event.stage] += 1
        if event.error_message:
            errors_by_stage[event.stage][event.error_message.strip()] += 1

    patterns: list[FailurePattern] = []
    for stage, failure_count in failures_by_stage.most_common():
        common_errors = [error for error, _ in errors_by_stage[stage].most_common(3)]
        patterns.append(
            FailurePattern(
                stage=stage,
                failure_count=failure_count,
                share_of_failures=failure_count / total_failures,
                common_errors=common_errors,
            )
        )

    return patterns
