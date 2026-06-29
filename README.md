# CI/CD Pipeline Analyzer

Tooling for parsing Jenkins and GitHub Actions logs, detecting failure trends, slow stages, flaky stages, and surfacing actionable suggestions.

## What is included

- FastAPI backend for log analysis
- Streamlit dashboard for interactive review
- Parsers for Jenkins-style and GitHub Actions-style logs
- Stage, failure, flaky-stage, and bottleneck analysis
- Example log files and unit tests

## Project layout

```
ci_cd_analyzer/
├── main.py
├── parser/
├── analyzer/
├── models/
├── utils/
└── ui/
```

## Run locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn ci_cd_analyzer.main:app --reload
```

Start the Streamlit dashboard:

```bash
streamlit run ci_cd_analyzer/ui/streamlit_app.py
```

## Input format examples

Jenkins example:

```text
Stage: Build - SUCCESS - 120 sec
Stage: Test - FAILED - 300 sec - Error: Timeout waiting for test container
```

GitHub Actions example:

```text
::group::Build | SUCCESS | 95 sec
::group::Test | FAILED | 220 sec | Error: AssertionError
```
