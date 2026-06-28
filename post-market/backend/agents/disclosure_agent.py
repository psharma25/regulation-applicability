"""
Disclosure agent: turns a verified, triaged advisory into publishable artifacts.

Produces three things:
  1. advisory_md  -- human-readable security advisory (CVD output)
  2. csaf         -- a CSAF 2.0 / VEX document (machine-readable, what downstream
                     SBOM/VEX tooling and CISA expect)
  3. fda_report   -- a DRAFT reporting summary aligned to postmarket cybersecurity
                     expectations for cyber devices (FD&C 524B). Clearly marked as
                     a draft for regulatory review -- not legal/regulatory advice.

The LLM writes the prose where present; deterministic templates guarantee a valid,
complete artifact when it is not.
"""
import time

from . import base


def _vendor_meta(org):
    return {
        "name": org.get("name", "Example Medical, Inc."),
        "namespace": org.get("namespace", "https://psirt.example.com"),
        "contact": org.get("contact", "psirt@example.com"),
    }


def build_csaf(advisory, org):
    cve = advisory["cve_id"]
    detail = advisory.get("cve_detail") or {}
    triage = advisory.get("triage") or {}
    vex = triage.get("vex_status", "under_investigation")
    vendor = _vendor_meta(org)

    affected = triage.get("affected_devices", [])
    branches, product_ids, rels = [], [], []
    status_products = []
    for i, dev in enumerate(affected):
        pid = f"PROD-{i}"
        product_ids.append(pid)
        status_products.append(pid)
        branches.append({
            "category": "product_name",
            "name": dev["device_name"],
            "product": {
                "name": f"{dev['device_name']} ({dev.get('fda_number') or 'n/a'})",
                "product_id": pid,
            },
        })

    status_key = {
        "known_affected": "known_affected",
        "known_not_affected": "known_not_affected",
        "fixed": "fixed",
    }.get(vex, "under_investigation")

    vuln = {
        "cve": cve,
        "title": advisory.get("title"),
        "cwe": ({"id": detail.get("cwes", ["CWE-noinfo"])[0],
                 "name": detail.get("cwes", ["unknown"])[0]} if detail.get("cwes") else None),
        "product_status": {status_key: status_products or ["PROD-NONE"]},
        "flags": ([{"label": "vulnerable_code_not_present",
                    "product_ids": status_products or ["PROD-NONE"]}]
                  if status_key == "known_not_affected" else []),
        "scores": ([{"cvss_v3": {"baseScore": detail.get("cvss"),
                                 "baseSeverity": detail.get("severity")},
                     "products": status_products or ["PROD-NONE"]}]
                   if detail.get("cvss") else []),
        "remediations": [{
            "category": "vendor_fix" if status_key in ("known_affected", "fixed") else "none_available",
            "details": triage.get("remediation") or "See vendor advisory for fixed versions.",
            "product_ids": status_products or ["PROD-NONE"],
        }],
    }
    if vuln["cwe"] is None:
        vuln.pop("cwe")

    return {
        "document": {
            "category": "csaf_vex",
            "csaf_version": "2.0",
            "title": f"{vendor['name']} Security Advisory: {cve}",
            "publisher": {"category": "vendor", "name": vendor["name"],
                          "namespace": vendor["namespace"]},
            "tracking": {
                "id": advisory["id"],
                "status": "final",
                "version": "1",
                "initial_release_date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "current_release_date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "revision_history": [{"number": "1", "date": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                      time.gmtime()), "summary": "Initial release"}],
            },
        },
        "product_tree": {"branches": branches} if branches else {"branches": []},
        "vulnerabilities": [vuln],
    }


def build_advisory_md(advisory, org):
    cve = advisory["cve_id"]
    detail = advisory.get("cve_detail") or {}
    triage = advisory.get("triage") or {}
    ver = advisory.get("verification") or {}
    vendor = _vendor_meta(org)
    affected = triage.get("affected_devices", [])

    # LLM prose for the summary + impact, deterministic template otherwise.
    summary = None
    if base.llm_available():
        prompt = (
            f"Write a concise, factual security advisory body (no title, no markdown headers) "
            f"for a medical device manufacturer's PSIRT.\n"
            f"CVE: {cve}\nSeverity: {detail.get('severity')} (CVSS {detail.get('cvss')})\n"
            f"KEV/known-exploited: {detail.get('in_kev')}\n"
            f"Description: {detail.get('description')}\n"
            f"Affected products: {[d['device_name'] for d in affected]}\n"
            f"Verification result: {ver.get('status')} -- {ver.get('evidence')}\n"
            f"Triage rationale: {triage.get('rationale')}\n"
            f"Cover: summary, affected products, clinical/patient-safety impact in plain terms, "
            f"and recommended actions for healthcare delivery organizations. 4 short paragraphs max."
        )
        summary = base.generate(prompt, system="You are a medical device PSIRT advisory writer. Be precise and non-alarmist.")

    if not summary:
        prod_list = ", ".join(d["device_name"] for d in affected) or "under assessment"
        kev_line = (" This vulnerability is listed in the CISA Known Exploited Vulnerabilities "
                    "catalog and should be prioritized." if detail.get("in_kev") else "")
        summary = (
            f"{vendor['name']} is publishing this advisory regarding {cve}, a "
            f"{detail.get('severity','').lower()}-severity vulnerability (CVSS {detail.get('cvss')}).{kev_line}\n\n"
            f"Affected products: {prod_list}.\n\n"
            f"Triage assessment: {triage.get('rationale')}\n\n"
            f"Verification: status reported as '{ver.get('status','pending')}'. "
            f"Evidence: {ver.get('evidence','—')}.\n\n"
            f"Recommended actions: Healthcare delivery organizations should apply available "
            f"vendor remediations, validate compensating controls, and contact "
            f"{vendor['contact']} for deployment guidance."
        )

    lines = [
        f"# {vendor['name']} Security Advisory — {cve}",
        "",
        f"**Advisory ID:** {advisory['id']}  ",
        f"**CVE:** {cve}  ",
        f"**Severity:** {detail.get('severity')} (CVSS {detail.get('cvss')})  ",
        f"**Known exploited (CISA KEV):** {'Yes' if detail.get('in_kev') else 'No'}  ",
        f"**VEX status:** {triage.get('vex_status')}  ",
        f"**Published:** {time.strftime('%Y-%m-%d')}",
        "",
        "## Overview",
        summary,
        "",
        "## Affected products",
    ]
    if affected:
        for d in affected:
            comps = ", ".join(f"{m['component']} {m.get('version') or ''}".strip()
                              for m in d["matched_components"])
            lines.append(f"- **{d['device_name']}** "
                         f"({d.get('submission') or 'n/a'} {d.get('fda_number') or ''}) — "
                         f"affected component(s): {comps}")
    else:
        lines.append("- None identified (known_not_affected).")
    lines += [
        "",
        "## Contact",
        f"Coordinated disclosure contact: {vendor['contact']}",
        "",
        "_This advisory was produced through a coordinated vulnerability disclosure "
        "workflow with documented verification and multi-stakeholder sign-off._",
    ]
    return "\n".join(lines)


FDA_DISCLAIMER = ("DRAFT for regulatory review. Generated to support, not replace, the "
                  "manufacturer's regulatory and legal assessment. Reporting obligations, "
                  "timelines, and submission pathways must be confirmed by qualified "
                  "regulatory affairs and legal counsel.")


def build_fda_report(advisory, org):
    cve = advisory["cve_id"]
    detail = advisory.get("cve_detail") or {}
    triage = advisory.get("triage") or {}
    affected = triage.get("affected_devices", [])
    vendor = _vendor_meta(org)

    return {
        "disclaimer": FDA_DISCLAIMER,
        "manufacturer": vendor["name"],
        "cve": cve,
        "severity": detail.get("severity"),
        "cvss": detail.get("cvss"),
        "known_exploited": detail.get("in_kev"),
        "framework_notes": [
            "FD&C Act section 524B applies to 'cyber devices' (those including software, "
            "with internet connectivity, that could be vulnerable to cybersecurity threats).",
            "Postmarket cybersecurity: assess whether the vulnerability is an uncontrolled "
            "risk that may affect device safety/essential performance; controlled risks may "
            "not require reporting but must be documented.",
            "Coordinated disclosure and SBOM/VEX sharing are expected practices; this report "
            "pairs with the attached CSAF/VEX artifact.",
        ],
        "affected_devices": [
            {"device": d["device_name"], "submission": d.get("submission"),
             "fda_number": d.get("fda_number"),
             "components": [m["component"] for m in d["matched_components"]]}
            for d in affected
        ],
        "risk_determination": ("uncontrolled-risk-candidate" if (detail.get("in_kev")
                               or (detail.get("cvss") or 0) >= 9.0) else "assess"),
        "recommended_artifacts": ["security advisory (CSAF/VEX)", "risk assessment record",
                                  "remediation/mitigation plan", "customer notification"],
    }


def draft(advisory, org):
    return {
        "advisory_md": build_advisory_md(advisory, org),
        "csaf": build_csaf(advisory, org),
        "fda_report": build_fda_report(advisory, org),
        "drafted_at": time.time(),
    }
