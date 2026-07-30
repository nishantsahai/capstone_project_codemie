# Top 5 Gherkin test cases (CI/CD Pipeline Analyzer)

## 1) Analyze Jenkins log successfully via API
**Feature:** Analyze pipeline logs via API

Scenario: Analyze a valid Jenkins log
  Given the CI/CD Analyzer API is running
  When I POST "/analyze" with JSON:
    | source   | log_text                              |
    | jenkins  | Stage: Build - SUCCESS - 120 sec       |
  Then the response status should be 200
  And the response should include "summary"
  And the response should include "stage_metrics"
  And the summary should include "total_runs" greater than 0

## 2) Analyze GitHub Actions log successfully via API
Scenario: Analyze a valid GitHub Actions log
  Given the CI/CD Analyzer API is running
  When I POST "/analyze" with JSON:
    | source  | log_text                                                     |
    | github  | ::group::Test | FAILED | 220 sec | Error: AssertionError      |
  Then the response status should be 200
  And the response should include "failure_patterns"

## 3) API rejects empty log_text with consistent error envelope
Scenario: Reject empty log_text
  Given the CI/CD Analyzer API is running
  When I POST "/analyze" with JSON:
    | source  | log_text |
    | jenkins |         |
  Then the response status should be 400
  And the response JSON should have "error" = "Invalid request"
  And the response JSON should have "details" array with an item where "loc" contains "log_text"

## 4) API rejects unsupported source with consistent error envelope
Scenario: Reject unsupported source
  Given the CI/CD Analyzer API is running
  When I POST "/analyze" with JSON:
    | source | log_text                        |
    | foo    | Stage: Build - SUCCESS - 120 sec |
  Then the response status should be 400
  And the response JSON should have "error" = "Invalid request"
  And the response JSON should have "details" array with an item where "loc" contains "source"

## 5) Streamlit UI analyzes sample log and renders stage analysis
**Feature:** Analyze pipeline logs via UI

Scenario: Analyze sample Jenkins log in Streamlit UI
  Given the Streamlit UI is running
  And the "Load sample log" option is enabled
  When I click "Analyze log"
  Then I should see "Stage analysis"
  And I should see "Total runs"
