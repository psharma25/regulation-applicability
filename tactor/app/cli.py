"""Headless CLI: run a scan and write the workbook without the web server.

    python -m app.cli            # full scan, writes xlsx to ./data
    python -m app.cli --no-llm   # force heuristic backend

Useful for cron / scheduled refreshes (the same pattern as a weekly auto-update).
"""
from __future__ import annotations

import argparse
import asyncio
import os

from .agent.orchestrator import Agent, new_scan
from .collectors.discovery import DiscoveryCollector
from .collectors.ransomwarelive import RansomwareLiveCollector
from .collectors.rss import CisaCollector, RssCollector
from .config import get_settings
from .export.workbook import build_workbook


async def main() -> None:
    parser = argparse.ArgumentParser(description="Threat actor reputation scan")
    parser.add_argument("--no-llm", action="store_true",
                        help="Force heuristic backend (skip Ollama)")
    args = parser.parse_args()
    if args.no_llm:
        os.environ["DISABLE_LLM"] = "1"

    agent = Agent(collectors=[
        RansomwareLiveCollector(), CisaCollector(), RssCollector(),
    ], discovery=DiscoveryCollector())
    scan = new_scan()
    await agent.run_scan(scan)
    path = build_workbook(scan, get_settings().data_dir)

    print("\n".join(scan.log))
    print(f"\nWorkbook: {path}")
    print(f"Discovered this scan: {scan.discovered_count}")
    print(f"{'Actor':<22}{'Severity':>10}{'Reliability':>14}{'  Source':<14}")
    for a in scan.actors:
        src = "discovered" if a.discovered else "seed"
        print(f"{a.name:<22}{a.threat_severity:>10}{a.deal_reliability:>14}  {src}")


if __name__ == "__main__":
    asyncio.run(main())
