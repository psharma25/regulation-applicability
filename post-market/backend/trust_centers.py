"""
Trust center / product-security registry, by company.

URLs verified against each vendor's own product-security pages and the
Health-ISAC Medical Device Manufacturer (MDM) Security directory
(https://health-isac.org/landing-page/mdm-security/), which curates manufacturer
product-security sites. Used to (a) give analysts a one-click jump to the
authoritative vendor source when triaging a component, and (b) attribute
security incidents to where the vendor officially publishes.

Verified: 2026-06. Vendor URLs change; the `source` directory is the fallback.
"""

DIRECTORY_SOURCE = "https://health-isac.org/landing-page/mdm-security/"

TRUST_CENTERS = [
    {
        "company": "Medtronic", "category": "MedTech", "sector": "MedTech",
        "trust_center": "https://www.medtronic.com/security",
        "advisories": "https://www.medtronic.com/en-us/e/product-security.html",
        "tags": ["CVD (ISO 29147)", "security bulletins", "HackerOne intake"],
        "note": "Coordinated disclosure program; publishes product security bulletins.",
    },
    {
        "company": "Philips", "category": "MedTech", "sector": "MedTech",
        "trust_center": "https://www.philips.com/security",
        "advisories": "https://www.philips.com/a-w/security/security-advisories.html",
        "tags": ["CVD", "dated advisories", "MDS2"],
        "note": "Maintains a dated, public product security advisory archive.",
    },
    {
        "company": "BD (Becton Dickinson)", "category": "MedTech", "sector": "MedTech",
        "trust_center": "https://www.bd.com/productsecurity",
        "advisories": "https://www.bd.com/productsecurity",
        "tags": ["CVE CNA", "publishes to CISA", "shares with H-ISAC"],
        "note": "First MedTech CVE Numbering Authority; tandem CISA disclosures.",
    },
    {
        "company": "GE HealthCare", "category": "MedTech", "sector": "MedTech",
        "trust_center": "https://www.gehealthcare.com/productsecurity/products",
        "advisories": "https://www.gehealthcare.com/productsecurity/products",
        "tags": ["CVD statement", "patch portal", "historical patch view"],
        "note": "Credentialed Product Security Portal with per-product patch status.",
    },
    {
        "company": "Baxter", "category": "MedTech", "sector": "MedTech",
        "trust_center": "https://www.baxter.com/product-security",
        "advisories": "https://www.baxter.com/product-security",
        "tags": ["CVD", "MDS2", "control framework"],
        "note": "Common Cybersecurity Control Framework for Medical Devices.",
    },
    {
        "company": "Siemens Healthineers", "category": "MedTech", "sector": "MedTech",
        "trust_center": "https://www.siemens-healthineers.com/support-documentation/cybersecurity",
        "advisories": "https://www.siemens-healthineers.com/support-documentation/cybersecurity",
        "tags": ["dated advisories", "teamplay Fleet portal"],
        "note": "Ongoing security advisories; customer portal for details.",
    },
    {
        "company": "Abbott", "category": "MedTech", "sector": "MedTech",
        "trust_center": "https://www.abbott.com/policies/cybersecurity/our-commitment-to-cybersecurity.html",
        "advisories": "https://www.abbott.com/policies/cybersecurity/our-commitment-to-cybersecurity.html",
        "tags": ["cybersecurity commitment", "CVD"],
        "note": "Product cybersecurity commitment and disclosure contact.",
    },
    {
        "company": "Boston Scientific", "category": "MedTech", "sector": "MedTech",
        "trust_center": "https://www.bostonscientific.com/en-US/customer-service/product-security.html",
        "advisories": "https://www.bostonscientific.com/en-US/customer-service/product-security.html",
        "tags": ["product security", "CVD"],
        "note": "Product security and vulnerability reporting.",
    },
    {
        "company": "B. Braun", "category": "MedTech", "sector": "MedTech",
        "trust_center": "https://www.bbraun.com/productsecurity",
        "advisories": "https://www.bbraun.com/productsecurity",
        "tags": ["product security", "CVD"],
        "note": "Product security portal and disclosure process.",
    },
    {
        "company": "Beckman Coulter", "category": "MedTech (Diagnostics)", "sector": "MedTech",
        "trust_center": "https://www.beckmancoulter.com/en/about-beckman-coulter/product-security",
        "advisories": "https://www.beckmancoulter.com/en/about-beckman-coulter/product-security",
        "tags": ["product security", "CVD"],
        "note": "Diagnostics product security and coordinated disclosure.",
    },
    {
        "company": "Arthrex", "category": "MedTech", "sector": "MedTech",
        "trust_center": "https://www.arthrex.com/product-security",
        "advisories": "https://www.arthrex.com/product-security",
        "tags": ["product security"],
        "note": "Product security information.",
    },
    # ---- OT / ICS vendors ----
    {
        "company": "Siemens ProductCERT", "category": "OT / ICS", "sector": "IT/OT",
        "trust_center": "https://www.siemens.com/cert",
        "advisories": "https://cert-portal.siemens.com/productcert/html/ssa.html",
        "tags": ["SSA advisories", "CSAF + RSS feeds", "reports to CISA"],
        "note": "Mature PSIRT; publishes Siemens Security Advisories (SSA) and CSAF feed.",
    },
    {
        "company": "Schneider Electric", "category": "OT / ICS", "sector": "IT/OT",
        "trust_center": "https://www.se.com/ww/en/work/support/cybersecurity/security-notifications.jsp",
        "advisories": "https://www.se.com/ww/en/work/support/cybersecurity/security-notifications.jsp",
        "tags": ["CPCERT / SEVD advisories", "CSAF", "reports to CISA"],
        "note": "Publishes SEVD security notifications (PDF + CSAF); coordinates with CISA.",
    },
    {
        "company": "Rockwell Automation", "category": "OT / ICS", "sector": "IT/OT",
        "trust_center": "https://www.rockwellautomation.com/en-us/trust-center/security-advisories.html",
        "advisories": "https://www.rockwellautomation.com/en-us/trust-center/security-advisories.html",
        "tags": ["PSIRT", "public advisory portal", "reports to CISA"],
        "note": "Trust Center with public security advisories; PSIRT rasecure@ra.rockwell.com.",
    },
    {
        "company": "Mitsubishi Electric", "category": "OT / ICS", "sector": "IT/OT",
        "trust_center": "https://www.mitsubishielectric.com/en/psirt/",
        "advisories": "https://www.mitsubishielectric.com/en/psirt/vulnerability/index.html",
        "tags": ["PSIRT", "MELSEC advisories"],
        "note": "PSIRT publishes vulnerability advisories; some products mitigation-only (no fix).",
    },
    {
        "company": "ABB", "category": "OT / ICS", "sector": "IT/OT",
        "trust_center": "https://global.abb/group/en/technology/cyber-security",
        "advisories": "https://global.abb/group/en/technology/cyber-security/alerts-and-notifications",
        "tags": ["cyber security alerts", "reports to CISA"],
        "note": "Cyber security alerts and notifications for ABB products.",
    },
    # ---- IT vendors ----
    {
        "company": "Microsoft (MSRC)", "category": "IT", "sector": "IT/OT",
        "trust_center": "https://msrc.microsoft.com/update-guide",
        "advisories": "https://msrc.microsoft.com/update-guide/vulnerability",
        "tags": ["SBOM component vendor", "monthly Patch Tuesday", "CSAF"],
        "note": "Common in device/IT SBOMs (Windows, .NET); Security Update Guide.",
    },
    {
        "company": "Cisco PSIRT", "category": "IT", "sector": "IT/OT",
        "trust_center": "https://sec.cloudapps.cisco.com/security/center/publicationListing.x",
        "advisories": "https://sec.cloudapps.cisco.com/security/center/publicationListing.x",
        "tags": ["PSIRT", "openVuln API", "CSAF"],
        "note": "Network/IT advisories; machine-readable openVuln API + CSAF.",
    },
    {
        "company": "Fortinet (FortiGuard PSIRT)", "category": "IT", "sector": "IT/OT",
        "trust_center": "https://www.fortiguard.com/psirt",
        "advisories": "https://www.fortiguard.com/psirt",
        "tags": ["PSIRT", "FG-IR advisories", "frequent KEV"],
        "note": "FortiOS / FortiGate advisories; several appear in CISA KEV.",
    },
    {
        "company": "Ivanti", "category": "IT", "sector": "IT/OT",
        "trust_center": "https://www.ivanti.com/blog/topics/security-advisory",
        "advisories": "https://forums.ivanti.com/s/security-advisories",
        "tags": ["security advisories", "frequent KEV"],
        "note": "Connect Secure / Policy Secure advisories; several appear in CISA KEV.",
    },
    {
        "company": "Progress (MOVEit)", "category": "IT", "sector": "IT/OT",
        "trust_center": "https://www.progress.com/security",
        "advisories": "https://community.progress.com/s/article/MOVEit-Transfer-Critical-Vulnerability",
        "tags": ["trust center", "MOVEit advisories", "KEV"],
        "note": "Managed file transfer; CVE-2023-34362 mass-exploited (CISA KEV).",
    },
    # ---- Authorities / directories ----
    {
        "company": "CISA ICS Advisories (ICSA)", "category": "Authority", "sector": "IT/OT",
        "trust_center": "https://www.cisa.gov/news-events/ics-advisories",
        "advisories": "https://www.cisa.gov/news-events/ics-advisories",
        "tags": ["ICSA", "OT/ICS/IoT", "co-published with vendors"],
        "note": "Government advisories for ICS/OT/IoT; co-published with manufacturers.",
    },
    {
        "company": "CISA KEV Catalog", "category": "Authority", "sector": "IT/OT",
        "trust_center": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        "advisories": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        "tags": ["known exploited", "actively exploited", "BOD 22-01"],
        "note": "Authoritative list of actively exploited CVEs; prioritize for remediation.",
    },
    {
        "company": "CISA ICS Medical Advisories", "category": "Authority", "sector": "MedTech",
        "trust_center": "https://www.cisa.gov/news-events/cybersecurity-advisories?f%5B0%5D=advisory_type%3A95",
        "advisories": "https://www.cisa.gov/news-events/cybersecurity-advisories?f%5B0%5D=advisory_type%3A95",
        "tags": ["ICSMA", "authoritative", "coordinated with vendors"],
        "note": "Government ICS Medical Advisories; co-published with manufacturers.",
    },
    {
        "company": "Health-ISAC MDM Directory", "category": "Authority", "sector": "MedTech",
        "trust_center": DIRECTORY_SOURCE,
        "advisories": DIRECTORY_SOURCE,
        "tags": ["directory", "manufacturer index"],
        "note": "Curated index of medical device manufacturer product-security sites.",
    },
]


def by_company():
    return {t["company"]: t for t in TRUST_CENTERS}


def match_for_supplier(supplier):
    """Best-effort link from an SBOM supplier/component to a trust center."""
    if not supplier:
        return None
    s = supplier.lower()
    for t in TRUST_CENTERS:
        c = t["company"].lower()
        if s in c or c.split()[0] in s:
            return t
    return None
