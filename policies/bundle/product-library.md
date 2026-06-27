# Product Security - Controlled Document Library



<!-- PRD-POL-001 -->
# PRD-POL-001 - Secure Software Development (SSDLC) Policy

## 1. Purpose
To embed security throughout the software development lifecycle so that products are designed, built, tested and maintained securely, aligned to **NIST SP 800-218 (SSDF)**, **ISO/IEC 27001:2022 A.8.25-A.8.31**, and for regulated devices **IEC 62304** and **FDA premarket cybersecurity** expectations.

## 2. Scope
Applies to all software developed, integrated or maintained by the Organization, including firmware, embedded, cloud and AI/ML components.

## 3. Policy Statements
1. Security requirements **shall** be defined and reviewed at the start of each initiative (SSDF PO/PW.1).
2. **Threat modeling shall** be performed for new products and significant changes, with findings tracked to closure (PW.1).
3. Developers **shall** follow the Secure Coding Standard; code **shall** undergo peer review (PW.7).
4. **SAST, SCA and DAST shall** be integrated into CI/CD with defined pass/fail gates (PW.7-PW.8).
5. A **Software Bill of Materials shall** be generated for every release (PS.3, FDA 524B).
6. Third-party and open-source components **shall** be approved, inventoried and monitored for vulnerabilities (PW.4).
7. Build and release pipelines **shall** be integrity-protected; artifacts **shall** be **code-signed** and provenance recorded (PS.1-PS.2).
8. No release **shall** ship without passing the **security release gate** (RV).
9. Discovered vulnerabilities **shall** be handled through the PSIRT process, including postmarket for regulated devices.
10. For medical devices, security activities **shall** be integrated with the design controls and risk management (IEC 62304, ISO 14971).

## 4. Roles & Responsibilities
- **Product Security** — owns the SSDLC program, gates and tooling.
- **Engineering / Dev Leads** — implement secure design, coding and testing.
- **Release Management** — enforces the release gate.
- **Regulatory / Quality** — integrates security into design controls (regulated products).

## 5. Compliance & Enforcement
Verified through pipeline evidence, gate records and audit. Releases bypassing gates are nonconformities requiring CAPA.

## 6. Exceptions
Documented, risk-assessed, time-bound and approved by Product Security leadership.

## 7. Review & Maintenance
Reviewed at least annually and on major toolchain or regulatory change.

## 8. References
NIST SP 800-218 (PO/PS/PW/RV); ISO/IEC 27001:2022 A.8.25-A.8.31; IEC 62304; ISO 14971; FDA 524B premarket cybersecurity; EU MDR Annex I; OWASP SAMM.


<!-- PRD-POL-002 -->
# PRD-POL-002 - Secure Software Development Framework (SSDF) Policy

## 1. Purpose
To adopt the NIST Secure Software Development Framework (SSDF, SP 800-218) practices across the product lifecycle.

## 2. Scope
Applies to all software and firmware developed or maintained by the Organization.

## 3. Policy Statements
1. The Organization **shall** implement SSDF practice groups: Prepare the Organization (PO), Protect the Software (PS), Produce Well-Secured Software (PW) and Respond to Vulnerabilities (RV).
2. Security roles, toolchains and training **shall** be established (PO).
3. Source, build and release artifacts **shall** be protected from tampering and unauthorized access (PS).
4. Software **shall** be designed, reviewed, coded and tested to minimize vulnerabilities (PW).
5. Released software **shall** have a process to identify, assess and remediate vulnerabilities (RV).
6. SSDF implementation **shall** be evidenced for attestation purposes (e.g., secure-software development attestation).
7. SSDF practices **shall** integrate with design controls for regulated products.

## 4. Roles & Responsibilities
- **Product Security** — owns SSDF adoption and evidence.
- **Engineering** — implements PW/PS practices.
- **PSIRT** — operates RV practices.
- **Leadership** — resources PO practices.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- NIST SP 800-218 (SSDF)
- NIST SSDF attestation guidance
- ISO/IEC 27001:2022 A.8.25-A.8.31
- EO 14028 (software supply chain)


<!-- PRD-POL-003 -->
# PRD-POL-003 - Software Bill of Materials (SBOM) Policy

## 1. Purpose
To require the generation, maintenance and exchange of accurate Software Bills of Materials so component risk and supply-chain integrity are transparent, aligned to **FDA 524B**, **NTIA minimum elements**, and **NIST SP 800-218 (PS.3)**.

## 2. Scope
Applies to all software and firmware released, distributed or deployed by the Organization, including third-party and open-source components.

## 3. Policy Statements
1. An SBOM **shall** be generated for **every release** in a machine-readable standard format (**SPDX** or **CycloneDX**).
2. Each SBOM **shall** include the NTIA minimum elements: supplier, component name, version, unique identifiers, dependency relationships, author and timestamp.
3. SBOMs **shall** capture **transitive dependencies**, not only direct ones.
4. Components **shall** be continuously mapped to known vulnerabilities; exploitability **shall** be communicated via **VEX** statements.
5. SBOMs and VEX **shall** be **maintained per release** and updated when components change.
6. For regulated medical devices, SBOMs **shall** be provided to FDA in premarket submissions and to customers postmarket per 524B.
7. SBOM generation **shall** be automated within CI/CD and the artifacts integrity-protected.

## 4. Roles & Responsibilities
- **Build / DevOps** — generates SBOMs in the pipeline.
- **Product Security** — validates accuracy, maps CVEs, authors VEX.
- **Compliance / Regulatory** — distributes to FDA and customers.
- **Engineering** — maintains accurate dependency declarations.

## 5. Compliance & Enforcement
Verified through release evidence and audit. A release without a valid SBOM **shall not** pass the security release gate.

## 6. Exceptions
Approved by Product Security leadership with documented justification and remediation timeline.

## 7. Review & Maintenance
Reviewed at least annually and on regulatory change.

## 8. References
FDA 524B; NTIA "Minimum Elements for an SBOM"; NIST SP 800-218 PS.3; SPDX (ISO/IEC 5962); CycloneDX; CISA SBOM guidance; IEC 81001-5-1.


<!-- PRD-POL-004 -->
# PRD-POL-004 - Threat Modeling Policy

## 1. Purpose
To require threat modeling so product security risks are identified and mitigated by design.

## 2. Scope
Applies to new products, major features and significant architectural changes.

## 3. Policy Statements
1. Threat models **shall** be created for new products and significant changes before implementation completes.
2. Threat modeling **shall** use a defined method (e.g., STRIDE) and consider the product's data flows and trust boundaries.
3. Identified threats **shall** be rated and tracked to mitigation or accepted with justification.
4. Threat models **shall** be reviewed by product security and updated as the design evolves.
5. For regulated devices, threat modeling **shall** support the security risk assessment and premarket submission.
6. Threat-model outputs **shall** inform security requirements and test cases.

## 4. Roles & Responsibilities
- **Engineering/Architects** — produce threat models.
- **Product Security** — reviews and approves.
- **Product Management** — accepts residual risk.
- **Regulatory** — incorporates outputs for devices.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- NIST SP 800-218 PW.1
- ISO/IEC 27001:2022 A.8.27
- FDA premarket cybersecurity (threat modeling)
- STRIDE / PASTA


<!-- PRD-POL-005 -->
# PRD-POL-005 - Software Supply Chain Security Policy

## 1. Purpose
To protect the integrity of the software supply chain from source to deployment.

## 2. Scope
Applies to source control, build systems, dependencies, artifacts and release pipelines.

## 3. Policy Statements
1. Build pipelines **shall** be hardened, access-controlled and produce reproducible, attestable builds where feasible.
2. Dependencies **shall** be obtained from trusted sources and verified for integrity.
3. Build and release artifacts **shall** be **signed** and their provenance recorded (e.g., SLSA-aligned attestations).
4. Access to source and CI/CD **shall** follow least privilege with MFA.
5. Secrets **shall not** be stored in source; secret scanning **shall** be enforced.
6. An SBOM **shall** accompany each release per the SBOM Policy.
7. Tampering or compromise of the pipeline **shall** be treated as a security incident.

## 4. Roles & Responsibilities
- **DevOps/Platform** — secures pipelines and provenance.
- **Product Security** — defines supply-chain controls.
- **Engineering** — manages dependencies securely.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- NIST SP 800-218 PS.1-PS.3, PW.4
- NIST SP 800-161 (C-SCRM)
- SLSA framework
- ISO/IEC 27001:2022 A.8.30, A.8.31


<!-- PRD-POL-006 -->
# PRD-POL-006 - Open-Source & Third-Party Component Policy

## 1. Purpose
To govern selection, approval, tracking and monitoring of open-source and third-party components.

## 2. Scope
Applies to all third-party and open-source components incorporated into products.

## 3. Policy Statements
1. Components **shall** be approved before use, considering security, maintenance status and license.
2. An inventory of components **shall** be maintained and reflected in the SBOM.
3. Components **shall** be continuously monitored for new vulnerabilities (SCA).
4. Vulnerable components **shall** be remediated within the timelines of the Vulnerability Scoring & Triage Standard.
5. License obligations **shall** be reviewed and complied with.
6. Abandoned or unmaintained components **shall** be replaced or risk-accepted.
7. Component provenance and integrity **shall** be verified.

## 4. Roles & Responsibilities
- **Engineering** — selects and maintains components.
- **Product Security** — approves and monitors components.
- **Legal** — reviews license obligations.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- NIST SP 800-218 PW.4
- ISO/IEC 27001:2022 A.8.28, A.8.30
- OWASP Dependency management


<!-- PRD-POL-007 -->
# PRD-POL-007 - Product Vulnerability Disclosure Policy

## 1. Purpose
To provide a clear channel for external parties to report product vulnerabilities and to handle them responsibly.

## 2. Scope
Applies to externally reported vulnerabilities in Organization products and services.

## 3. Policy Statements
1. A public **vulnerability disclosure policy** and intake channel (e.g., security.txt) **shall** be published.
2. Reports **shall** be acknowledged within a defined timeframe and handled confidentially.
3. Researchers acting in good faith **shall not** be pursued legally (safe-harbor statement).
4. Reports **shall** be triaged and routed to the PSIRT process.
5. Reporters **shall** be kept informed and credited where appropriate and desired.
6. Coordinated disclosure timelines **shall** be defined and honored.

## 4. Roles & Responsibilities
- **PSIRT** — receives and coordinates reports.
- **Engineering** — validates and fixes.
- **Legal/Comms** — manage safe harbor and disclosure.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 29147 (vulnerability disclosure)
- ISO/IEC 30111 (handling)
- FDA postmarket cybersecurity
- CISA CVD guidance


<!-- PRD-POL-008 -->
# PRD-POL-008 - Coordinated Disclosure & PSIRT Policy

## 1. Purpose
To establish a Product Security Incident Response Team (PSIRT) and a coordinated process for receiving, handling and disclosing product vulnerabilities.

## 2. Scope
Applies to security vulnerabilities affecting Organization products, from intake through remediation and disclosure.

## 3. Policy Statements
1. A **PSIRT shall** be established with defined membership, authority and escalation paths.
2. Vulnerabilities **shall** be handled under a documented process aligned to ISO/IEC 30111, regardless of source (research, internal, customer, monitoring).
3. Vulnerabilities **shall** be validated, scored and assigned remediation timelines per the Vulnerability Scoring & Triage Standard.
4. Coordinated disclosure **shall** balance user protection with timely transparency; disclosure timelines **shall** be defined.
5. Security advisories and, where applicable, **VEX** statements **shall** be issued to affected customers.
6. Regulatory reporting obligations (e.g., for devices) **shall** be assessed and met within required timeframes.
7. PSIRT **shall** coordinate with enterprise incident response when an issue spans products and infrastructure.
8. PSIRT performance and cases **shall** be tracked and reviewed for improvement.

## 4. Roles & Responsibilities
- **PSIRT Lead** — owns and coordinates the PSIRT process.
- **Engineering** — validates and remediates vulnerabilities.
- **Regulatory** — assesses reportability for regulated products.
- **Communications/Legal** — manage disclosure and safe harbor.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 30111 (handling)
- ISO/IEC 29147 (disclosure)
- FIRST PSIRT Services Framework
- FDA postmarket cybersecurity


<!-- PRD-POL-009 -->
# PRD-POL-009 - Secure Release & Deployment Policy

## 1. Purpose
To define the security gates that must be satisfied before a release is deployed or shipped.

## 2. Scope
Applies to all product releases and deployments.

## 3. Policy Statements
1. A release **shall not** proceed without passing the **security release gate**.
2. Required evidence **shall** include passing SAST/DAST/SCA, a current threat model, an SBOM and resolution or approved waiver of open findings.
3. Security sign-off **shall** be recorded prior to release.
4. Emergency releases **shall** follow an expedited gate with retrospective review.
5. Releases **shall** be built from protected pipelines and signed.
6. Gate evidence **shall** be retained for audit and, for devices, regulatory submission.

## 4. Roles & Responsibilities
- **Release Management** — enforces the gate.
- **Product Security** — provides sign-off.
- **Engineering** — supplies evidence and remediations.
- **Product Owner** — authorizes release.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- NIST SP 800-218 RV, PW.8
- ISO/IEC 27001:2022 A.8.29, A.8.31
- FDA premarket cybersecurity


<!-- PRD-POL-010 -->
# PRD-POL-010 - Product Cryptography & Code Signing Policy

## 1. Purpose
To define approved cryptography for products and to ensure release artifacts are signed and verifiable.

## 2. Scope
Applies to cryptography embedded in products and to signing of product artifacts and updates.

## 3. Policy Statements
1. Products **shall** use only approved, current cryptographic algorithms and protocols (see Product Cryptography Standard).
2. Secrets and keys **shall not** be hard-coded in products or source.
3. Release artifacts and firmware updates **shall** be **digitally signed**; devices **shall** verify signatures before installation.
4. Signing keys **shall** be protected in HSMs with strict access control.
5. Cryptographic implementations **shall** avoid custom/unvetted algorithms.
6. Products **shall** support secure key provisioning and rotation where applicable.
7. Post-quantum readiness **shall** be considered for long-lived products.

## 4. Roles & Responsibilities
- **Product Security/Engineering** — implement approved crypto and signing.
- **Key Custodians** — protect signing keys.
- **Release Management** — enforce signing.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- NIST SP 800-218 PS.2
- NIST SP 800-57; FIPS 140-3
- ISO/IEC 27001:2022 A.8.24
- FDA premarket (cryptographic protection)


<!-- PRD-POL-011 -->
# PRD-POL-011 - Security Requirements & Design Policy

## 1. Purpose
To ensure security requirements are derived, documented and reviewed as part of product design.

## 2. Scope
Applies to all product development and significant changes.

## 3. Policy Statements
1. Security requirements **shall** be derived from threat models, regulation, customer obligations and a baseline requirements catalog.
2. Requirements **shall** be documented, testable and traceable to design and verification.
3. A **secure design review shall** be conducted at defined milestones.
4. Security requirements **shall** be maintained as the product evolves.
5. For devices, security requirements **shall** integrate with design controls and risk management.
6. Requirement deviations **shall** be risk-assessed and approved.

## 4. Roles & Responsibilities
- **Product Security** — owns the requirements baseline and reviews.
- **Engineering** — implements and traces requirements.
- **Regulatory/Quality** — integrate with design controls.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- NIST SP 800-218 PW.1-PW.2
- ISO/IEC 27001:2022 A.8.27
- IEC 62304; ISO 14971 (devices)
- FDA premarket cybersecurity


<!-- PRD-POL-012 -->
# PRD-POL-012 - Premarket Cybersecurity Submission Policy

## 1. Purpose
To define the cybersecurity content required in premarket submissions for regulated devices.

## 2. Scope
Applies to premarket submissions for cyber devices subject to FDA Section 524B and equivalent obligations.

## 3. Policy Statements
1. Premarket submissions **shall** include a security risk assessment, threat model and architecture views.
2. A **Software Bill of Materials shall** be provided with the submission.
3. Plans for monitoring, identifying and addressing postmarket vulnerabilities **shall** be documented.
4. Security testing evidence (e.g., SAST/DAST/SCA, penetration testing) **shall** be included.
5. Labelling **shall** communicate security-relevant information to users.
6. Submissions **shall** demonstrate a secure development lifecycle consistent with recognized frameworks.
7. Security documentation **shall** be controlled within the QMS design file.

## 4. Roles & Responsibilities
- **Regulatory Affairs** — compiles and submits.
- **Product Security** — provides security evidence.
- **Engineering/Quality** — supply design and test artifacts.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- FDA FD&C Act Section 524B
- FDA premarket cybersecurity guidance
- IEC 81001-5-1; IEC 62304
- NIST SP 800-218


<!-- PRD-POL-013 -->
# PRD-POL-013 - Postmarket Cybersecurity Management Policy

## 1. Purpose
To manage cybersecurity of marketed devices through surveillance, patching and reporting.

## 2. Scope
Applies to released/regulated products throughout their supported lifecycle.

## 3. Policy Statements
1. Postmarket vulnerability monitoring (including component/SBOM monitoring) **shall** be performed continuously.
2. Vulnerabilities **shall** be assessed for patient-safety and security impact and remediated within risk-based timelines.
3. Security updates **shall** be delivered through validated, signed mechanisms.
4. Reportable events **shall** be reported to regulators within required timeframes.
5. Customers/users **shall** receive timely security advisories and, where relevant, VEX.
6. End-of-support **shall** be communicated with security implications.
7. Postmarket activities **shall** be evidenced within the QMS.

## 4. Roles & Responsibilities
- **PSIRT** — coordinates postmarket vulnerability handling.
- **Regulatory** — assesses and files reports.
- **Engineering** — develops and delivers updates.
- **Quality** — maintains records.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- FDA postmarket management of cybersecurity in medical devices
- FD&C Act 524B
- ISO/IEC 30111
- IEC 81001-5-1


<!-- PRD-POL-014 -->
# PRD-POL-014 - Software Maintenance & Patch Policy

## 1. Purpose
To maintain and patch released software in a controlled, validated manner.

## 2. Scope
Applies to maintenance and patching of released/regulated products.

## 3. Policy Statements
1. Maintenance releases and patches **shall** follow the secure development lifecycle and release gate.
2. Changes **shall** be assessed for safety, security and regulatory impact (impact/change analysis).
3. Patches **shall** be verified and validated proportionate to risk before distribution.
4. Patch distribution **shall** use signed, integrity-protected mechanisms.
5. Patch records and validation evidence **shall** be retained in the QMS.
6. Customer communication **shall** accompany security-relevant patches.
7. Legacy/unsupported versions **shall** have a defined support and risk position.

## 4. Roles & Responsibilities
- **Engineering** — develops and validates patches.
- **Quality/Regulatory** — assess impact and reportability.
- **Product Security** — confirms security adequacy.
- **Support** — communicates to customers.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- IEC 62304 (maintenance process)
- FDA postmarket cybersecurity
- ISO 13485:2016 Cl. 7.3, 7.5
- NIST SP 800-218 RV


<!-- PRD-POL-015 -->
# PRD-POL-015 - Penetration Testing Policy

## 1. Purpose
To govern penetration testing of products to validate security before and after release.

## 2. Scope
Applies to penetration testing of Organization products and supporting services.

## 3. Policy Statements
1. Products **shall** undergo penetration testing at defined milestones (e.g., major release) and periodically thereafter.
2. Testing scope and rules of engagement **shall** be defined and authorized in advance.
3. Testers **shall** be competent and independent of the development team for assurance value.
4. Findings **shall** be risk-rated and remediated within defined timelines; critical findings may block release.
5. Retesting **shall** confirm remediation.
6. Test reports **shall** be retained for audit and, for devices, submission.
7. Testing **shall** avoid impact to production and patient safety.

## 4. Roles & Responsibilities
- **Product Security** — commissions and oversees testing.
- **Testers (internal/external)** — execute within scope.
- **Engineering** — remediate findings.
- **Regulatory** — use evidence for submissions.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- NIST SP 800-115 (testing)
- OWASP Testing Guide
- FDA premarket cybersecurity (security testing)
- ISO/IEC 27001:2022 A.8.29


<!-- PRD-POL-016 -->
# PRD-POL-016 - AI/ML Model Security Policy

## 1. Purpose
To secure AI/ML components within products against model-specific and supply-chain threats.

## 2. Scope
Applies to products that incorporate AI/ML models, including third-party and open models.

## 3. Policy Statements
1. AI/ML components **shall** be inventoried, threat-modeled and risk-assessed (including data poisoning, evasion, model extraction and prompt injection).
2. Training and inference data **shall** be governed for integrity, provenance and privacy.
3. Model and dataset provenance **shall** be recorded; third-party models **shall** be vetted.
4. Models **shall** be evaluated for robustness, bias and safety prior to release proportionate to risk.
5. Inputs/outputs **shall** be validated and constrained to mitigate misuse and injection.
6. Model artifacts **shall** be integrity-protected and access-controlled.
7. Postmarket monitoring **shall** cover model drift and emerging AI vulnerabilities.

## 4. Roles & Responsibilities
- **Product Security/ML Engineering** — secure AI components.
- **Data Governance** — manage data integrity and provenance.
- **Product Security** — threat-model and monitor AI risk.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- NIST AI RMF 1.0
- ISO/IEC 42001
- OWASP Top 10 for LLM Applications
- MITRE ATLAS


<!-- PRD-STD-001 -->
# PRD-STD-001 - Secure Coding Standard

## 1. Purpose & Scope
To define language-level secure coding controls against common weaknesses. Applies to all code developed or maintained by the Organization.

## 2. Normative Requirements
1. Input **shall** be validated and output **shall** be encoded to prevent injection and XSS.
2. Parameterized queries **shall** be used; dynamic query concatenation is prohibited.
3. Authentication, authorization and session handling **shall** use vetted frameworks, not custom schemes.
4. Secrets **shall not** be hard-coded; sensitive data **shall** be handled per the cryptography standards.
5. Error handling **shall** avoid leaking sensitive information; fail securely.
6. Memory-unsafe operations **shall** be avoided or mitigated in applicable languages.
7. Code **shall** be peer-reviewed and pass SAST before merge.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Injection/XSS prevention | OWASP ASVS V5; CWE-79/89 |
| Auth & session | OWASP ASVS V2-V3; NIST SP 800-218 PW.5 |
| Secrets & crypto | ISO/IEC 27001:2022 A.8.24; CWE-798 |

## 4. Metrics & Compliance
- SAST findings per KLOC trend.
- Percentage of merges with required review.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- OWASP ASVS
- CWE Top 25
- NIST SP 800-218 PW.5-PW.7


<!-- PRD-STD-002 -->
# PRD-STD-002 - Threat Modeling Standard

## 1. Purpose & Scope
To define the method, depth and review criteria for threat modeling. Applies to threat modeling across products and major changes.

## 2. Normative Requirements
1. Threat models **shall** include a data-flow diagram with trust boundaries.
2. STRIDE (or an approved method) **shall** be applied to each element/flow.
3. Threats **shall** be rated and linked to mitigations or accepted risks.
4. Threat models **shall** be reviewed and signed off by product security.
5. Models **shall** be updated on significant design change.
6. Outputs **shall** generate security requirements and test cases.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| DFD & boundaries | NIST SP 800-218 PW.1 |
| STRIDE coverage | Microsoft SDL; OWASP Threat Modeling |
| Traceability to mitigations | ISO/IEC 27001:2022 A.8.27 |

## 4. Metrics & Compliance
- Percentage of releases with current threat models.
- Threat-to-mitigation closure rate.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- NIST SP 800-218 PW.1
- Microsoft SDL Threat Modeling
- OWASP Threat Modeling


<!-- PRD-STD-003 -->
# PRD-STD-003 - SBOM & VEX Standard

## 1. Purpose & Scope
To define required SBOM/VEX formats, fields and exchange. Applies to all released software and firmware.

## 2. Normative Requirements
1. SBOMs **shall** be produced in SPDX or CycloneDX in machine-readable form.
2. SBOMs **shall** include the NTIA minimum elements and transitive dependencies.
3. SBOMs **shall** be generated automatically in CI/CD per release.
4. VEX statements **shall** communicate exploitability status of known vulnerabilities.
5. SBOM/VEX **shall** be retained and provided to customers and, for devices, to FDA.
6. SBOM accuracy **shall** be validated before release.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Format & minimum elements | NTIA minimum elements; SPDX (ISO/IEC 5962); CycloneDX |
| Generation & retention | NIST SP 800-218 PS.3 |
| Regulatory exchange | FDA 524B |

## 4. Metrics & Compliance
- Percentage of releases with valid SBOM.
- SBOM accuracy findings.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- NTIA SBOM minimum elements
- SPDX / CycloneDX
- NIST SP 800-218 PS.3
- FDA 524B


<!-- PRD-STD-004 -->
# PRD-STD-004 - Application Security Testing Standard

## 1. Purpose & Scope
To define SAST/DAST/SCA coverage and pass criteria. Applies to security testing in the product CI/CD pipeline.

## 2. Normative Requirements
1. SAST **shall** run on every build of in-scope code; high/critical findings **shall** block merge unless waived.
2. SCA **shall** run on every build to detect vulnerable/over-permissive dependencies.
3. DAST **shall** run against running applications at defined milestones.
4. Pass criteria and waiver authority **shall** be defined; waivers **shall** be time-bound.
5. Findings **shall** flow to tracking and remediation per the Vulnerability Scoring & Triage Standard.
6. Tooling **shall** be kept current.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| SAST/DAST/SCA gates | NIST SP 800-218 PW.7-PW.8 |
| Dependency analysis | NIST SP 800-218 PW.4 |
| Pass/waiver governance | ISO/IEC 27001:2022 A.8.29 |

## 4. Metrics & Compliance
- Gate pass rate.
- Open high/critical findings by age.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- NIST SP 800-218 PW.4-PW.8
- OWASP testing standards


<!-- PRD-STD-005 -->
# PRD-STD-005 - Software Composition Analysis Standard

## 1. Purpose & Scope
To define dependency scanning and license/vulnerability gates (SCA). Applies to all third-party and open-source dependencies.

## 2. Normative Requirements
1. Dependencies **shall** be scanned for known vulnerabilities on each build.
2. Direct and transitive dependencies **shall** be included.
3. Vulnerable dependencies **shall** be remediated within Vulnerability Scoring & Triage timelines.
4. License compliance **shall** be checked; prohibited licenses **shall** be blocked.
5. Dependency provenance/integrity **shall** be verified (e.g., checksums, signatures).
6. Results **shall** feed the SBOM and component inventory.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Dependency scanning | NIST SP 800-218 PW.4 |
| License governance | Open-source policy; legal review |
| Provenance | NIST SP 800-161; SLSA |

## 4. Metrics & Compliance
- Vulnerable dependencies by severity.
- Blocked-license incidents.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- NIST SP 800-218 PW.4
- NIST SP 800-161
- SLSA


<!-- PRD-STD-006 -->
# PRD-STD-006 - Product Cryptography Standard

## 1. Purpose & Scope
To define approved cryptography for shipped products. Applies to cryptography embedded in or used by products.

## 2. Normative Requirements
1. Products **shall** use TLS 1.2+ for network communications.
2. Symmetric/asymmetric algorithms and key sizes **shall** meet the enterprise Encryption Standard minimums.
3. Random number generation **shall** use cryptographically secure sources.
4. Custom or deprecated cryptography **shall not** be used.
5. Keys/secrets **shall not** be hard-coded; secure storage **shall** be used.
6. Where required, cryptographic modules **shall** be FIPS 140-3 validated.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Algorithms & protocols | NIST SP 800-57; SP 800-52 |
| Module validation | FIPS 140-3 |
| Key handling in products | NIST SP 800-218 PS.2 |

## 4. Metrics & Compliance
- Products using deprecated crypto (target zero).
- FIPS-validated coverage where required.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- NIST SP 800-52, 800-57
- FIPS 140-3
- ISO/IEC 27001:2022 A.8.24


<!-- PRD-STD-007 -->
# PRD-STD-007 - Code Signing & Artifact Integrity Standard

## 1. Purpose & Scope
To define signing keys, provenance and verification for artifacts. Applies to all build/release artifacts and firmware updates.

## 2. Normative Requirements
1. All release artifacts and updates **shall** be digitally signed.
2. Signing keys **shall** be protected in HSMs with access control and audit.
3. Build provenance/attestations **shall** be generated and verifiable (SLSA-aligned where feasible).
4. Consumers/devices **shall** verify signatures before execution/installation.
5. Key compromise **shall** trigger revocation and re-signing under the incident process.
6. Signing **shall** be enforced by the release gate.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Artifact signing | NIST SP 800-218 PS.2 |
| Provenance/attestation | SLSA; NIST SP 800-161 |
| Key protection | FIPS 140-3; NIST SP 800-57 |

## 4. Metrics & Compliance
- Percentage of artifacts signed.
- Signature-verification failures investigated.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- NIST SP 800-218 PS.2
- SLSA
- FIPS 140-3


<!-- PRD-STD-008 -->
# PRD-STD-008 - Security Requirements Standard

## 1. Purpose & Scope
To define the baseline security requirements catalog for products. Applies to all products as a starting baseline, tailored by threat model.

## 2. Normative Requirements
1. Products **shall** authenticate and authorize access to security-relevant functions.
2. Sensitive data **shall** be protected in transit and at rest.
3. Products **shall** log security-relevant events for forensics.
4. Products **shall** validate inputs and fail securely.
5. Products **shall** support secure update with signature verification.
6. Products **shall** avoid default credentials and support credential change.
7. Requirements **shall** be tailored using the threat model and applicable regulation.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Baseline requirements | NIST SP 800-218 PW.1-PW.2; OWASP ASVS |
| Device expectations | IEC 81001-5-1; FDA premarket |

## 4. Metrics & Compliance
- Requirement coverage per product.
- Traceability completeness to verification.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- OWASP ASVS
- NIST SP 800-218 PW.1-PW.2
- IEC 81001-5-1


<!-- PRD-STD-009 -->
# PRD-STD-009 - Vulnerability Scoring & Triage Standard

## 1. Purpose & Scope
To define CVSS-based scoring and triage thresholds for product vulnerabilities. Applies to vulnerabilities affecting Organization products and components.

## 2. Normative Requirements
1. Vulnerabilities **shall** be scored with CVSS and adjusted for exploitability and product context (including safety for devices).
2. Remediation timelines **shall** be defined by severity and deployment context.
3. Actively exploited vulnerabilities **shall** be expedited regardless of base score.
4. For devices, patient-safety impact **shall** be factored into prioritization.
5. Exceptions **shall** require compensating controls and approval.
6. Triage decisions **shall** be recorded and feed VEX.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Scoring | CVSS; CISA KEV |
| Safety weighting | FDA postmarket cybersecurity; ISO 14971 |
| Handling | ISO/IEC 30111 |

## 4. Metrics & Compliance
- Median time to triage.
- SLA compliance by severity.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- CVSS
- ISO/IEC 30111
- FDA postmarket cybersecurity


<!-- PRD-STD-010 -->
# PRD-STD-010 - Secure Design Review Standard

## 1. Purpose & Scope
To define criteria and gates for security design review. Applies to security design reviews at defined milestones.

## 2. Normative Requirements
1. A security design review **shall** occur before significant implementation begins and before release.
2. Reviews **shall** assess the threat model, security requirements coverage and architecture.
3. Reviews **shall** produce documented findings with owners and due dates.
4. Critical design findings **shall** be resolved or risk-accepted before proceeding.
5. Reviewers **shall** include product security and senior engineering.
6. Review records **shall** be retained.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Design review gate | NIST SP 800-218 PW.2 |
| Architecture & requirements | ISO/IEC 27001:2022 A.8.27 |

## 4. Metrics & Compliance
- Reviews completed on schedule.
- Critical design findings reopened.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- NIST SP 800-218 PW.2
- Microsoft SDL design review
- OWASP SAMM


<!-- PRD-PRO-001 -->
# PRD-PRO-001 - Threat Modeling Procedure

## 1. Purpose
To produce and review a product threat model.

## 2. Scope
Applies to threat modeling for new products and major changes.

## 3. Roles (RACI)
| Activity | Architect/Dev | Product Security | Product Mgmt |
| --- | --- | --- | --- |
| Build DFD & boundaries | R | A | I |
| Enumerate threats (STRIDE) | R | A | C |
| Rate & define mitigations | R | A | C |
| Review & sign off | C | A | C |
| Feed requirements/tests | R | A | I |

## 4. Process Steps
1. **Model the system** — create a data-flow diagram with trust boundaries. Outputs: DFD.
2. **Enumerate threats** — apply STRIDE to each element and flow. Outputs: threat list.
3. **Rate & mitigate** — score threats and define mitigations or accept risk. Outputs: rated threats.
4. **Review** — product security reviews and signs off. Outputs: approved threat model.
5. **Trace** — generate security requirements and test cases. Outputs: requirements/tests.

## 5. Records & Evidence
- Threat models, review sign-offs, derived requirements.

## 6. Related Documents & References
- Threat Modeling Standard (PRD-STD-002)
- Threat Modeling Policy (PRD-POL-004)


<!-- PRD-PRO-002 -->
# PRD-PRO-002 - PSIRT Vulnerability Handling Procedure

## 1. Purpose
To triage, fix and disclose product vulnerabilities through the PSIRT process.

## 2. Scope
Applies to internally and externally identified product vulnerabilities.

## 3. Roles (RACI)
| Activity | PSIRT Lead | Engineering | Product Mgmt | Regulatory | Comms |
| --- | --- | --- | --- | --- | --- |
| Intake & acknowledge | A | I | I | I | I |
| Validate & score | A | R | C | I | I |
| Decide fix & timeline | R | C | A | C | I |
| Develop & verify fix | A | R | C | I | I |
| Assess reportability | C | C | C | A | I |
| Advisory & VEX / disclose | A | C | C | C | R |

## 4. Process Steps
1. **Intake** — receive and acknowledge the report; open a case. Outputs: case.
2. **Validate & score** — reproduce and score (CVSS + context/safety). Outputs: severity.
3. **Plan** — decide fix approach and timeline. Outputs: plan.
4. **Fix** — develop, test and stage the fix through the release gate. Outputs: fix.
5. **Report** — assess regulatory reportability and file if required. Outputs: regulatory filing.
6. **Disclose** — publish advisory/VEX and coordinate disclosure. Outputs: advisory.

## 5. Records & Evidence
- PSIRT cases, scoring, fixes, advisories, VEX, regulatory filings.

## 6. Related Documents & References
- Coordinated Disclosure & PSIRT Policy (PRD-POL-008)
- ISO/IEC 30111 / 29147
- Postmarket Cybersecurity Management Policy (PRD-POL-013)


<!-- PRD-PRO-003 -->
# PRD-PRO-003 - Penetration Testing Procedure

## 1. Purpose
To scope, execute and remediate product penetration tests.

## 2. Scope
Applies to penetration testing of products and supporting services.

## 3. Roles (RACI)
| Activity | Product Security | Testers | Engineering |
| --- | --- | --- | --- |
| Define scope & RoE | A | C | C |
| Execute test | C | A | I |
| Report findings | C | A | I |
| Remediate | A | I | R |
| Retest & close | A | R | C |

## 4. Process Steps
1. **Scope** — define targets, rules of engagement and safety constraints. Outputs: scope/RoE.
2. **Execute** — perform testing per scope. Outputs: raw findings.
3. **Report** — risk-rate findings with reproduction. Outputs: report.
4. **Remediate** — fix findings within timelines (criticals may block release). Outputs: fixes.
5. **Retest** — verify remediation and close. Outputs: closure evidence.

## 5. Records & Evidence
- Scope/RoE, test reports, remediation and retest evidence.

## 6. Related Documents & References
- Penetration Testing Policy (PRD-POL-015)
- NIST SP 800-115
- OWASP Testing Guide


<!-- PRD-PRO-004 -->
# PRD-PRO-004 - Security Release Gate Procedure

## 1. Purpose
To collect evidence and obtain sign-off required to release.

## 2. Scope
Applies to all product releases passing the security gate.

## 3. Roles (RACI)
| Activity | Dev Lead | Product Security | Release Mgr | Product Owner |
| --- | --- | --- | --- | --- |
| Assemble evidence | R | A | C | I |
| Verify gate criteria | C | A | C | I |
| Security sign-off | I | A | C | C |
| Authorize release | I | C | R | A |

## 4. Process Steps
1. **Assemble** — collect SAST/DAST/SCA results, threat model, SBOM and finding status. Outputs: evidence pack.
2. **Verify** — confirm gate criteria met or waivers approved. Outputs: gate checklist.
3. **Sign off** — product security records security sign-off. Outputs: sign-off.
4. **Release** — release management/product owner authorize deployment. Outputs: release record.

## 5. Records & Evidence
- Gate evidence packs, sign-offs and release records.

## 6. Related Documents & References
- Secure Release & Deployment Policy (PRD-POL-009)
- NIST SP 800-218 RV


<!-- PRD-PRO-005 -->
# PRD-PRO-005 - SBOM Review & VEX Issuance Procedure

## 1. Purpose
To review SBOMs and publish VEX statements.

## 2. Scope
Applies to SBOM validation and VEX issuance per release.

## 3. Roles (RACI)
| Activity | Product Security | Build/DevOps | Compliance |
| --- | --- | --- | --- |
| Validate SBOM | A | R | I |
| Map components to CVEs | A | R | I |
| Author VEX | A | C | C |
| Publish/distribute | A | I | R |

## 4. Process Steps
1. **Validate** — confirm SBOM completeness/accuracy (incl. transitive deps). Outputs: validated SBOM.
2. **Analyze** — map components to known CVEs. Outputs: vulnerability mapping.
3. **VEX** — determine exploitability and author VEX statements. Outputs: VEX.
4. **Distribute** — publish to customers and, for devices, to FDA. Outputs: distribution record.

## 5. Records & Evidence
- SBOMs, vulnerability mappings, VEX statements, distribution records.

## 6. Related Documents & References
- SBOM Policy (PRD-POL-003)
- SBOM & VEX Standard (PRD-STD-003)


<!-- PRD-WI-001 -->
# PRD-WI-001 - SAST/DAST Pipeline WI

## 1. Purpose
To wire SAST/DAST/SCA into CI/CD with enforced gates.

## 2. Prerequisites
- Access to the CI/CD pipeline.
- Approved security tools and pass criteria.
- Defined waiver authority.

## 3. Step-by-Step Instructions
1. Add SAST and SCA steps to run on every build/PR.
2. Configure DAST to run against deployed test environments at milestones.
3. Set pass/fail thresholds; configure high/critical findings to block merge/release.
4. Route findings to the tracking system.
5. Configure time-bound waiver handling with approver.
6. Validate the pipeline blocks a seeded test finding.

## 4. Verification
- Pipeline runs SAST/SCA on each build and DAST at milestones.
- Seeded high finding blocks the gate.
- Findings appear in tracking.

## 5. Escalation
If gates cannot be enforced or are bypassed, halt releases of affected components and notify product security.

## 6. Related Documents
- Application Security Testing Standard (PRD-STD-004)
- Secure Software Development (SSDLC) Policy (PRD-POL-001)


<!-- PRD-WI-002 -->
# PRD-WI-002 - SBOM Generation WI

## 1. Purpose
To produce and attach an SBOM to a build.

## 2. Prerequisites
- SBOM generation tool integrated in CI/CD.
- Defined output format (SPDX or CycloneDX).

## 3. Step-by-Step Instructions
1. Run the SBOM generator against the build, including transitive dependencies.
2. Validate the SBOM contains the NTIA minimum elements.
3. Attach the SBOM to the release artifact and store it as a controlled record.
4. Run SCA against the SBOM to identify known vulnerabilities.
5. Record any deviations for VEX authoring.

## 4. Verification
- SBOM present in standard format with required fields.
- SBOM attached to the release and retained.
- SCA results captured.

## 5. Escalation
If an SBOM cannot be generated or is incomplete, block the release gate and notify product security.

## 6. Related Documents
- SBOM Policy (PRD-POL-003)
- SBOM & VEX Standard (PRD-STD-003)


<!-- PRD-WI-003 -->
# PRD-WI-003 - CVE Triage WI

## 1. Purpose
To assess a newly published CVE against the product inventory.

## 2. Prerequisites
- Access to SBOMs/component inventory.
- CVE/advisory source.
- Triage criteria (PRD-STD-009).

## 3. Step-by-Step Instructions
1. Identify affected components and versions from the CVE.
2. Search SBOMs/inventory for matching components across products.
3. Determine applicability and exploitability in product context.
4. Score and assign remediation per the triage standard.
5. Record the decision and prepare a VEX statement (affected / not affected / fixed).
6. Open remediation tasks for affected products.

## 4. Verification
- All products checked against the CVE.
- Applicability and score recorded.
- VEX status determined.

## 5. Escalation
If a critical, actively exploited CVE affects shipped products, invoke the PSIRT process and expedite.

## 6. Related Documents
- Vulnerability Scoring & Triage Standard (PRD-STD-009)
- PSIRT Vulnerability Handling Procedure (PRD-PRO-002)


<!-- PRD-WI-004 -->
# PRD-WI-004 - Code Signing WI

## 1. Purpose
To sign and verify a release artifact.

## 2. Prerequisites
- Access to signing service/HSM.
- Approved signing key.
- Release artifact ready and gated.

## 3. Step-by-Step Instructions
1. Confirm the artifact passed the security release gate.
2. Submit the artifact to the signing service using the protected key.
3. Generate and attach build provenance/attestation where applicable.
4. Verify the signature and provenance on a clean system.
5. Publish the signed artifact and record the signing event.

## 4. Verification
- Signature verifies with the correct key.
- Provenance/attestation present and valid.
- Signing event logged.

## 5. Escalation
If signature verification fails or key misuse is suspected, stop distribution, revoke as needed and raise an incident.

## 6. Related Documents
- Product Cryptography & Code Signing Policy (PRD-POL-010)
- Code Signing & Artifact Integrity Standard (PRD-STD-007)


<!-- PRD-RACI-001 -->
# PRD-RACI-001 - PSIRT Vulnerability Handling - RACI Matrix

Intake to coordinated disclosure of product flaws (ISO/IEC 29147 & 30111; FDA postmarket cyber).

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

| Activity | Reporter / Finder | PSIRT Lead | Engineering | Product Mgmt | Legal / Reg | CISO |
| --- | --- | --- | --- | --- | --- | --- |
| Receive & acknowledge report | R | A | I | I | I | I |
| Validate & assess (CVSS) | C | A | R | C | I | I |
| Decide fix & timeline | I | R | C | A | C | C |
| Develop & verify fix | I | A | R | C | I | I |
| Regulatory reportability call | I | C | C | C | R | A |
| Publish advisory & VEX | I | R | C | A | C | I |
| Coordinated disclosure | C | R | I | A | C | I |



<!-- PRD-RACI-002 -->
# PRD-RACI-002 - Secure Release Gate - RACI Matrix

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



<!-- PRD-RACI-003 -->
# PRD-RACI-003 - SBOM Generation & VEX Issuance - RACI Matrix

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
