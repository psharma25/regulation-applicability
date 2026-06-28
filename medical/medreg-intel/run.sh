#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 backend/data/build_data.py
python3 build_site.py
echo "Built docs/data.js and standalone index.html"
