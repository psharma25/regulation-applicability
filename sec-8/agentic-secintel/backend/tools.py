"""Tools the agent can call. Each tool is a plain function over the dataset; the
TOOLS schema is sent to the LLM so it can decide which to invoke (function calling)."""
import json
import dataset

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "filter_incidents",
            "description": "Return security incidents filtered by domain, product, nation-state involvement, or threat category. Use this to look up which incidents match the user's question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "Industry/regulatory domain, e.g. 'Manufacturing', 'FDA / Medical Device', 'Telecom'. Omit for all."},
                    "product_id": {"type": "string", "description": "Specific incident id to fetch one entity. Omit for all."},
                    "nation_state": {"type": "boolean", "description": "True to return only nation-state-attributed incidents."},
                    "threat_category": {"type": "string", "description": "e.g. 'Ransomware', 'Nation-state espionage', 'Credential theft', 'Device vulnerability'."},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compute_statistics",
            "description": "Compute aggregate statistics (incident count, individuals impacted, nation-state count, SEC/state-AG reporting counts, totals by domain and threat) over a filtered set.",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "nation_state": {"type": "boolean"},
                    "threat_category": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_incident",
            "description": "Get the full record for a single incident by its id.",
            "parameters": {
                "type": "object",
                "properties": {"incident_id": {"type": "string"}},
                "required": ["incident_id"],
            },
        },
    },
]


def _slim(i):
    return {
        "id": i["id"], "entity": i["entity"], "domains": i["domains"], "year": i["year"],
        "threat_category": i["threat_category"], "impacted": i["impacted"],
        "reported_sec": i["reported_sec"], "sec_item": i["sec_item"],
        "reported_state_ag": i["reported_state_ag"], "nation_state": i["nation_state"],
        "attribution": i["attribution"], "financial_loss": i["financial_loss"],
    }


def run_tool(name, args):
    args = args or {}
    if name == "filter_incidents":
        rows = dataset.filter_incidents(
            domain=args.get("domain"), product_id=args.get("product_id"),
            nation_state=args.get("nation_state"), threat_category=args.get("threat_category"))
        return {"count": len(rows), "incidents": [_slim(i) for i in rows]}
    if name == "compute_statistics":
        rows = dataset.filter_incidents(
            domain=args.get("domain"), nation_state=args.get("nation_state"),
            threat_category=args.get("threat_category"))
        return dataset.compute_stats(rows)
    if name == "get_incident":
        i = dataset.get_incident(args.get("incident_id", ""))
        return i or {"error": "not found"}
    return {"error": f"unknown tool {name}"}
