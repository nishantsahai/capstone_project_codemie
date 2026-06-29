from __future__ import annotations

from pathlib import Path
import unittest

from ci_cd_analyzer.analyzer.flaky_detector import detect_flaky
from ci_cd_analyzer.parser.github_parser import parse_github_log
from ci_cd_analyzer.parser.jenkins_parser import parse_jenkins_log
from ci_cd_analyzer.utils.helpers import analyze_pipeline_log


class PipelineAnalysisTests(unittest.TestCase):
    def test_parse_jenkins_log(self) -> None:
        log_text = """
Stage: Build - SUCCESS - 120 sec
Stage: Test - FAILED - 300 sec - Error: Timeout waiting for test container
Stage: Deploy - SKIPPED
""".strip()

        events = parse_jenkins_log(log_text)
        self.assertEqual(3, len(events))
        self.assertEqual("Build", events[0].stage)
        self.assertEqual("FAILED", events[1].status)
        self.assertEqual(300.0, events[1].duration_seconds)

    def test_parse_github_log(self) -> None:
        log_text = """
::group::Build | SUCCESS | 95 sec
::group::Test | FAILED | 220 sec | Error: AssertionError
""".strip()

        events = parse_github_log(log_text)
        self.assertEqual(2, len(events))
        self.assertEqual("Build", events[0].stage)
        self.assertEqual("FAILED", events[1].status)
        self.assertEqual("AssertionError", events[1].error_message)

    def test_detect_flaky_sequence(self) -> None:
        self.assertTrue(detect_flaky(["SUCCESS", "FAILED", "SUCCESS", "FAILED"]))

    def test_build_report_for_jenkins_sample(self) -> None:
        log_text = Path("examples/jenkins_sample.log").read_text(encoding="utf-8")
        report = analyze_pipeline_log("jenkins", log_text)

        self.assertEqual(1, report.summary.total_runs)
        self.assertGreaterEqual(len(report.stage_metrics), 3)
        self.assertTrue(any(item.stage == "Test" for item in report.failure_patterns))
        self.assertTrue(any(item.stage == "Test" for item in report.flaky_stages))


if __name__ == "__main__":
    unittest.main()
