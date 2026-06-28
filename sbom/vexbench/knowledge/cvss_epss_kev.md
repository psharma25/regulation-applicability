# Exploitability signals — CVSS, EPSS, KEV

## CVSS base score
CVSS measures the intrinsic severity of a vulnerability, not the likelihood it will be exploited in
a given environment. Base score bands: 9.0–10.0 Critical, 7.0–8.9 High, 4.0–6.9 Medium,
0.1–3.9 Low. Severity is necessary but not sufficient for risk — a Critical CVSS with no reachable
path and no exploit may pose little actual risk.

## EPSS
The Exploit Prediction Scoring System estimates the probability (0 to 1) that a vulnerability will
be exploited in the wild within the next 30 days. EPSS is empirical and updates daily. A low CVSS
with a high EPSS can deserve more urgency than a high CVSS with negligible EPSS. Treat EPSS as the
likelihood signal and CVSS as the severity signal; they answer different questions.

## CISA KEV
The Known Exploited Vulnerabilities catalog lists vulnerabilities with confirmed, reliable evidence
of active exploitation. Presence on KEV is the strongest single likelihood signal: it should drive
likelihood to at least High regardless of EPSS, and usually warrants prioritized remediation.

## Combining signals into likelihood
A defensible likelihood estimate blends: EPSS probability, KEV presence (overrides upward), exploit
maturity (none / proof-of-concept / functional / weaponized), attack vector (network exposure
raises likelihood; local or physical lowers it), and reachability. If the vulnerable code is not in
the execute path, exploitation likelihood collapses even when CVSS and EPSS are high.

## Reachability and configuration
Two devices shipping the same component can have very different real risk. Network-reachable,
exposed services with weaponized exploits are urgent. Code compiled in but never invoked, or
reachable only by a trusted local actor behind other controls, is far less so. Capturing
reachability is what separates a credible medical-device risk assessment from a raw scanner dump.
