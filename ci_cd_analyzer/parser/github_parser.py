from __future__ import annotations

import re
from typing import List

from ..models.schema import StageEvent

GITHUB_STAGE_PATTERN = re.compile(
    r"^(?:::group::)?(?P<stage>[^|:]+?)\s*\|\s*(?P<status>SUCCESS|FAILED|SKIPPED|UNSTABLE|UNKNOWN)"
    r"(?:\s*\|\s*(?P<duration>\d+(?:\.\d+)?)\s*(?:sec|s|seconds?))?"
    r"(?:\s*\|\s*Error:\s*(?P<error>.+))?$",
    re.IGNORECASE,
)


def parse_github_log(log_text: str) -> List[StageEvent]:
    events: List[StageEvent] = []

    for raw_line in log_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        match = GITHUB_STAGE_PATTERN.match(line)
        if not match:
            continue

        duration_value = match.group("duration")
        events.append(
            StageEvent(
                stage=match.group("stage").strip(),
                status=match.group("status").upper(),
                duration_seconds=float(duration_value) if duration_value else None,
                error_message=match.group("error").strip() if match.group("error") else None,
                raw_line=raw_line,
            )
        )

    return events
