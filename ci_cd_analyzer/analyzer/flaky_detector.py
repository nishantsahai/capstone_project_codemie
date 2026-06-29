from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Sequence

from ..models.schema import FlakyStageInsight, StageEvent


def _canonical_status(status: str) -> str:
    normalized = status.upper()
    if normalized in {"SUCCESS", "PASSED", "PASS"}:
        return "PASS"
    if normalized in {"FAILED", "FAIL", "ERROR"}:
        return "FAIL"
    if normalized == "SKIPPED":
        return "SKIP"
    return "OTHER"


def detect_flaky(status_list: Sequence[str]) -> bool:
    canonical_statuses = [_canonical_status(status) for status in status_list]
    compact = "".join(status[0] for status in canonical_statuses if status in {"PASS", "FAIL"})
    if len(compact) < 4:
        return False
    if "PFPF" in compact or "FPFP" in compact:
        return True

    toggles = 0
    for left, right in zip(canonical_statuses, canonical_statuses[1:]):
        if left in {"PASS", "FAIL"} and right in {"PASS", "FAIL"} and left != right:
            toggles += 1

    return toggles >= 3 and {"PASS", "FAIL"}.issubset(set(canonical_statuses))


def detect_flaky_stages(events: Iterable[StageEvent]) -> List[FlakyStageInsight]:
    stage_history: Dict[str, List[str]] = defaultdict(list)
    for event in events:
        stage_history[event.stage].append(event.status)

    insights: List[FlakyStageInsight] = []
    for stage, statuses in stage_history.items():
        if not detect_flaky(statuses):
            continue

        normalized = [_canonical_status(status) for status in statuses]
        pattern = [status for status in normalized if status in {"PASS", "FAIL"}]
        insights.append(
            FlakyStageInsight(
                stage=stage,
                pattern=pattern,
                insight=f"{stage} alternates between passing and failing across runs, which is a flaky signal.",
            )
        )

    return insights
