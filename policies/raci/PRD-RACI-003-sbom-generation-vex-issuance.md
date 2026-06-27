# SBOM Generation & VEX Issuance - RACI Matrix

Producing, validating and exchanging SBOM/VEX (FDA 524B; NTIA minimum elements).

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

| Activity | Build / DevOps | Product Security | Engineering | Compliance | Customer Support |
| --- | --- | --- | --- | --- | --- |
| Generate SBOM in CI/CD | R | A | C | I | I |
| Validate completeness & accuracy | C | R | C | A | I |
| Map components to CVEs | I | A | R | C | I |
| Author VEX statements | I | R | C | A | I |
| Distribute to customers / FDA | I | A | I | R | C |
| Maintain on each release | R | A | C | C | I |
