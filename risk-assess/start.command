#!/bin/bash
# Double-click on macOS to run the program and open it in your browser.
cd "$(dirname "$0")"
echo "Setting up Risk Assessment AI (first run installs dependencies)..."
python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install -q -r requirements.txt
python3 -c "import threading,webbrowser; threading.Timer(2.5, lambda: webbrowser.open('http://localhost:8000')).start()"
echo "Opening http://localhost:8000  (press Ctrl+C to stop)"
uvicorn backend.main:app --port 8000
