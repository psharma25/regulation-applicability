#!/usr/bin/env python3
"""BitSense Compliance Agent - regulation register refresh.

Runs weekly in GitHub Actions (or on demand via workflow_dispatch). It maintains
regulations.json, which Security Policy Studio loads at runtime to flag documents
whose cited frameworks have changed. Offline/deterministic by design: it stamps a
scan date and preserves/updates a canonical register. Extend CANON or plug in an
authoritative feed (fda.gov, csrc.nist.gov, eur-lex, hhs.gov) as needed.

(c) 2026 BitSense. All rights reserved.
"""
import json, os, datetime

REG_PATH = os.path.join(os.path.dirname(__file__), "..", "regulations.json")

# Canonical register. 'updated' dates after the studio baseline (2026-01-31) cause
# the app to flag every document that references the framework.
CANON = [
  {"id":"iso27001","name":"ISO/IEC 27001","version":"2022 (+Amd 1:2024)","updated":"2024-02-01","note":"Amendment 1 (2024) adds climate-change consideration to 4.1/4.2.","match":["27001"]},
  {"id":"fda_524b","name":"FDA Premarket Cybersecurity / FD&C Act 524B","version":"Final guidance 2025-06-27","updated":"2025-06-27","note":"Final premarket cybersecurity guidance; mandatory SBOM, postmarket plan, CVD. Verify latest on fda.gov.","match":["524b","premarket cybersecurity","fda postmarket"]},
  {"id":"fda_qmsr","name":"FDA QMSR (21 CFR 820)","version":"QMSR effective 2026-02-02","updated":"2026-02-02","note":"QMSR aligns 21 CFR 820 with ISO 13485; effective 2 Feb 2026.","match":["21 cfr 820","qmsr"]},
  {"id":"eu_ai_act","name":"EU AI Act","version":"Reg (EU) 2024/1689 (+Digital Omnibus 2026)","updated":"2026-05-07","note":"Phased application; high-risk (incl. medical devices) deferred per Digital Omnibus. Verify dates.","match":["eu ai act","ai act"]},
  {"id":"eu_cra","name":"EU Cyber Resilience Act","version":"Reg (EU) 2024/2847","updated":"2024-12-10","note":"In force; main obligations ~Dec 2027. Verify phased dates.","match":["cyber resilience act","eu cra"]},
  {"id":"hipaa","name":"HIPAA Security & Breach Notification Rules","version":"45 CFR 160/164","updated":"2013-01-25","note":"Safeguards for ePHI + Breach Notification Rule. HHS proposed a Security Rule update (2025) - verify on hhs.gov.","match":["hipaa","ephi","45 cfr 164","protected health"]},
  {"id":"gdpr","name":"EU GDPR","version":"Reg (EU) 2016/679","updated":"2018-05-25","note":"Lawful basis, data-subject rights, 72-hour breach notification, transfers.","match":["gdpr","general data protection","data subject"]},
  {"id":"pqc_fips","name":"NIST PQC Standards (FIPS 203/204/205)","version":"Final 2024-08-13","updated":"2024-08-13","note":"ML-KEM, ML-DSA, SLH-DSA finalized; begin crypto-agility and migration planning.","match":["fips 203","fips 204","fips 205","ml-kem","ml-dsa","slh-dsa","post-quantum","post quantum"]},
]

def load_existing():
    try:
        with open(REG_PATH) as f:
            data = json.load(f)
        return data if isinstance(data, list) else data.get("regulations", [])
    except Exception:
        return []

def main():
    existing = {r["id"]: r for r in load_existing() if isinstance(r, dict) and r.get("id")}
    for r in CANON:
        existing[r["id"]] = {**existing.get(r["id"], {}), **r}
    out = {
        "generated": datetime.date.today().isoformat(),
        "source": "BitSense Compliance Agent",
        "regulations": sorted(existing.values(), key=lambda r: r.get("updated",""), reverse=True),
    }
    with open(REG_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {len(out['regulations'])} regulations to regulations.json ({out['generated']})")

if __name__ == "__main__":
    main()
