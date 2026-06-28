"""Domain mapping libraries used by both the Excel 'mapping' sheets and the API.

medical    -> Hazard mapping (ISO 14971 / ISO/TR 24971 Annex C style)
finance    -> Risk taxonomy (ISO 31000 / COSO / Basel)
technology -> Threat catalog (STRIDE / NIST / FAIR)
"""

MEDICAL_CATEGORIES = [
    "Electrical energy", "Thermal energy", "Mechanical energy", "Radiation energy",
    "Biological (infection)", "Chemical / biocompatibility", "Functional / loss of performance",
    "Software fault", "Information / labeling", "Use error", "Cybersecurity", "Environmental / EMC",
]

CONTROL_TYPES = ["Inherently safe design", "Protective measure", "Information for safety"]
AFFECTED_PARTIES = ["Patient", "User / Operator", "Bystander", "Service personnel", "Environment"]
FINANCE_CATEGORIES = ["Credit", "Market", "Liquidity", "Operational", "Compliance", "Strategic"]
TREATMENTS = ["Avoid", "Reduce", "Transfer / Insure", "Accept"]
STRIDE = ["Spoofing", "Tampering", "Repudiation", "Information disclosure",
          "Denial of service", "Elevation of privilege", "Supply chain", "IP theft"]
TECH_CONTROL_TYPES = ["Inherently secure design", "Protective measure", "Detective control", "Procedural control"]

LIBRARIES = {
    "medical": {
        "sheet": "Hazard Mapping",
        "title": "Hazard Mapping — ISO 14971 / ISO/TR 24971 (Annex C style)",
        "columns": ["Hazard category", "Hazard", "Typical hazardous situation", "Potential harm", "Typ. Severity"],
        "rows": [
            ["Electrical energy", "Leakage current / insulation failure", "Patient contacts live part", "Electric shock / burns", 4],
            ["Thermal energy", "Surface over-temperature", "Skin contact with hot surface", "Thermal burn", 3],
            ["Mechanical energy", "Sharp edge / moving part", "Contact during use or service", "Laceration / crush injury", 3],
            ["Radiation energy", "Excess dose / output", "Patient over-exposed", "Tissue damage / long-term cancer risk", 4],
            ["Biological (infection)", "Inadequate reprocessing / non-sterile", "Contaminated device used on patient", "Infection / sepsis", 4],
            ["Chemical / biocompatibility", "Leachables / cytotoxic material", "Prolonged tissue contact", "Toxic or allergic reaction", 3],
            ["Functional / loss of performance", "Therapy delivery failure", "Therapy not delivered or incorrect", "Injury from missed / incorrect therapy", 4],
            ["Software fault", "Logic error, crash, race condition", "Incorrect output or no output", "Misdiagnosis / wrong therapy", 4],
            ["Information / labeling", "Ambiguous IFU or labeling", "User misunderstands intended use", "Use error leading to harm", 3],
            ["Use error", "Confusing UI / alarm fatigue", "Critical step omitted or mis-set", "Delayed or incorrect treatment", 4],
            ["Cybersecurity", "Unauthorized access / tampering (STRIDE)", "Malicious change to settings or data", "Inappropriate therapy / data loss", 4],
            ["Environmental / EMC", "Electromagnetic interference", "Device malfunctions near EM source", "Temporary loss of function", 3],
        ],
        "dropdowns": {"category": MEDICAL_CATEGORIES, "control": CONTROL_TYPES, "affected": AFFECTED_PARTIES},
    },
    "finance": {
        "sheet": "Risk Taxonomy",
        "title": "Risk Taxonomy — ISO 31000 / COSO ERM / Basel",
        "columns": ["L1 Category", "L2 Subcategory", "Typical driver", "Example KRI", "Typical treatment"],
        "rows": [
            ["Credit", "Default risk", "Borrower deterioration / downturn", "NPL ratio", "Collateral + single-name limits"],
            ["Credit", "Concentration risk", "Sector or single-name exposure", "Single-name % of capital", "Diversification limits"],
            ["Market", "Interest-rate risk", "Rate volatility", "DV01 / duration gap", "Interest-rate swaps (hedging)"],
            ["Market", "FX risk", "Currency moves", "Open FX position", "FX hedges"],
            ["Market", "Equity / commodity", "Price volatility", "Value at Risk (VaR)", "Position limits"],
            ["Liquidity", "Funding liquidity", "Deposit outflow / loss of confidence", "LCR / NSFR", "Liquidity buffer + contingency funding plan"],
            ["Liquidity", "Market liquidity", "Asset illiquidity", "Days-to-liquidate / bid-ask", "Hold high-quality liquid assets"],
            ["Operational", "Process failure", "Manual error / breaks", "Error rate / reconciliation breaks", "Automation + controls"],
            ["Operational", "Fraud", "Internal or external fraud", "Fraud loss / alert volume", "Segregation of duties"],
            ["Operational", "Cyber / IT", "System compromise or outage", "Incident count / downtime", "Security & resilience controls"],
            ["Compliance", "AML / KYC", "Monitoring gaps", "SAR backlog", "Enhanced monitoring + KYC"],
            ["Compliance", "Conduct / regulatory", "Rule breaches", "Findings / fines", "Compliance program + training"],
            ["Strategic", "Business model", "Market / tech shift", "Revenue decline vs plan", "Strategy review + diversification"],
        ],
        "dropdowns": {"category": FINANCE_CATEGORIES, "treatment": TREATMENTS},
    },
    "technology": {
        "sheet": "Threat Catalog",
        "title": "Threat Catalog — STRIDE / NIST / FAIR (mapped to loss types)",
        "columns": ["STRIDE category", "Threat", "Example attack", "Affected asset", "Typical control", "Mapped loss types"],
        "rows": [
            ["Spoofing", "Identity spoofing", "Credential phishing / token theft", "Authentication system", "MFA + anomaly detection", "Reputation, Financial"],
            ["Tampering", "Data / parameter tampering", "Modify therapy or config in transit", "Device / API", "Input validation + signed payloads", "Financial, IP"],
            ["Repudiation", "Action repudiation", "Missing or alterable audit logs", "Logging system", "Tamper-evident logging", "Financial"],
            ["Information disclosure", "Data breach", "PII / PHI exfiltration", "Customer database", "Encryption at rest + DLP", "Reputation, Financial"],
            ["Denial of service", "Service outage", "Volumetric DDoS / resource exhaustion", "SaaS platform", "Rate limiting + multi-region HA", "Financial, Reputation"],
            ["Elevation of privilege", "Privilege escalation", "Exploit + lateral movement", "Servers / cloud accounts", "Least privilege + patching", "Financial, IP"],
            ["Supply chain", "Dependency compromise", "Malicious or copyleft dependency", "Build pipeline", "SBOM + licence scan + SLSA provenance", "IP, Financial"],
            ["IP theft", "Trade-secret exfiltration", "Insider copies source code", "Source-code repository", "Access monitoring + DLP + NDA", "IP"],
        ],
        "dropdowns": {"stride": STRIDE, "control": TECH_CONTROL_TYPES},
    },
}


def get(domain):
    return LIBRARIES.get(domain)
