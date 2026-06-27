# Secure Release Gate - RACI Matrix

Security evidence and sign-off required to ship (NIST SP 800-218 PW/RV).

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

| Activity | Dev Lead | Product Security | QA | Release Mgr | Product Owner |
| --- | --- | --- | --- | --- | --- |
| Complete threat model & review | R | A | I | I | C |
| Pass SAST / DAST / SCA gates | R | A | C | I | I |
| Generate & attach SBOM | R | A | I | C | I |
| Resolve / waive open findings | R | A | I | I | C |
| Security sign-off | C | R | C | A | C |
| Approve release to production | C | C | C | R | A |
