"""Collector base class.

A collector gathers public evidence about a named actor. Every collector must
be safe to run unattended: only public, free, non-login-walled sources, with
graceful degradation (return [] on any failure rather than raising).
"""
from __future__ import annotations

import httpx

from ..config import get_settings
from ..models import Evidence


class BaseCollector:
    name: str = "base"

    def __init__(self) -> None:
        self.settings = get_settings()

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self.settings.http_timeout,
            headers={"User-Agent": self.settings.user_agent},
            follow_redirects=True,
        )

    async def collect(self, actor_name: str, aliases: list[str]) -> list[Evidence]:
        raise NotImplementedError

    @staticmethod
    def _matches(text: str, names: list[str]) -> bool:
        low = (text or "").lower()
        return any(n.lower() in low for n in names if n)
