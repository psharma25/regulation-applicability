@echo off
cd /d "%~dp0"
python backend\data\build_data.py
pip install -r requirements.txt
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
