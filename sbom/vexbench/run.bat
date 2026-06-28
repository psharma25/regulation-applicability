@echo off
REM One-click run for Windows.
cd /d "%~dp0"
if not exist .venv (
  echo Creating virtualenv ...
  python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo.
echo Starting VEX Bench on http://localhost:8000
python app.py
