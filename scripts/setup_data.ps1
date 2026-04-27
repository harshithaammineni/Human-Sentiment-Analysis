# EEEM068 Human Sentiment Analysis -- one-click data setup (PowerShell)
# Run from the project root or anywhere; this script cd's to the project root.

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
Write-Host "[setup_data] Project root: $projectRoot"

Write-Host "[setup_data] Installing Python deps from requirements.txt ..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "[setup_data] Running download_data.py ..."
python scripts/download_data.py --config scripts/data_sources.json --strict-verify

Write-Host "[setup_data] DONE -- data/raw is ready."
Write-Host "Open notebooks/01_dataset_preparation.ipynb in VS Code to continue."
