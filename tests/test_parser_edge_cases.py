from __future__ import annotations

from ci_cd_analyzer.parser.jenkins_parser import parse_jenkins_log


def test_jenkins_parser_is_case_insensitive_for_status() -> None:
    log_text = "Stage: Build - success - 2 sec\nStage: Test - failed - 1 sec\n"
    events = parse_jenkins_log(log_text)
    assert len(events) == 2
    assert events[0].status == "SUCCESS"
    assert events[1].status == "FAILED"
