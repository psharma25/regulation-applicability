"""Weekly scan scheduler (APScheduler). Runs the agentic scan on a cron cadence
so heavy work happens off the request path \u2014 users get instant cached results."""
from apscheduler.schedulers.background import BackgroundScheduler
from ..config import settings
from ..db import SessionLocal
from . import scan

_scheduler = None


def _job():
    db = SessionLocal()
    try:
        scan.run_scan(db)
    finally:
        db.close()


def start():
    global _scheduler
    if not settings.ENABLE_SCHEDULER or _scheduler:
        return
    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(_job, "cron", day_of_week=settings.SCAN_CRON_DAY,
                       hour=settings.SCAN_CRON_HOUR, id="weekly_scan",
                       replace_existing=True)
    _scheduler.start()
