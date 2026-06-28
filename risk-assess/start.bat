@echo off
REM Double-click on Windows to run the program and open it in your browser.
cd /d %~dp0
echo Setting up Risk Assessment AI (first run installs dependencies)...
python -m venv .venv 2>nul
call .venv\Scripts\activate
pip install -q -r requirements.txt
start "" http://localhost:8000
echo Opening http://localhost:8000  (close this window or press Ctrl+C to stop)
uvicorn backend.main:app --port 8000
