# BitSense Blog

A dynamic, tag-searchable blog with server-side image/video upload and one-click
sharing to LinkedIn, X, Bluesky, Reddit, and email. FastAPI + SQLite backend,
vanilla-JS frontend, no build step.

## Features
- **Posts** in Markdown, with cover media, summary, and draft/published status
- **Tag taxonomy** with live counts; filter the feed by tag or free-text search
- **Media upload** — drag-and-drop or browse; images and video stored server-side
  and inserted into the post body automatically (first upload becomes the cover)
- **Share out** — every post and card has LinkedIn / X / Bluesky / Reddit / Email
  buttons plus copy-link
- **Edit / delete** from the post view
- Single SQLite file; uploads on local disk

## Run locally (one click)
```bash
./run.sh
```
Then open http://localhost:8000. On localhost, publishing is open — no token needed.

Manual alternative:
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Want sample content on a fresh DB? `python3 seed.py` adds two example posts.

## Run with Docker
```bash
docker compose up --build
```
Data (database + uploads) persists in the `blog-data` volume.

## Locking it down before going public
Write endpoints (create / edit / delete / upload) are **open when no token is set**.
Before exposing the site to the internet, set a token:
```bash
export ADMIN_TOKEN="a-long-random-string"
```
The frontend will then prompt for it on first publish and remember it in the browser.
Reads stay public; only writes require the token.

## Configuration (environment variables)
| Variable        | Default            | Purpose                                  |
|-----------------|--------------------|------------------------------------------|
| `ADMIN_TOKEN`   | _(unset = open)_   | Bearer token required for write actions  |
| `MAX_UPLOAD_MB` | `200`              | Per-file upload ceiling                  |
| `BLOG_DB`       | `./blog.db`        | SQLite path                              |
| `BLOG_UPLOADS`  | `./uploads`        | Media storage directory                  |

## Project layout
```
app/main.py        FastAPI app: posts CRUD, upload, tags, search
static/index.html  Frontend shell
static/styles.css  Design system
static/app.js      Feed, editor, upload, markdown, sharing
run.sh             venv + install + serve
Dockerfile         Container build
docker-compose.yml Container run with persistent volume
seed.py            Optional sample posts
```

## Notes
- The frontend renders Markdown itself (no external JS dependency); only the
  web fonts load from a CDN, with system-font fallback.
- Video is referenced in post bodies with `@[video](/uploads/…)`; images use
  standard `![alt](/uploads/…)`.
- Share links use public intent URLs — no API keys or app registration required.
