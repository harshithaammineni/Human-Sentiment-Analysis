#!/usr/bin/env bash
# EEEM068 Human Sentiment Analysis -- one-click data setup (bash).
# Works on Linux/macOS and on Windows via Git Bash.
set -euo pipefail

cd "$(dirname "$0")/.."
echo "[setup_data] Project root: $(pwd)"

echo "[setup_data] Installing Python deps from requirements.txt ..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "[setup_data] Running download_data.py ..."
python scripts/download_data.py --config scripts/data_sources.json --strict-verify

echo "[setup_data] DONE -- data/raw is ready."
echo "Open notebooks/01_dataset_preparation.ipynb in VS Code to continue."
