"""ransomware.live collector.

ransomware.live exposes a free public API that aggregates ransomware group
leak-site postings. We use it to derive recent victim volume and group
metadata. Endpoints are best-effort; the collector degrades gracefully if the
schema changes or the host is unreachable.
"""
from __future__ import annotations

from ..models import Evidence
from .base import BaseCollector


class RansomwareLiveCollector(BaseCollector):
    name = "ransomware.live"

    def _slug(self, actor_name: str) -> str:
        return actor_name.lower().replace(" ", "").replace("_", "")

    async def collect(self, actor_name: str, aliases: list[str]) -> list[Evidence]:
        base = self.settings.ransomwarelive_base
        names = [actor_name, *aliases]
        evidence: list[Evidence] = []

        async with self._client() as client:
            # Try a per-group endpoint first, then fall back to recent victims.
            for candidate in {self._slug(n) for n in names}:
                try:
                    r = await client.get(f"{base}/group/{candidate}")
                    if r.status_code == 200:
                        data = r.json()
                        victims = data.get("victims") or data.get("posts") or []
                        evidence.append(
                            Evidence(
                                source=self.name,
                                title=f"{actor_name}: {len(victims)} tracked victims",
                                url=f"https://www.ransomware.live/group/{candidate}",
                                snippet=(data.get("description") or "")[:600],
                                raw={"victim_count": len(victims)},
                            )
                        )
                        break
                except Exception:
                    continue

            # Recent cross-group victims, filtered to this actor.
            try:
                r = await client.get(f"{base}/recentvictims")
                if r.status_code == 200:
                    recent = r.json()
                    hits = [
                        v
                        for v in recent
                        if self._matches(v.get("group_name", ""), names)
                    ]
                    if hits:
                        sample = hits[0]
                        evidence.append(
                            Evidence(
                                source=self.name,
                                title=f"{actor_name}: {len(hits)} recent leak-site postings",
                                snippet=(
                                    f"Most recent victim sector: "
                                    f"{sample.get('activity', 'n/a')}; "
                                    f"country: {sample.get('country', 'n/a')}"
                                ),
                                raw={"recent_count": len(hits)},
                            )
                        )
            except Exception:
                pass

        return evidence
