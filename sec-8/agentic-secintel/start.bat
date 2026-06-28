@echo off
REM One-click start for Windows. Double-click this file.
cd /d "%~dp0"
if not exist .venv ( python -m venv .venv )
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
if "%SEC_USER_AGENT%"=="" set SEC_USER_AGENT=SecIntel research client admin@example.com
start "" http://localhost:8000
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
