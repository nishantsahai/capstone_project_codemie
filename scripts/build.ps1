$ErrorActionPreference = 'Stop'

# Build script for CI/CD Analyzer
# Usage (PowerShell):
#   .\scripts\build.ps1

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
  Write-Error "Virtual environment not found at .venv. Create it with: python -m venv .venv"
}

$py = ".venv\Scripts\python.exe"

& $py -m pip install -U pip
& $py -m pip install -e ".[dev]"
& $py -m pip install build

# Run tests
& $py -m pytest

# Build artifacts
New-Item -ItemType Directory -Force -Path "artifacts\dist" | Out-Null
& $py -m build --outdir "artifacts\dist"

Write-Host "Build complete. Artifacts are in artifacts/dist"