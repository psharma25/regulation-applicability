"""RSS-based collectors: CISA advisories and configurable threat-intel feeds.

These pull recent public reporting that mentions an actor by name or alias.
feedparser handles malformed feeds gracefully; network errors return [].
"""
from __future__ import annotations

import asyncio

import feedparser

from ..models import Evidence
from .base import BaseCollector


class _RssCollectorMixin(BaseCollector):
    feeds: list[str] = []
    max_items_per_actor: int = 5

    async def _fetch_feed(self, url: str) -> list[dict]:
        # feedparser is synchronous; run it off the event loop.
        def _parse() -> list[dict]:
            parsed = feedparser.parse(
                url, request_headers={"User-Agent": self.settings.user_agent}
            )
            return parsed.entries or []

        try:
            return await asyncio.to_thread(_parse)
        except Exception:
            return []

    async def collect(self, actor_name: str, aliases: list[str]) -> list[Evidence]:
        names = [actor_name, *aliases]
        out: list[Evidence] = []
        results = await asyncio.gather(*(self._fetch_feed(u) for u in self.feeds))
        for entries in results:
            for e in entries:
                blob = f"{e.get('title', '')} {e.get('summary', '')}"
                if self._matches(blob, names):
                    out.append(
                        Evidence(
                            source=self.name,
                            title=e.get("title", "")[:200],
                            url=e.get("link"),
                            snippet=e.get("summary", "")[:600],
                            published=e.get("published", ""),
                        )
                    )
                if len(out) >= self.max_items_per_actor:
                    break
        return out


class CisaCollector(_RssCollectorMixin):
    name = "CISA advisories"

    def __init__(self) -> None:
        super().__init__()
        self.feeds = [self.settings.cisa_feed]


class RssCollector(_RssCollectorMixin):
    name = "threat-intel RSS"

    def __init__(self) -> None:
        super().__init__()
        self.feeds = self.settings.extra_rss
