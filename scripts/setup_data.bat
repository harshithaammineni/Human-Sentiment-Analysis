@echo off
REM ============================================================
REM  EEEM068 Human Sentiment Analysis -- one-click data setup
REM  Runs locally on Windows (works from VS Code terminal too).
REM
REM  Steps:
REM    1. Install Python dependencies into the active environment.
REM    2. Run scripts/download_data.py with scripts/data_sources.json.
REM
REM  Edit scripts/data_sources.json first and paste the three Google
REM  Drive file IDs from the MSCTD repo's README (En-De train/dev/test
REM  image archives).
REM ============================================================

setlocal
cd /d "%~dp0\.."
echo [setup_data] Project root: %CD%

echo.
echo [setup_data] Installing Python deps from requirements.txt ...
python -m pip install --upgrade pip
if errorlevel 1 goto :error
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo [setup_data] Running download_data.py ...
python scripts\download_data.py --config scripts\data_sources.json --strict-verify
if errorlevel 1 goto :error

echo.
echo [setup_data] DONE -- data/raw is ready. Open notebooks/01_dataset_preparation.ipynb in VS Code.
exit /b 0

:error
echo.
echo [setup_data] FAILED with error level %errorlevel%
echo   - Check that python and git are on your PATH.
echo   - Check that scripts\data_sources.json has real Google Drive file IDs.
echo   - To download text files only (no IDs needed) run:
echo       python scripts\download_data.py --skip-images
exit /b %errorlevel%
