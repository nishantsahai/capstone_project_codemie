# CI/CD Pipeline Analyzer

A small toolkit (FastAPI + Streamlit) to analyze CI/CD pipeline logs (Jenkins and GitHub Actions) and surface:
- stage metrics (avg duration, failure rate)
- bottlenecks
- failure patterns
- flaky stage insights

## Setup (recommended)

```bash
python -m venv .venv
# activate venv
pip install -e .[dev]
```

## Run the API

```bash
uvicorn ci_cd_analyzer.main:app --reload
```

## Run the Streamlit UI

```bash
streamlit run ci_cd_analyzer/ui/streamlit_app.py
```

## API usage

`POST /analyze`

Example:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"source":"jenkins","log_text":"Stage: Build - SUCCESS - 120 sec"}'
```

Validation errors return HTTP 400 with the following envelope:

```json
{
  "error": "Invalid request",
  "details": [
    {"loc": ["body", "log_text"], "msg": "log_text is required.", "type": "value_error"}
  ]
}
```
