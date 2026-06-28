"""
BitSense Blog — dynamic blog backend.

FastAPI + SQLite. Posts with Markdown bodies, tag taxonomy, full-text-ish
search, and server-side image/video upload. Write operations are gated behind
an optional admin token so the same build is safe to run locally (open) or
deploy publicly (locked).

Run:  uvicorn app.main:app --reload   (or use ./run.sh)
"""
import os
import re
import json
import sqlite3
import secrets
import mimetypes
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("BLOG_DB", BASE_DIR / "blog.db"))
UPLOAD_DIR = Path(os.environ.get("BLOG_UPLOADS", BASE_DIR / "uploads"))
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# If unset, write endpoints are OPEN (fine for localhost). Set this before
# exposing the site to the internet.
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "").strip()

MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "200"))
ALLOWED_MEDIA = {
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/avif", "image/svg+xml",
    "video/mp4", "video/webm", "video/quicktime", "video/ogg",
}

app = FastAPI(title="BitSense Blog", version="1.0.0")


# ---------------------------------------------------------------- database ---
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                slug        TEXT UNIQUE NOT NULL,
                title       TEXT NOT NULL,
                summary     TEXT NOT NULL DEFAULT '',
                body        TEXT NOT NULL DEFAULT '',
                tags        TEXT NOT NULL DEFAULT '[]',  -- json array
                cover       TEXT,                        -- media url
                status      TEXT NOT NULL DEFAULT 'published', -- draft|published
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at);
            CREATE INDEX IF NOT EXISTS idx_posts_status  ON posts(status);
            """
        )


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def slugify(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    s = re.sub(r"[\s_-]+", "-", s)
    return s[:80] or "post"


def unique_slug(conn, base: str, post_id: Optional[int] = None) -> str:
    slug, n = base, 1
    while True:
        row = conn.execute(
            "SELECT id FROM posts WHERE slug = ? AND id IS NOT ?",
            (slug, post_id),
        ).fetchone()
        if not row:
            return slug
        n += 1
        slug = f"{base}-{n}"


def normalize_tags(raw) -> list[str]:
    if isinstance(raw, str):
        raw = [t for t in re.split(r"[,\n]", raw)]
    out, seen = [], set()
    for t in raw or []:
        t = str(t).strip().lower()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def row_to_post(row) -> dict:
    d = dict(row)
    d["tags"] = json.loads(d.get("tags") or "[]")
    return d


# ------------------------------------------------------------------- auth ---
def require_admin(authorization: str = Header(default="")):
    """Open when ADMIN_TOKEN is unset; otherwise require a Bearer token."""
    if not ADMIN_TOKEN:
        return True
    token = authorization.replace("Bearer ", "").strip()
    if not token or not secrets.compare_digest(token, ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="Admin token required.")
    return True


# --------------------------------------------------------------- read API ---
@app.get("/api/config")
def get_config():
    """Frontend uses this to decide whether to show a token prompt."""
    return {"auth_required": bool(ADMIN_TOKEN), "max_upload_mb": MAX_UPLOAD_MB}


@app.get("/api/posts")
def list_posts(
    tag: Optional[str] = None,
    q: Optional[str] = None,
    status: str = "published",
    include_drafts: bool = False,
):
    where, params = [], []
    if not include_drafts:
        where.append("status = ?")
        params.append(status)
    if tag:
        where.append("EXISTS (SELECT 1 FROM json_each(posts.tags) WHERE value = ?)")
        params.append(tag.strip().lower())
    if q:
        where.append("(title LIKE ? OR summary LIKE ? OR body LIKE ?)")
        like = f"%{q}%"
        params += [like, like, like]
    sql = "SELECT * FROM posts"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY datetime(created_at) DESC"
    with db() as conn:
        rows = conn.execute(sql, params).fetchall()
    return {"posts": [row_to_post(r) for r in rows]}


@app.get("/api/posts/{slug}")
def get_post(slug: str):
    with db() as conn:
        row = conn.execute("SELECT * FROM posts WHERE slug = ?", (slug,)).fetchone()
    if not row:
        raise HTTPException(404, "Post not found.")
    return row_to_post(row)


@app.get("/api/tags")
def list_tags():
    """All tags with post counts, busiest first."""
    with db() as conn:
        rows = conn.execute(
            """
            SELECT value AS tag, COUNT(*) AS count
            FROM posts, json_each(posts.tags)
            WHERE posts.status = 'published'
            GROUP BY value ORDER BY count DESC, value ASC
            """
        ).fetchall()
    return {"tags": [dict(r) for r in rows]}


# -------------------------------------------------------------- write API ---
@app.post("/api/posts")
def create_post(payload: dict, _=Depends(require_admin)):
    title = (payload.get("title") or "").strip()
    if not title:
        raise HTTPException(400, "Title is required.")
    tags = normalize_tags(payload.get("tags"))
    ts = now_iso()
    with db() as conn:
        slug = unique_slug(conn, slugify(payload.get("slug") or title))
        cur = conn.execute(
            """INSERT INTO posts (slug, title, summary, body, tags, cover, status,
                                  created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                slug, title,
                (payload.get("summary") or "").strip(),
                payload.get("body") or "",
                json.dumps(tags),
                payload.get("cover") or None,
                "draft" if payload.get("status") == "draft" else "published",
                ts, ts,
            ),
        )
        row = conn.execute("SELECT * FROM posts WHERE id = ?", (cur.lastrowid,)).fetchone()
    return row_to_post(row)


@app.put("/api/posts/{slug}")
def update_post(slug: str, payload: dict, _=Depends(require_admin)):
    with db() as conn:
        row = conn.execute("SELECT * FROM posts WHERE slug = ?", (slug,)).fetchone()
        if not row:
            raise HTTPException(404, "Post not found.")
        title = (payload.get("title") or row["title"]).strip()
        new_slug = row["slug"]
        if payload.get("slug") and slugify(payload["slug"]) != row["slug"]:
            new_slug = unique_slug(conn, slugify(payload["slug"]), row["id"])
        tags = normalize_tags(payload["tags"]) if "tags" in payload else json.loads(row["tags"])
        conn.execute(
            """UPDATE posts SET slug=?, title=?, summary=?, body=?, tags=?, cover=?,
                                status=?, updated_at=? WHERE id=?""",
            (
                new_slug, title,
                payload.get("summary", row["summary"]).strip() if isinstance(payload.get("summary", row["summary"]), str) else row["summary"],
                payload.get("body", row["body"]),
                json.dumps(tags),
                payload.get("cover", row["cover"]) or None,
                "draft" if payload.get("status") == "draft" else ("published" if payload.get("status") == "published" else row["status"]),
                now_iso(), row["id"],
            ),
        )
        out = conn.execute("SELECT * FROM posts WHERE id = ?", (row["id"],)).fetchone()
    return row_to_post(out)


@app.delete("/api/posts/{slug}")
def delete_post(slug: str, _=Depends(require_admin)):
    with db() as conn:
        cur = conn.execute("DELETE FROM posts WHERE slug = ?", (slug,))
    if cur.rowcount == 0:
        raise HTTPException(404, "Post not found.")
    return {"deleted": slug}


# ----------------------------------------------------------------- upload ---
@app.post("/api/upload")
async def upload_media(file: UploadFile = File(...), _=Depends(require_admin)):
    ctype = file.content_type or mimetypes.guess_type(file.filename or "")[0] or ""
    if ctype not in ALLOWED_MEDIA:
        raise HTTPException(415, f"Unsupported media type: {ctype or 'unknown'}")
    ext = Path(file.filename or "").suffix or mimetypes.guess_extension(ctype) or ""
    name = f"{datetime.now():%Y%m%d-%H%M%S}-{secrets.token_hex(4)}{ext}"
    dest = UPLOAD_DIR / name
    size = 0
    limit = MAX_UPLOAD_MB * 1024 * 1024
    with dest.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > limit:
                out.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(413, f"File exceeds {MAX_UPLOAD_MB} MB limit.")
            out.write(chunk)
    kind = "video" if ctype.startswith("video/") else "image"
    return {"url": f"/uploads/{name}", "kind": kind, "type": ctype, "bytes": size}


@app.get("/uploads/{name}")
def serve_upload(name: str):
    safe = Path(name).name
    path = UPLOAD_DIR / safe
    if not path.exists():
        raise HTTPException(404, "Media not found.")
    return FileResponse(path)


# ------------------------------------------------------------------ pages ---
@app.get("/healthz")
def healthz():
    return {"ok": True}


# Static frontend (mounted last so /api/* takes precedence).
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


@app.on_event("startup")
def _startup():
    init_db()
