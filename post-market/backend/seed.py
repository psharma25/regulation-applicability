"""Seed a realistic medical-device inventory so the console is usable out of the box."""
import os
import time
import uuid

from . import db
from .agents import disclosure_agent, triage_agent

DAY = 86400
ORG = {
    "name": os.environ.get("ORG_NAME", "Meridian Medical Systems"),
    "namespace": os.environ.get("ORG_NAMESPACE", "https://psirt.meridianmed.example"),
    "contact": os.environ.get("ORG_CONTACT", "psirt@meridianmed.example"),
}

SEED_DEVICES = [
    {
        "id": "DEV-INFUSION-01", "name": "Aurora Infusion Pump", "model": "AIP-3000",
        "submission": "510(k)", "fda_number": "K221234", "cyber_device": 1,
        "sbom": [
            {"component": "openssl", "version": "3.0.8", "supplier": "OpenSSL",
             "cpe": "cpe:2.3:a:openssl:openssl:3.0.8:*:*:*:*:*:*:*"},
            {"component": "busybox", "version": "1.35.0", "supplier": "BusyBox",
             "cpe": "cpe:2.3:a:busybox:busybox:1.35.0:*:*:*:*:*:*:*"},
            {"component": "libcurl", "version": "7.85.0", "supplier": "curl",
             "cpe": "cpe:2.3:a:haxx:libcurl:7.85.0:*:*:*:*:*:*:*"},
            {"component": "freertos", "version": "10.4.6", "supplier": "Amazon",
             "cpe": "cpe:2.3:o:amazon:freertos:10.4.6:*:*:*:*:*:*:*"},
        ],
    },
    {
        "id": "DEV-MONITOR-02", "name": "Sentinel Patient Monitor", "model": "SPM-X1",
        "submission": "PMA", "fda_number": "P210045", "cyber_device": 1,
        "sbom": [
            {"component": "linux_kernel", "version": "5.15.0", "supplier": "Linux",
             "cpe": "cpe:2.3:o:linux:linux_kernel:5.15.0:*:*:*:*:*:*:*"},
            {"component": "openssl", "version": "1.1.1t", "supplier": "OpenSSL",
             "cpe": "cpe:2.3:a:openssl:openssl:1.1.1t:*:*:*:*:*:*:*"},
            {"component": "dropbear", "version": "2022.83", "supplier": "Dropbear",
             "cpe": "cpe:2.3:a:dropbear_ssh_project:dropbear_ssh:2022.83:*:*:*:*:*:*:*"},
            {"component": "mqtt", "version": "1.6.15", "supplier": "Eclipse Mosquitto",
             "cpe": "cpe:2.3:a:eclipse:mosquitto:1.6.15:*:*:*:*:*:*:*"},
        ],
    },
    {
        "id": "DEV-IMAGING-03", "name": "Lumen Imaging Workstation", "model": "LIW-700",
        "submission": "510(k)", "fda_number": "K198877", "cyber_device": 1,
        "sbom": [
            {"component": "windows_10_iot", "version": "21H2", "supplier": "Microsoft",
             "cpe": "cpe:2.3:o:microsoft:windows_10:21h2:*:*:*:*:*:*:*"},
            {"component": "dcmtk", "version": "3.6.7", "supplier": "OFFIS",
             "cpe": "cpe:2.3:a:offis:dcmtk:3.6.7:*:*:*:*:*:*:*"},
            {"component": "log4j", "version": "2.17.1", "supplier": "Apache",
             "cpe": "cpe:2.3:a:apache:log4j:2.17.1:*:*:*:*:*:*:*"},
        ],
    },
    # ---- IT/OT estate (connected lab/industrial products and gateways the org ships/operates) ----
    {
        "id": "DEV-LABCTRL-04", "name": "Steratec Lab Automation Controller", "model": "LAC-200",
        "submission": "Class I exempt", "fda_number": "—", "cyber_device": 1,
        "sbom": [
            {"component": "jquery", "version": "3.4.1", "supplier": "jQuery",
             "cpe": "cpe:2.3:a:jquery:jquery:3.4.1:*:*:*:*:*:*:*"},
            {"component": "openssl", "version": "3.0.8", "supplier": "OpenSSL",
             "cpe": "cpe:2.3:a:openssl:openssl:3.0.8:*:*:*:*:*:*:*"},
            {"component": "busybox", "version": "1.35.0", "supplier": "BusyBox",
             "cpe": "cpe:2.3:a:busybox:busybox:1.35.0:*:*:*:*:*:*:*"},
        ],
    },
    {
        "id": "DEV-GATEWAY-05", "name": "MeridianConnect IoT Gateway", "model": "MCG-10",
        "submission": "n/a (infrastructure)", "fda_number": "—", "cyber_device": 1,
        "sbom": [
            {"component": "libcurl", "version": "7.85.0", "supplier": "Haxx",
             "cpe": "cpe:2.3:a:haxx:libcurl:7.85.0:*:*:*:*:*:*:*"},
            {"component": "mosquitto", "version": "2.0.14", "supplier": "Eclipse",
             "cpe": "cpe:2.3:a:eclipse:mosquitto:2.0.14:*:*:*:*:*:*:*"},
            {"component": "openssl", "version": "1.1.1t", "supplier": "OpenSSL",
             "cpe": "cpe:2.3:a:openssl:openssl:1.1.1t:*:*:*:*:*:*:*"},
        ],
    },
]


def ensure_seed():
    if db.list_devices():
        return
    for d in SEED_DEVICES:
        db.upsert_device(d)


# Illustrative incidents sourced from public vendor / CISA advisories (verified 2026-06).
# patch_deployed wording mirrors what the source actually stated; where deployment is
# rolling or customer-applied, that is said plainly rather than inventing a date.
SEED_INCIDENTS = [
    {
        "id": "INC-CONTEC-CMS8000",
        "vendor": "Contec Health", "product": "CMS8000 Patient Monitor (rebadged Epsimed MN-120)",
        "title": "Embedded backdoor + out-of-bounds write (RCE) + plaintext patient-data spillage",
        "cve": "CVE-2024-12248", "severity": "CRITICAL", "cvss": 9.8,
        "status": "monitoring",
        "disclosed_date": "2025-01-30",
        "patch_available": "None — CISA/FDA advised removing devices from networks",
        "patch_deployed": "No vendor patch; mitigation = remove/segment device",
        "source_url": "https://www.cisa.gov/news-events/ics-medical-advisories/icsma-25-030-01",
        "cisa_url": "https://www.cisa.gov/news-events/ics-medical-advisories/icsma-25-030-01",
        "vendor_disclosed": 0, "vendor_disclosure_url": None,
        "trust_center": None,
    },
    {
        "id": "INC-MDT-PACEART",
        "vendor": "Medtronic", "product": "Paceart Optima System",
        "title": "Deserialization of untrusted data in optional Paceart Messaging Service (RCE/DoS)",
        "cve": "CVE-2023-31222", "severity": "CRITICAL", "cvss": 9.8,
        "status": "patch_available",
        "disclosed_date": "2023-06-29",
        "patch_available": "Vendor software update; interim mitigation: disable optional messaging service",
        "patch_deployed": "Customer-applied via vendor update; interim service-disable provided",
        "source_url": "https://www.cisa.gov/news-events/ics-medical-advisories/icsma-23-180-01",
        "cisa_url": "https://www.cisa.gov/news-events/ics-medical-advisories/icsma-23-180-01",
        "vendor_disclosed": 1, "vendor_disclosure_url": "https://www.medtronic.com/security",
        "trust_center": "https://www.medtronic.com/security",
    },
    {
        "id": "INC-BD-SYNAPSYS",
        "vendor": "BD (Becton Dickinson)", "product": "BD Diagnostic Solutions / Synapsys",
        "title": "Default credentials on affected diagnostic products",
        "cve": None, "severity": "HIGH", "cvss": 8.2,
        "status": "mitigated",
        "disclosed_date": "2024-12-17",
        "patch_available": "Remediation developed by BD",
        "patch_deployed": "Rolling — deployed via BD Field Service; majority scheduled H1 2025",
        "source_url": "https://www.cisa.gov/news-events/ics-medical-advisories/icsma-24-352-01",
        "cisa_url": "https://www.cisa.gov/news-events/ics-medical-advisories/icsma-24-352-01",
        "vendor_disclosed": 1, "vendor_disclosure_url": "https://www.bd.com/productsecurity",
        "trust_center": "https://www.bd.com/productsecurity",
    },
    {
        "id": "INC-PHI-ISP",
        "vendor": "Philips", "product": "IntelliSpace Portal & Advanced Visualization Workspace",
        "title": "Unauthenticated remote code execution / server file confidentiality",
        "cve": None, "severity": "HIGH", "cvss": None,
        "status": "mitigated",
        "disclosed_date": "2025-04-10",
        "patch_available": "Customer-applied mitigations; software-only products with customer OS",
        "patch_deployed": "Per Philips field action / customer-validated procedure",
        "source_url": "https://www.philips.com/a-w/security/security-advisories/product-security-2025.html",
        "cisa_url": None,
        "vendor_disclosed": 1,
        "vendor_disclosure_url": "https://www.philips.com/a-w/security/security-advisories.html",
        "trust_center": "https://www.philips.com/security",
    },
    {
        "id": "INC-SHS-SYNGO",
        "vendor": "Siemens Healthineers", "product": "syngo.plaza VB30E",
        "title": "Insecure password encryption vulnerability",
        "cve": None, "severity": "MEDIUM", "cvss": None,
        "status": "patch_available",
        "disclosed_date": "2026-02-10",
        "patch_available": "Update available via teamplay Fleet portal",
        "patch_deployed": "Customer-applied via teamplay Fleet customer portal",
        "source_url": "https://www.siemens-healthineers.com/support-documentation/cybersecurity",
        "cisa_url": None,
        "vendor_disclosed": 1,
        "vendor_disclosure_url": "https://www.siemens-healthineers.com/support-documentation/cybersecurity",
        "trust_center": "https://www.siemens-healthineers.com/support-documentation/cybersecurity",
    },
]


def ensure_incident_seed():
    if db.incidents_seeded():
        return
    for inc in SEED_INCIDENTS + SEED_INCIDENTS_ITOT:
        inc = dict(inc); inc["seeded"] = 1
        inc.setdefault("sector", "MedTech")
        db.upsert_incident(inc)


# Third-party IT/OT advisories affecting the enterprise's operated estate (plant
# OT + corporate IT). Real CVEs from CISA ICS Advisories / CISA KEV. Vendor
# disclosure status reflects each vendor's public posture; patch_deployed is the
# (synthetic) org rollout note, while patch_available reflects the real vendor fix.
SEED_INCIDENTS_ITOT = [
    {
        "id": "INC-SE-POWERLOGIC", "sector": "IT/OT",
        "vendor": "Schneider Electric", "product": "PowerLogic HDPM6000",
        "title": "Authorization bypass + Modbus memory-buffer write (EoP / DoS)",
        "cve": "CVE-2024-10497", "severity": "HIGH", "cvss": 8.8, "status": "resolved",
        "disclosed_date": "2025-01-28",
        "patch_available": "Fixed in HDPM6000 v0.62.11 (SEVD per CISA ICSA-25-028-02)",
        "patch_deployed": "2025-03-14 — firmware v0.62.11 applied to plant power-meters; Modbus segmented",
        "source_url": "https://www.cisa.gov/news-events/ics-advisories/icsa-25-028-02",
        "cisa_url": "https://www.cisa.gov/news-events/ics-advisories/icsa-25-028-02",
        "vendor_disclosed": 1,
        "vendor_disclosure_url": "https://www.se.com/ww/en/work/support/cybersecurity/security-notifications.jsp",
        "trust_center": "https://www.se.com/ww/en/work/support/cybersecurity/security-notifications.jsp",
    },
    {
        "id": "INC-SIE-IAM", "sector": "IT/OT",
        "vendor": "Siemens", "product": "Industrial products (IAM client)",
        "title": "Missing TLS server-certificate validation (machine-in-the-middle)",
        "cve": "CVE-2025-40800", "severity": "HIGH", "cvss": 7.4, "status": "patch_available",
        "disclosed_date": "2025-12-11",
        "patch_available": "Per Siemens SSA-868571 (update / network hardening)",
        "patch_deployed": "Scheduled — next OT maintenance window; interim network protection applied",
        "source_url": "https://www.cisa.gov/news-events/ics-advisories/icsa-25-345-04",
        "cisa_url": "https://www.cisa.gov/news-events/ics-advisories/icsa-25-345-04",
        "vendor_disclosed": 1, "vendor_disclosure_url": "https://www.siemens.com/cert",
        "trust_center": "https://www.siemens.com/cert",
    },
    {
        "id": "INC-RA-MICRO8XX", "sector": "IT/OT",
        "vendor": "Rockwell Automation", "product": "Micro850 / Micro870 controllers",
        "title": "Malformed CIP/IPv6 packet handling — recoverable fault (DoS)",
        "cve": "CVE-2025-13824", "severity": "HIGH", "cvss": 7.5, "status": "patch_available",
        "disclosed_date": "2025-12-18",
        "patch_available": "Rockwell firmware update (per CISA advisory)",
        "patch_deployed": "Planned — staged to line PLCs after validation; ingress CIP filtering in place",
        "source_url": "https://www.rockwellautomation.com/en-us/trust-center/security-advisories.html",
        "cisa_url": "https://www.cisa.gov/news-events/ics-advisories",
        "vendor_disclosed": 1,
        "vendor_disclosure_url": "https://www.rockwellautomation.com/en-us/trust-center/security-advisories.html",
        "trust_center": "https://www.rockwellautomation.com/en-us/trust-center/security-advisories.html",
    },
    {
        "id": "INC-ME-MELSEC", "sector": "IT/OT",
        "vendor": "Mitsubishi Electric", "product": "MELSEC iQ-F series CPU",
        "title": "Cleartext transmission of credentials over SLMP (info disclosure)",
        "cve": "CVE-2025-7731", "severity": "HIGH", "cvss": 7.5, "status": "mitigated",
        "disclosed_date": "2025-09-02",
        "patch_available": "No fixed version planned — vendor recommends VPN/segmentation",
        "patch_deployed": "No vendor fix — mitigated via OT VLAN segmentation + encrypted transport",
        "source_url": "https://www.mitsubishielectric.com/en/psirt/",
        "cisa_url": "https://www.cisa.gov/news-events/ics-advisories",
        "vendor_disclosed": 1, "vendor_disclosure_url": "https://www.mitsubishielectric.com/en/psirt/",
        "trust_center": "https://www.mitsubishielectric.com/en/psirt/",
    },
    {
        "id": "INC-PROGRESS-MOVEIT", "sector": "IT/OT",
        "vendor": "Progress Software", "product": "MOVEit Transfer (managed file transfer)",
        "title": "SQL injection → unauthorized DB access / RCE (mass-exploited)",
        "cve": "CVE-2023-34362", "severity": "CRITICAL", "cvss": 9.8, "status": "resolved",
        "disclosed_date": "2023-06-01",
        "patch_available": "Progress patched releases (CISA KEV — actively exploited)",
        "patch_deployed": "2023-06-02 — emergency patch applied; IOCs swept, no compromise found",
        "source_url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        "cisa_url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        "vendor_disclosed": 1, "vendor_disclosure_url": "https://www.progress.com/security",
        "trust_center": "https://www.progress.com/security",
    },
    {
        "id": "INC-FORTINET-FORTIOS", "sector": "IT/OT",
        "vendor": "Fortinet", "product": "FortiOS SSL-VPN (perimeter)",
        "title": "Out-of-bounds write → unauthenticated RCE",
        "cve": "CVE-2024-21762", "severity": "CRITICAL", "cvss": 9.6, "status": "resolved",
        "disclosed_date": "2024-02-08",
        "patch_available": "FortiGuard PSIRT FG-IR-24-015 (CISA KEV — actively exploited)",
        "patch_deployed": "2024-02-09 — FortiOS upgraded on all gateways; SSL-VPN disabled during window",
        "source_url": "https://www.fortiguard.com/psirt",
        "cisa_url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        "vendor_disclosed": 1, "vendor_disclosure_url": "https://www.fortiguard.com/psirt",
        "trust_center": "https://www.fortiguard.com/psirt",
    },
]


def ensure_disclosure_seed():
    if db.list_advisories():
        return
    devices = db.list_devices()
    for spec in SEED_DISCLOSURES + SEED_DISCLOSURES_ITOT:
        _seed_one(spec, devices)


# IT/OT disclosures: the enterprise's own connected lab/industrial products
# (driven by component CVEs that match their SBOMs) plus a notable third-party
# OT CVE assessed as not-applicable to show the cross-reference.
SEED_DISCLOSURES_ITOT = [
    {
        "cve": "CVE-2020-11023", "severity": "MEDIUM", "cvss": 6.9, "in_kev": True, "sector": "IT/OT",
        "title": "jQuery: passing crafted HTML to manipulation methods can execute untrusted code (XSS)",
        "cpes": ["cpe:2.3:a:jquery:jquery:3.4.1:*:*:*:*:*:*:*"], "cwes": ["CWE-79"],
        "authority": "CISA KEV", "cisa_url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        "ext_vendor": None, "vendor_disclosed": None, "vendor_disclosure_url": None,
        "state": "PUBLISHED", "days_ago": 15, "durations": [0.5, 2.0, 1.0, 3.0, 0.5],
        "evidence": "jQuery 3.4.1 bundled in Steratec LAC-200 web UI; upgraded to 3.5.1. Verified no exploit path in shipped config.",
    },
    {
        "cve": "CVE-2022-32221", "severity": "HIGH", "cvss": 8.1, "in_kev": False, "sector": "IT/OT",
        "title": "curl/libcurl: POST-after-PUT may reuse wrong credentials / read freed memory",
        "cpes": ["cpe:2.3:a:haxx:libcurl:7.85.0:*:*:*:*:*:*:*"], "cwes": ["CWE-416"],
        "authority": "NVD", "cisa_url": "https://nvd.nist.gov/vuln/detail/CVE-2022-32221",
        "ext_vendor": None, "vendor_disclosed": None, "vendor_disclosure_url": None,
        "state": "IN_REVIEW", "days_ago": 5, "durations": [0.5, 2.0, 1.0],
        "evidence": "libcurl 7.85.0 in MeridianConnect MCG-10 gateway; updated to 7.86.0.",
        "partial_signoffs": [("security", "approved")],
    },
    {
        "cve": "CVE-2025-5296", "severity": "HIGH", "cvss": 7.3, "in_kev": False, "sector": "IT/OT",
        "title": "Schneider Electric SESU — race condition enabling local privilege escalation",
        "cpes": ["cpe:2.3:a:schneider-electric:software_update:-:*:*:*:*:*:*:*"], "cwes": ["CWE-362"],
        "authority": "CISA ICSA", "cisa_url": "https://www.cisa.gov/news-events/ics-advisories/icsa-25-266-03",
        "ext_vendor": "Schneider Electric", "vendor_disclosed": True,
        "vendor_disclosure_url": "https://www.se.com/ww/en/work/support/cybersecurity/security-notifications.jsp",
        "state": "NOT_APPLICABLE", "days_ago": 9, "durations": [0.5],
    },
]


# ---------------------------------------------------------------------------
# Prepopulated disclosures driven by real example CVEs (CISA ICS Medical
# Advisories / CISA KEV / NVD). Some are not applicable to this org's devices
# (third-party medical devices) and are filed as known_not_affected; others
# match the org SBOM and are driven through the pipeline with backdated
# timelines so the process map and metrics are populated on first launch.
# ---------------------------------------------------------------------------

# Reached-state ordering for seeding
_ORDER = ["INGESTED", "TRIAGED", "VERIFIED", "DRAFT_READY", "IN_REVIEW", "APPROVED", "PUBLISHED", "NOT_APPLICABLE"]

SEED_DISCLOSURES = [
    # --- third-party medical-device CVEs from CISA: NOT applicable to our devices ---
    {
        "cve": "CVE-2024-12248", "severity": "CRITICAL", "cvss": 9.8, "in_kev": False,
        "title": "Contec CMS8000 patient monitor — out-of-bounds write (RCE); same advisory carries hidden backdoor CVE-2025-0626 and data-spillage CVE-2025-0683",
        "cpes": ["cpe:2.3:o:contec:cms8000_firmware:-:*:*:*:*:*:*:*"], "cwes": ["CWE-787"],
        "authority": "CISA ICSMA", "cisa_url": "https://www.cisa.gov/news-events/ics-medical-advisories/icsma-25-030-01",
        "ext_vendor": "Contec Health", "vendor_disclosed": False, "vendor_disclosure_url": None,
        "state": "NOT_APPLICABLE", "days_ago": 13, "durations": [0.4],
    },
    {
        "cve": "CVE-2023-31222", "severity": "CRITICAL", "cvss": 9.8, "in_kev": False,
        "title": "Medtronic Paceart Optima — deserialization of untrusted data in optional messaging service (RCE/DoS)",
        "cpes": ["cpe:2.3:a:medtronic:paceart_optima:-:*:*:*:*:*:*:*"], "cwes": ["CWE-502"],
        "authority": "CISA ICSMA", "cisa_url": "https://www.cisa.gov/news-events/ics-medical-advisories/icsma-23-180-01",
        "ext_vendor": "Medtronic", "vendor_disclosed": True,
        "vendor_disclosure_url": "https://www.medtronic.com/security",
        "state": "NOT_APPLICABLE", "days_ago": 11, "durations": [0.6],
    },
    # --- component CVEs that match our SBOM: driven through the pipeline ---
    {
        "cve": "CVE-2021-44228", "severity": "CRITICAL", "cvss": 10.0, "in_kev": True,
        "title": "Apache Log4j2 JNDI remote code execution (Log4Shell)",
        "cpes": ["cpe:2.3:a:apache:log4j:2.14.1:*:*:*:*:*:*:*"], "cwes": ["CWE-502", "CWE-917"],
        "authority": "CISA KEV", "cisa_url": "https://www.cisa.gov/news-events/news/apache-log4j-vulnerability-guidance",
        "ext_vendor": None, "vendor_disclosed": None, "vendor_disclosure_url": None,
        "state": "PUBLISHED", "days_ago": 16, "durations": [0.5, 2.5, 1.5, 4.0, 0.5],
        "evidence": "Reproduced on Lumen LIW-700 imaging workstation (log4j present); JNDI lookup triggered in lab. Ref TICKET-3312.",
    },
    {
        "cve": "CVE-2023-38545", "severity": "HIGH", "cvss": 8.8, "in_kev": False,
        "title": "curl/libcurl SOCKS5 heap buffer overflow",
        "cpes": ["cpe:2.3:a:haxx:libcurl:7.85.0:*:*:*:*:*:*:*"], "cwes": ["CWE-787"],
        "authority": "NVD", "cisa_url": "https://nvd.nist.gov/vuln/detail/CVE-2023-38545",
        "ext_vendor": None, "vendor_disclosed": None, "vendor_disclosure_url": None,
        "state": "PUBLISHED", "days_ago": 12, "durations": [0.8, 3.0, 1.0, 3.5, 0.6],
        "evidence": "libcurl 7.85.0 confirmed in Aurora AIP-3000; SOCKS5 path not reachable in default config but updated out of caution.",
    },
    {
        "cve": "CVE-2022-3602", "severity": "HIGH", "cvss": 7.5, "in_kev": False,
        "title": "OpenSSL X.509 email address 4-byte buffer overflow (\"SpookySSL\")",
        "cpes": ["cpe:2.3:a:openssl:openssl:3.0.6:*:*:*:*:*:*:*"], "cwes": ["CWE-787"],
        "authority": "NVD", "cisa_url": "https://nvd.nist.gov/vuln/detail/CVE-2022-3602",
        "ext_vendor": None, "vendor_disclosed": None, "vendor_disclosure_url": None,
        "state": "IN_REVIEW", "days_ago": 11, "durations": [0.6, 2.4, 1.2],
        "evidence": "OpenSSL 3.0.x in Aurora AIP-3000 and Sentinel SPM-X1; updated to 3.0.7. Verified in lab.",
        "partial_signoffs": [("security", "approved"), ("legal", "approved")],
    },
    {
        "cve": "CVE-2021-28831", "severity": "HIGH", "cvss": 7.5, "in_kev": False,
        "title": "BusyBox decompress_gunzip invalid free / out-of-bounds read",
        "cpes": ["cpe:2.3:a:busybox:busybox:1.33.0:*:*:*:*:*:*:*"], "cwes": ["CWE-476"],
        "authority": "NVD", "cisa_url": "https://nvd.nist.gov/vuln/detail/CVE-2021-28831",
        "ext_vendor": None, "vendor_disclosed": None, "vendor_disclosure_url": None,
        "state": "DRAFT_READY", "days_ago": 4, "durations": [0.7, 2.0, 0.8],
        "evidence": "BusyBox in Aurora AIP-3000 firmware; gunzip path used by update routine. Confirmed on lab unit.",
    },
]

# which checkpoints exist by the time a given state is reached
_STATE_CHECKPOINTS = {
    "NOT_APPLICABLE": ["ingested", "triaged"],
    "DRAFT_READY":    ["ingested", "triaged", "verified", "drafted", "submitted-for-review"],
    "IN_REVIEW":      ["ingested", "triaged", "verified", "drafted", "submitted-for-review"],
    "PUBLISHED":      ["ingested", "triaged", "verified", "drafted", "submitted-for-review", "approved", "published"],
}
# checkpoint -> index of the duration that ends at it (durations are per macro step)
_DUR_BEFORE = {"triaged": 0, "verified": 1, "submitted-for-review": 2, "approved": 3, "published": 4}


def _seed_one(spec, devices):
    cve = spec["cve"]
    if db.get_advisory_by_cve(cve):
        return
    adv_id = "ADV-" + uuid.uuid4().hex[:10]
    detail = {"id": cve, "title": spec["title"], "severity": spec["severity"], "cvss": spec["cvss"],
              "in_kev": spec["in_kev"], "cpes": spec.get("cpes", []), "cwes": spec.get("cwes", []),
              "description": spec["title"]}
    start = time.time() - spec["days_ago"] * DAY
    db.insert_advisory({
        "id": adv_id, "cve_id": cve, "title": spec["title"][:240],
        "source": spec["authority"], "severity": spec["severity"], "cvss": spec["cvss"],
        "in_kev": spec["in_kev"], "state": "INGESTED", "cve_detail": detail,
        "cisa_url": spec["cisa_url"], "authority": spec["authority"], "ext_vendor": spec.get("ext_vendor"),
        "vendor_disclosed": spec.get("vendor_disclosed"), "vendor_disclosure_url": spec.get("vendor_disclosure_url"),
        "sector": spec.get("sector", "MedTech"),
        "created_at": start, "updated_at": time.time(),
    })

    # deterministic SBOM triage
    hits = triage_agent.match_devices(detail, devices)
    applicable = len(hits) > 0
    vex = "known_affected" if applicable else "known_not_affected"
    if spec["state"] == "NOT_APPLICABLE":
        applicable, vex = False, "known_not_affected"
    rationale = ("Deterministic SBOM match: " + ", ".join(sorted({m["component"] for h in hits for m in h["matched_components"]}))
                 if applicable else
                 "No SBOM component or CPE in the device inventory matches this CVE (third-party medical device). "
                 "Filed as known_not_affected (vulnerable_code_not_present).")
    triage = {"applicable": applicable, "vex_status": vex, "affected_devices": hits if applicable else [],
              "rationale": rationale, "agent_trace": [], "llm_used": False}
    db.update_advisory(adv_id, triage=triage, state=spec["state"])

    # checkpoints with backdated timestamps
    durs = spec["durations"]; t = start
    cps = _STATE_CHECKPOINTS.get(spec["state"], ["ingested", "triaged"])
    db.log_at(adv_id, "feed-agent", "seed-ingested", f"{cve} via {spec['authority']}", t)
    for cp in cps[1:]:
        idx = _DUR_BEFORE.get(cp)
        if idx is not None and idx < len(durs):
            t = t + durs[idx] * DAY
        action = {"triaged": "triaged", "verified": "verified", "drafted": "drafted",
                  "submitted-for-review": "submitted-for-review", "approved": "approved",
                  "published": "published"}[cp]
        db.log_at(adv_id, "workflow", action, action, t)

    # verification + document for advanced states
    if spec["state"] in ("DRAFT_READY", "IN_REVIEW", "PUBLISHED"):
        db.update_advisory(adv_id, verification={"status": "confirmed", "evidence": spec.get("evidence", ""),
                                                 "by": "p.sharma", "at": start + sum(durs[:2]) * DAY})
        adv = db.get_advisory(adv_id)
        doc = {
            "advisory_md": _seed_advisory_md(adv),
            "csaf": disclosure_agent.build_csaf(adv, ORG),
            "fda_report": disclosure_agent.build_fda_report(adv, ORG),
            "drafted_at": start,
        }
        db.update_advisory(adv_id, document=doc)

    # sign-offs
    if spec["state"] == "PUBLISHED":
        for role in db.get_required_roles():
            db.add_signoff(adv_id, role, "approved", role + "-lead", "ok")
    if spec.get("partial_signoffs"):
        for role, dec in spec["partial_signoffs"]:
            db.add_signoff(adv_id, role, dec, role + "-lead", "ok")


def _seed_advisory_md(adv):
    det = adv.get("cve_detail") or {}; tr = adv.get("triage") or {}
    devs = tr.get("affected_devices", [])
    prod = ", ".join(d["device_name"] for d in devs) or "under assessment"
    return (f"# {ORG['name']} Security Advisory — {adv['cve_id']}\n\n"
            f"**Severity:** {adv['severity']} (CVSS {adv['cvss']})  \n"
            f"**VEX status:** {tr.get('vex_status')}  \n**Affected products:** {prod}\n\n"
            f"## Overview\n{adv.get('title')}\n\n## Assessment\n{tr.get('rationale')}\n\n"
            f"## Contact\n{ORG['contact']}\n")
