"""Domain Excel template registry."""
from . import medical, finance, technology

GENERATORS = {
    "medical": {
        "label": "Medical Device (ISO 14971)",
        "description": "Patient-safety risk: Severity x Probability (P1 x P2), risk controls, residual risk, benefit-risk.",
        "build": medical.build,
        "filename": "medical_risk_assessment.xlsx",
    },
    "finance": {
        "label": "Finance (ISO 31000 / COSO / Basel)",
        "description": "Credit, market, liquidity, operational & compliance risk with Expected Annual Loss ($).",
        "build": finance.build,
        "filename": "finance_risk_assessment.xlsx",
    },
    "technology": {
        "label": "Technology (Reputation / Financial / IP loss)",
        "description": "Tech & cyber risk scored across reputation, financial and IP-loss dimensions (NIST / ISO 27005 / FAIR).",
        "build": technology.build,
        "filename": "technology_risk_assessment.xlsx",
    },
}


def domains():
    return [{"id": k, "label": v["label"], "description": v["description"]} for k, v in GENERATORS.items()]


def generate(domain, path):
    if domain not in GENERATORS:
        raise KeyError(domain)
    return GENERATORS[domain]["build"](path)
