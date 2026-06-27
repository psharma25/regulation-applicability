# M&A Security - Controlled Document Library



<!-- MNA-POL-001 -->
# MNA-POL-001 - M&A Cybersecurity Due Diligence Policy

## 1. Purpose
To ensure cybersecurity, privacy and technology risks of acquisition or investment targets are identified, quantified and reflected in deal decisions and post-close planning.

## 2. Scope
Applies to all mergers, acquisitions, investments and joint ventures evaluated by the Organization.

## 3. Policy Statements
1. A cybersecurity due-diligence assessment **shall** be performed for every material transaction before signing or, where not feasible, before close.
2. Diligence depth **shall** scale with deal value, data sensitivity and the target's role in critical operations.
3. The assessment **shall** cover governance, identity, infrastructure, application/product security, data protection, third parties, prior incidents/breaches and regulatory exposure.
4. Known breaches, active compromises and undisclosed incidents **shall** be treated as material findings and escalated to the deal team.
5. Identified risks **shall** be quantified (remediation cost and risk exposure) and provided as an input to valuation and deal terms.
6. Security representations, warranties and remediation conditions **shall** be recommended to Legal for the agreement.
7. A prioritized post-close remediation and integration security plan **shall** be produced for material risks.
8. Diligence findings **shall** be handled as Restricted and access limited to the deal team under confidentiality obligations.

## 4. Roles & Responsibilities
- **Executive Sponsor / Deal Lead** — accountable for the transaction and risk acceptance.
- **Security Due Diligence Lead** — plans and executes the assessment and reports findings.
- **Legal / Corporate Development** — translate findings into terms and conditions.
- **CISO** — sets diligence requirements and reviews material risk.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.5.7, A.5.19-A.5.23
- NIST SP 800-161 (C-SCRM)
- NIST CSF 2.0 (GOVERN)
- Acquirer M&A due-diligence good practice


<!-- MNA-POL-002 -->
# MNA-POL-002 - Post-Merger Integration Security Policy

## 1. Purpose
To integrate an acquired entity into the enterprise securely, raising it to Organization control baselines without importing unacceptable risk.

## 2. Scope
Applies to all post-close integration of acquired environments, systems, identities and data.

## 3. Policy Statements
1. Acquired environments **shall not** be interconnected with Organization networks until a security baseline assessment is completed and critical gaps are addressed or compensated.
2. An integration security plan **shall** define sequencing, interim controls and target end-state.
3. Acquired identities and privileged access **shall** be inventoried, rationalized and brought under Organization IAM and MFA.
4. Acquired endpoints and servers **shall** be brought to the Organization hardening, logging and EDR baselines.
5. Acquired internet-facing assets **shall** be discovered, assessed and remediated on a priority basis.
6. Interim interconnection **shall** use least-connectivity, monitored segmentation until full integration.
7. Integration milestones **shall** require security sign-off; residual risk **shall** be tracked to closure.
8. Data inherited from the target **shall** be classified and protected per Organization policy.

## 4. Roles & Responsibilities
- **Integration Manager** — owns the integration program.
- **Security Integration Lead** — defines and verifies security baselines and interconnection.
- **Enterprise & Acquired IT** — execute remediation and consolidation.
- **CISO** — approves interconnection and accepts residual risk.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.5.9, A.8.9, A.8.20-A.8.22
- NIST CSF 2.0
- CIS Controls v8 1-4
- NIST SP 800-161


<!-- MNA-POL-003 -->
# MNA-POL-003 - Carve-Out & Divestiture Security Policy

## 1. Purpose
To securely separate a divested or carved-out business so that confidentiality, integrity and availability are preserved and only authorized data and access transfer to the buyer.

## 2. Scope
Applies to divestitures, spin-offs and carve-outs of business units, including associated QMS records for regulated products.

## 3. Policy Statements
1. A separation security plan **shall** define which identities, data, systems and access transfer, remain or are deleted.
2. Access of divested-unit personnel to retained Organization systems **shall** be removed on the agreed date; retained-personnel access to divested systems **shall** likewise be removed.
3. Data **shall** be partitioned by entitlement; only data the buyer is contractually entitled to **shall** be migrated, and commingled data **shall** be resolved before transfer.
4. Personal data transfer **shall** rely on an approved lawful basis and transfer mechanism.
5. For regulated products, the **device master record, design history and quality records shall** be transferred or copied to the buyer and retained as required by regulation.
6. Residual Organization data on transferred assets **shall** be securely removed; buyer data on retained assets **shall** be removed.
7. Secure deletion of separated data **shall** be verified and certified.
8. Transitional services, if any, **shall** be governed by the TSA Security Policy and time-bound.

## 4. Roles & Responsibilities
- **Separation Manager** — owns the carve-out program.
- **Security Separation Lead** — designs and verifies separation of identity, data and infrastructure.
- **Divesting Business Unit** — supports inventory and execution.
- **Legal** — defines entitlement, lawful basis and TSA terms.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.5.10, A.8.10 (deletion), A.8.11
- ISO 13485:2016 Cl. 4.2.5 (record retention/transfer)
- NIST SP 800-88 (sanitization)
- Applicable privacy/transfer law


<!-- MNA-POL-004 -->
# MNA-POL-004 - Transitional Service Agreement (TSA) Security Policy

## 1. Purpose
To manage the security risks of transitional services provided between buyer and seller after close, where shared systems and access persist temporarily.

## 2. Scope
Applies to all Transitional Service Agreements (TSAs) involving access to information, systems or facilities.

## 3. Policy Statements
1. Each TSA **shall** document the services, the data and access involved, the security controls and an exit date.
2. Access under a TSA **shall** be least-privilege, individually attributable, MFA-protected and logged.
3. Cross-party access **shall** terminate automatically at TSA exit; extensions **shall** require re-approval.
4. Security responsibilities and incident-notification obligations between parties **shall** be defined in the TSA.
5. Shared environments **shall** be segmented and monitored for the TSA duration.
6. TSA exit **shall** trigger removal of access, return or deletion of data and confirmation of separation.
7. TSA security status **shall** be reviewed periodically until all services are exited.

## 4. Roles & Responsibilities
- **TSA / Separation Manager** — owns TSA operation and exit.
- **Security** — defines and monitors TSA security controls.
- **Both Parties' IT** — operate within agreed controls.
- **Legal** — defines TSA security and liability terms.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 A.5.19-A.5.22, A.8.15-A.8.16
- NIST SP 800-161
- NIST CSF 2.0 (GOVERN, PROTECT)


<!-- MNA-POL-005 -->
# MNA-POL-005 - M&A Data Protection & Privacy Policy

## 1. Purpose
To ensure personal and regulated data is handled lawfully and securely throughout diligence, integration and separation.

## 2. Scope
Applies to all processing of personal and regulated data in connection with transactions.

## 3. Policy Statements
1. Personal data exchanged during diligence **shall** be minimized, pseudonymized or aggregated where possible, and shared through secure data rooms.
2. A lawful basis and, where required, transfer mechanism **shall** be confirmed before personal data is disclosed or transferred.
3. Data subjects' rights and notification obligations **shall** be assessed for the transaction.
4. A data-protection impact assessment **shall** be performed where the transaction presents high privacy risk.
5. Access to diligence data rooms **shall** be controlled, logged and revoked on completion.
6. On close, records of processing and data inventories **shall** be reconciled and updated.
7. Retention and deletion of transaction data **shall** follow the retention schedule and legal holds.

## 4. Roles & Responsibilities
- **Privacy / DPO** — oversees lawful processing and transfers.
- **Security** — protects diligence data and data rooms.
- **Legal / Corporate Development** — confirm lawful basis and terms.
- **Data Owners** — maintain inventories and entitlements.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27701
- ISO/IEC 27001:2022 A.5.34, A.8.10-A.8.12
- GDPR Art. 6, 25, 28, 44-49 (where applicable)
- NIST Privacy Framework


<!-- MNA-POL-006 -->
# MNA-POL-006 - Acquisition Security Risk Acceptance Policy

## 1. Purpose
To govern how inherited and transaction-related security risks are formally accepted, conditioned or remediated, with appropriate authority.

## 2. Scope
Applies to security risks identified in diligence, integration and separation that are not fully remediated before a decision point.

## 3. Policy Statements
1. Material unremediated risks **shall** be documented with impact, likelihood and remediation cost/time.
2. Risk acceptance **shall** be made by an authority commensurate with the risk level, with the CISO consulted for security-significant risks.
3. Accepted risks **shall** carry a remediation plan, owner and deadline, and **shall** be tracked in the risk register.
4. Deal terms (price adjustment, escrow, warranties, conditions) **shall** be considered as risk-treatment options.
5. Critical risks (e.g., active compromise, regulatory non-compliance) **shall** be escalated to executive sponsors before close.
6. Post-close, accepted risks **shall** be reviewed until remediated or formally re-accepted.
7. Risk-acceptance decisions and rationale **shall** be retained as records.

## 4. Roles & Responsibilities
- **Executive Sponsor / Deal Lead** — accepts risk within authority.
- **CISO** — advises on and co-signs security-significant acceptances.
- **Security DD/Integration Lead** — quantifies and tracks risk.
- **Risk & Compliance** — maintains the register.

## 5. Compliance & Enforcement
Compliance with this document is monitored through internal audit, management review and control metrics. Non-conformities are recorded and remediated through corrective action. Non-compliance may result in removal of access and disciplinary action up to and including termination; for third parties, contractual remedies apply.

## 6. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 7. Review & Maintenance
This document **shall** be reviewed at least annually and upon significant change to the business, technology, threat landscape or applicable regulation, and re-approved by its owner.

## 8. References
- ISO/IEC 27001:2022 Cl. 6.1.3, 8.3; A.5.4
- NIST CSF 2.0 (GOVERN)
- ISO 31000
- Enterprise Risk Management Policy (ENT-POL-002)


<!-- MNA-STD-001 -->
# MNA-STD-001 - Cybersecurity Due Diligence Assessment Standard

## 1. Purpose & Scope
To define the scope, depth and evidence required for cybersecurity due diligence of a target. Applies to all cybersecurity due-diligence assessments of acquisition or investment targets.

## 2. Normative Requirements
1. Diligence **shall** assess governance, IAM, infrastructure/network, endpoint, cloud, application/product security, data protection, third-party/supply chain, prior incidents and regulatory posture.
2. Evidence **shall** be requested (policies, certifications, audit/pentest reports, breach history, SBOMs where relevant) and validated rather than accepted at face value.
3. External attack-surface and breach-exposure checks **shall** be performed where permitted.
4. Findings **shall** be risk-rated and red flags (active compromise, undisclosed breach, critical exposure) **shall** be flagged immediately.
5. Remediation effort and cost **shall** be estimated for material findings.
6. A diligence report **shall** be produced for the deal team with an executive summary and risk register.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Assessment domains | NIST CSF 2.0; ISO/IEC 27001:2022 Annex A |
| Supply-chain & third party | NIST SP 800-161; ISO/IEC 27001 A.5.19-A.5.23 |
| Evidence validation | SOC 2 / ISO 27001 certification review |

## 4. Metrics & Compliance
- Coverage of diligence domains.
- Material findings identified vs. discovered post-close.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- NIST CSF 2.0
- ISO/IEC 27001:2022 Annex A
- NIST SP 800-161


<!-- MNA-STD-002 -->
# MNA-STD-002 - Integration Security Baseline Standard

## 1. Purpose & Scope
To define the minimum security controls an acquired environment must meet before interconnection with Organization networks. Applies to acquired environments pending integration.

## 2. Normative Requirements
1. MFA **shall** be enforced on privileged and remote access before interconnection.
2. EDR and centralized logging **shall** be deployed to acquired endpoints/servers in scope.
3. Internet-facing assets **shall** be inventoried and critical/high vulnerabilities remediated or mitigated.
4. Default and shared credentials **shall** be eliminated; privileged accounts **shall** be vaulted.
5. Interconnection **shall** be through monitored, least-connectivity segmentation, not flat trust.
6. Backups of critical acquired data **shall** be confirmed before changes.
7. A baseline assessment **shall** be signed off before any production interconnection.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Pre-connection baseline | CIS Controls v8 1-6; ISO/IEC 27001:2022 A.8.9 |
| Segmentation | ISO/IEC 27001:2022 A.8.20-A.8.22; NIST SP 800-53 SC-7 |
| MFA & privileged access | NIST SP 800-63B; ISO/IEC 27001 A.8.2, A.8.5 |

## 4. Metrics & Compliance
- Baseline pass rate before interconnection.
- Critical exposures open at interconnection (target zero).

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- CIS Controls v8
- ISO/IEC 27001:2022 A.8.9, A.8.20-A.8.22
- NIST SP 800-63B


<!-- MNA-STD-003 -->
# MNA-STD-003 - Data Separation & Migration Standard

## 1. Purpose & Scope
To define requirements for splitting, migrating and deleting data during integration or separation. Applies to data migration and separation in integrations, carve-outs and divestitures, including regulated records.

## 2. Normative Requirements
1. Data **shall** be inventoried and mapped to entitlement (transfer / retain / delete) before migration.
2. Migration **shall** preserve integrity and confidentiality, using encrypted transfer and verified completeness.
3. Commingled data **shall** be resolved so each party retains only entitled data.
4. Regulated quality/design records **shall** be transferred or copied and retained per ISO 13485 / applicable regulation.
5. Secure deletion **shall** meet recognized sanitization methods and be evidenced by certificates.
6. Personal-data migration **shall** confirm lawful basis and transfer mechanism.
7. Migration and deletion **shall** be reconciled and signed off.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Data mapping & entitlement | ISO/IEC 27001:2022 A.5.12, A.8.11 |
| Secure deletion | NIST SP 800-88; ISO/IEC 27001:2022 A.8.10 |
| Regulated record transfer | ISO 13485:2016 Cl. 4.2.5 |

## 4. Metrics & Compliance
- Records migrated vs. inventory.
- Deletion certificates obtained for separated data.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- NIST SP 800-88
- ISO/IEC 27001:2022 A.8.10-A.8.12
- ISO 13485:2016 Cl. 4.2.5


<!-- MNA-STD-004 -->
# MNA-STD-004 - Target Security Maturity Scoring Standard

## 1. Purpose & Scope
To provide a consistent scoring model for a target's security maturity and deal red flags. Applies to scoring outputs of cybersecurity due diligence.

## 2. Normative Requirements
1. Target maturity **shall** be scored per domain on a defined scale (e.g., 1-5) with descriptors.
2. A weighted overall score **shall** be derived, weighting critical-operation and data-sensitivity domains higher.
3. Defined red flags (active compromise, undisclosed breach, no MFA, unsupported critical systems, regulatory non-compliance) **shall** be recorded regardless of score.
4. Scores **shall** be accompanied by remediation cost/effort estimates.
5. Scoring criteria **shall** be applied consistently across deals to enable comparison.
6. Scores and red flags **shall** be reported to the deal team and inform terms.

## 3. Control Mapping
| Requirement | Mapped Controls / Clauses |
| --- | --- |
| Maturity model | NIST CSF 2.0 tiers; ISO/IEC 27001 Annex A coverage |
| Red-flag criteria | CISA KEV; breach disclosure review |

## 4. Metrics & Compliance
- Score consistency across assessors.
- Red-flag detection rate.

## 5. Exceptions
Exceptions **shall** be documented, risk-assessed, time-bound and approved by the document owner (and the CISO for security-significant exceptions). A register of active exceptions with expiry dates and compensating controls **shall** be maintained and reviewed at least quarterly.

## 6. References
- NIST CSF 2.0
- ISO/IEC 27001:2022 Annex A
- CVSS / CISA KEV (for exposure)


<!-- MNA-PRO-001 -->
# MNA-PRO-001 - Cybersecurity Due Diligence Procedure

## 1. Purpose
To execute cybersecurity due diligence from initiation through findings and valuation input.

## 2. Scope
Applies to security due diligence on targets.

## 3. Roles (RACI)
| Activity | Deal Lead | Security DD Lead | Target | CISO |
| --- | --- | --- | --- | --- |
| Initiate & scope DD | A | R | I | C |
| Request & collect evidence | I | A | R | I |
| Assess & score | I | A | C | C |
| Quantify & report | C | A | I | C |
| Feed terms & planning | A | R | I | C |

## 4. Process Steps
1. **Initiate & scope** — confirm deal context, scope and data-room access. Outputs: DD scope.
2. **Collect evidence** — issue the target questionnaire and request artifacts; validate. Outputs: evidence set.
3. **Assess & score** — evaluate domains, run permitted external checks, score maturity and flag red flags. Outputs: scored findings.
4. **Quantify & report** — estimate remediation cost/effort and produce the DD report. Outputs: DD report.
5. **Feed deal** — provide inputs to valuation, terms and the post-close security plan. Outputs: recommendations.

## 5. Records & Evidence
- DD scope, questionnaire responses, evidence, scored findings, DD report.

## 6. Related Documents & References
- Cybersecurity Due Diligence Assessment Standard (MNA-STD-001)
- M&A Cybersecurity Due Diligence Policy (MNA-POL-001)


<!-- MNA-PRO-002 -->
# MNA-PRO-002 - Post-Merger Integration Procedure

## 1. Purpose
To plan and execute secure integration of an acquired entity after close.

## 2. Scope
Applies to post-merger integration of acquired environments.

## 3. Roles (RACI)
| Activity | Integration Mgr | Security Integration Lead | Acquired IT | CISO |
| --- | --- | --- | --- | --- |
| Build integration plan | A | R | C | C |
| Baseline environment | C | A | R | I |
| Approve interconnection | C | R | I | A |
| Remediate & consolidate | A | C | R | I |
| Sign off integration | C | R | I | A |

## 4. Process Steps
1. **Plan** — define sequencing, interim controls and end-state. Outputs: integration security plan.
2. **Baseline** — assess the acquired environment against the Integration Security Baseline Standard. Outputs: baseline report.
3. **Interconnect** — approve least-connectivity segmentation once critical gaps are addressed. Outputs: interconnection approval.
4. **Remediate & consolidate** — fix gaps and consolidate identity, endpoints, logging and tooling. Outputs: remediation evidence.
5. **Sign off** — confirm end-state and track residual risk. Outputs: integration sign-off.

## 5. Records & Evidence
- Integration plan, baseline report, interconnection approval, remediation and sign-off.

## 6. Related Documents & References
- Integration Security Baseline Standard (MNA-STD-002)
- Post-Merger Integration Security Policy (MNA-POL-002)


<!-- MNA-PRO-003 -->
# MNA-PRO-003 - Carve-Out Separation Procedure

## 1. Purpose
To separate identities, data and infrastructure for a divestiture or carve-out.

## 2. Scope
Applies to carve-out and divestiture separation, including regulated records.

## 3. Roles (RACI)
| Activity | Separation Mgr | Security Separation Lead | Divesting BU | Legal |
| --- | --- | --- | --- | --- |
| Plan separation & TSA | A | C | C | R |
| Separate identity & access | C | A | R | I |
| Split & migrate data | A | R | C | C |
| Verify & certify deletion | C | A | R | C |
| Exit & sign off | A | R | C | C |

## 4. Process Steps
1. **Plan** — define what transfers/retains/deletes and any TSA. Outputs: separation plan.
2. **Separate identity** — remove cross-entity access on the agreed date. Outputs: access changes.
3. **Split & migrate data** — partition by entitlement and migrate entitled data securely. Outputs: migration record.
4. **Verify deletion** — securely delete residual/commingled data and certify. Outputs: deletion certificates.
5. **Exit & sign off** — close transitional services and confirm separation. Outputs: separation sign-off.

## 5. Records & Evidence
- Separation plan, access changes, migration records, deletion certificates, sign-off.

## 6. Related Documents & References
- Data Separation & Migration Standard (MNA-STD-003)
- Carve-Out & Divestiture Security Policy (MNA-POL-003)


<!-- MNA-PRO-004 -->
# MNA-PRO-004 - TSA Security Management Procedure

## 1. Purpose
To operate and exit transitional services securely.

## 2. Scope
Applies to services provided under a TSA after close.

## 3. Roles (RACI)
| Activity | TSA Mgr | Security | Both Parties IT | Legal |
| --- | --- | --- | --- | --- |
| Document TSA security | A | R | C | C |
| Provision controlled access | C | A | R | I |
| Monitor during TSA | C | A | R | I |
| Exit & remove access | A | R | C | C |

## 4. Process Steps
1. **Document** — capture services, data, access, controls and exit date. Outputs: TSA security schedule.
2. **Provision** — grant least-privilege, MFA, logged access; segment shared environments. Outputs: access config.
3. **Monitor** — review access and activity for the TSA duration. Outputs: monitoring records.
4. **Exit** — terminate access, return/delete data and confirm separation at exit. Outputs: exit confirmation.

## 5. Records & Evidence
- TSA security schedule, access configuration, monitoring records, exit confirmation.

## 6. Related Documents & References
- Transitional Service Agreement (TSA) Security Policy (MNA-POL-004)
- Data Separation & Migration Standard (MNA-STD-003)


<!-- MNA-WI-001 -->
# MNA-WI-001 - Target Security Questionnaire WI

## 1. Purpose
To issue and evaluate the target security questionnaire during diligence.

## 2. Prerequisites
- Approved DD scope and NDA in place.
- Secure data room or transfer channel.
- Standard questionnaire template.

## 3. Step-by-Step Instructions
1. Tailor the questionnaire to the target's profile and deal type.
2. Issue it to the target through the secure data room with a due date.
3. Track responses and request supporting evidence (certifications, reports, breach history).
4. Validate responses against evidence; note gaps and inconsistencies.
5. Map responses to the assessment domains and scoring model.
6. Record findings and flag any red flags immediately to the DD lead.

## 4. Verification
- All domains have a response and supporting evidence or a noted gap.
- Red flags escalated.
- Findings recorded for scoring.

## 5. Escalation
If the target discloses (or evidence reveals) an active compromise or undisclosed breach, escalate to the DD lead and executive sponsor before proceeding.

## 6. Related Documents
- Cybersecurity Due Diligence Assessment Standard (MNA-STD-001)
- Cybersecurity Due Diligence Procedure (MNA-PRO-001)


<!-- MNA-WI-002 -->
# MNA-WI-002 - Day-1 Access & Identity Cutover WI

## 1. Purpose
To provision and restrict access at deal close (Day-1 cutover).

## 2. Prerequisites
- Approved Day-1 access plan.
- Identity sources for both entities.
- Change approval for cutover.

## 3. Step-by-Step Instructions
1. Confirm which accounts are provisioned, retained or disabled at close.
2. Provision Day-1 access for required personnel using least privilege and MFA.
3. Disable or restrict access that must not persist past close (both directions).
4. Apply interim segmentation for any interconnection.
5. Verify privileged access is vaulted and logged.
6. Record all cutover actions with timestamps.

## 4. Verification
- Required Day-1 access works; disallowed access is removed.
- MFA enforced; privileged access vaulted.
- Cutover actions logged.

## 5. Escalation
If access cannot be cut over or restricted as planned, hold interconnection and escalate to the integration/separation manager and Security.

## 6. Related Documents
- Post-Merger Integration Procedure (MNA-PRO-002)
- Identity & Access Management Policy (ITS-POL-001)


<!-- MNA-WI-003 -->
# MNA-WI-003 - Data Egress & Separation Verification WI

## 1. Purpose
To verify that data has been migrated, separated and deleted as planned.

## 2. Prerequisites
- Data inventory and entitlement map.
- Migration and deletion completed.
- Access to source and target systems.

## 3. Step-by-Step Instructions
1. Reconcile migrated data against the entitlement map for completeness and accuracy.
2. Confirm no commingled or out-of-scope data was transferred.
3. Run secure deletion on residual/source data per the sanitization method.
4. Obtain or generate deletion certificates for separated data.
5. Spot-check retained systems for absence of buyer/divested data.
6. Record verification results and sign off.

## 4. Verification
- Migrated data matches entitlement; no out-of-scope data transferred.
- Deletion certified for separated data.
- Verification recorded and signed off.

## 5. Escalation
If data is found commingled, mis-migrated, or not deleted, halt sign-off and escalate to the separation manager, Security and Legal.

## 6. Related Documents
- Data Separation & Migration Standard (MNA-STD-003)
- Carve-Out Separation Procedure (MNA-PRO-003)


<!-- MNA-RACI-001 -->
# MNA-RACI-001 - M&A Cybersecurity Due Diligence - RACI Matrix

Roles for assessing a target's security posture across the deal lifecycle.

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

| Activity | Deal Lead | Security DD Lead | Target/Seller | Legal | Executive Sponsor |
| --- | --- | --- | --- | --- | --- |
| Define DD scope & access | A | R | C | C | I |
| Issue security questionnaire | I | A | R | C | I |
| Assess findings & score risk | C | A | C | I | I |
| Quantify remediation cost | C | A | I | C | I |
| Report to deal team | C | A | I | C | C |
| Risk-adjust / accept for close | R | C | I | C | A |



<!-- MNA-RACI-002 -->
# MNA-RACI-002 - Post-Merger Integration - RACI Matrix

Roles for securely integrating an acquired environment after close.

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

| Activity | Integration Mgr | Security Integration Lead | Acquired IT | Enterprise IT | CISO |
| --- | --- | --- | --- | --- | --- |
| Build integration security plan | A | R | C | C | C |
| Baseline acquired environment | C | A | R | C | I |
| Approve network interconnection | C | R | I | C | A |
| Remediate critical gaps | A | C | R | C | I |
| Consolidate identity & tooling | A | R | C | R | I |
| Close integration & sign off | C | R | I | C | A |



<!-- MNA-RACI-003 -->
# MNA-RACI-003 - Carve-Out / Divestiture Separation - RACI Matrix

Roles for securely separating a divested business unit.

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

| Activity | Separation Mgr | Security Separation Lead | Divesting BU | Buyer | Legal |
| --- | --- | --- | --- | --- | --- |
| Define separation scope & TSA | A | C | C | C | R |
| Separate identities & access | C | A | R | I | I |
| Split / migrate data | A | R | C | C | C |
| Verify & certify data deletion | C | A | R | I | C |
| Exit transitional services | A | R | C | C | I |
| Final separation sign-off | C | R | I | C | A |
