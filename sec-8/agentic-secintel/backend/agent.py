"""Agentic loop.

Primary mode: a local open-source LLM served by Ollama (https://ollama.com).
The agent sends the tool schema, lets the model choose tools, executes them,
feeds results back, and iterates until the model answers. 100% open-source and
local — no data leaves the machine, no API keys.

Fallback mode: if Ollama is not reachable, a transparent heuristic planner calls
the same tools from keyword intent so the platform is fully usable out of the box.
"""
import os, re, json, requests
import tools as toolmod
import dataset

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")
MAX_STEPS = 5

SYSTEM = (
    "You are SecIntel, an analyst for a virtual CISO. You answer questions about a "
    "dataset of security incidents reported to U.S. state Attorneys General and/or the SEC. "
    "Always ground claims in the tools — call filter_incidents or compute_statistics before "
    "stating numbers, entities, or attribution. Be concise and executive-ready. When an "
    "incident is nation-state attributed, name the actor. Note when data is reported vs. "
    "estimated. Never invent incidents that the tools do not return."
)


def ollama_available():
    try:
        requests.get(f"{OLLAMA_URL}/api/tags", timeout=1.5)
        return True
    except Exception:
        return False


def _chat(messages):
    r = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={"model": OLLAMA_MODEL, "messages": messages, "tools": toolmod.TOOLS, "stream": False},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["message"]


def run_agent(user_message, filters=None, history=None):
    """Returns {reply, mode, trace:[{tool,args,result_summary}]}."""
    filters = filters or {}
    ctx = ""
    if filters.get("domain") and filters["domain"] != "All domains":
        ctx += f" The user is currently viewing the '{filters['domain']}' domain."
    if filters.get("product_id") and filters["product_id"] != "All products":
        ctx += f" Focused incident id: {filters['product_id']}."

    if not ollama_available():
        return _heuristic(user_message, filters)

    messages = [{"role": "system", "content": SYSTEM + ctx}]
    for h in (history or [])[-6:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_message})

    trace = []
    for _ in range(MAX_STEPS):
        try:
            msg = _chat(messages)
        except Exception as e:
            return {"reply": f"LLM error ({e}); falling back.", **_heuristic(user_message, filters)}
        calls = msg.get("tool_calls") or []
        if not calls:
            return {"reply": msg.get("content", "").strip() or "(no answer)", "mode": f"ollama:{OLLAMA_MODEL}", "trace": trace}
        messages.append(msg)
        for c in calls:
            fn = c["function"]["name"]
            args = c["function"].get("arguments") or {}
            if isinstance(args, str):
                try: args = json.loads(args)
                except Exception: args = {}
            result = toolmod.run_tool(fn, args)
            trace.append({"tool": fn, "args": args, "result_summary": _summarize(result)})
            messages.append({"role": "tool", "content": json.dumps(result)})
    return {"reply": "Reached step limit without a final answer.", "mode": f"ollama:{OLLAMA_MODEL}", "trace": trace}


def _summarize(result):
    if isinstance(result, dict):
        if "records_impacted" in result:  # stats dict
            return f"{result['incidents']} incidents, {result['records_impacted']:,} individuals"
        if "count" in result:             # filter result
            return f"{result['count']} incident(s)"
        if "entity" in result:            # single incident
            return result["entity"]
    return "ok"


# ---------------------------------------------------------------- heuristic
def _heuristic(user_message, filters):
    q = user_message.lower()
    trace = []
    domain = filters.get("domain") if filters.get("domain") not in (None, "All domains") else None
    for d in dataset.domains():
        if d.lower() in q:
            domain = d
    nation = True if re.search(r"nation.?state|china|russia|espionage|apt", q) else None
    threat = None
    for t in ["ransomware", "credential", "espionage", "device", "wiper", "social"]:
        if t in q:
            threat = {"ransomware": "Ransomware", "credential": "Credential theft",
                      "espionage": "Nation-state espionage", "device": "Device vulnerability",
                      "wiper": "Wiper / destructive", "social": "Social engineering"}[t]

    if any(w in q for w in ["how many", "statistic", "stats", "total", "count", "aggregate", "average"]):
        stats = toolmod.run_tool("compute_statistics", {"domain": domain, "nation_state": nation, "threat_category": threat})
        trace.append({"tool": "compute_statistics", "args": {"domain": domain, "nation_state": nation, "threat_category": threat}, "result_summary": _summarize(stats)})
        scope = domain or "all domains"
        reply = (f"Across {scope}{' (nation-state only)' if nation else ''}: "
                 f"**{stats['incidents']} incidents**, ~**{stats['records_impacted']:,} individuals** impacted, "
                 f"**{stats['nation_state']}** nation-state-attributed, **{stats['reported_sec']}** reported to the SEC, "
                 f"**{stats['reported_state_ag']}** reported to a state AG. "
                 f"Top threat types: {', '.join(list(stats['by_threat'])[:3])}.")
        return {"reply": reply, "mode": "heuristic (Ollama offline)", "trace": trace}

    res = toolmod.run_tool("filter_incidents", {"domain": domain, "nation_state": nation, "threat_category": threat})
    trace.append({"tool": "filter_incidents", "args": {"domain": domain, "nation_state": nation, "threat_category": threat}, "result_summary": _summarize(res)})
    rows = res["incidents"]
    if not rows:
        return {"reply": "No incidents in the seed dataset match that. Try a domain like 'Manufacturing' or 'FDA / Medical Device', or ask for nation-state incidents.", "mode": "heuristic (Ollama offline)", "trace": trace}
    lines = []
    for i in rows[:8]:
        tag = f" — nation-state: {i['attribution'].split(';')[0]}" if i["nation_state"] else ""
        sec = f", SEC {i['sec_item']}" if i["reported_sec"] else ""
        lines.append(f"• {i['entity']} ({i['year']}) — {i['threat_category']}, {i['impacted']}{sec}{tag}")
    head = f"{len(rows)} matching incident(s)" + (f" in {domain}" if domain else "") + (", nation-state only" if nation else "") + ":"
    note = "\n\n(Heuristic mode — start Ollama for full agentic reasoning. See README.)"
    return {"reply": head + "\n" + "\n".join(lines) + note, "mode": "heuristic (Ollama offline)", "trace": trace}
