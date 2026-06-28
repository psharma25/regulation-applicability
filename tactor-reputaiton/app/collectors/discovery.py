"""Discovery collector.

Unlike the per-actor collectors, this one enumerates *which actors exist* on
public sources, so a scan can surface groups that are not yet in the seed
config. It queries ransomware.live for the current group roster and recent
victim postings, returning candidate group names with a recent victim count.

Returns [] on any failure, so discovery never blocks a scan.
"""
from __future__ import annotations

import httpx

from ..config import get_settings


class DiscoveryCollector:
    name = "discovery"

    def __init__(self) -> None:
        self.settings = get_settings()

    async def discover(self) -> list[dict]:
        base = self.settings.ransomwarelive_base
        candidates: dict[str, dict] = {}

        headers = {"User-Agent": self.settings.user_agent}
        async with httpx.AsyncClient(
            timeout=self.settings.http_timeout, headers=headers, follow_redirects=True
        ) as client:
            # 1) Full group roster.
            try:
                r = await client.get(f"{base}/groups")
                if r.status_code == 200:
                    for g in r.json():
                        name = (g.get("name") or g.get("group_name") or "").strip()
                        if name:
                            candidates.setdefault(
                                name,
                                {
                                    "name": name,
                                    "recent_count": 0,
                                    "sample_sector": None,
                                    "sample_country": None,
                                    "description": (g.get("description") or "")[:400],
                                },
                            )
            except Exception:
                pass

            # 2) Recent victims — gives us volume + which groups are active now.
            try:
                r = await client.get(f"{base}/recentvictims")
                if r.status_code == 200:
                    for v in r.json():
                        name = (v.get("group_name") or "").strip()
                        if not name:
                            continue
                        entry = candidates.setdefault(
                            name,
                            {"name": name, "recent_count": 0,
                             "sample_sector": None, "sample_country": None,
                             "description": ""},
                        )
                        entry["recent_count"] += 1
                        entry["sample_sector"] = entry["sample_sector"] or v.get("activity")
                        entry["sample_country"] = entry["sample_country"] or v.get("country")
            except Exception:
                pass

        return list(candidates.values())
