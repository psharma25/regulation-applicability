#!/usr/bin/env bash
# Regenerate the static GitHub Pages build (docs/) from the backend seed data.
set -e
cd "$(dirname "$0")/.."
python3 -c "import json; d=json.load(open('backend/data/incidents.json')); s=json.load(open('backend/data/agency_stats.json')); open('docs/data.js','w').write('window.SECINTEL_DATA = '+json.dumps(d,separators=(',',':'))+';\\nwindow.SECINTEL_STATS = '+json.dumps(s,separators=(',',':'))+';')"
cp frontend/styles.css docs/styles.css
echo "Rebuilt docs/data.js and docs/styles.css"
