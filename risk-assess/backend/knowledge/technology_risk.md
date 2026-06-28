# Technology & Cyber Risk — NIST, ISO 27005, FAIR

## Frameworks
The NIST Risk Management Framework (RMF, SP 800-37) and NIST Cybersecurity Framework (CSF 2.0: Govern, Identify, Protect, Detect, Respond, Recover) structure technology risk. ISO/IEC 27005 provides information-security risk management aligned to the ISO 27001 ISMS. FAIR (Factor Analysis of Information Risk) is a quantitative model expressing risk as Loss Event Frequency x Loss Magnitude.

## Loss dimensions
Technology risk impact is often multi-dimensional. This template scores three explicit loss types: Reputation loss (brand damage, customer churn, media exposure), Financial loss (fines, remediation cost, lost revenue, SLA penalties), and IP loss (theft or forced disclosure of source code, trade secrets, patents). Aggregate Impact is taken as the worst-case dimension: MAX(Reputation, Financial, IP). Risk Score = Likelihood x Aggregate Impact.

## Common scenarios
Data breach / PII exfiltration (reputation + financial), source-code or trade-secret theft (IP), critical SaaS outage (financial + reputation), and open-source licence/IP infringement from an unvetted dependency (IP + financial). Supply-chain risk is managed with an SBOM (Software Bill of Materials), dependency and licence scanning in CI, and provenance attestation (SLSA, sigstore).

## Threat modeling
STRIDE classifies threats as Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, and Elevation of privilege. Threat-model-as-code (e.g., pytm, OWASP Threat Dragon) generates data-flow diagrams and threat lists from a declarative model. Attack graphs map exploitable transitions across assets; overlaying CVEs from the SBOM (prioritized by EPSS/KEV) reveals reachable attack paths. For connected medical devices, FDA section 524B requires a security risk management report, a machine-readable SBOM, a Secure Product Development Framework, and a postmarket cybersecurity management plan.

## Treatment
Controls follow defense-in-depth: inherently secure design (secure-by-design, least privilege, encryption), protective measures (WAF, MFA, monitoring, DLP), and procedural controls (training, IR plans, NDAs). Residual risk is re-scored after controls and tracked with KRIs.
