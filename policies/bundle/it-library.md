# IT Security - Controlled Document Library



<!-- ITS-POL-001 -->
# ITS-POL-001 - Identity & Access Management Policy

## 1. Purpose
To govern the full lifecycle of digital identities and their entitlements, ensuring authenticated, authorized and accountable access, per **ISO/IEC 27001:2022 A.5.15-A.5.18, A.8.2-A.8.5**.

## 2. Scope
Applies to all identity types — workforce, privileged, service/machine and third-party — across all systems within scope.

## 3. Policy Statements
1. Identities **shall** be **uniquely** assigned and traceable to an accountable owner; shared interactive identities are prohibited.
2. **Role-based access control (RBAC)** with documented role definitions **shall** be the default authorization model.
3. **Multi-factor authentication shall** be enforced for all remote, privileged and sensitive access, using phishing-resistant methods where feasible.
4. **Privileged accounts shall** be vaulted, individually attributable, just-in-time where practical, and session-logged.
5. **Service and machine identities shall** be inventoried, owned, and credential-rotated; secrets **shall not** be hard-coded.
6. Joiner/mover/leaver changes **shall** be executed promptly; termination access removal **shall** complete the same business day.
7. **Access recertification shall** occur at least every six months (privileged quarterly).
8. Federation and SSO **shall** be preferred; directory integrations **shall** enforce centralized policy.

## 4. Roles & Responsibilities
- **IAM Team** — operates the identity platform and lifecycle automation.
- **System Owners** — define roles and authorize/recertify access.
- **Security** — monitors privileged activity and policy conformance.
- **Managers / HR** — trigger lifecycle events.

## 5. Compliance & Enforcement
Verified through access reviews, privileged-session monitoring and audit. Orphaned, excessive or unauthorized access is a reportable nonconformity.

## 6. Exceptions
Break-glass and standing exceptions **shall** be documented, monitored and CISO-approved.

## 7. Review & Maintenance
Reviewed at least annually.

## 8. References
ISO/IEC 27001:2022 A.5.15-A.5.18, A.8.2-A.8.5; NIST SP 800-63; NIST SP 800-53 AC/IA families; NIST SP 800-171 3.1.x / 3.5.x; CMMC AC & IA.


<!-- ITS-POL-002 -->
# ITS-POL-002 - Privileged Access Management Policy

## 1. Purpose
To control administrative and elevated access so privileged actions are minimized, authorized, attributable and monitored.

## 2. Scope
Applies to all privileged accounts and elevated entitlements across systems, applications, infrastructure and cloud.

## 3. Policy Statements
1. Privileged access **shall** be granted only on documented need and approved by the system owner.
2. Privileged accounts **shall** be individually attributable; shared admin accounts are prohibited except vaulted break-glass.
3. Privileged credentials **shall** be vaulted, rotated and retrieved through a privileged-access management (PAM) solution.
4. **Just-in-time** elevation with time limits **shall** be used where technically feasible.
5. Privileged sessions **shall** be logged and, for the most sensitive systems, recorded.
6. Multi-factor authentication **shall** be enforced for all privileged access.
7. Privileged entitlements **shall** be recertified at least quarterly.
8. Break-glass accounts **shall** be sealed, monitored and reviewed after every use.

## 4. Roles & Responsibilities
- **System Owners** — authorize and recertify privileged access.
- **PAM/IAM Team** — operates the vault and elevation workflows.
- **Security** — monitors privileged sessions.
- **Privileged Users** — comply with elevation and logging requirements.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.8.2, A.8.5, A.8.18
- NIST SP 800-53 AC-2(7), AC-6
- NIST SP 800-171 3.1.5-3.1.7
- CMMC AC.L2


<!-- ITS-POL-003 -->
# ITS-POL-003 - Network Security Policy

## 1. Purpose
To protect Organization networks through segmentation, controlled connectivity and monitoring.

## 2. Scope
Applies to all wired, wireless, virtual and cloud networks and remote-access services.

## 3. Policy Statements
1. Networks **shall** be segmented into trust zones; sensitive and OT environments **shall** be isolated from general networks.
2. Traffic between zones **shall** be controlled by default-deny rules and inspected where appropriate.
3. Remote access **shall** use encrypted, MFA-protected channels (VPN or zero-trust access).
4. Network devices **shall** be hardened, patched and centrally managed.
5. Network changes **shall** follow change management; rule bases **shall** be reviewed periodically.
6. Network activity **shall** be logged and monitored for anomalies.
7. Wireless networks **shall** use strong authentication and encryption; guest access **shall** be isolated.

## 4. Roles & Responsibilities
- **Network Engineering** — designs and operates the network securely.
- **Security** — sets requirements and monitors traffic.
- **Change Management** — governs network changes.
- **OT/Plant teams** — coordinate segmentation for industrial systems.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.8.20-A.8.22
- NIST SP 800-53 SC-7
- IEC 62443-3-3 (zones & conduits)
- NIST SP 800-82 (OT)


<!-- ITS-POL-004 -->
# ITS-POL-004 - Firewall & Perimeter Policy

## 1. Purpose
To govern firewall and boundary-protection rule management to enforce least-connectivity.

## 2. Scope
Applies to all firewalls, security groups, ACLs and boundary-protection devices.

## 3. Policy Statements
1. Rule bases **shall** operate on default-deny; only justified, documented flows **shall** be permitted.
2. Each rule **shall** record owner, business justification and review date.
3. Rule changes **shall** be requested, risk-reviewed and approved through change management.
4. Overly permissive ('any-any') rules **shall** be prohibited and remediated.
5. Rule bases **shall** be reviewed at least every six months and stale rules removed.
6. Boundary devices **shall** be hardened, patched and logged centrally.

## 4. Roles & Responsibilities
- **Firewall/Network Team** — implements and reviews rules.
- **Rule Owners** — justify and re-certify their rules.
- **Security** — risk-reviews changes.
- **Change Management** — approves changes.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.8.20, A.8.21
- NIST SP 800-41
- NIST SP 800-53 SC-7, CM-7


<!-- ITS-POL-005 -->
# ITS-POL-005 - Endpoint Security Policy

## 1. Purpose
To protect endpoints against compromise through hardening, detection, encryption and control.

## 2. Scope
Applies to all servers, workstations, laptops and managed mobile endpoints.

## 3. Policy Statements
1. Endpoints **shall** be deployed from a hardened baseline and centrally managed.
2. Endpoint detection and response (**EDR**) **shall** be installed, active and monitored on all supported endpoints.
3. Disk encryption **shall** be enabled on all portable endpoints.
4. Only approved software **shall** run; application allow-listing **shall** be used on high-risk endpoints.
5. Endpoints **shall** be patched within the timelines of the Patch Management Standard.
6. Local administrative rights **shall** be restricted and managed.
7. Lost or compromised endpoints **shall** be remotely locked or wiped and reported.

## 4. Roles & Responsibilities
- **Endpoint/IT Operations** — deploys and maintains endpoints.
- **Security/SOC** — monitors EDR and responds.
- **Users** — keep devices managed and report issues.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.8.1, A.8.7, A.8.24
- NIST SP 800-53 SI-3, SC-28
- CIS Controls v8 4 & 10


<!-- ITS-POL-006 -->
# ITS-POL-006 - Mobile Device & BYOD Policy

## 1. Purpose
To secure mobile and personally-owned (BYOD) devices that access Organization data.

## 2. Scope
Applies to all mobile devices, including BYOD, used to access Organization information or services.

## 3. Policy Statements
1. Mobile access to Organization data **shall** require enrollment in mobile device management (MDM) or a managed container.
2. Devices **shall** enforce screen lock, encryption and minimum OS version; jailbroken/rooted devices **shall** be blocked.
3. Organization data on BYOD **shall** be containerized and remotely wipeable without affecting personal data where feasible.
4. Only approved apps **shall** access Organization data; sideloading of risky apps **shall** be restricted.
5. Lost or stolen devices **shall** be reported promptly and the Organization data wiped.
6. BYOD use **shall** be subject to user acknowledgment of monitoring and wipe terms.

## 4. Roles & Responsibilities
- **IT/MDM Team** — operates enrollment and policy enforcement.
- **Security** — sets device requirements.
- **Users** — maintain compliant devices and report loss.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.6.7, A.8.1
- NIST SP 800-124
- NIST SP 800-53 AC-19


<!-- ITS-POL-007 -->
# ITS-POL-007 - Cryptography & Key Management Policy

## 1. Purpose
To ensure cryptography is used appropriately and that keys are managed securely throughout their lifecycle.

## 2. Scope
Applies to all use of cryptography and all cryptographic keys across Organization systems and products.

## 3. Policy Statements
1. Only approved, current algorithms and key lengths **shall** be used (see Encryption Standard); deprecated algorithms are prohibited.
2. Data classified Confidential or Restricted **shall** be encrypted at rest and in transit.
3. Keys **shall** be generated, stored, distributed, rotated, archived and destroyed under documented procedures.
4. Private and secret keys **shall** be protected in hardware security modules or equivalent where feasible.
5. Key access **shall** follow least privilege with separation of duties for key-management functions.
6. Compromised keys **shall** be revoked and replaced under the incident process.
7. Cryptographic agility **shall** be considered, including readiness for post-quantum migration.

## 4. Roles & Responsibilities
- **Cryptography/Key Custodians** — manage the key lifecycle.
- **Security Architecture** — approves algorithms and standards.
- **System Owners** — apply approved cryptography.
- **Security** — assures compliance.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.8.24
- NIST SP 800-57 (key management)
- NIST SP 800-53 SC-12, SC-13
- FIPS 140-3


<!-- ITS-POL-008 -->
# ITS-POL-008 - Certificate Management Policy

## 1. Purpose
To manage the lifecycle of digital certificates to prevent outages and trust failures.

## 2. Scope
Applies to all TLS, code-signing, client and device certificates used by the Organization.

## 3. Policy Statements
1. Certificates **shall** be issued only from approved certificate authorities.
2. A complete **certificate inventory** with expiry tracking **shall** be maintained.
3. Certificates **shall** be renewed before expiry; automated renewal **shall** be used where feasible.
4. Private keys **shall** be protected and **shall not** be shared across unrelated systems.
5. Weak keys, algorithms and short validity violations **shall** be prohibited (see Certificate & PKI Standard).
6. Compromised or mis-issued certificates **shall** be revoked promptly.
7. Internal CA infrastructure **shall** be hardened and access-controlled.

## 4. Roles & Responsibilities
- **PKI/Certificate Team** — operates issuance and renewal.
- **Service Owners** — track and renew their certificates.
- **Security** — sets PKI requirements and monitors expiry.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.8.24
- NIST SP 800-57
- CA/Browser Forum Baseline Requirements


<!-- ITS-POL-009 -->
# ITS-POL-009 - Cloud Security Policy

## 1. Purpose
To secure the Organization's use of cloud services under the shared-responsibility model.

## 2. Scope
Applies to all IaaS, PaaS and SaaS services and cloud accounts used by the Organization.

## 3. Policy Statements
1. Cloud accounts/subscriptions **shall** be governed centrally with enforced guardrails and baselines.
2. The shared-responsibility split **shall** be documented for each service.
3. Identity **shall** be federated; root/owner accounts **shall** be protected with MFA and seldom used.
4. Cloud resources **shall** be deployed via reviewed infrastructure-as-code with secure defaults.
5. Data **shall** be classified, encrypted and access-controlled; public exposure **shall** be prevented by default.
6. Cloud security posture **shall** be continuously monitored (CSPM) and misconfigurations remediated.
7. Logging **shall** be enabled across cloud accounts and centralized for monitoring.

## 4. Roles & Responsibilities
- **Cloud Platform/Engineering** — operates landing zones and guardrails.
- **Security** — defines baselines and monitors posture.
- **Workload Owners** — secure their cloud workloads.
- **CISO** — owns cloud risk.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.5.23, A.8.x
- ISO/IEC 27017 / 27018
- CIS Benchmarks (cloud)
- NIST SP 800-53; CSA CCM


<!-- ITS-POL-010 -->
# ITS-POL-010 - Email & Messaging Security Policy

## 1. Purpose
To protect against email- and messaging-borne threats and data exposure.

## 2. Scope
Applies to all Organization email and messaging services.

## 3. Policy Statements
1. Inbound mail **shall** be filtered for spam, malware and phishing; sandboxing of attachments **shall** be used where feasible.
2. Email authentication (**SPF, DKIM, DMARC**) **shall** be enforced for Organization domains.
3. Sensitive information **shall not** be sent through unapproved messaging channels; encryption **shall** be available for sensitive email.
4. External email **shall** be visibly tagged to reduce impersonation risk.
5. Suspected phishing **shall** be reportable with a one-click mechanism and triaged by Security.
6. Auto-forwarding to external domains **shall** be restricted.
7. Messaging platforms **shall** enforce retention and DLP consistent with policy.

## 4. Roles & Responsibilities
- **Messaging/IT Team** — operates filtering and authentication.
- **Security/SOC** — triages reported phishing.
- **Users** — report suspicious messages.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.8.20, A.8.23
- NIST SP 800-177 (Trustworthy Email)
- DMARC/DKIM/SPF (RFC 7489, 6376, 7208)


<!-- ITS-POL-011 -->
# ITS-POL-011 - Logging, Monitoring & SIEM Policy

## 1. Purpose
To ensure security-relevant events are logged, protected, retained and monitored to enable detection and investigation.

## 2. Scope
Applies to all in-scope systems, applications, network and cloud services.

## 3. Policy Statements
1. Security-relevant events **shall** be logged with sufficient detail (who, what, when, where, outcome).
2. Logs **shall** be forwarded to a central, time-synchronized platform (SIEM) and protected from alteration.
3. Log retention **shall** meet the Logging & Audit Standard and applicable regulation.
4. Detection use cases/alerts **shall** be defined, tuned and monitored.
5. Privileged and authentication events **shall** be logged and reviewed.
6. Clocks **shall** be synchronized to an authoritative time source.
7. Access to logs **shall** be restricted and itself logged.

## 4. Roles & Responsibilities
- **SOC/Monitoring Team** — operates the SIEM and triages alerts.
- **System Owners** — ensure log sources are onboarded.
- **Security** — defines detection use cases.
- **Incident Response** — uses logs for investigation.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.8.15, A.8.16, A.8.17
- NIST SP 800-92
- NIST SP 800-53 AU family


<!-- ITS-POL-012 -->
# ITS-POL-012 - Vulnerability & Patch Management Policy

## 1. Purpose
To ensure security vulnerabilities are systematically discovered, prioritized and remediated within risk-based timeframes, per **ISO/IEC 27001:2022 A.8.8** and NIST SP 800-40.

## 2. Scope
Applies to all Organization-managed assets — servers, endpoints, network and OT devices, containers, cloud workloads and applications — within scope.

## 3. Policy Statements
1. A complete, current **asset inventory shall** underpin vulnerability management; unmanaged assets are prohibited on production networks.
2. **Authenticated vulnerability scanning shall** be performed at least monthly, and continuously for internet-facing assets.
3. Findings **shall** be **prioritized** using CVSS plus exploitability and asset criticality (e.g., CISA KEV).
4. Remediation **shall** meet the following maximum timelines from validation:

| Severity | Internet-facing | Internal |
|---|---|---|
| Critical | 7 days | 15 days |
| High | 15 days | 30 days |
| Medium | 30 days | 90 days |
| Low | 90 days | Best effort |

5. Patches **shall** be tested before deployment except under the **emergency-change** path for actively exploited critical flaws.
6. Where remediation is infeasible, a **risk-based exception** with compensating controls **shall** be approved and time-bound.
7. Remediation status and SLA compliance **shall** be reported to leadership monthly.

## 4. Roles & Responsibilities
- **SecOps / VM Team** — scans, scores, tracks and reports.
- **System Owners** — accountable for timely remediation.
- **IT Operations** — tests and deploys patches.
- **CISO** — approves exceptions and owns the program.

## 5. Compliance & Enforcement
Verified through scan data, SLA dashboards and audit. Missed SLAs without an approved exception are nonconformities.

## 6. Exceptions
Documented, compensated, time-bound and CISO-approved; tracked in the exception register.

## 7. Review & Maintenance
Reviewed at least annually.

## 8. References
ISO/IEC 27001:2022 A.8.8; NIST SP 800-40; NIST SP 800-53 RA-5 / SI-2; NIST SP 800-171 3.11.x / 3.14.x; CISA KEV catalog. For OT, align with IEC 62443-2-3 patch management.


<!-- ITS-POL-013 -->
# ITS-POL-013 - Malware Protection Policy

## 1. Purpose
To prevent, detect and respond to malware across Organization systems.

## 2. Scope
Applies to all endpoints, servers, email and removable media within scope.

## 3. Policy Statements
1. Anti-malware/EDR **shall** be deployed, current and active on all supported systems.
2. Signatures and engines **shall** update automatically; detections **shall** alert the SOC.
3. Email and web traffic **shall** be scanned; risky file types **shall** be controlled.
4. Removable media **shall** be scanned and controlled per the Wireless & Removable Media Policy.
5. Suspected infections **shall** be isolated and handled under the incident process.
6. Application allow-listing **shall** be used on high-risk systems.
7. Users **shall not** disable malware protection.

## 4. Roles & Responsibilities
- **Security/SOC** — monitors and responds to detections.
- **IT Operations** — maintains agents and updates.
- **Users** — keep protection enabled and report alerts.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.8.7
- NIST SP 800-83
- NIST SP 800-53 SI-3


<!-- ITS-POL-014 -->
# ITS-POL-014 - Backup & Recovery Policy

## 1. Purpose
To ensure data and systems can be restored after loss, corruption or ransomware through reliable, tested backups.

## 2. Scope
Applies to all critical data and systems within scope.

## 3. Policy Statements
1. Backups **shall** be performed at frequencies meeting defined recovery-point objectives (**RPO**).
2. Backups **shall** follow a resilient strategy (e.g., 3-2-1) with at least one **immutable or offline** copy.
3. Backup data **shall** be encrypted and access-controlled.
4. Restore tests **shall** be performed at least quarterly for critical systems and recorded.
5. Recovery-time objectives (**RTO**) **shall** be defined and validated.
6. Backup infrastructure **shall** be segregated from production credentials to resist ransomware.
7. Backup failures **shall** alert and be remediated promptly.

## 4. Roles & Responsibilities
- **Backup/IT Operations** — operates and tests backups.
- **System Owners** — define RPO/RTO.
- **Security** — assures backup integrity and isolation.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.8.13
- NIST SP 800-53 CP-9, CP-10
- NIST SP 800-209


<!-- ITS-POL-015 -->
# ITS-POL-015 - Change Management Policy

## 1. Purpose
To ensure changes to systems and configurations are controlled, assessed and reversible.

## 2. Scope
Applies to changes to production systems, applications, infrastructure and configurations across the ISMS and QMS.

## 3. Policy Statements
1. All changes **shall** be requested, risk-assessed and authorized before implementation.
2. Changes **shall** be classified (standard, normal, emergency) with appropriate approval paths.
3. Security impact **shall** be assessed for each change.
4. Changes **shall** be tested and have a documented rollback plan.
5. Emergency changes **shall** follow an expedited path and be reviewed retrospectively.
6. Change records **shall** be retained and traceable.
7. Segregation of duties **shall** apply between request, approval and implementation where feasible.

## 4. Roles & Responsibilities
- **Change Manager / CAB** — governs and approves changes.
- **Requestors/Implementers** — submit and execute changes.
- **Security** — assesses security impact.
- **QA** — validates changes affecting regulated product.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.8.32
- ISO 13485:2016 Cl. 7.5
- NIST SP 800-53 CM-3


<!-- ITS-POL-016 -->
# ITS-POL-016 - Configuration Management Policy

## 1. Purpose
To establish and maintain secure baseline configurations and control configuration drift.

## 2. Scope
Applies to all managed systems, devices and cloud resources.

## 3. Policy Statements
1. Approved baseline configurations **shall** be defined for each platform (see Hardening Standard).
2. Systems **shall** be deployed from approved baselines or images.
3. Configuration **shall** be managed as code or via configuration-management tooling where feasible.
4. Drift from baseline **shall** be detected and remediated.
5. Unauthorized configuration changes **shall** be prevented or alerted.
6. A configuration inventory/CMDB **shall** be maintained.
7. Baselines **shall** be reviewed and updated for new threats and versions.

## 4. Roles & Responsibilities
- **Configuration/Platform Team** — maintains baselines and CMDB.
- **System Owners** — keep systems compliant.
- **Security** — defines and audits baselines.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.8.9
- NIST SP 800-53 CM family
- CIS Benchmarks


<!-- ITS-POL-017 -->
# ITS-POL-017 - Data Loss Prevention Policy

## 1. Purpose
To prevent unauthorized disclosure or exfiltration of sensitive data.

## 2. Scope
Applies to sensitive data in use, in motion and at rest across endpoints, email, web and cloud.

## 3. Policy Statements
1. DLP controls **shall** be deployed to detect and prevent unauthorized movement of Confidential and Restricted data.
2. DLP policies **shall** align to data classification and regulatory obligations.
3. High-risk egress channels (email, web upload, removable media, cloud sync) **shall** be monitored and controlled.
4. DLP alerts **shall** be triaged; confirmed exfiltration **shall** be handled as an incident.
5. Encryption and rights management **shall** support DLP for the most sensitive data.
6. DLP exceptions **shall** be documented and time-bound.

## 4. Roles & Responsibilities
- **Security/DLP Team** — operates and tunes DLP.
- **Data Owners** — define sensitive data and rules.
- **Incident Response** — handles confirmed exfiltration.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.8.12
- NIST SP 800-53 AC-4, SC-7
- Data Classification & Handling Policy (ENT-POL-005)


<!-- ITS-POL-018 -->
# ITS-POL-018 - Secure Configuration & Hardening Policy

## 1. Purpose
To mandate hardening of systems and platforms to reduce attack surface.

## 2. Scope
Applies to all operating systems, applications, databases, containers and cloud services.

## 3. Policy Statements
1. Systems **shall** be hardened to an approved baseline before production use.
2. Unused services, ports, accounts and features **shall** be disabled or removed.
3. Default credentials **shall** be changed and administrative interfaces protected.
4. Hardening **shall** be verified by automated configuration scanning.
5. Deviations **shall** be risk-assessed, documented and approved.
6. Baselines **shall** track recognized benchmarks (e.g., CIS) and be updated regularly.

## 4. Roles & Responsibilities
- **Platform/Engineering Teams** — apply hardening.
- **Security** — defines baselines and verifies compliance.
- **System Owners** — maintain hardened state.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.8.9
- CIS Benchmarks
- NIST SP 800-53 CM-6, CM-7
- DISA STIGs (where applicable)


<!-- ITS-POL-019 -->
# ITS-POL-019 - Wireless & Removable Media Policy

## 1. Purpose
To control the security risks of wireless networks and removable media.

## 2. Scope
Applies to all Organization wireless networks and use of removable media.

## 3. Policy Statements
1. Corporate wireless **shall** use strong authentication (e.g., 802.1X/WPA3-Enterprise) and encryption.
2. Guest wireless **shall** be isolated from corporate and OT networks.
3. Rogue access points **shall** be detected and removed.
4. Use of removable media **shall** be restricted by default and require business justification.
5. Permitted removable media **shall** be encrypted and malware-scanned on connection.
6. Sensitive data on removable media **shall** be encrypted and tracked; loss **shall** be reported.
7. Auto-run of removable media **shall** be disabled.

## 4. Roles & Responsibilities
- **Network/Endpoint Teams** — enforce wireless and media controls.
- **Security** — sets requirements and monitors.
- **Users** — follow media-handling rules.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.7.10, A.8.1, A.8.20
- NIST SP 800-53 MP-7, AC-18
- NIST SP 800-97 (wireless)


<!-- ITS-STD-001 -->
# ITS-STD-001 - System Hardening & Configuration Standard

## 1. Purpose & Scope
To define baseline configuration requirements by platform. Applies to operating systems, databases, containers, network devices and cloud services.

## 2. Normative Requirements
1. Each platform **shall** have a documented baseline derived from a recognized benchmark (e.g., CIS Level 1+).
2. Administrative interfaces **shall** be restricted, authenticated with MFA and not exposed publicly.
3. Only required services and ports **shall** be enabled.
4. Logging and time synchronization **shall** be enabled per the Logging & Audit Standard.
5. Baseline compliance **shall** be scanned at least monthly with deviations remediated or risk-accepted.
6. Images and templates **shall** be patched and re-baselined on a defined cadence.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Hardened baselines | ISO/IEC 27001:2022 A.8.9; CIS Benchmarks |
| Least functionality | NIST SP 800-53 CM-7 |
| Configuration monitoring | NIST SP 800-53 CM-6, SI-7 |

## 4. Metrics & Compliance
- Baseline compliance percentage by platform.
- Mean time to remediate configuration drift.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- ISO/IEC 27001:2022 A.8.9
- CIS Benchmarks
- NIST SP 800-53 CM family


<!-- ITS-STD-002 -->
# ITS-STD-002 - Encryption Standard

## 1. Purpose & Scope
To define minimum cryptographic algorithms, protocols and data-protection requirements. Applies to all encryption of data in transit and at rest across Organization systems.

## 2. Normative Requirements
1. Data in transit **shall** use TLS 1.2 or higher; TLS 1.0/1.1 and SSL are prohibited.
2. Symmetric encryption **shall** use AES-128 or stronger (AES-256 for Restricted).
3. Asymmetric keys **shall** be RSA-3072+ or ECC P-256+; hashing **shall** use SHA-256 or stronger.
4. Data classified Confidential/Restricted **shall** be encrypted at rest.
5. Deprecated algorithms (MD5, SHA-1, DES, 3DES, RC4) **shall not** be used.
6. Cryptographic modules **shall** be FIPS 140-3 validated where required by contract or regulation.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Transit encryption | ISO/IEC 27001:2022 A.8.24; NIST SP 800-52 (TLS) |
| At-rest encryption | NIST SP 800-53 SC-28 |
| Algorithm selection | NIST SP 800-57; FIPS 140-3 |

## 4. Metrics & Compliance
- Percentage of services enforcing TLS 1.2+.
- Findings of deprecated algorithm use.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- ISO/IEC 27001:2022 A.8.24
- NIST SP 800-52, 800-57
- FIPS 140-3


<!-- ITS-STD-003 -->
# ITS-STD-003 - Certificate & PKI Standard

## 1. Purpose & Scope
To define PKI and certificate profile requirements. Applies to all certificates and certificate authorities used by the Organization.

## 2. Normative Requirements
1. Public-facing certificates **shall** have validity not exceeding the CA/Browser Forum maximum.
2. Keys **shall** meet the minimum sizes in the Encryption Standard.
3. Certificates **shall** be issued only from approved CAs with documented trust chains.
4. Wildcard and long-lived certificates **shall** be minimized and justified.
5. Revocation (CRL/OCSP) **shall** be available and monitored.
6. Internal CA keys **shall** be protected in HSMs with split control.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Certificate profiles & validity | CA/Browser Forum Baseline Requirements |
| Key protection | NIST SP 800-57; FIPS 140-3 |
| Lifecycle & revocation | ISO/IEC 27001:2022 A.8.24 |

## 4. Metrics & Compliance
- Certificates expiring without renewal.
- Percentage of CA keys in HSMs.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- CA/Browser Forum BR
- NIST SP 800-57
- ISO/IEC 27001:2022 A.8.24


<!-- ITS-STD-004 -->
# ITS-STD-004 - IAM & MFA Standard

## 1. Purpose & Scope
To define authenticator assurance, MFA and session requirements. Applies to authentication to all Organization systems.

## 2. Normative Requirements
1. Remote, privileged and sensitive access **shall** require MFA at AAL2 or higher.
2. Phishing-resistant authenticators (FIDO2/WebAuthn, PIV/CAC) **shall** be used for privileged and high-risk access where feasible.
3. SMS-based OTP **shall** be avoided for privileged access.
4. Identity federation/SSO **shall** be preferred over local credentials.
5. Sessions **shall** expire after defined idle and absolute lifetimes.
6. Step-up authentication **shall** be required for sensitive transactions.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| MFA & assurance | NIST SP 800-63B (AAL2+); ISO/IEC 27001:2022 A.8.5 |
| Phishing resistance | FIDO2/WebAuthn; NIST 800-171 3.5.3 |
| Session management | NIST SP 800-53 AC-12 |

## 4. Metrics & Compliance
- MFA coverage by access type.
- Percentage of privileged access using phishing-resistant MFA.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- NIST SP 800-63B
- ISO/IEC 27001:2022 A.5.17, A.8.5
- NIST SP 800-171 3.5.x


<!-- ITS-STD-005 -->
# ITS-STD-005 - Vulnerability Management Standard

## 1. Purpose & Scope
To define vulnerability severity scoring and remediation timelines. Applies to all vulnerability findings across in-scope assets.

## 2. Normative Requirements
1. Findings **shall** be scored using CVSS plus exploitability (e.g., CISA KEV) and asset criticality.
2. Remediation **shall** meet the timelines in the Vulnerability & Patch Management Policy.
3. Internet-facing assets **shall** be scanned continuously; internal assets at least monthly.
4. Authenticated scanning **shall** be used where feasible.
5. Exceptions **shall** require compensating controls and time limits.
6. Remediation SLA compliance **shall** be reported monthly.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Scoring & prioritization | CVSS; CISA KEV; ISO/IEC 27001:2022 A.8.8 |
| Scan coverage | NIST SP 800-53 RA-5 |
| Remediation SLAs | NIST SP 800-40 |

## 4. Metrics & Compliance
- SLA compliance by severity.
- Open critical/high vulnerabilities by age.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- ISO/IEC 27001:2022 A.8.8
- NIST SP 800-40
- NIST SP 800-53 RA-5
- CISA KEV


<!-- ITS-STD-006 -->
# ITS-STD-006 - Cloud Security Baseline Standard

## 1. Purpose & Scope
To define mandatory guardrails for cloud accounts and workloads. Applies to all IaaS/PaaS accounts and subscriptions.

## 2. Normative Requirements
1. Root/owner accounts **shall** have MFA and be used only for break-glass.
2. Centralized logging and a security-monitoring baseline **shall** be enabled in every account.
3. Public exposure of storage and databases **shall** be blocked by default; exceptions require approval.
4. Encryption at rest **shall** be enabled using managed keys; customer-managed keys for Restricted data.
5. Infrastructure **shall** be provisioned via reviewed IaC; manual changes **shall** be minimized.
6. Posture management (CSPM) **shall** continuously check against the baseline.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Account guardrails | ISO/IEC 27017; CIS cloud benchmarks |
| Data protection | ISO/IEC 27018; NIST SP 800-53 SC-28 |
| Posture monitoring | CSA CCM; NIST SP 800-53 CA-7 |

## 4. Metrics & Compliance
- CSPM compliance score.
- Number of public-exposure exceptions.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- ISO/IEC 27017 / 27018
- CIS cloud benchmarks
- CSA CCM
- NIST SP 800-53


<!-- ITS-STD-007 -->
# ITS-STD-007 - Logging & Audit Standard

## 1. Purpose & Scope
To define required log events, fields, retention and integrity. Applies to all in-scope log sources.

## 2. Normative Requirements
1. Logs **shall** capture authentication, authorization, privileged actions, configuration changes and security events.
2. Each event **shall** include timestamp (synchronized), source, actor, action and outcome.
3. Logs **shall** be centralized, access-controlled and protected against tampering.
4. Security logs **shall** be retained for at least 12 months (or longer where required), with 90 days readily searchable.
5. Critical detections **shall** generate alerts to the SOC.
6. Log source coverage **shall** be monitored for gaps.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Event coverage & fields | ISO/IEC 27001:2022 A.8.15; NIST SP 800-92 |
| Integrity & access | NIST SP 800-53 AU-9 |
| Retention | NIST SP 800-53 AU-11; sector regulation |

## 4. Metrics & Compliance
- Log-source coverage percentage.
- Alert triage time.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- ISO/IEC 27001:2022 A.8.15-A.8.17
- NIST SP 800-92
- NIST SP 800-53 AU family


<!-- ITS-STD-008 -->
# ITS-STD-008 - Network Segmentation Standard

## 1. Purpose & Scope
To define network zoning, trust boundaries and flow control requirements. Applies to all network environments, including OT and cloud.

## 2. Normative Requirements
1. Networks **shall** be divided into trust zones with documented allowed flows (default-deny).
2. OT/ICS environments **shall** be segmented from IT per a defensible architecture (e.g., zones & conduits).
3. Management interfaces **shall** reside on dedicated management networks.
4. East-west traffic in sensitive zones **shall** be controlled and inspected where feasible.
5. Inter-zone flows **shall** be reviewed at least every six months.
6. Remote access **shall** terminate into a controlled zone, not directly into sensitive segments.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Segmentation & flows | ISO/IEC 27001:2022 A.8.20-A.8.22; NIST SP 800-53 SC-7 |
| OT zones & conduits | IEC 62443-3-3; NIST SP 800-82 |

## 4. Metrics & Compliance
- Percentage of zones with documented flow policy.
- Stale inter-zone rules removed per review.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- ISO/IEC 27001:2022 A.8.20-A.8.22
- IEC 62443-3-3
- NIST SP 800-82
- NIST SP 800-53 SC-7


<!-- ITS-STD-009 -->
# ITS-STD-009 - Patch Management Standard

## 1. Purpose & Scope
To define patch cadence and SLAs for deployment. Applies to all managed assets requiring patching.

## 2. Normative Requirements
1. Vendor patches **shall** be assessed within defined windows of release.
2. Standard patch cadence **shall** be at least monthly; out-of-band patching **shall** apply to actively exploited flaws.
3. Patches **shall** be tested before broad deployment, except emergency cases.
4. Patch deployment **shall** meet the remediation timelines in the Vulnerability Management Standard.
5. Patch compliance **shall** be measured and reported.
6. Unsupported/end-of-life software **shall** be remediated or risk-accepted with compensating controls.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Patch cadence & SLAs | ISO/IEC 27001:2022 A.8.8; NIST SP 800-40 |
| Testing & rollback | NIST SP 800-53 CM-3, SI-2 |

## 4. Metrics & Compliance
- Patch compliance percentage.
- EOL systems remaining.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- ISO/IEC 27001:2022 A.8.8
- NIST SP 800-40
- NIST SP 800-53 SI-2


<!-- ITS-STD-010 -->
# ITS-STD-010 - Backup & Recovery Standard

## 1. Purpose & Scope
To define backup frequency, recovery objectives and restore-test requirements. Applies to all critical data and systems.

## 2. Normative Requirements
1. Each critical system **shall** have documented RPO and RTO.
2. Backup frequency **shall** meet the RPO; critical data RPO **shall not** exceed 24 hours unless risk-accepted.
3. At least one backup copy **shall** be immutable or offline to resist ransomware.
4. Restore tests **shall** be performed at least quarterly for critical systems.
5. Backups **shall** be encrypted and access-controlled.
6. Backup success/failure **shall** be monitored and remediated.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Backup & RPO/RTO | ISO/IEC 27001:2022 A.8.13; NIST SP 800-53 CP-9/CP-10 |
| Immutability & ransomware | NIST SP 800-209 |

## 4. Metrics & Compliance
- Restore-test success rate.
- Backup failure rate.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- ISO/IEC 27001:2022 A.8.13
- NIST SP 800-53 CP family
- NIST SP 800-209


<!-- ITS-PRO-001 -->
# ITS-PRO-001 - Patch Management Procedure

## 1. Purpose
To operate the regular and emergency patching workflow.

## 2. Scope
Applies to patching of all managed assets.

## 3. Roles (RACI)
| Activity | System Owner | Patch/IT Ops | Security | Change Mgmt |
| --- | --- | --- | --- | --- |
| Identify applicable patches | I | R | A | I |
| Risk-assess & schedule | C | R | A | C |
| Test patches | C | R | C | I |
| Approve change | C | C | C | A |
| Deploy & verify | A | R | C | I |

## 4. Process Steps
1. **Identify** — collect applicable patches from vendor feeds and vulnerability data. Outputs: patch list.
2. **Assess** — prioritize by severity/exploitability and schedule within SLA. Outputs: schedule.
3. **Test** — validate in non-production; prepare rollback. Outputs: test results.
4. **Approve** — obtain change approval (expedited for emergencies). Outputs: change record.
5. **Deploy** — roll out in waves and verify success. Outputs: deployment report.
6. **Confirm** — rescan to confirm remediation and update compliance. Outputs: updated status.

## 5. Records & Evidence
- Patch lists, test results, change records, deployment and compliance reports.

## 6. Related Documents & References
- Patch Management Standard (ITS-STD-009)
- Vulnerability & Patch Management Policy (ITS-POL-012)
- Change Management Policy (ITS-POL-015)


<!-- ITS-PRO-002 -->
# ITS-PRO-002 - Vulnerability Remediation Procedure

## 1. Purpose
To take a vulnerability finding from identification to verified closure.

## 2. Scope
Applies to vulnerabilities identified by scanning, testing or disclosure.

## 3. Roles (RACI)
| Activity | VM/SecOps | System Owner | Security | CISO |
| --- | --- | --- | --- | --- |
| Validate finding | R | C | A | I |
| Assign & prioritize | A | R | C | I |
| Remediate | C | R | A | I |
| Grant exception | C | C | R | A |
| Verify closure | R | C | A | I |

## 4. Process Steps
1. **Validate** — confirm the finding and remove false positives. Outputs: validated finding.
2. **Prioritize** — score and assign to the system owner with an SLA. Outputs: assignment.
3. **Remediate** — patch, reconfigure or mitigate. Outputs: remediation action.
4. **Exception (if needed)** — document compensating controls and obtain approval. Outputs: exception record.
5. **Verify** — rescan/retest and close. Outputs: closure evidence.

## 5. Records & Evidence
- Findings, assignments, remediation evidence, exceptions and closures.

## 6. Related Documents & References
- Vulnerability Management Standard (ITS-STD-005)
- Vulnerability & Patch Management Policy (ITS-POL-012)


<!-- ITS-PRO-003 -->
# ITS-PRO-003 - Privileged Access Management Procedure

## 1. Purpose
To request, approve, check out and review privileged access.

## 2. Scope
Applies to all privileged access via the PAM solution.

## 3. Roles (RACI)
| Activity | Requestor | System Owner | PAM/IAM | Security |
| --- | --- | --- | --- | --- |
| Request access | R | A | C | I |
| Approve | I | A | C | C |
| Check out / elevate | R | I | A | I |
| Monitor session | I | I | C | A |
| Review & revoke | I | A | R | C |

## 4. Process Steps
1. **Request** — submit a privileged-access request with justification and duration. Outputs: request.
2. **Approve** — system owner approves; security reviews high-risk requests. Outputs: approval.
3. **Elevate** — retrieve credentials or elevate just-in-time through the vault. Outputs: session.
4. **Monitor** — log/record the session. Outputs: session log.
5. **Revoke & review** — expire access and include in quarterly recertification. Outputs: review record.

## 5. Records & Evidence
- Access requests, approvals, session logs and recertifications.

## 6. Related Documents & References
- Privileged Access Management Policy (ITS-POL-002)
- IAM & MFA Standard (ITS-STD-004)


<!-- ITS-PRO-004 -->
# ITS-PRO-004 - Certificate Lifecycle Procedure

## 1. Purpose
To request, issue, renew and revoke certificates.

## 2. Scope
Applies to all managed certificates.

## 3. Roles (RACI)
| Activity | Service Owner | PKI Team | Security |
| --- | --- | --- | --- |
| Request certificate | R | A | C |
| Validate & issue | C | A | C |
| Deploy | R | C | I |
| Renew before expiry | A | R | I |
| Revoke if compromised | C | R | A |

## 4. Process Steps
1. **Request** — submit CSR with required attributes to an approved CA. Outputs: request.
2. **Issue** — validate and issue per the Certificate & PKI Standard. Outputs: certificate.
3. **Deploy** — install and verify the certificate and chain. Outputs: deployment confirmation.
4. **Track & renew** — monitor expiry and renew (automate where feasible). Outputs: renewal.
5. **Revoke** — revoke compromised or superseded certificates and replace. Outputs: revocation.

## 5. Records & Evidence
- Certificate inventory, requests, renewals and revocations.

## 6. Related Documents & References
- Certificate Management Policy (ITS-POL-008)
- Certificate & PKI Standard (ITS-STD-003)


<!-- ITS-PRO-005 -->
# ITS-PRO-005 - Backup & Restore Procedure

## 1. Purpose
To operate and validate backup and restore.

## 2. Scope
Applies to backup and recovery of critical data and systems.

## 3. Roles (RACI)
| Activity | Backup/IT Ops | System Owner | Security |
| --- | --- | --- | --- |
| Configure backups | R | A | C |
| Monitor jobs | R | I | C |
| Perform restore test | R | A | C |
| Report results | A | C | I |

## 4. Process Steps
1. **Configure** — set backup scope, schedule and immutability to meet RPO. Outputs: backup config.
2. **Monitor** — track job success and remediate failures. Outputs: job status.
3. **Restore test** — perform scheduled restore to validate recoverability and RTO. Outputs: test record.
4. **Report** — record results and feed metrics. Outputs: report.

## 5. Records & Evidence
- Backup configurations, job logs, restore-test records.

## 6. Related Documents & References
- Backup & Recovery Policy (ITS-POL-014)
- Backup & Recovery Standard (ITS-STD-010)


<!-- ITS-WI-001 -->
# ITS-WI-001 - Firewall Rule Change WI

## 1. Purpose
To request, review and apply a firewall rule change.

## 2. Prerequisites
- Approved change request with business justification.
- Access to firewall management.
- Current rule base export.

## 3. Step-by-Step Instructions
1. Capture the requested flow (source, destination, port, protocol, justification, owner).
2. Review against least-connectivity; reject 'any-any' requests.
3. Risk-assess and obtain change approval.
4. Implement the rule with description and review date.
5. Test the flow and confirm no unintended access.
6. Document the change and update the rule base record.

## 4. Verification
- Requested flow works; no broader access than approved.
- Rule has owner, justification and review date.
- Change record completed.

## 5. Escalation
If the change causes an outage or unexpected exposure, roll back and notify Security and the change manager.

## 6. Related Documents
- Firewall & Perimeter Policy (ITS-POL-004)
- Network Segmentation Standard (ITS-STD-008)
- Change Management Policy (ITS-POL-015)


<!-- ITS-WI-002 -->
# ITS-WI-002 - MFA Enrollment WI

## 1. Purpose
To enroll strong (phishing-resistant where feasible) authentication for a user or admin.

## 2. Prerequisites
- Verified identity of the enrollee.
- Approved authenticator type per the IAM & MFA Standard.
- Access to the identity platform.

## 3. Step-by-Step Instructions
1. Confirm the enrollee's identity through an approved method.
2. Register the approved authenticator (FIDO2 key, authenticator app, PIV) — prefer phishing-resistant for admins.
3. Test authentication with the new factor.
4. Register a backup factor and record recovery options.
5. For admins, associate the factor with privileged access in the PAM solution.
6. Record completion.

## 4. Verification
- User can authenticate with MFA.
- Backup factor registered.
- Admin MFA bound to privileged access.

## 5. Escalation
If identity cannot be verified or enrollment fails repeatedly, halt and escalate to the IAM team and Security.

## 6. Related Documents
- IAM & MFA Standard (ITS-STD-004)
- Identity & Access Management Policy (ITS-POL-001)


<!-- ITS-WI-003 -->
# ITS-WI-003 - Server Hardening WI

## 1. Purpose
To apply and verify the hardening baseline on a server.

## 2. Prerequisites
- Approved baseline for the OS/platform.
- Configuration scanning tool.
- Change approval for production.

## 3. Step-by-Step Instructions
1. Deploy from the approved hardened image or apply the baseline configuration.
2. Disable unused services, ports and accounts; change default credentials.
3. Enable logging, time sync and EDR.
4. Run the configuration scan against the baseline.
5. Remediate deviations or record approved exceptions.
6. Record the hardened state in the CMDB.

## 4. Verification
- Configuration scan passes the baseline (or deviations are approved).
- EDR and logging active.
- CMDB updated.

## 5. Escalation
If hardening breaks a required function, document, risk-assess and seek an approved exception before exposing the system.

## 6. Related Documents
- Secure Configuration & Hardening Policy (ITS-POL-018)
- System Hardening & Configuration Standard (ITS-STD-001)


<!-- ITS-WI-004 -->
# ITS-WI-004 - Certificate Renewal WI

## 1. Purpose
To renew and deploy an expiring certificate.

## 2. Prerequisites
- Certificate expiry alert.
- Access to the CA and target service.
- Service owner availability.

## 3. Step-by-Step Instructions
1. Identify the expiring certificate and its dependencies.
2. Generate a new CSR meeting the Certificate & PKI Standard.
3. Obtain the certificate from the approved CA.
4. Deploy to the service and verify the full chain.
5. Confirm services operate and old certificate is retired.
6. Update the certificate inventory and expiry tracker.

## 4. Verification
- New certificate served with valid chain.
- No expiry/trust errors.
- Inventory updated.

## 5. Escalation
If renewal cannot complete before expiry, escalate to the service owner and PKI team; plan a maintenance window to avoid outage.

## 6. Related Documents
- Certificate Management Policy (ITS-POL-008)
- Certificate & PKI Standard (ITS-STD-003)


<!-- ITS-RACI-001 -->
# ITS-RACI-001 - Vulnerability & Patch Management - RACI Matrix

Discovery to verified remediation with SLAs (ISO 27001 A.8.8; NIST SP 800-40).

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

| Activity | System Owner | SecOps / VM | IT Operations | Change Mgmt | CISO |
| --- | --- | --- | --- | --- | --- |
| Run vulnerability scans | I | R | C | I | A |
| Score & prioritize findings | C | R | I | I | A |
| Assign remediation owner | A | R | C | I | I |
| Test & deploy patch | A | C | R | C | I |
| Approve emergency change | C | C | C | R | A |
| Verify & close finding | A | R | C | I | I |
| Grant risk-based exception | C | R | I | I | A |



<!-- ITS-RACI-002 -->
# ITS-RACI-002 - Identity Lifecycle (Joiner / Mover / Leaver) - RACI Matrix

Provisioning, modification and de-provisioning of access (ISO 27001 A.5.16-A.5.18).

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

| Activity | People Manager | HR | IAM / IT | System Owner | Security |
| --- | --- | --- | --- | --- | --- |
| Raise joiner / mover / leaver request | R | A | C | I | I |
| Define role-based entitlements | C | I | R | A | C |
| Provision accounts & access | I | I | R | A | I |
| Adjust on role change | R | C | A | C | I |
| Revoke on termination (same day) | A | R | R | C | C |
| Recertify access periodically | C | I | R | A | C |



<!-- ITS-RACI-003 -->
# ITS-RACI-003 - Change Management - RACI Matrix

Controlled change to production systems (ISO 27001 A.8.32; ISO 13485 Cl.7.5).

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

| Activity | Requestor | Change Mgr | CAB | IT Operations | Security | QA |
| --- | --- | --- | --- | --- | --- | --- |
| Submit change request | R | A | I | C | C | I |
| Assess risk & impact | C | R | C | C | A | C |
| CAB review & approval | I | R | A | C | C | C |
| Implement change | C | A | I | R | C | I |
| Validate & verify | C | A | I | R | C | R |
| Close & document | I | R | I | C | C | A |
