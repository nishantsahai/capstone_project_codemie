#!/usr/bin/env bash
set -euo pipefail

# Build script for CI/CD Analyzer
# Usage:
#   ./scripts/build.sh

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -x ".venv/Scripts/python.exe" && ! -x ".venv/bin/python" ]]; then
  echo "Virtual environment not found at .venv. Create it with: python -m venv .venv" >&2
  exit 1
fi

PY=".venv/bin/python"
if [[ -x ".venv/Scripts/python.exe" ]]; then
  PY=".venv/Scripts/python.exe"
fi

"$PY" -m pip install -U pip
"$PY" -m pip install -e ".[dev]"
"$PY" -m pip install build

"$PY" -m pytest

mkdir -p artifacts/dist
"$PY" -m build --outdir artifacts/dist

echo "Build complete. Artifacts are in artifacts/dist"