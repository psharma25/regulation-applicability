"""
SQLite data layer for the Medical Device CVD console.

No ORM on purpose: this stays dependency-light and easy to audit, which is what
a regulated PSIRT program wants. One file, plain SQL, JSON columns for the
flexible payloads (CVE detail, agent rationale, advisory document).
"""
import json
import os
import sqlite3
import threading
import time
from contextlib import contextmanager

DB_PATH = os.environ.get("CVD_DB_PATH", os.path.join(os.path.dirname(__file__), "cvd.db"))
_lock = threading.Lock()


SCHEMA = """
CREATE TABLE IF NOT EXISTS devices (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    model       TEXT,
    submission  TEXT,              -- 510(k) / PMA / De Novo / none
    fda_number  TEXT,              -- K-number or P-number
    cyber_device INTEGER DEFAULT 1,-- subject to FD&C 524B
    sbom        TEXT NOT NULL      -- JSON list of {component, version, cpe, supplier}
);

CREATE TABLE IF NOT EXISTS advisories (
    id            TEXT PRIMARY KEY,
    cve_id        TEXT NOT NULL,
    title         TEXT,
    source        TEXT,            -- NVD / KEV / MANUAL
    severity      TEXT,            -- CRITICAL/HIGH/MEDIUM/LOW/NONE
    cvss          REAL,
    in_kev        INTEGER DEFAULT 0,
    state         TEXT NOT NULL,   -- workflow state machine value
    cve_detail    TEXT,            -- JSON raw-ish detail used by agents
    triage        TEXT,            -- JSON {applicable, affected_devices[], rationale, agent_trace[]}
    verification  TEXT,            -- JSON {status, evidence, by, at}
    document      TEXT,            -- JSON {advisory_md, csaf, fda_report}
    cisa_url      TEXT,            -- authoritative CISA ICSMA / NVD link
    authority     TEXT,            -- "CISA ICSMA" / "NVD"
    ext_vendor    TEXT,            -- third-party vendor named in the CVE (if any)
    vendor_disclosed INTEGER,      -- 1/0/NULL: did that vendor disclose on its trust center
    vendor_disclosure_url TEXT,
    sector        TEXT,            -- "MedTech" / "IT/OT"
    created_at    REAL,
    updated_at    REAL,
    UNIQUE(cve_id)
);

CREATE TABLE IF NOT EXISTS signoffs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    advisory_id TEXT NOT NULL,
    role        TEXT NOT NULL,     -- security / legal / business / regulatory / ...
    decision    TEXT NOT NULL,     -- approved / rejected
    actor       TEXT,
    comment     TEXT,
    at          REAL,
    FOREIGN KEY (advisory_id) REFERENCES advisories(id)
);

CREATE TABLE IF NOT EXISTS audit (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    advisory_id TEXT,
    actor       TEXT,
    action      TEXT NOT NULL,
    detail      TEXT,
    at          REAL
);

CREATE TABLE IF NOT EXISTS config (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS incidents (
    id              TEXT PRIMARY KEY,
    vendor          TEXT NOT NULL,
    product         TEXT,
    title           TEXT NOT NULL,
    cve             TEXT,              -- may be null if vendor advisory has no CVE
    severity        TEXT,
    cvss            REAL,
    status          TEXT,              -- monitoring / mitigated / patch_available / resolved
    disclosed_date  TEXT,             -- YYYY-MM-DD (vendor/CISA advisory date)
    patch_available TEXT,             -- date or version when a fix was released
    patch_deployed  TEXT,             -- when/how the patch was deployed in the field
    source_url      TEXT,             -- authoritative vendor/CISA advisory link
    cisa_url        TEXT,             -- CISA ICSMA advisory link (CVE impacted per CISA)
    vendor_disclosed INTEGER,         -- did the vendor disclose on its trust center
    vendor_disclosure_url TEXT,
    trust_center    TEXT,             -- vendor trust center link
    affected_device TEXT,             -- optional link to internal device id
    sector          TEXT,             -- "MedTech" / "IT/OT"
    seeded          INTEGER DEFAULT 0,
    created_at      REAL,
    updated_at      REAL
);
"""

# Roles that must validate (sign off) before an advisory can publish. Org-configurable.
# Maps to the enterprise validation step: legal, business, security, communication.
DEFAULT_REQUIRED_ROLES = ["security", "legal", "business", "communication"]


@contextmanager
def conn():
    c = sqlite3.connect(DB_PATH, timeout=30)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init_db():
    with _lock, conn() as c:
        c.executescript(SCHEMA)
        cur = c.execute("SELECT value FROM config WHERE key='required_roles'")
        if cur.fetchone() is None:
            c.execute(
                "INSERT INTO config(key, value) VALUES('required_roles', ?)",
                (json.dumps(DEFAULT_REQUIRED_ROLES),),
            )


def get_required_roles():
    with conn() as c:
        row = c.execute("SELECT value FROM config WHERE key='required_roles'").fetchone()
        return json.loads(row["value"]) if row else DEFAULT_REQUIRED_ROLES


def set_required_roles(roles):
    with conn() as c:
        c.execute(
            "INSERT INTO config(key,value) VALUES('required_roles',?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (json.dumps(list(roles)),),
        )


def log(advisory_id, actor, action, detail=""):
    with conn() as c:
        c.execute(
            "INSERT INTO audit(advisory_id,actor,action,detail,at) VALUES(?,?,?,?,?)",
            (advisory_id, actor, action, detail, time.time()),
        )


def log_at(advisory_id, actor, action, detail, at):
    """Audit entry with an explicit timestamp (used by seeding for realistic timelines)."""
    with conn() as c:
        c.execute(
            "INSERT INTO audit(advisory_id,actor,action,detail,at) VALUES(?,?,?,?,?)",
            (advisory_id, actor, action, detail, at),
        )


# ---- device helpers ---------------------------------------------------------

def upsert_device(d):
    with conn() as c:
        c.execute(
            "INSERT INTO devices(id,name,model,submission,fda_number,cyber_device,sbom) "
            "VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET "
            "name=excluded.name, model=excluded.model, submission=excluded.submission, "
            "fda_number=excluded.fda_number, cyber_device=excluded.cyber_device, sbom=excluded.sbom",
            (d["id"], d["name"], d.get("model"), d.get("submission"),
             d.get("fda_number"), int(d.get("cyber_device", 1)), json.dumps(d["sbom"])),
        )


def list_devices():
    with conn() as c:
        rows = c.execute("SELECT * FROM devices ORDER BY name").fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["sbom"] = json.loads(d["sbom"])
            d["cyber_device"] = bool(d["cyber_device"])
            out.append(d)
        return out


# ---- advisory helpers -------------------------------------------------------

_JSON_FIELDS = ("cve_detail", "triage", "verification", "document")


def _row_to_advisory(r):
    a = dict(r)
    for f in _JSON_FIELDS:
        a[f] = json.loads(a[f]) if a.get(f) else None
    a["in_kev"] = bool(a["in_kev"])
    a["vendor_disclosed"] = (None if a.get("vendor_disclosed") is None else bool(a["vendor_disclosed"]))
    return a


def get_advisory(advisory_id):
    with conn() as c:
        r = c.execute("SELECT * FROM advisories WHERE id=?", (advisory_id,)).fetchone()
        if not r:
            return None
        a = _row_to_advisory(r)
        a["signoffs"] = [dict(s) for s in c.execute(
            "SELECT * FROM signoffs WHERE advisory_id=? ORDER BY at", (advisory_id,)).fetchall()]
        a["audit"] = [dict(x) for x in c.execute(
            "SELECT * FROM audit WHERE advisory_id=? ORDER BY at", (advisory_id,)).fetchall()]
        return a


def get_advisory_by_cve(cve_id):
    with conn() as c:
        r = c.execute("SELECT id FROM advisories WHERE cve_id=?", (cve_id,)).fetchone()
        return get_advisory(r["id"]) if r else None


def list_advisories():
    with conn() as c:
        rows = c.execute("SELECT * FROM advisories ORDER BY updated_at DESC").fetchall()
        return [_row_to_advisory(r) for r in rows]


def insert_advisory(a):
    now = a.get("created_at", time.time())
    with conn() as c:
        c.execute(
            "INSERT OR IGNORE INTO advisories"
            "(id,cve_id,title,source,severity,cvss,in_kev,state,cve_detail,"
            "cisa_url,authority,ext_vendor,vendor_disclosed,vendor_disclosure_url,"
            "sector,created_at,updated_at) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (a["id"], a["cve_id"], a.get("title"), a.get("source"), a.get("severity"),
             a.get("cvss"), int(a.get("in_kev", 0)), a["state"],
             json.dumps(a.get("cve_detail")),
             a.get("cisa_url"), a.get("authority"), a.get("ext_vendor"),
             (None if a.get("vendor_disclosed") is None else int(a.get("vendor_disclosed"))),
             a.get("vendor_disclosure_url"), a.get("sector"),
             now, a.get("updated_at", now)),
        )


def update_advisory(advisory_id, **fields):
    if not fields:
        return
    sets, vals = [], []
    for k, v in fields.items():
        if k in _JSON_FIELDS:
            v = json.dumps(v)
        sets.append(f"{k}=?")
        vals.append(v)
    sets.append("updated_at=?")
    vals.append(time.time())
    vals.append(advisory_id)
    with conn() as c:
        c.execute(f"UPDATE advisories SET {', '.join(sets)} WHERE id=?", vals)


def clear_signoffs(advisory_id):
    """Reset sign-offs for a fresh review round. Audit log retains full history."""
    with conn() as c:
        c.execute("DELETE FROM signoffs WHERE advisory_id=?", (advisory_id,))


def add_signoff(advisory_id, role, decision, actor, comment):
    with conn() as c:
        c.execute(
            "INSERT INTO signoffs(advisory_id,role,decision,actor,comment,at) VALUES(?,?,?,?,?,?)",
            (advisory_id, role, decision, actor, comment, time.time()),
        )


# ---- incidents --------------------------------------------------------------

def upsert_incident(inc):
    now = time.time()
    with conn() as c:
        c.execute(
            "INSERT INTO incidents(id,vendor,product,title,cve,severity,cvss,status,"
            "disclosed_date,patch_available,patch_deployed,source_url,cisa_url,"
            "vendor_disclosed,vendor_disclosure_url,trust_center,"
            "affected_device,sector,seeded,created_at,updated_at) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(id) DO UPDATE SET vendor=excluded.vendor,product=excluded.product,"
            "title=excluded.title,cve=excluded.cve,severity=excluded.severity,cvss=excluded.cvss,"
            "status=excluded.status,disclosed_date=excluded.disclosed_date,"
            "patch_available=excluded.patch_available,patch_deployed=excluded.patch_deployed,"
            "source_url=excluded.source_url,cisa_url=excluded.cisa_url,"
            "vendor_disclosed=excluded.vendor_disclosed,"
            "vendor_disclosure_url=excluded.vendor_disclosure_url,"
            "trust_center=excluded.trust_center,"
            "affected_device=excluded.affected_device,sector=excluded.sector,"
            "updated_at=excluded.updated_at",
            (inc["id"], inc["vendor"], inc.get("product"), inc["title"], inc.get("cve"),
             inc.get("severity"), inc.get("cvss"), inc.get("status"),
             inc.get("disclosed_date"), inc.get("patch_available"), inc.get("patch_deployed"),
             inc.get("source_url"), inc.get("cisa_url"),
             (None if inc.get("vendor_disclosed") is None else int(inc.get("vendor_disclosed"))),
             inc.get("vendor_disclosure_url"), inc.get("trust_center"),
             inc.get("affected_device"), inc.get("sector"), int(inc.get("seeded", 0)), now, now),
        )


def list_incidents():
    with conn() as c:
        rows = c.execute(
            "SELECT * FROM incidents ORDER BY COALESCE(disclosed_date,'') DESC, updated_at DESC"
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r); d["seeded"] = bool(d["seeded"])
            d["vendor_disclosed"] = (None if d.get("vendor_disclosed") is None else bool(d["vendor_disclosed"]))
            out.append(d)
        return out


def update_incident(incident_id, **fields):
    if not fields:
        return
    sets = [f"{k}=?" for k in fields]
    vals = list(fields.values())
    sets.append("updated_at=?"); vals.append(time.time()); vals.append(incident_id)
    with conn() as c:
        c.execute(f"UPDATE incidents SET {', '.join(sets)} WHERE id=?", vals)


def incidents_seeded():
    with conn() as c:
        return c.execute("SELECT COUNT(*) n FROM incidents").fetchone()["n"] > 0
