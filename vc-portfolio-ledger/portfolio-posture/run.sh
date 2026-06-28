#!/usr/bin/env bash
# PostureLedger — one-click local run. No build, no dependencies.
set -e
PORT="${1:-8000}"
echo "PostureLedger running at  http://localhost:${PORT}"
echo "Ctrl+C to stop."
if command -v python3 >/dev/null 2>&1; then
  python3 -m http.server "${PORT}"
elif command -v python >/dev/null 2>&1; then
  python -m SimpleHTTPServer "${PORT}"
else
  echo "No Python found. You can also just open index.html directly in a browser."
  exit 1
fi
