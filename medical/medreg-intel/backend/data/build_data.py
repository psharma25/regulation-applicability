"""Builds the MedReg Intel corpus → backend/data/*.json and docs/data.js.

Content is sourced from FDA guidance (524B / June 27 2025 final Cybersecurity guidance,
PCCP final guidance), EU MDR/IVDR + MDCG 2019-16, IMDRF, and named real-world device
cybersecurity incidents and recalls. Treat as a curated reference; verify each item
against the linked source before regulatory use.
"""
import json, os

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

# ----------------------------------------------------------------- regulations
REGULATIONS = [
 # --- US ---
 dict(id="fdc-201h", region="US", jurisdiction="United States", authority="FDA", year="1938+",
      name="FD&C Act §201(h) — Device definition", citation="21 U.S.C. 321(h)",
      cyber=False, ai=False, summary="Statutory definition of a 'device'; the gate that determines whether software (SaMD) or AI is regulated as a device.",
      url="https://www.fda.gov/medical-devices"),
 dict(id="part-807", region="US", jurisdiction="United States", authority="FDA", year="1976+",
      name="21 CFR 807 — Establishment registration & 510(k)", citation="21 CFR 807 Subpart E",
      cyber=False, ai=False, summary="Premarket notification [510(k)] requirements and substantial-equivalence framework.",
      url="https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-807"),
 dict(id="part-814", region="US", jurisdiction="United States", authority="FDA", year="1986+",
      name="21 CFR 814 — Premarket approval (PMA)", citation="21 CFR 814",
      cyber=False, ai=False, summary="PMA pathway for Class III devices; supplements for changes.",
      url="https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-814"),
 dict(id="denovo", region="US", jurisdiction="United States", authority="FDA", year="2018",
      name="21 CFR 860.220 — De Novo classification", citation="21 CFR 860 Subpart D",
      cyber=False, ai=False, summary="Risk-based pathway for novel low/moderate-risk devices with no predicate.",
      url="https://www.fda.gov/medical-devices/premarket-submissions-selecting-and-preparing-correct-submission/de-novo-classification-request"),
 dict(id="sec524b", region="US", jurisdiction="United States", authority="FDA / Congress", year="2023",
      name="FD&C Act §524B — Ensuring Cybersecurity of Devices", citation="21 U.S.C. 360n-2 (FDORA §3305)",
      cyber=True, ai=False,
      summary="Statutory cyber mandate for 'cyber devices'. Requires a postmarket vulnerability plan + CVD, secure design/patching, and an SBOM. Non-compliance is a prohibited act (RTA / enforcement).",
      url="https://www.fda.gov/medical-devices/digital-health-center-excellence/cybersecurity"),
 dict(id="premarket-cyber-2025", region="US", jurisdiction="United States", authority="FDA", year="2025",
      name="Premarket Cybersecurity Guidance (final, June 27 2025)",
      citation="Cybersecurity in Medical Devices: QMS Considerations and Content of Premarket Submissions",
      cyber=True, ai=False,
      summary="Adds Section VII for §524B 'cyber devices'. Mandatory SBOM, SPDF, security architecture (8 control categories), threat modeling, testing, and labeling. Expands 'cyber device' to any device able to connect to the internet — including USB/Bluetooth/Wi-Fi.",
      url="https://www.fda.gov/regulatory-information/search-fda-guidance-documents/cybersecurity-medical-devices-quality-management-system-considerations-and-content-premarket"),
 dict(id="postmarket-cyber", region="US", jurisdiction="United States", authority="FDA", year="2016",
      name="Postmarket Management of Cybersecurity in Medical Devices", citation="FDA guidance (Dec 2016)",
      cyber=True, ai=False,
      summary="Risk-based postmarket vulnerability management, monitoring, and remediation; CVD; reporting under 21 CFR 806.",
      url="https://www.fda.gov/regulatory-information/search-fda-guidance-documents/postmarket-management-cybersecurity-medical-devices"),
 dict(id="qmsr", region="US", jurisdiction="United States", authority="FDA", year="2026",
      name="21 CFR 820 — Quality Management System Regulation (QMSR)", citation="21 CFR 820 (harmonized with ISO 13485, eff. Feb 2 2026)",
      cyber=False, ai=False, summary="QMS requirements; 2026 QMSR harmonizes 21 CFR 820 with ISO 13485:2016.",
      url="https://www.fda.gov/medical-devices/quality-system-qs-regulationmedical-device-current-good-manufacturing-practices-cgmp"),
 dict(id="part-803", region="US", jurisdiction="United States", authority="FDA", year="1984+",
      name="21 CFR 803 — Medical Device Reporting (MDR)", citation="21 CFR 803",
      cyber=True, ai=False, summary="Mandatory adverse-event reporting (MAUDE). Cyber events causing/contributing to harm are reportable.",
      url="https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-803"),
 dict(id="part-806", region="US", jurisdiction="United States", authority="FDA", year="1997+",
      name="21 CFR 806 — Corrections & Removals", citation="21 CFR 806",
      cyber=True, ai=False, summary="Reporting of field corrections/removals — the pathway many cybersecurity patches/recalls follow.",
      url="https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-806"),
 dict(id="udi-830", region="US", jurisdiction="United States", authority="FDA", year="2013+",
      name="21 CFR 801 / 830 — Labeling & UDI", citation="21 CFR 801, 830",
      cyber=False, ai=False, summary="Unique Device Identification and labeling; security labeling expectations flow from premarket guidance.",
      url="https://www.fda.gov/medical-devices/device-advice-comprehensive-regulatory-assistance/unique-device-identification-system-udi-system"),
 dict(id="pccp-2024", region="US", jurisdiction="United States", authority="FDA", year="2024",
      name="Predetermined Change Control Plan (PCCP) for AI-enabled devices", citation="FDA final guidance (Dec 2024)",
      cyber=False, ai=True,
      summary="Lets manufacturers pre-specify and get authorization for future AI/ML model changes (description of modifications, modification protocol, impact assessment) without a new submission.",
      url="https://www.fda.gov/regulatory-information/search-fda-guidance-documents/marketing-submission-recommendations-predetermined-change-control-plan-artificial-intelligence"),
 dict(id="ai-lifecycle-2025", region="US", jurisdiction="United States", authority="FDA", year="2025",
      name="AI-Enabled Device Software Functions — Lifecycle & Marketing Submission (draft)", citation="FDA draft guidance (Jan 2025)",
      cyber=False, ai=True,
      summary="Total product lifecycle recommendations for AI device software functions: transparency, bias, performance monitoring, and documentation.",
      url="https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-and-machine-learning-software-medical-device"),
 dict(id="gmlp", region="US/International", jurisdiction="US/UK/Canada", authority="FDA/MHRA/Health Canada", year="2021",
      name="Good Machine Learning Practice (GMLP) — 10 guiding principles", citation="FDA-MHRA-HC joint",
      cyber=False, ai=True, summary="Ten principles for ML device development: data quality, reference standards, human-AI team, monitoring.",
      url="https://www.fda.gov/medical-devices/software-medical-device-samd/good-machine-learning-practice-medical-device-development-guiding-principles"),
 # --- EU ---
 dict(id="eu-mdr", region="EU", jurisdiction="European Union", authority="EU / Notified Bodies", year="2021",
      name="EU MDR 2017/745 — Medical Device Regulation", citation="Regulation (EU) 2017/745",
      cyber=True, ai=False, summary="EU device framework. Annex I §17 requires IT security, repeatability/reliability, and protection against unauthorized access.",
      url="https://eur-lex.europa.eu/eli/reg/2017/745/oj"),
 dict(id="eu-ivdr", region="EU", jurisdiction="European Union", authority="EU / Notified Bodies", year="2022",
      name="EU IVDR 2017/746 — In Vitro Diagnostic Regulation", citation="Regulation (EU) 2017/746",
      cyber=True, ai=False, summary="IVD framework with equivalent security essential requirements (Annex I).",
      url="https://eur-lex.europa.eu/eli/reg/2017/746/oj"),
 dict(id="mdcg-2019-16", region="EU", jurisdiction="European Union", authority="MDCG", year="2019",
      name="MDCG 2019-16 — Guidance on Cybersecurity for medical devices", citation="MDCG 2019-16 Rev.1",
      cyber=True, ai=False, summary="Operationalizes MDR/IVDR security essential requirements: secure design, IFU, verification, postmarket.",
      url="https://health.ec.europa.eu/document/download/cf30f17b-2dd8-4c70-9d5b-9a6f9f6f3b1f_en"),
 dict(id="eu-cra", region="EU", jurisdiction="European Union", authority="EU", year="2024",
      name="EU Cyber Resilience Act (CRA)", citation="Regulation (EU) 2024/2847",
      cyber=True, ai=False, summary="Horizontal cyber requirements for products with digital elements; medical devices largely deferred to MDR/IVDR but interplay matters.",
      url="https://eur-lex.europa.eu/eli/reg/2024/2847/oj"),
 dict(id="eu-ai-act", region="EU", jurisdiction="European Union", authority="EU", year="2024",
      name="EU AI Act", citation="Regulation (EU) 2024/1689",
      cyber=False, ai=True, summary="Risk-based AI rules. AI medical devices are generally 'high-risk' — adds risk management, data governance, transparency, human oversight on top of MDR.",
      url="https://eur-lex.europa.eu/eli/reg/2024/1689/oj"),
 dict(id="nis2", region="EU", jurisdiction="European Union", authority="EU", year="2023",
      name="NIS2 Directive", citation="Directive (EU) 2022/2555",
      cyber=True, ai=False, summary="Cybersecurity obligations for essential/important entities incl. healthcare operators; incident reporting.",
      url="https://eur-lex.europa.eu/eli/dir/2022/2555/oj"),
 dict(id="gdpr", region="EU", jurisdiction="European Union", authority="EU", year="2018",
      name="GDPR 2016/679", citation="Regulation (EU) 2016/679",
      cyber=True, ai=False, summary="Data protection; relevant to device telemetry, PHI, and breach notification.",
      url="https://eur-lex.europa.eu/eli/reg/2016/679/oj"),
 # --- International / standards ---
 dict(id="imdrf-cyber", region="International", jurisdiction="IMDRF", authority="IMDRF", year="2020+",
      name="IMDRF Principles & Practices for Medical Device Cybersecurity", citation="IMDRF/CYBER WG/N60, N70",
      cyber=True, ai=False, summary="Globally-harmonized cybersecurity principles, TPLC, and legacy device guidance.",
      url="https://www.imdrf.org/documents"),
 dict(id="iso-13485", region="International", jurisdiction="ISO", authority="ISO", year="2016",
      name="ISO 13485:2016 — QMS for medical devices", citation="ISO 13485:2016",
      cyber=False, ai=False, summary="Quality management system standard; basis for QMSR harmonization.",
      url="https://www.iso.org/standard/59752.html"),
 dict(id="iso-14971", region="International", jurisdiction="ISO", authority="ISO", year="2019",
      name="ISO 14971:2019 — Risk management", citation="ISO 14971:2019",
      cyber=True, ai=False, summary="Risk management process; cyber security risk integrates via AAMI TIR57 / SW96.",
      url="https://www.iso.org/standard/72704.html"),
 dict(id="iec-62304", region="International", jurisdiction="IEC", authority="IEC", year="2006/2015",
      name="IEC 62304 — Medical device software lifecycle", citation="IEC 62304:2006/AMD1:2015",
      cyber=True, ai=False, summary="Software development lifecycle processes; safety classification A/B/C.",
      url="https://www.iso.org/standard/38421.html"),
 dict(id="iec-81001-5-1", region="International", jurisdiction="IEC", authority="IEC", year="2021",
      name="IEC 81001-5-1 — Health software security activities", citation="IEC 81001-5-1:2021",
      cyber=True, ai=False, summary="Security activities across the health-software lifecycle; referenced by MDCG and FDA.",
      url="https://www.iso.org/standard/76097.html"),
 dict(id="aami-sw96", region="International", jurisdiction="AAMI/ANSI", authority="AAMI", year="2023",
      name="ANSI/AAMI SW96:2023 — Security risk management", citation="ANSI/AAMI SW96:2023",
      cyber=True, ai=False, summary="Device-specific security risk management standard; referenced by FDA 2025 guidance.",
      url="https://www.aami.org"),
 dict(id="aami-tir57", region="International", jurisdiction="AAMI", authority="AAMI", year="2016",
      name="AAMI TIR57 — Principles for medical device security risk management", citation="AAMI TIR57:2016",
      cyber=True, ai=False, summary="Bridges ISO 14971 safety risk and security risk management.",
      url="https://www.aami.org"),
 dict(id="ul-2900", region="US/International", jurisdiction="UL", authority="UL", year="2017",
      name="UL 2900-2-1 — Software cybersecurity for network-connectable devices (healthcare)", citation="UL 2900-2-1",
      cyber=True, ai=False, summary="Testable security requirements for healthcare network-connected products.",
      url="https://www.ul.com"),
 # --- Other national ---
 dict(id="uk-mhra", region="UK", jurisdiction="United Kingdom", authority="MHRA", year="2002+",
      name="UK MDR 2002 (as amended) + DCB0129/0160", citation="UK MDR 2002; DCB0129/DCB0160",
      cyber=True, ai=False, summary="UKCA marking; NHS clinical risk management standards DCB0129 (manufacturer) / DCB0160 (deployer).",
      url="https://www.gov.uk/government/organisations/medicines-and-healthcare-products-regulatory-agency"),
 dict(id="health-canada", region="Canada", jurisdiction="Canada", authority="Health Canada", year="2019",
      name="Health Canada — Premarket cybersecurity guidance + CMDR", citation="SOR/98-282 (CMDR)",
      cyber=True, ai=False, summary="Canadian Medical Devices Regulations + premarket cybersecurity expectations.",
      url="https://www.canada.ca/en/health-canada.html"),
 dict(id="tga", region="Australia", jurisdiction="Australia", authority="TGA", year="2019/2021",
      name="TGA — Medical device cybersecurity guidance", citation="TGA cybersecurity guidance",
      cyber=True, ai=False, summary="Pre/postmarket cybersecurity expectations for the ARTG.",
      url="https://www.tga.gov.au"),
 dict(id="pmda", region="Japan", jurisdiction="Japan", authority="PMDA/MHLW", year="2021+",
      name="Japan PMDA — Medical device cybersecurity", citation="MHLW notifications",
      cyber=True, ai=False, summary="Cybersecurity requirements aligned to IMDRF for the Japanese market.",
      url="https://www.pmda.go.jp/english/"),
 dict(id="nmpa", region="China", jurisdiction="China", authority="NMPA", year="2022",
      name="China NMPA — Medical device cybersecurity registration guidance", citation="NMPA technical guidance",
      cyber=True, ai=False, summary="Registration-stage cybersecurity documentation requirements for China.",
      url="https://english.nmpa.gov.cn"),
]

# ----------------------------------------------------------------- submission types
SUBMISSIONS = [
 dict(id="510k-traditional", region="US", name="510(k) — Traditional", pathway="Premarket Notification",
      when="Most Class II devices; demonstrate substantial equivalence (SE) to a predicate.",
      form="eSTAR", review="~90 FDA days (MDUFA goal)", cyber="Required for cyber devices (§524B)", ai="PCCP optional",
      reqs=["Indications for use & device description", "Substantial-equivalence comparison + predicate",
            "Performance testing (bench/clinical as needed)", "Software documentation (per Software guidance)",
            "Cybersecurity documentation (SBOM, threat model, security risk mgmt, architecture, testing) for cyber devices",
            "Labeling incl. security labeling"],
      url="https://www.fda.gov/medical-devices/premarket-notification-510k"),
 dict(id="510k-special", region="US", name="510(k) — Special", pathway="Premarket Notification",
      when="Modification to your own legally-marketed device where SE is well-established.",
      form="eSTAR", review="~30 FDA days (goal)", cyber="Cyber docs if change impacts cybersecurity", ai="PCCP optional",
      reqs=["Declaration of conformity to design controls", "Description of the modification",
            "Risk analysis of the change", "Cyber: Vulnerability Mgmt Plan + no-critical-vuln attestation + SBOM (even for legacy)"],
      url="https://www.fda.gov/medical-devices/premarket-notification-510k/types-510k-submissions"),
 dict(id="510k-abbreviated", region="US", name="510(k) — Abbreviated", pathway="Premarket Notification",
      when="Reliance on guidance documents, special controls, or recognized consensus standards.",
      form="eSTAR", review="~90 FDA days", cyber="Required for cyber devices", ai="PCCP optional",
      reqs=["Summary reports relying on standards/special controls", "Declarations of conformity", "Cyber documentation as applicable"],
      url="https://www.fda.gov/medical-devices/premarket-notification-510k/types-510k-submissions"),
 dict(id="pma", region="US", name="PMA — Premarket Approval", pathway="Premarket Approval",
      when="Class III / highest-risk devices; valid scientific evidence of safety & effectiveness.",
      form="eCopy/CDRH Portal", review="~180 FDA days", cyber="Required for cyber devices", ai="PCCP optional",
      reqs=["Clinical & non-clinical evidence", "Manufacturing information (QMS)", "Full risk/benefit",
            "Cybersecurity documentation package", "Postmarket study commitments as applicable"],
      url="https://www.fda.gov/medical-devices/premarket-submissions-selecting-and-preparing-correct-submission/premarket-approval-pma"),
 dict(id="pma-supplement", region="US", name="PMA Supplement", pathway="Premarket Approval",
      when="Changes to an approved PMA device (panel-track, 180-day, real-time, 30-day notice).",
      form="CDRH Portal", review="Varies by type", cyber="Cyber docs if change impacts cybersecurity", ai="PCCP-governed changes",
      reqs=["Description & justification of change", "Verification/validation", "Updated risk & cyber documentation"],
      url="https://www.fda.gov/medical-devices/premarket-approval-pma/pma-supplements-and-amendments"),
 dict(id="denovo-req", region="US", name="De Novo Classification Request", pathway="De Novo",
      when="Novel low/moderate-risk device with no predicate.",
      form="eSTAR", review="~150 FDA days", cyber="Required for cyber devices", ai="PCCP optional",
      reqs=["Device description & classification rationale", "Proposed special controls", "Benefit-risk",
            "Cybersecurity documentation", "Labeling"],
      url="https://www.fda.gov/medical-devices/premarket-submissions-selecting-and-preparing-correct-submission/de-novo-classification-request"),
 dict(id="hde", region="US", name="HDE — Humanitarian Device Exemption", pathway="HDE",
      when="Humanitarian Use Devices (HUD) for conditions affecting ≤8,000 patients/yr in the US.",
      form="CDRH Portal", review="~75 FDA days", cyber="Required for cyber devices", ai="PCCP optional",
      reqs=["HUD designation", "Probable benefit", "Cybersecurity documentation as applicable"],
      url="https://www.fda.gov/medical-devices/premarket-submissions-selecting-and-preparing-correct-submission/humanitarian-device-exemption"),
 dict(id="presub", region="US", name="Pre-Submission (Q-Sub)", pathway="Q-Submission",
      when="Get FDA feedback before a submission — strongly advised for novel cyber/AI devices.",
      form="Q-Sub", review="~70–75 days to meeting", cyber="Recommended to align cyber strategy early", ai="Recommended to align PCCP",
      reqs=["Specific questions for FDA", "Device & development context", "Proposed testing/PCCP/cyber approach"],
      url="https://www.fda.gov/regulatory-information/search-fda-guidance-documents/requests-feedback-and-meetings-medical-device-submissions-q-submission-program"),
 dict(id="513g", region="US", name="513(g) — Request for classification", pathway="513(g)",
      when="Ask FDA for the classification/regulatory status of a device.",
      form="513(g)", review="~60 days", cyber="N/A", ai="N/A",
      reqs=["Device description", "Proposed classification/questions"],
      url="https://www.fda.gov/medical-devices/premarket-submissions-selecting-and-preparing-correct-submission"),
 dict(id="ide", region="US", name="IDE — Investigational Device Exemption", pathway="IDE",
      when="Clinical investigation of a significant-risk device.",
      form="CDRH Portal", review="~30 days", cyber="Cyber considerations for connected investigational devices", ai="As applicable",
      reqs=["Investigational plan & protocol", "Report of prior investigations", "IRB approval", "Risk analysis"],
      url="https://www.fda.gov/medical-devices/premarket-submissions-selecting-and-preparing-correct-submission/investigational-device-exemption-ide"),
 dict(id="eu-ce", region="EU", name="CE marking (MDR) — Technical Documentation", pathway="Conformity assessment",
      when="Placing a device on the EU market; Notified Body involvement by class.",
      form="Annex II/III Tech Doc", review="Varies by Notified Body", cyber="MDR Annex I §17 + MDCG 2019-16", ai="EU AI Act (high-risk)",
      reqs=["Annex II technical documentation", "GSPR checklist incl. §17 security", "Clinical evaluation (Annex XIV)",
            "Cybersecurity per MDCG 2019-16", "Post-market surveillance & PSUR"],
      url="https://health.ec.europa.eu/medical-devices-sector_en"),
]

# ----------------------------------------------------------------- requirements
REQUIREMENTS = [
 # cyber
 dict(id="r-srm", cat="Cybersecurity", name="Security Risk Management Plan & file",
      cite="524B(b)(2); 2025 guidance §V; AAMI SW96; ISO 14971",
      applies=["510k-traditional","pma","denovo-req","hde","eu-ce"],
      desc="Document the security risk process, threats, controls, and residual risk, integrated with the safety risk file.",
      artifacts=["Security risk management plan","Security risk assessment matrix","Traceability to controls"]),
 dict(id="r-threat", cat="Cybersecurity", name="Threat model",
      cite="2025 guidance §V.A.2", applies=["510k-traditional","pma","denovo-req","eu-ce"],
      desc="System-level threat model (e.g., STRIDE) covering device, comms, cloud, and update paths; informs controls and testing.",
      artifacts=["Threat model document","Data-flow diagrams","Trust boundaries"]),
 dict(id="r-sbom", cat="Cybersecurity", name="Software Bill of Materials (SBOM)",
      cite="524B(b)(3); 2025 guidance §V.A.4(b)/§VII.C.3; NTIA minimum elements",
      applies=["510k-traditional","510k-special","pma","denovo-req","hde","eu-ce"],
      desc="Machine- and human-readable SBOM of commercial, open-source, and off-the-shelf components, with support/EOL info and known vulnerabilities.",
      artifacts=["CycloneDX or SPDX SBOM","Known-vulnerability list","Support/EOL dates"]),
 dict(id="r-arch", cat="Cybersecurity", name="Security architecture views",
      cite="2025 guidance §V.A.3", applies=["510k-traditional","pma","denovo-req","eu-ce"],
      desc="Global system, multi-patient harm, updateability/patchability, and security-use-case views of the device and connected systems.",
      artifacts=["Global system view","Updateability view","Security use case views"]),
 dict(id="r-controls", cat="Cybersecurity", name="Security controls (8 categories)",
      cite="2025 guidance Appendix 1", applies=["510k-traditional","pma","denovo-req","eu-ce"],
      desc="Authentication, authorization, cryptography, code/data integrity, confidentiality, event detection/logging, resiliency/recovery, and firmware/SW updates.",
      artifacts=["Controls matrix","Design evidence per category"]),
 dict(id="r-testing", cat="Cybersecurity", name="Cybersecurity testing",
      cite="2025 guidance §V.B", applies=["510k-traditional","pma","denovo-req","eu-ce"],
      desc="Vulnerability scanning, SAST/DAST, software composition analysis, fuzzing, and penetration testing with reports & coverage rationale.",
      artifacts=["Pen-test report","Vuln scan results","SBOM/SCA results","Fuzz/abuse-case results"]),
 dict(id="r-cvd", cat="Cybersecurity", name="Vulnerability monitoring & CVD plan",
      cite="524B(b)(1); Postmarket guidance", applies=["510k-traditional","510k-special","pma","denovo-req","hde","eu-ce"],
      desc="Postmarket plan to monitor, identify, and address vulnerabilities, including a coordinated vulnerability disclosure process and timelines.",
      artifacts=["Postmarket vuln mgmt plan","CVD policy","Patch/update SLAs"]),
 dict(id="r-labeling", cat="Cybersecurity", name="Security labeling & documentation for users",
      cite="2025 guidance §V.C", applies=["510k-traditional","pma","denovo-req","eu-ce"],
      desc="Security-relevant labeling: supported configurations, controls, update mechanisms, and known limitations (e.g., MDS2).",
      artifacts=["Security labeling","MDS2 form","Hardening/Configuration guide"]),
 # AI
 dict(id="r-pccp", cat="AI", name="Predetermined Change Control Plan (PCCP)",
      cite="FDA PCCP final guidance (2024)", applies=["510k-traditional","pma","denovo-req"],
      desc="Pre-specify allowed AI/ML modifications: description of modifications, modification protocol (data/retraining/validation), and impact assessment.",
      artifacts=["Description of modifications","Modification protocol","Impact assessment"]),
 dict(id="r-gmlp", cat="AI", name="Good Machine Learning Practice (GMLP) evidence",
      cite="FDA-MHRA-HC GMLP (2021)", applies=["510k-traditional","pma","denovo-req"],
      desc="Demonstrate the 10 GMLP principles: representative data, reference standards, model design, human-AI team, and monitoring.",
      artifacts=["Data management plan","Reference-standard rationale","Human-factors evidence"]),
 dict(id="r-ai-transparency", cat="AI", name="AI transparency & labeling",
      cite="FDA AI lifecycle draft (2025); EU AI Act", applies=["510k-traditional","pma","denovo-req","eu-ce"],
      desc="Model card-style transparency: intended use, inputs/outputs, performance, limitations, and user-facing explanations.",
      artifacts=["Model description / card","Performance summary","Limitations & subgroup performance"]),
 dict(id="r-ai-perf", cat="AI", name="AI performance validation & bias/generalizability",
      cite="FDA AI lifecycle draft (2025)", applies=["510k-traditional","pma","denovo-req"],
      desc="Validation on representative, independent data with subgroup analysis to characterize bias and generalizability.",
      artifacts=["Validation protocol & results","Subgroup performance","Data provenance"]),
 dict(id="r-ai-monitoring", cat="AI", name="Postmarket AI performance monitoring",
      cite="FDA AI lifecycle draft (2025)", applies=["510k-traditional","pma","denovo-req"],
      desc="Monitor real-world performance, drift, and triggers for retraining/notification within the PCCP envelope.",
      artifacts=["Monitoring plan","Drift thresholds","Retraining triggers"]),
 # QMS / SW / clinical / labeling
 dict(id="r-sw-doc", cat="Software", name="Software documentation (Documentation Level)",
      cite="FDA Content of Premarket Submissions for Device Software Functions (2023)",
      applies=["510k-traditional","510k-special","pma","denovo-req","eu-ce"],
      desc="Basic vs Enhanced documentation level: architecture, requirements, V&V, unresolved anomalies.",
      artifacts=["Software description","Architecture","V&V","Anomaly list"]),
 dict(id="r-qms", cat="QMS", name="Quality management system",
      cite="21 CFR 820 / QMSR; ISO 13485", applies=["pma","eu-ce"],
      desc="Design controls, CAPA, supplier controls, and (2026) QMSR-harmonized ISO 13485 processes.",
      artifacts=["Design history file","CAPA records","Supplier agreements"]),
 dict(id="r-clinical", cat="Clinical", name="Clinical / performance evidence",
      cite="21 CFR 814; MDR Annex XIV", applies=["pma","denovo-req","eu-ce"],
      desc="Clinical evaluation or investigation appropriate to risk and novelty.",
      artifacts=["Clinical evaluation report","Study protocol & results"]),
 dict(id="r-interop", cat="Cybersecurity", name="Interoperability",
      cite="FDA Interoperability guidance (2017)", applies=["510k-traditional","pma","denovo-req","eu-ce"],
      desc="Define electronic interfaces, data exchange, and the security of interoperable connections.",
      artifacts=["Interface specs","Risk of misconnection analysis"]),
]

# ----------------------------------------------------------------- FDA cyber incidents (real, named)
INCIDENTS = [
 dict(id="baxter-life2000-2025", device="Welch Allyn Life2000 Ventilator", maker="Baxter / Hillrom", year="2025",
      kind="Class I recall (cybersecurity)", impact="4,100+ units permanently removed",
      summary="Cybersecurity vulnerability found via internal testing; Baxter permanently pulled all Life2000 ventilators. FDA designated a Class I recall (May 9, 2025).",
      source="https://www.healthcare-brew.com/stories/2025/06/02/recall-roundup-fda-medical-device-recalls-may-2025"),
 dict(id="contec-cms8000-2025", device="Contec CMS8000 patient monitor", maker="Contec", year="2025",
      kind="FDA + CISA safety communication", impact="Backdoor / hardcoded behavior",
      summary="FDA and CISA warned of a backdoor in Contec CMS8000 patient monitors transmitting data to a hardcoded IP and enabling remote code execution.",
      source="https://www.fda.gov/medical-devices/safety-communications"),
 dict(id="illumina-ucs-2023", device="Illumina sequencing instruments (UCS)", maker="Illumina", year="2023",
      kind="FDA + CISA advisory (CVE-2023-1968/1966)", impact="Remote takeover of NGS instruments",
      summary="Universal Copy Service vulnerability in Illumina sequencers could allow remote access/control; FDA and CISA issued advisories and Illumina shipped a patch.",
      source="https://www.fda.gov/medical-devices/safety-communications"),
 dict(id="bd-alaris-2021", device="BD Alaris Infusion System", maker="Becton Dickinson", year="2021",
      kind="510(k) incl. cybersecurity updates", impact="Most-used acute-care infusion pump",
      summary="BD filed a 510(k) to bring Alaris up to date and address open recall issues, including cybersecurity updates to the system software.",
      source="https://www.sec.gov/Archives/edgar/data/0000010795/000001079521000039/bd_newsxalarisx5submission.htm"),
 dict(id="medtronic-minimed-2019", device="MiniMed 508 / Paradigm insulin pumps", maker="Medtronic", year="2019",
      kind="FDA safety communication / recall", impact="Wireless protocol could alter insulin delivery",
      summary="FDA warned that wireless vulnerabilities could let a nearby attacker alter insulin delivery; affected models were recalled and patients advised to switch.",
      source="https://www.fda.gov/medical-devices/safety-communications"),
 dict(id="medtronic-conexus-2019", device="Conexus telemetry (ICDs/CRT-Ds)", maker="Medtronic", year="2019",
      kind="FDA safety communication (CVE-2019-6538)", impact="Unauthenticated RF telemetry",
      summary="The Conexus radio-frequency telemetry protocol lacked authentication/encryption, allowing potential read/modify of device settings; mitigations and updates issued.",
      source="https://www.fda.gov/medical-devices/safety-communications"),
 dict(id="abbott-stjude-2017", device="St. Jude/Abbott pacemakers + Merlin@home", maker="Abbott (St. Jude)", year="2017",
      kind="FDA safety communication / firmware update", impact="~465,000 pacemakers",
      summary="Vulnerabilities in implantable cardiac devices and the Merlin@home transmitter led to an FDA-cleared firmware update for ~465,000 pacemakers.",
      source="https://www.fda.gov/medical-devices/safety-communications"),
 dict(id="ge-imaging-2020", device="GE Healthcare imaging/monitoring devices", maker="GE Healthcare", year="2020",
      kind="FDA + CISA advisory (MDhex)", impact="Default credentials / exposed services",
      summary="'MDhex' vulnerabilities in GE patient-monitoring and imaging products (default credentials, exposed services) prompted FDA/CISA advisories and patches.",
      source="https://www.cisa.gov/news-events/ics-medical-advisories"),
 dict(id="philips-2021", device="Philips patient-monitoring / informatics", maker="Philips", year="2021",
      kind="FDA + CISA advisory", impact="Multiple CVEs",
      summary="Multiple Philips products (e.g., patient information center, interoperability) had disclosed vulnerabilities with coordinated advisories and remediation.",
      source="https://www.cisa.gov/news-events/ics-medical-advisories"),
 dict(id="swisslog-pneumatic-2021", device="Swisslog Translogic PTS (Nexus)", maker="Swisslog Healthcare", year="2021",
      kind="FDA + CISA advisory (PwnedPiper)", impact="Hospital pneumatic tube systems",
      summary="'PwnedPiper' vulnerabilities in the Nexus Control Panel of widely-deployed hospital pneumatic tube systems could allow full takeover; patches issued.",
      source="https://www.cisa.gov/news-events/ics-medical-advisories"),
]

# ----------------------------------------------------------------- RTA / fines examples
RTA_FINES = [
 dict(id="rta-cyber-524b", trigger="RTA — missing §524B cybersecurity content", since="Oct 1, 2023",
      what="Cyber-device premarket submission lacking the required vulnerability plan, secure-design processes, or SBOM is refused at acceptance review.",
      lesson="Include the full cyber package (plan, processes, SBOM) at submission — not after.",
      source="https://www.fda.gov/medical-devices/digital-health-center-excellence/cybersecurity-medical-devices-frequently-asked-questions-faqs"),
 dict(id="rta-legacy-change", trigger="RTA — legacy device change without cyber docs", since="2023+",
      what="A change to a pre-2023 device claiming equivalence still needs a Vulnerability Mgmt Plan, no-critical-vuln attestation, and SBOM.",
      lesson="Even Special 510(k)s for old devices now need a minimum cyber baseline.",
      source="https://blog.cm-dm.com/post/2025/07/04/2025-update-of-FDA-Premarket-Cybersecurity-guidance"),
 dict(id="rta-510k-admin", trigger="RTA — 510(k) administrative completeness", since="ongoing",
      what="Missing eSTAR fields, truth-and-accuracy statement, financial certification, or indications mismatch triggers Refuse-to-Accept.",
      lesson="Run the FDA RTA checklist before submitting; eSTAR enforces many fields.",
      source="https://www.fda.gov/medical-devices/premarket-notification-510k"),
 dict(id="fca-cyber", trigger="False Claims Act exposure for cyber deficiencies", since="2025",
      what="Selling devices to federal programs while non-compliant with §524B cyber obligations is being scrutinized under the FCA.",
      lesson="Cyber non-compliance is now a legal/financial risk beyond the submission itself.",
      source="https://www.morganlewis.com/blogs/asprescribed/2025/11/from-vulnerability-to-violation-fda-cybersecurity-requirements-for-medical-devices-and-fca-enforcement"),
 dict(id="prohibited-act", trigger="§524B non-compliance is a 'prohibited act'", since="2023",
      what="FDORA makes failing to meet cyber requirements a prohibited act under the FD&C Act — enabling injunctions/penalties.",
      lesson="Treat cyber requirements as enforceable law, not guidance.",
      source="https://www.complizen.ai/post/fda-cybersecurity-compliance-standards-2025-complete-guide"),
 dict(id="recall-cyber-806", trigger="Field correction/recall for unpatched vulnerability", since="ongoing",
      what="Unaddressed exploitable vulnerabilities can force a 21 CFR 806 correction/removal or recall (e.g., Baxter Life2000 Class I).",
      lesson="A weak postmarket plan turns a vulnerability into a recall.",
      source="https://www.healthcare-brew.com/stories/2025/06/02/recall-roundup-fda-medical-device-recalls-may-2025"),
 dict(id="ai-pccp-scope", trigger="AI change outside an authorized PCCP", since="2024+",
      what="Modifying an AI model beyond what an authorized PCCP covers requires a new marketing submission.",
      lesson="Scope the PCCP modification protocol carefully — or re-submit.",
      source="https://www.fda.gov/regulatory-information/search-fda-guidance-documents/marketing-submission-recommendations-predetermined-change-control-plan-artificial-intelligence"),
]

# ----------------------------------------------------------------- AI requirements (focused)
AI_REQS = [
 dict(id="ai-pccp", name="Predetermined Change Control Plan", detail="Description of modifications + modification protocol + impact assessment, authorized at clearance.", cite="FDA PCCP final guidance (2024)"),
 dict(id="ai-gmlp", name="GMLP — 10 guiding principles", detail="Multidisciplinary expertise, good software engineering & security, representative datasets, independent train/test, reference standards, model design tailored to data/use, human-AI team focus, testing in clinically relevant conditions, clear user info, deployed-model monitoring.", cite="FDA/MHRA/Health Canada (2021)"),
 dict(id="ai-transparency", name="Transparency", detail="Intended use, logic, inputs/outputs, performance, and limitations communicated to users (model card-style).", cite="FDA AI transparency principles (2024)"),
 dict(id="ai-bias", name="Bias & generalizability", detail="Representative data and subgroup performance to characterize and mitigate bias.", cite="FDA AI lifecycle draft (2025)"),
 dict(id="ai-data", name="Data management", detail="Provenance, quality, independence of training vs test data, and reference-standard rationale.", cite="GMLP / AI lifecycle"),
 dict(id="ai-monitoring", name="Real-world performance monitoring", detail="Drift detection, performance dashboards, and retraining/notification triggers within the PCCP.", cite="FDA AI lifecycle draft (2025)"),
 dict(id="ai-euact", name="EU AI Act (high-risk) overlay", detail="Risk management, data governance, technical documentation, logging, human oversight, accuracy/robustness/cybersecurity on top of MDR/IVDR.", cite="Regulation (EU) 2024/1689"),
 dict(id="ai-cyber", name="AI-specific cybersecurity", detail="Address adversarial ML, data poisoning, and model/inference integrity within the security risk file.", cite="FDA 2025 cyber guidance + AAMI SW96"),
]

# ----------------------------------------------------------------- downloadable templates (markdown)
TEMPLATES = {
"cybersecurity-management-plan": ("Cybersecurity Management Plan", "Cybersecurity", """# Cybersecurity Management Plan
**Device:** <name / model>  · **Manufacturer:** <legal name>  · **Submission:** <510(k)/PMA/De Novo>
**Regulatory basis:** FD&C Act §524B; FDA Premarket Cybersecurity Guidance (June 27, 2025); AAMI SW96; ISO 14971; IEC 81001-5-1

## 1. Scope & device context
- Intended use / intended environment:
- Connectivity (Wi-Fi / Bluetooth / USB / cellular / cloud) — confirms 'cyber device' status:
- Related systems (update servers, mobile apps, cloud):

## 2. Roles & governance
- Product security owner / PSIRT contact:
- Secure Product Development Framework (SPDF) reference:

## 3. Security risk management (ref. SW96 / ISO 14971)
- Risk process & acceptance criteria:
- Link to Security Risk Assessment file:

## 4. Threat model
- Methodology (e.g., STRIDE) & link to model:

## 5. Security architecture views
- [ ] Global system view  [ ] Multi-patient harm view  [ ] Updateability/patchability view  [ ] Security use case views

## 6. SBOM
- Format (CycloneDX/SPDX), location, support/EOL, known vulnerabilities:

## 7. Verification & validation (testing)
- [ ] Vulnerability scan  [ ] SAST  [ ] DAST  [ ] SCA  [ ] Fuzzing  [ ] Penetration test

## 8. Postmarket plan
- Monitoring, CVD policy, patch/update SLAs, 806/803 reporting triggers:

## 9. Labeling
- Security labeling, MDS2, hardening guide:
"""),
"security-risk-assessment": ("Security Risk Assessment", "Cybersecurity", """# Security Risk Assessment (SW96 / ISO 14971-aligned)
**Device:** <name>  · **Version:** <x.y>  · **Date:** <yyyy-mm-dd>

| ID | Asset | Threat (STRIDE) | Vulnerability | Exploitability | Patient-harm impact | Control(s) | Residual risk |
|----|-------|-----------------|---------------|----------------|---------------------|------------|---------------|
| S-01 | | Spoofing | | High/Med/Low | | Authentication | |
| S-02 | | Tampering | | | | Integrity / signing | |
| S-03 | | Repudiation | | | | Logging | |
| S-04 | | Information disclosure | | | | Encryption | |
| S-05 | | Denial of service | | | | Resiliency / recovery | |
| S-06 | | Elevation of privilege | | | | Authorization | |

**Risk acceptance criteria:** <define>  ·  **Overall residual risk acceptable?** <yes/no + rationale>
"""),
"threat-model": ("Threat Model", "Cybersecurity", """# Threat Model
**Device:** <name>  ·  **Method:** STRIDE  ·  **Date:** <yyyy-mm-dd>

## 1. System decomposition
- Components, data stores, external entities:
- Data-flow diagram (link):
- Trust boundaries:

## 2. Threats by element (STRIDE)
- Spoofing / Tampering / Repudiation / Information disclosure / DoS / Elevation of privilege

## 3. Attack surfaces
- Physical ports (USB/serial), wireless (BLE/Wi-Fi/cellular), network services, update channel, cloud/API, mobile app

## 4. Mitigations & residual risk
- Map each threat → control → test → residual risk (link to Security Risk Assessment)
"""),
"sbom-cyclonedx": ("SBOM (CycloneDX skeleton)", "Cybersecurity", """{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "metadata": {
    "component": { "type": "application", "name": "<device-software>", "version": "<x.y.z>" },
    "supplier": { "name": "<manufacturer>" }
  },
  "components": [
    {
      "type": "library",
      "name": "<component>",
      "version": "<version>",
      "supplier": { "name": "<supplier>" },
      "licenses": [{ "license": { "id": "<SPDX-id>" } }],
      "properties": [
        { "name": "support:level", "value": "<supported/EOL>" },
        { "name": "support:endOfSupport", "value": "<yyyy-mm-dd>" }
      ]
    }
  ],
  "vulnerabilities": []
}
"""),
"vulnerability-disclosure-policy": ("Coordinated Vulnerability Disclosure Policy", "Cybersecurity", """# Coordinated Vulnerability Disclosure (CVD) Policy
**Manufacturer:** <name>  ·  **Contact:** security@<domain>  ·  **PGP / report portal:** <link>

## Scope
- Products & versions covered:

## How to report
- Channel, expected acknowledgment time (e.g., 3 business days):

## Our commitments
- Triage SLA, status updates, no legal action for good-faith research (safe harbor):

## Coordination & timelines
- Target remediation windows by severity (e.g., Critical ≤ X days), CISA/ICS-CERT coordination, advisory publication:

## Reporting to regulators
- Triggers for 21 CFR 806 correction/removal and 803 MDR reporting:
"""),
"postmarket-cyber-plan": ("Postmarket Cybersecurity Plan", "Cybersecurity", """# Postmarket Cybersecurity Management Plan
**Device:** <name>  ·  **Regulatory basis:** §524B(b)(1); FDA Postmarket Cybersecurity guidance

## 1. Monitoring
- Sources: SBOM-to-CVE matching, CISA KEV, vendor feeds, researcher reports

## 2. Assessment
- Exploitability + patient-harm scoring; controlled vs uncontrolled risk

## 3. Remediation
- Patch/update mechanism, validation, deployment, customer notification ≤ 30 days for vulnerabilities

## 4. Disclosure & reporting
- CVD process, advisory publication, 806/803 triggers

## 5. Metrics
- Mean time to remediate, % devices updated, open critical vulns
"""),
"premarket-cyber-checklist": ("Premarket Cybersecurity Documentation Checklist", "Cybersecurity", """# Premarket Cybersecurity Documentation Checklist (§524B / 2025 guidance)
- [ ] Cyber-device determination & rationale (connectivity)
- [ ] Security risk management plan + assessment file (SW96/14971)
- [ ] Threat model (STRIDE) + data-flow diagrams
- [ ] Security architecture views (global / multi-patient harm / updateability / use-case)
- [ ] Security controls matrix (8 categories: authn, authz, crypto, integrity, confidentiality, detection/logging, resiliency/recovery, updates)
- [ ] SBOM (machine + human readable) with support/EOL + known vulns
- [ ] Cybersecurity testing: vuln scan, SAST, DAST, SCA, fuzzing, penetration test (+ coverage rationale)
- [ ] Postmarket vulnerability management + CVD plan with timelines
- [ ] Security labeling / MDS2 / hardening guide
- [ ] Interoperability interface + misconnection risk analysis
"""),
"pccp-ai": ("Predetermined Change Control Plan (AI)", "AI", """# Predetermined Change Control Plan (PCCP)
**AI/ML device:** <name>  ·  **Basis:** FDA PCCP final guidance (2024)

## 1. Description of modifications
- What may change (e.g., re-training on new data, threshold tuning, added input sources) and bounds:

## 2. Modification protocol
- Data management (provenance, quality, independence):
- Re-training / re-tuning methodology:
- Performance evaluation (metrics, acceptance criteria, subgroup analysis):
- Update & versioning procedures:

## 3. Impact assessment
- Benefits, risks, and how risks are controlled & verified for each modification type:

## 4. Transparency
- How users are informed of changes (labeling/version notes):
"""),
"gmlp-checklist": ("GMLP Checklist (10 principles)", "AI", """# Good Machine Learning Practice (GMLP) Checklist
- [ ] 1. Multidisciplinary expertise across the lifecycle
- [ ] 2. Good software engineering & security practices
- [ ] 3. Clinical study participants & datasets representative of intended population
- [ ] 4. Training datasets independent of test sets
- [ ] 5. Reference datasets based on best available methods
- [ ] 6. Model design tailored to data & intended use
- [ ] 7. Focus on the human-AI team performance
- [ ] 8. Testing under clinically relevant conditions
- [ ] 9. Clear, essential information for users
- [ ] 10. Deployed models monitored for performance & re-training risks managed
"""),
"510k-cyber-section": ("510(k) Cybersecurity Section Outline", "Cybersecurity", """# 510(k) — Cybersecurity Section (eSTAR)
1. Device cyber description & connectivity (cyber-device status)
2. Security risk management summary (link to file)
3. Threat model summary
4. Architecture views
5. Security controls implemented (8 categories)
6. SBOM (attach machine-readable + summary)
7. Cybersecurity testing summary + reports
8. Postmarket plan & CVD
9. Security labeling
10. Conclusions / reasonable assurance of cybersecurity
"""),
"presub-request": ("Pre-Submission (Q-Sub) Request", "Submission", """# Pre-Submission (Q-Sub) Request
**Device:** <name>  ·  **Sponsor:** <name>  ·  **Type:** Pre-Submission

## 1. Purpose & specific questions for FDA
1.
2.

## 2. Device description & intended use

## 3. Regulatory history / proposed pathway

## 4. Proposed testing / cybersecurity strategy / PCCP (if AI)

## 5. Meeting request & preferred format/date
"""),
}

# ----------------------------------------------------------------- additional standards (ISO/IEC/AAMI/NIST)
REGULATIONS += [
 dict(id="iso-81001-1", region="International", jurisdiction="ISO/IEC", authority="ISO/IEC", year="2021",
      name="IEC 81001-1 — Health software & health IT: safety, effectiveness & security", citation="IEC 81001-1:2021",
      cyber=True, ai=False, summary="Foundational principles & concepts tying together safety, effectiveness, and security across the health-software lifecycle.",
      url="https://www.iso.org/standard/71538.html"),
 dict(id="iso-80001", region="International", jurisdiction="IEC", authority="IEC", year="2021",
      name="IEC 80001-1 — Risk management of IT networks with medical devices", citation="IEC 80001-1:2021",
      cyber=True, ai=False, summary="Risk management for connecting medical devices to IT networks (the deployer side of connectivity).",
      url="https://www.iso.org/standard/72026.html"),
 dict(id="iec-62366", region="International", jurisdiction="IEC", authority="IEC", year="2015",
      name="IEC 62366-1 — Usability engineering", citation="IEC 62366-1:2015/AMD1:2020",
      cyber=False, ai=False, summary="Usability engineering process; relevant to safe use of security controls and AI outputs.",
      url="https://www.iso.org/standard/63179.html"),
 dict(id="iso-14155", region="International", jurisdiction="ISO", authority="ISO", year="2020",
      name="ISO 14155 — Clinical investigation of medical devices (GCP)", citation="ISO 14155:2020",
      cyber=False, ai=False, summary="Good clinical practice for device clinical investigations.",
      url="https://www.iso.org/standard/71690.html"),
 dict(id="iec-60601", region="International", jurisdiction="IEC", authority="IEC", year="2020",
      name="IEC 60601-1 — Basic safety & essential performance", citation="IEC 60601-1 (3.2)",
      cyber=False, ai=False, summary="Electrical medical equipment basic safety; essential-performance concept underpins cyber harm analysis.",
      url="https://www.iso.org/standard/65529.html"),
 dict(id="aami-tir97", region="International", jurisdiction="AAMI", authority="AAMI", year="2019",
      name="AAMI TIR97 — Postmarket security management", citation="AAMI TIR97:2019",
      cyber=True, ai=False, summary="Principles for postmarket cybersecurity management of devices in the field.",
      url="https://www.aami.org"),
 dict(id="iso-27001", region="International", jurisdiction="ISO/IEC", authority="ISO/IEC", year="2022",
      name="ISO/IEC 27001 — Information security management (ISMS)", citation="ISO/IEC 27001:2022",
      cyber=True, ai=False, summary="Organizational ISMS; common manufacturer control baseline behind product security.",
      url="https://www.iso.org/standard/27001"),
 dict(id="iso-27799", region="International", jurisdiction="ISO", authority="ISO", year="2016",
      name="ISO 27799 — Health informatics security management", citation="ISO 27799:2016",
      cyber=True, ai=False, summary="Applies ISO 27002 controls to protected health information.",
      url="https://www.iso.org/standard/62777.html"),
 dict(id="nist-csf", region="US/International", jurisdiction="NIST", authority="NIST", year="2024",
      name="NIST Cybersecurity Framework 2.0", citation="NIST CSF 2.0",
      cyber=True, ai=False, summary="Govern/Identify/Protect/Detect/Respond/Recover functions; widely mapped in device security programs.",
      url="https://www.nist.gov/cyberframework"),
 dict(id="nist-80053", region="US", jurisdiction="NIST", authority="NIST", year="2020",
      name="NIST SP 800-53 Rev.5 — Security & privacy controls", citation="NIST SP 800-53 Rev.5",
      cyber=True, ai=False, summary="Control catalog frequently referenced for device/cloud control selection.",
      url="https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final"),
 dict(id="nist-80030", region="US", jurisdiction="NIST", authority="NIST", year="2012",
      name="NIST SP 800-30 — Guide for conducting risk assessments", citation="NIST SP 800-30 Rev.1",
      cyber=True, ai=False, summary="Risk assessment methodology supporting security risk management.",
      url="https://csrc.nist.gov/pubs/sp/800/30/r1/final"),
 dict(id="nist-ai-rmf", region="US/International", jurisdiction="NIST", authority="NIST", year="2023",
      name="NIST AI Risk Management Framework 1.0", citation="NIST AI RMF 1.0",
      cyber=False, ai=True, summary="Govern/Map/Measure/Manage for trustworthy AI; complements GMLP and the EU AI Act.",
      url="https://www.nist.gov/itl/ai-risk-management-framework"),
]

# reg type + version/last_updated (for the regulation register tracker)
_REG_TYPE = {"fdc-201h":"Law","sec524b":"Law","part-807":"Regulation","part-814":"Regulation","denovo":"Regulation",
 "qmsr":"Regulation","part-803":"Regulation","part-806":"Regulation","udi-830":"Regulation",
 "premarket-cyber-2025":"Guidance","postmarket-cyber":"Guidance","pccp-2024":"Guidance","ai-lifecycle-2025":"Guidance","gmlp":"Guidance",
 "eu-mdr":"Regulation","eu-ivdr":"Regulation","mdcg-2019-16":"Guidance","eu-cra":"Regulation","eu-ai-act":"Regulation","nis2":"Directive","gdpr":"Regulation",
 "imdrf-cyber":"Guidance","uk-mhra":"Regulation","health-canada":"Regulation","tga":"Guidance","pmda":"Guidance","nmpa":"Guidance"}
_REG_UPDATED = {"premarket-cyber-2025":"2025-06-27","sec524b":"2023-03-29","postmarket-cyber":"2016-12-28","qmsr":"2026-02-02",
 "pccp-2024":"2024-12-04","ai-lifecycle-2025":"2025-01-07","gmlp":"2021-10-27","eu-mdr":"2021-05-26","eu-ivdr":"2022-05-26",
 "mdcg-2019-16":"2020-07","eu-cra":"2024-11-23","eu-ai-act":"2024-08-01","nis2":"2023-01-16","gdpr":"2018-05-25",
 "imdrf-cyber":"2023-03","nist-csf":"2024-02-26","eu-ai-act-":""}
for _r in REGULATIONS:
    _r.setdefault("type", _REG_TYPE.get(_r["id"], "Standard" if _r["authority"] in ("ISO","IEC","ISO/IEC","AAMI","UL","NIST") else "Regulation"))
    _r.setdefault("last_updated", _REG_UPDATED.get(_r["id"], str(_r.get("year", ""))))
    _r.setdefault("version", _r.get("citation", ""))

# ---- link requirements -> regulations + technology profiles + how-to guidance ----
_TECH_ALL = ["Software","Hardware","Firmware","Connected","Cloud","AWS","Azure","GCP","SaMD","SiMD","AI"]
_REQ_LINK = {
 "r-srm": dict(regs=["sec524b","premarket-cyber-2025","aami-sw96","iso-14971","aami-tir57","nist-80030"],
   tech=["Software","Firmware","Connected","Cloud","SaMD","SiMD","AI"],
   guidance="Stand up a security risk process tied into ISO 14971. Inventory assets, enumerate threats, rate exploitability x patient-harm, select controls, and record residual risk acceptance."),
 "r-threat": dict(regs=["premarket-cyber-2025","iec-81001-5-1","nist-csf"],
   tech=["Software","Connected","Cloud","AWS","Azure","GCP","SaMD","SiMD","AI"],
   guidance="Build a STRIDE threat model spanning the device, its wireless/USB interfaces, cloud/back-end, and the update path. Derive controls and test cases from each threat."),
 "r-sbom": dict(regs=["sec524b","premarket-cyber-2025"],
   tech=["Software","Firmware","Cloud","SaMD","SiMD","AI"],
   guidance="Generate a CycloneDX/SPDX SBOM from your build pipeline, enrich with supplier/support/EOL and known CVEs, and keep it continuously updated through postmarket."),
 "r-arch": dict(regs=["premarket-cyber-2025"],
   tech=["Software","Connected","Cloud","AWS","Azure","GCP"],
   guidance="Produce the four architecture views (global system, multi-patient harm, updateability, security use cases) showing trust boundaries, data flows, and the patch path."),
 "r-controls": dict(regs=["premarket-cyber-2025","nist-80053","iso-27001"],
   tech=["Software","Hardware","Firmware","Connected","Cloud","AWS","Azure","GCP"],
   guidance="Implement and evidence all eight control categories. For cloud (AWS/Azure/GCP), map shared-responsibility controls: IAM, KMS/HSM, network isolation, logging."),
 "r-testing": dict(regs=["premarket-cyber-2025","ul-2900"],
   tech=["Software","Firmware","Connected","Cloud","SaMD","SiMD","AI"],
   guidance="Run SAST, DAST, software-composition analysis, fuzzing, and an independent penetration test. Provide reports plus a coverage rationale traced to the threat model."),
 "r-cvd": dict(regs=["sec524b","postmarket-cyber","aami-tir97"],
   tech=["Software","Firmware","Connected","Cloud","SaMD","SiMD","AI"],
   guidance="Publish a security@ intake and CVD policy, triage on SLAs, and run a postmarket loop matching SBOM components to CISA KEV and vendor feeds; patch within defined timelines."),
 "r-labeling": dict(regs=["premarket-cyber-2025","udi-830"],
   tech=["Software","Hardware","Connected"],
   guidance="Provide security labeling (MDS2), a hardening/secure-configuration guide, supported configurations, and known limitations for users and integrators."),
 "r-pccp": dict(regs=["pccp-2024","nist-ai-rmf"],
   tech=["SaMD","SiMD","AI","Cloud"],
   guidance="Pre-specify the bounded set of model changes, the protocol to make them (data, retraining, validation), and an impact assessment authorized at clearance."),
 "r-gmlp": dict(regs=["gmlp","nist-ai-rmf"],
   tech=["SaMD","AI","Cloud"],
   guidance="Evidence the 10 GMLP principles across data management, model design, human-AI team performance, and deployed-model monitoring."),
 "r-ai-transparency": dict(regs=["ai-lifecycle-2025","eu-ai-act"],
   tech=["SaMD","AI"],
   guidance="Publish a model card: intended use, inputs/outputs, performance with confidence, subgroup limitations, and user-facing explanations."),
 "r-ai-perf": dict(regs=["ai-lifecycle-2025","nist-ai-rmf"],
   tech=["SaMD","AI"],
   guidance="Validate on independent, representative data; report subgroup performance to characterize bias and generalizability; document data provenance."),
 "r-ai-monitoring": dict(regs=["ai-lifecycle-2025"],
   tech=["SaMD","AI","Cloud"],
   guidance="Monitor real-world performance and drift; define thresholds and retraining/notification triggers that stay inside the authorized PCCP."),
 "r-sw-doc": dict(regs=["part-807","iec-62304"],
   tech=["Software","Firmware","SaMD","SiMD"],
   guidance="Select Basic vs Enhanced documentation level by risk; supply software description, architecture, requirements, V&V, and unresolved-anomaly list."),
 "r-qms": dict(regs=["qmsr","iso-13485"],
   tech=["Software","Hardware"],
   guidance="Operate design controls, CAPA, and supplier controls under ISO 13485 / the 2026 QMSR; keep a design history file."),
 "r-clinical": dict(regs=["part-814","eu-mdr","iso-14155"],
   tech=["SaMD","Hardware","AI"],
   guidance="Provide clinical or performance evidence proportional to risk and novelty; for AI, characterize performance in the intended population."),
 "r-interop": dict(regs=["premarket-cyber-2025","iso-80001"],
   tech=["Connected","Cloud","Software"],
   guidance="Specify electronic interfaces and data exchange; analyze misconnection/interoperability risk and secure the connections."),
}
for _q in REQUIREMENTS:
    _l = _REQ_LINK.get(_q["id"], {})
    _q["regs"] = _l.get("regs", [])
    _q["tech"] = _l.get("tech", [])
    _q["guidance"] = _l.get("guidance", "")
    _q["evidence"] = _q.get("artifacts", [])

# ---- additional cross-agency incidents + timeline/why on all incidents ----
INCIDENTS += [
 dict(id="urgent11-2019", device="URGENT/11 (IPnet/VxWorks TCP-IP stack)", maker="Multiple manufacturers", year="2019",
      kind="FDA safety communication + ICS-CERT", impact="Many connected devices (imaging, infusion, monitors)",
      summary="Eleven vulnerabilities in the IPnet TCP/IP stack (used by VxWorks and others) could allow remote code execution; FDA and CISA/ICS-CERT urged manufacturers to assess and patch.",
      source="https://www.fda.gov/medical-devices/safety-communications"),
 dict(id="swyentooth-2020", device="SweynTooth (BLE SoC vulnerabilities)", maker="Multiple manufacturers", year="2020",
      kind="FDA safety communication", impact="Bluetooth Low Energy medical devices",
      summary="A family of BLE chipset vulnerabilities could let a nearby attacker crash, deadlock, or bypass security on connected devices; FDA notified manufacturers to evaluate impact.",
      source="https://www.fda.gov/medical-devices/safety-communications"),
 dict(id="access7-2022", device="Access:7 (PTC Axeda agent)", maker="PTC / device makers", year="2022",
      kind="FDA + CISA advisory", impact="Remote-management agent in medical & IoT devices",
      summary="Seven vulnerabilities in the PTC Axeda remote-management agent embedded in medical and IoT devices could allow full remote takeover; coordinated FDA/CISA disclosure and patches.",
      source="https://www.cisa.gov/news-events/ics-medical-advisories"),
]
_INC_META = {
 "baxter-life2000-2025": dict(agency="FDA", date="2025-05-09", why="A cybersecurity vulnerability found in internal testing could compromise the ventilator; Baxter removed the product and FDA classified the highest-severity (Class I) recall."),
 "contec-cms8000-2025": dict(agency="FDA + CISA", date="2025-01-30", why="Reported because the monitor contained a backdoor sending patient data to a hardcoded IP and allowing remote code execution — a patient-safety and privacy risk."),
 "illumina-ucs-2023": dict(agency="FDA + CISA", date="2023-04-27", why="Reported so labs would patch a remotely exploitable flaw in genomic sequencers that could alter results or expose data."),
 "bd-alaris-2021": dict(agency="FDA", date="2021-04-26", why="Filed to bring the most-used infusion pump's clearance current and close open recall and cybersecurity gaps."),
 "medtronic-minimed-2019": dict(agency="FDA", date="2019-06-27", why="Reported because an unauthenticated wireless protocol could let a nearby attacker change insulin delivery; pumps were recalled."),
 "medtronic-conexus-2019": dict(agency="FDA", date="2019-03-21", why="Reported because the RF telemetry lacked authentication/encryption, allowing potential read/modify of implant settings."),
 "abbott-stjude-2017": dict(agency="FDA", date="2017-08-29", why="Reported after research showed implantable cardiac devices and the home transmitter could be exploited; a firmware update was mandated."),
 "ge-imaging-2020": dict(agency="FDA + CISA", date="2020-01-23", why="Reported because default credentials and exposed services ('MDhex') could let attackers reach monitoring/imaging systems."),
 "philips-2021": dict(agency="FDA + CISA", date="2021-05-20", why="Coordinated disclosure of multiple CVEs across patient-information and interoperability products."),
 "swisslog-pneumatic-2021": dict(agency="FDA + CISA", date="2021-08-02", why="Reported because 'PwnedPiper' flaws in hospital pneumatic-tube control panels could allow full takeover of a critical logistics system."),
 "urgent11-2019": dict(agency="FDA + CISA", date="2019-10-01", why="Reported to push manufacturers/operators to assess a widely-embedded networking stack with remote-code-execution risk."),
 "swyentooth-2020": dict(agency="FDA", date="2020-03-03", why="Reported so manufacturers using affected BLE chips would evaluate crash/security-bypass impact on patients."),
 "access7-2022": dict(agency="FDA + CISA", date="2022-03-08", why="Reported because a remote-management agent embedded across many devices could be fully taken over."),
}
for _i in INCIDENTS:
    _m = _INC_META.get(_i["id"], {})
    _i["agency"] = _m.get("agency", "FDA")
    _i["date"] = _m.get("date", str(_i.get("year","")))
    _i["why"] = _m.get("why", "")
INCIDENTS.sort(key=lambda x: x.get("date",""), reverse=True)

# ---- timeline + why on RTA/fines ----
_RTA_META = {
 "rta-cyber-524b": dict(date="2023-10-01", why="FDA began refusing cyber-device submissions that lack §524B content, to force security in at design time rather than after market."),
 "rta-legacy-change": dict(date="2025-06-27", why="The 2025 final guidance clarified that even legacy-device changes must carry a minimum cyber baseline, closing a gap exploited by 'minor change' claims."),
 "rta-510k-admin": dict(date="2019-09-25", why="Administrative completeness has long been an RTA gate; eSTAR now enforces it up front."),
 "fca-cyber": dict(date="2025-11-05", why="Selling to federal programs while non-compliant with cyber obligations creates False Claims Act exposure — a financial, not just regulatory, risk."),
 "prohibited-act": dict(date="2023-03-29", why="FDORA made cyber non-compliance a prohibited act, giving FDA injunction/penalty authority."),
 "recall-cyber-806": dict(date="2025-05-09", why="When postmarket monitoring fails, an exploitable vulnerability can escalate into a 21 CFR 806 correction/removal or recall (e.g., Baxter Life2000)."),
 "ai-pccp-scope": dict(date="2024-12-04", why="Changing an AI model beyond an authorized PCCP requires a new submission — scoping the modification protocol is what avoids re-filing."),
}
for _t in RTA_FINES:
    _m = _RTA_META.get(_t["id"], {})
    _t["date"] = _m.get("date", _t.get("since",""))
    _t["why"] = _m.get("why", "")
RTA_FINES.sort(key=lambda x: x.get("date",""), reverse=True)

# ---- template guidance ("what to do") + evidence ("what to show") ----
_TPL_META = {
 "cybersecurity-management-plan": dict(guidance="The umbrella plan FDA reviewers open first. Fill the device context and connectivity (this confirms 'cyber device' status), then link out to each sub-artifact. Keep it traceable.",
   evidence=["Completed plan","Links to SRM file, threat model, SBOM, test reports","Named PSIRT/security owner"]),
 "security-risk-assessment": dict(guidance="Enumerate assets and threats with STRIDE, score exploitability and patient-harm separately, then map controls and residual risk. Tie acceptance criteria to your safety risk file.",
   evidence=["Risk matrix with residual risk","Acceptance criteria & rationale","Traceability to controls and tests"]),
 "threat-model": dict(guidance="Decompose the system, draw data-flow diagrams and trust boundaries, then walk STRIDE per element. Every threat needs a control and a test.",
   evidence=["Data-flow diagrams","STRIDE threat table","Threat-to-control-to-test traceability"]),
 "sbom-cyclonedx": dict(guidance="Emit this from your build (don't hand-write it). Add supplier, license, support level, and end-of-support per component, and attach a known-vulnerability list.",
   evidence=["Machine-readable SBOM (CycloneDX/SPDX)","Support/EOL per component","Known-vulnerability list"]),
 "vulnerability-disclosure-policy": dict(guidance="Make it easy to report to you and clear what you'll do. State a safe-harbor, acknowledgment and remediation SLAs, and how you coordinate with CISA and notify regulators.",
   evidence=["Published CVD policy & security contact","Triage/remediation SLAs","Regulator-reporting triggers (806/803)"]),
 "postmarket-cyber-plan": dict(guidance="Show the loop: monitor sources (SBOM->CVE, CISA KEV), assess exploitability x harm, remediate and notify within timelines. Define your metrics.",
   evidence=["Monitoring sources & cadence","Severity-based patch SLAs","Customer-notification process (<=30 days)"]),
 "premarket-cyber-checklist": dict(guidance="Use this as the pre-submission gate. Every unchecked box is a likely Refuse-to-Accept. Attach the artifact next to each item.",
   evidence=["Each checklist item satisfied with a linked artifact"]),
 "pccp-ai": dict(guidance="Define the bounded changes you may make, the protocol to make them safely, and the impact assessment — all authorized at clearance so you don't re-file for each retrain.",
   evidence=["Description of modifications","Modification protocol (data/retrain/validate)","Impact assessment"]),
 "gmlp-checklist": dict(guidance="Walk the 10 principles and attach evidence for each — especially representative data, independent test sets, and deployed-model monitoring.",
   evidence=["Data management & representativeness","Independent train/test split","Monitoring plan"]),
 "510k-cyber-section": dict(guidance="The cybersecurity section of an eSTAR 510(k). Summarize each artifact and conclude with the reasonable-assurance statement reviewers look for.",
   evidence=["Summaries of SRM, threat model, architecture, SBOM, testing","Reasonable-assurance conclusion"]),
 "presub-request": dict(guidance="Ask FDA specific, answerable questions before you submit. For novel cyber/AI devices, align your testing and PCCP strategy here to de-risk the submission.",
   evidence=["Specific questions","Proposed cyber/PCCP strategy","Meeting request"]),
}

# ================================================================ v3 refinements
# --- more international regulations + standards ---
REGULATIONS += [
 dict(id="fda-mma", region="US", jurisdiction="United States", authority="FDA", year="2022",
      name="FDA Policy for Device Software Functions & Mobile Medical Applications", citation="FDA guidance (Sep 2022)",
      cyber=False, ai=False, summary="Clarifies which mobile/software functions FDA regulates as devices and its enforcement-discretion approach for mobile medical apps on iOS/Android.",
      url="https://www.fda.gov/medical-devices/digital-health-center-excellence/device-software-functions-including-mobile-medical-applications"),
 dict(id="swissmedic", region="International", jurisdiction="Switzerland", authority="Swissmedic", year="2021",
      name="Swissmedic — MedDO (Medical Devices Ordinance)", citation="MedDO (SR 812.213)",
      cyber=True, ai=False, summary="Swiss device framework aligned to EU MDR; cybersecurity expected via MDCG-equivalent practice.",
      url="https://www.swissmedic.ch"),
 dict(id="anvisa", region="International", jurisdiction="Brazil", authority="ANVISA", year="2022",
      name="ANVISA RDC 751/2022 — Brazil device regulation", citation="RDC 751/2022",
      cyber=True, ai=False, summary="Brazilian medical device classification & registration; growing cybersecurity expectations.",
      url="https://www.gov.br/anvisa"),
 dict(id="mfds", region="International", jurisdiction="South Korea", authority="MFDS", year="2022",
      name="MFDS — Korea medical device cybersecurity guidance", citation="MFDS guidance",
      cyber=True, ai=False, summary="Korean premarket cybersecurity review expectations, aligned to IMDRF.",
      url="https://www.mfds.go.kr/eng"),
 dict(id="hsa-sg", region="International", jurisdiction="Singapore", authority="HSA", year="2021",
      name="HSA Singapore — Cybersecurity of medical devices", citation="HSA regulatory guidance",
      cyber=True, ai=False, summary="Pre/postmarket cybersecurity requirements for the Singapore market.",
      url="https://www.hsa.gov.sg"),
 dict(id="iso-42001", region="International", jurisdiction="ISO/IEC", authority="ISO/IEC", year="2023",
      name="ISO/IEC 42001 — AI management system", citation="ISO/IEC 42001:2023",
      cyber=False, ai=True, summary="Management-system standard for responsible AI; complements GMLP and the EU AI Act.",
      url="https://www.iso.org/standard/81230.html"),
 dict(id="iso-23894", region="International", jurisdiction="ISO/IEC", authority="ISO/IEC", year="2023",
      name="ISO/IEC 23894 — AI risk management", citation="ISO/IEC 23894:2023",
      cyber=False, ai=True, summary="Guidance on managing AI-specific risks across the lifecycle.",
      url="https://www.iso.org/standard/77304.html"),
 dict(id="iso-24971", region="International", jurisdiction="ISO", authority="ISO", year="2020",
      name="ISO/TR 24971 — Guidance on ISO 14971", citation="ISO/TR 24971:2020",
      cyber=True, ai=False, summary="Practical guidance for applying risk management, including security considerations.",
      url="https://www.iso.org/standard/74437.html"),
 dict(id="iso-27002", region="International", jurisdiction="ISO/IEC", authority="ISO/IEC", year="2022",
      name="ISO/IEC 27002 — Information security controls", citation="ISO/IEC 27002:2022",
      cyber=True, ai=False, summary="Control catalog supporting ISMS and product security baselines.",
      url="https://www.iso.org/standard/75652.html"),
 dict(id="etsi-303645", region="International", jurisdiction="ETSI", authority="ETSI", year="2020",
      name="ETSI EN 303 645 — Consumer IoT security baseline", citation="ETSI EN 303 645",
      cyber=True, ai=False, summary="Baseline security provisions relevant to connected home/consumer health devices.",
      url="https://www.etsi.org"),
 dict(id="iec-60601-4-5", region="International", jurisdiction="IEC", authority="IEC", year="2021",
      name="IEC TR 60601-4-5 — Security capabilities for medical electrical equipment", citation="IEC TR 60601-4-5:2021",
      cyber=True, ai=False, summary="Technical report mapping IEC 62443 security capability levels to medical electrical equipment.",
      url="https://www.iso.org/standard/74438.html"),
]

# --- technology profiles on regulations + submissions (for the lens) ---
def _auto_tech(r):
    t = set()
    if r.get("ai"): t |= {"AI", "SaMD"}
    if r.get("cyber"): t |= {"Software", "Connected"}
    nm = (r["name"] + r.get("summary", "")).lower()
    if any(k in nm for k in ("device", "mdr", "510", "pma", "qms", "13485", "60601", "electrical", "hardware", "udi")): t |= {"Hardware", "Software"}
    if any(k in nm for k in ("software", "saMd".lower(), "samd", "62304", "81001", "ai", "cloud", "health software")): t |= {"Software"}
    if any(k in nm for k in ("cloud", "network", "80001", "iot", "27001", "27002")): t |= {"Cloud", "Connected"}
    if any(k in nm for k in ("firmware", "iot", "embedded", "62443", "303 645")): t |= {"Firmware"}
    return sorted(t) or ["Software"]
_REG_TECH = {
 "fda-mma": ["Mobile-iOS", "Mobile-Android", "Software", "SaMD", "Connected"],
 "eu-ai-act": ["AI", "SaMD", "SiMD"], "gmlp": ["AI", "SaMD"], "pccp-2024": ["AI", "SaMD", "SiMD"],
 "ai-lifecycle-2025": ["AI", "SaMD"], "iso-42001": ["AI"], "iso-23894": ["AI"], "nist-ai-rmf": ["AI", "SaMD"],
 "iec-60601": ["Hardware", "Software"], "iec-60601-4-5": ["Hardware", "Firmware", "Connected"],
 "iso-80001": ["Connected", "Cloud", "Hardware"], "etsi-303645": ["Firmware", "Connected", "Hardware"],
 "iso-27001": ["Software", "Cloud", "Connected"], "iso-27002": ["Software", "Cloud", "Connected"],
}
for _r in REGULATIONS:
    _r["tech"] = _REG_TECH.get(_r["id"], _auto_tech(_r))

_SUB_TECH = {
 "510k-traditional": ["Hardware", "Software", "Firmware", "Connected", "SaMD", "SiMD", "AI"],
 "510k-special": ["Software", "Firmware", "Connected", "SaMD", "AI"],
 "510k-abbreviated": ["Hardware", "Software", "Connected"],
 "pma": ["Hardware", "Software", "Connected", "SaMD", "AI"],
 "pma-supplement": ["Software", "Connected", "AI"],
 "denovo-req": ["Hardware", "Software", "SaMD", "SiMD", "AI"],
 "hde": ["Hardware", "Software", "Connected"],
 "presub": ["Software", "SaMD", "SiMD", "AI", "Connected", "Cloud"],
 "513g": ["Software", "Hardware", "SaMD"],
 "ide": ["Hardware", "Software", "Connected", "AI"],
 "eu-ce": ["Hardware", "Software", "Firmware", "Connected", "Cloud", "SaMD", "SiMD", "AI"],
}
for _s in SUBMISSIONS:
    _s["tech"] = _SUB_TECH.get(_s["id"], ["Software"])

# mobile medical apps run on iOS/Android — tag every SaMD item with the mobile profiles
for _coll in (REGULATIONS, SUBMISSIONS, REQUIREMENTS):
    for _r in _coll:
        _t = _r.get("tech", [])
        if "SaMD" in _t and "Mobile-iOS" not in _t:
            _r["tech"] = _t + ["Mobile-iOS", "Mobile-Android"]

# --- jurisdiction grouping for the lens (US vs International) ---
for _coll in (REGULATIONS, SUBMISSIONS):
    for _r in _coll:
        reg = _r.get("region", "")
        _r["us"] = "US" in reg
        _r["intl"] = reg != "US"

# --- "what to submit if a control cannot be implemented" ---
_REQ_IFNOT = {
 "r-srm": "Document the gap as a security risk: record why the control is infeasible, the compensating controls, the residual risk, and formal risk acceptance signed by the security/quality owner.",
 "r-threat": "If a threat cannot be fully mitigated, capture it as accepted residual risk with compensating controls and a monitoring/detection plan; reflect it in labeling.",
 "r-sbom": "If a complete SBOM cannot be provided, FDA expects a written justification for each missing element and an addendum plan to supply it; you must still attest to no known critical vulnerabilities.",
 "r-arch": "If a view cannot be produced (e.g., third-party black-box component), state the limitation, provide the supplier's security documentation, and analyze the residual exposure.",
 "r-controls": "Submit a risk-based justification per FDA guidance: why the control is infeasible, the compensating controls (segmentation, physical access, logging), residual risk and acceptance, plus user labeling describing the limitation.",
 "r-testing": "If a test type is not applicable, justify the exclusion against the threat model; if testing reveals unresolved findings, provide a remediation plan with timelines and interim mitigations.",
 "r-cvd": "If full patch capability is infeasible (e.g., legacy hardware), provide compensating controls, end-of-support communication, and a managed-risk plan; document this in labeling.",
 "r-labeling": "If a security feature is absent, the labeling must clearly disclose the limitation and the compensating operational controls the user must apply.",
 "r-pccp": "If a change falls outside the PCCP, do not deploy it under the PCCP — submit a new marketing submission; document the decision rationale.",
 "r-gmlp": "If a principle cannot be met (e.g., limited representative data), justify it, quantify the impact on generalizability, and add postmarket monitoring to detect underperformance.",
 "r-ai-transparency": "If full transparency is constrained by IP, provide the safety-relevant performance and limitation information needed for safe use, with rationale for any withheld detail.",
 "r-ai-perf": "If subgroup data is limited, disclose the limitation, avoid claims beyond the validated population, and commit to postmarket performance monitoring.",
 "r-ai-monitoring": "If real-world monitoring is constrained, define proxy metrics and a periodic re-validation schedule, and state the limitation in labeling.",
 "r-sw-doc": "If an artifact is unavailable for a legacy/OTS component, provide the available documentation plus a risk assessment of the gap.",
 "r-qms": "Nonconformities are handled through CAPA; document the deviation, containment, root cause, and corrective action.",
 "r-clinical": "If clinical data is limited, justify with a benefit-risk rationale, real-world evidence, or a postmarket study commitment.",
 "r-interop": "If an interface cannot be fully secured, analyze and disclose the misconnection risk and provide operational mitigations in labeling.",
}
for _q in REQUIREMENTS:
    _q["if_not_implementable"] = _REQ_IFNOT.get(_q["id"], "Document the gap as residual risk with compensating controls, a justification, and formal risk acceptance.")

# --- international + recent CVE incidents; disclosure + mitigation on all ---
INCIDENTS += [
 dict(id="wannacry-nhs-2017", device="Imaging & connected devices (NHS estate)", maker="Multiple", year="2017",
      kind="Ransomware (WannaCry)", impact="UK NHS — ~80 trusts, thousands of appointments cancelled",
      summary="WannaCry ransomware (EternalBlue, CVE-2017-0144) spread to unpatched Windows-based medical devices and hospital systems, taking imaging and other equipment offline.",
      source="https://www.enisa.europa.eu"),
 dict(id="hse-ireland-2021", device="Hospital IT & connected devices (HSE)", maker="Multiple", year="2021",
      kind="Ransomware (Conti)", impact="Ireland HSE — national health service crippled for weeks",
      summary="A Conti ransomware attack on Ireland's Health Service Executive disrupted diagnostic systems and connected devices nationwide; recovery cost was substantial.",
      source="https://www.enisa.europa.eu"),
 dict(id="duesseldorf-2020", device="Hospital systems (Uniklinik Düsseldorf)", maker="Multiple", year="2020",
      kind="Ransomware", impact="Germany — emergency care diverted",
      summary="A ransomware attack exploiting a Citrix vulnerability (CVE-2019-19781) forced a German university hospital to divert emergency patients during an outage.",
      source="https://www.bsi.bund.de"),
 dict(id="singhealth-2018", device="EHR / health records (SingHealth)", maker="SingHealth", year="2018",
      kind="APT data breach", impact="Singapore — 1.5M patient records",
      summary="A targeted intrusion exfiltrated 1.5M patient records including the Prime Minister's; a Committee of Inquiry drove sweeping cybersecurity reforms.",
      source="https://www.csa.gov.sg"),
 dict(id="bbraun-infusomat-2021", device="B. Braun Infusomat Space infusion pump", maker="B. Braun", year="2021",
      kind="Vulnerability disclosure (CVE-2021-33885 et al.)", impact="Unauthenticated firmware/dose manipulation",
      summary="McAfee researchers disclosed flaws allowing unauthenticated modification of pump configuration/doses; B. Braun issued fixes and mitigations via coordinated disclosure.",
      source="https://www.cisa.gov/news-events/ics-medical-advisories"),
 dict(id="microdicom-2024", device="MicroDicom DICOM Viewer", maker="MicroDicom", year="2024",
      kind="CISA ICS medical advisory (CVE-2024-33606/25578/25569)", impact="RCE / file handling in imaging software",
      summary="CISA issued an advisory for vulnerabilities in a widely-used DICOM viewer that could allow code execution when opening crafted images; updates released.",
      source="https://www.cisa.gov/news-events/ics-medical-advisories"),
]
_INC_META2 = {
 "baxter-life2000-2025": dict(region="US", cve="—", disclosure="Found in internal testing; FDA Class I recall + manufacturer field action.", mitigation="Product permanently removed from service; customers transitioned to alternatives."),
 "contec-cms8000-2025": dict(region="US/International", cve="CVE-2024-12248, CVE-2025-0626, CVE-2025-0683", disclosure="Coordinated FDA + CISA advisory after researcher analysis.", mitigation="Disable network connectivity / isolate; firmware remediation; monitor for hardcoded-IP traffic."),
 "illumina-ucs-2023": dict(region="US/International", cve="CVE-2023-1968, CVE-2023-1966", disclosure="Manufacturer + FDA + CISA coordinated advisory.", mitigation="Vendor software patch (UCS removal/hardening); network isolation of instruments."),
 "bd-alaris-2021": dict(region="US", cve="—", disclosure="510(k) bringing clearance current; addressed open recall items.", mitigation="Updated system software with cybersecurity improvements."),
 "medtronic-minimed-2019": dict(region="US/International", cve="—", disclosure="FDA safety communication + recall.", mitigation="Patients switched to models with mitigations; affected pumps recalled."),
 "medtronic-conexus-2019": dict(region="US/International", cve="CVE-2019-6538, CVE-2019-6540", disclosure="FDA safety communication + ICS-CERT advisory.", mitigation="Programmer/monitor updates; physical-access and monitoring controls; staged firmware."),
 "abbott-stjude-2017": dict(region="US", cve="—", disclosure="FDA safety communication after researcher/short-seller disclosure.", mitigation="FDA-cleared firmware update for ~465,000 pacemakers via clinic."),
 "ge-imaging-2020": dict(region="US/International", cve="CVE-2020-6961…6970 (MDhex)", disclosure="Coordinated FDA + CISA advisory.", mitigation="Vendor patches; network segmentation; change default credentials."),
 "philips-2021": dict(region="US/International", cve="multiple", disclosure="Coordinated vendor + CISA advisories.", mitigation="Patches and configuration hardening; segmentation."),
 "swisslog-pneumatic-2021": dict(region="US/International", cve="CVE-2021-37161…37165 (PwnedPiper)", disclosure="Researcher (Armis) + CISA coordinated disclosure.", mitigation="Firmware update for Nexus Control Panel; network isolation."),
 "urgent11-2019": dict(region="US/International", cve="CVE-2019-12255 (+10)", disclosure="Researcher (Armis) + FDA + ICS-CERT.", mitigation="Vendor stack patches; segmentation; monitoring of affected devices."),
 "swyentooth-2020": dict(region="US/International", cve="SweynTooth family", disclosure="Researchers (SUTD) + FDA notification.", mitigation="BLE SoC firmware updates from chip vendors integrated by device makers."),
 "access7-2022": dict(region="US/International", cve="CVE-2022-25246… (Access:7)", disclosure="Researcher (Forescout/CyberMDX) + FDA + CISA.", mitigation="PTC Axeda agent updates; disable unused services; segmentation."),
 "wannacry-nhs-2017": dict(region="International", cve="CVE-2017-0144 (EternalBlue)", disclosure="Public outbreak; NCSC/ENISA response.", mitigation="Emergency patching (MS17-010), kill-switch domain, segmentation, offline backups."),
 "hse-ireland-2021": dict(region="International", cve="—", disclosure="Public incident; national response + independent review.", mitigation="Rebuild from backups, EDR rollout, segmentation, identity hardening."),
 "duesseldorf-2020": dict(region="International", cve="CVE-2019-19781 (Citrix ADC)", disclosure="Public incident; BSI involvement.", mitigation="Patch Citrix, restore systems, divert emergencies during outage."),
 "singhealth-2018": dict(region="International", cve="—", disclosure="Government Committee of Inquiry report.", mitigation="Internet surfing separation, privileged-access controls, database monitoring, 2FA."),
 "bbraun-infusomat-2021": dict(region="US/International", cve="CVE-2021-33882…33886", disclosure="McAfee ATR coordinated disclosure with vendor.", mitigation="Firmware fixes; network isolation; restrict wireless access."),
 "microdicom-2024": dict(region="US/International", cve="CVE-2024-33606, CVE-2024-25578, CVE-2024-25569", disclosure="CISA ICS medical advisory (coordinated).", mitigation="Update to fixed version; don't open untrusted DICOM files; segmentation."),
}
for _i in INCIDENTS:
    _m = _INC_META2.get(_i["id"], {})
    _i["region"] = _m.get("region", "US")
    _i["cve"] = _m.get("cve", "—")
    _i["disclosure"] = _m.get("disclosure", "")
    _i["mitigation"] = _m.get("mitigation", "")
    _i.setdefault("agency", "FDA")
INCIDENTS.sort(key=lambda x: x.get("date", ""), reverse=True)

# --- international enforcement / fines ---
RTA_FINES += [
 dict(id="gdpr-health-fine", trigger="GDPR fine — inadequate security of health data", since="2018+",
      what="EU data-protection authorities have fined hospitals/providers for failing to secure patient data (Art. 32), including breaches involving connected systems.",
      lesson="Device telemetry and PHI security carry GDPR exposure independent of MDR.",
      source="https://edpb.europa.eu", date="2023-01-01", why="Reported/enforced because controllers failed to implement appropriate technical security measures for health data.", region="International"),
 dict(id="mhra-fsn", trigger="MHRA Field Safety Notice / corrective action (UK)", since="ongoing",
      what="MHRA requires manufacturers to issue Field Safety Notices and corrective actions for device safety/cyber issues affecting the UK market.",
      lesson="Postmarket cyber issues trigger FSNs and MHRA reporting, mirroring FDA 806.",
      source="https://www.gov.uk/drug-device-alerts", date="2024-01-01", why="Issued to inform users and require corrective action when a marketed device poses a safety/security risk.", region="International"),
 dict(id="eu-mdr-noncompliance", trigger="EU MDR Annex I §17 / MDCG 2019-16 deficiency", since="2021+",
      what="Notified Bodies can withhold or suspend CE certificates where cybersecurity essential requirements or technical documentation are inadequate.",
      lesson="Weak MDCG 2019-16 evidence stalls or revokes CE marking.",
      source="https://health.ec.europa.eu/medical-devices-sector_en", date="2021-05-26", why="Raised because the conformity assessment found the security essential requirements unmet.", region="International"),
]
for _t in RTA_FINES:
    _t.setdefault("region", "US")
RTA_FINES.sort(key=lambda x: x.get("date", ""), reverse=True)

# --- worked "excellent" examples + detailed evidence-document lists per template ---
_TPL_EX = {
"cybersecurity-management-plan": dict(docs=["Cybersecurity Management Plan (this doc)","Security Risk Management Report (AAMI SW96)","Threat Model v1.2","SBOM (CycloneDX 1.5)","Cybersecurity Test Report (3rd-party pen test)","Postmarket Surveillance & CVD Plan","Security Labeling / MDS2","Architecture Views package"],
 example="""# Cybersecurity Management Plan — AcmeCardio Remote Monitor (Class II, 510(k) K24XXXXX)
**Manufacturer:** Acme Medical, Inc.  ·  **Cyber device:** Yes (Wi-Fi + Bluetooth + cloud companion)
**Basis:** §524B; FDA Premarket Cybersecurity Guidance (2025); AAMI SW96; ISO 14971; IEC 81001-5-1

## 1. Scope & context
Wearable cardiac monitor streaming ECG to a phone app and AWS back-end (us-east-1). Related systems: mobile app, OTA update service, clinician web portal.

## 2. Governance
Product Security Owner: J. Rivera (PSIRT lead, security@acmemedical.com). SPDF: SDL-PROC-014 rev C.

## 3. Security risk management
Per SW96/14971; 27 threats assessed; 3 residual risks accepted (see SRM-RPT-007). Acceptance: exploitability x patient-harm matrix, signed by Quality + Security.

## 4. Architecture views
Global system, multi-patient harm, updateability, and security use-case views in ARCH-PKG-003.

## 5. SBOM
CycloneDX 1.5 generated in CI (Syft); 142 components; OpenSSL 3.0.13, libcurl 8.7.1; 0 known critical CVEs at submission; support/EOL tracked.

## 6. Controls (8 categories)
Mutual-TLS auth, RBAC, AES-256 at rest / TLS 1.3 in transit, signed firmware, audit logging to CloudWatch, watchdog resiliency, signed OTA updates.

## 7. Testing
SAST (CodeQL), SCA (Syft+Grype), DAST (ZAP), fuzzing (BLE GATT), independent pen test (VendorX, 2026-02) — all findings closed or risk-accepted (TEST-RPT-011).

## 8. Postmarket
Monitoring: SBOM→CVE + CISA KEV daily; CVD policy published; critical patch SLA ≤ 30 days; 806/803 triggers defined.

## 9. Labeling
MDS2 completed; hardening guide HG-002 ships with device.
"""),
"security-risk-assessment": dict(docs=["Security Risk Management Report","Risk matrix (asset×threat×control)","Residual-risk acceptance record","Traceability matrix (threat→control→test)"],
 example="""# Security Risk Assessment — AcmeCardio Remote Monitor (excerpt)
| ID | Asset | Threat (STRIDE) | Exploitability | Patient harm | Control | Residual |
|----|-------|-----------------|----------------|--------------|---------|----------|
| S-01 | BLE link | Spoofing | Medium | Medium (missed alert) | Mutual-TLS pairing + bonding | Low (accepted) |
| S-02 | OTA update | Tampering | Low | High (malicious firmware) | Signed images, anti-rollback | Low |
| S-04 | Cloud API | Information disclosure | Medium | Low (PHI) | TLS1.3, RBAC, KMS, audit logs | Low |
| S-05 | Device | Denial of service | Medium | Medium | Local store-and-forward, watchdog | Low (accepted) |
Acceptance: residual risks S-01/S-05 accepted by Quality+Security 2026-02-18; rationale: compensating controls + monitoring.
"""),
"threat-model": dict(docs=["Threat Model document","Data-flow diagrams","Trust-boundary diagram","Threat→control→test traceability"],
 example="""# Threat Model — AcmeCardio Remote Monitor (STRIDE)
## Decomposition
Entities: wearable, mobile app, OTA service, AWS API, clinician portal. Trust boundaries: device↔phone (BLE), phone↔cloud (TLS), cloud↔portal.
## Key threats & mitigations
- Spoofing (BLE): pairing/bonding + mutual-TLS → tested (BLE-PEN-03)
- Tampering (OTA): code signing + anti-rollback → tested (OTA-TST-02)
- Info disclosure (API): TLS1.3 + RBAC + field encryption → DAST
- Elevation (cloud): least-privilege IAM, scoped tokens → IAM review
## Residual
DoS via RF jamming accepted; mitigated by local buffering + clinician alerting.
"""),
"sbom-cyclonedx": dict(docs=["Machine-readable SBOM (CycloneDX 1.5 JSON)","Known-vulnerability report (Grype)","Support/EOL register"],
 example="""{
  "bomFormat": "CycloneDX", "specVersion": "1.5",
  "metadata": { "component": { "type": "application", "name": "acmecardio-fw", "version": "3.2.1" },
                "supplier": { "name": "Acme Medical, Inc." } },
  "components": [
    { "type": "library", "name": "openssl", "version": "3.0.13",
      "licenses": [{ "license": { "id": "Apache-2.0" } }],
      "properties": [{ "name": "support:level", "value": "supported" }, { "name": "support:endOfSupport", "value": "2026-09-07" }] },
    { "type": "library", "name": "libcurl", "version": "8.7.1",
      "licenses": [{ "license": { "id": "curl" } }] },
    { "type": "operating-system", "name": "FreeRTOS", "version": "10.6.1" }
  ],
  "vulnerabilities": []
}
"""),
"vulnerability-disclosure-policy": dict(docs=["Published CVD policy (web)","security.txt","Triage SLA record","Advisory template"],
 example="""# Coordinated Vulnerability Disclosure Policy — Acme Medical
**Contact:** security@acmemedical.com · PGP: 0xA1B2… · Portal: acmemedical.com/security
## Scope
All Acme devices and cloud services (current + prior major version).
## Reporting & safe harbor
Report in good faith; we will not pursue legal action for testing within this policy. Acknowledge ≤ 3 business days.
## Timelines
Triage ≤ 5 days; fix targets — Critical ≤ 30 days, High ≤ 60, Medium ≤ 90. Coordinated advisory at fix availability; CVEs requested via CNA.
## Regulator reporting
Assess 21 CFR 806/803 triggers; coordinate with CISA where appropriate.
"""),
"postmarket-cyber-plan": dict(docs=["Postmarket Surveillance Plan","Monitoring source list","Patch SLA matrix","Customer-notification template"],
 example="""# Postmarket Cybersecurity Plan — AcmeCardio (excerpt)
## Monitoring
Daily: SBOM→NVD/Grype match + CISA KEV; vendor PSIRT feeds; researcher reports via CVD.
## Assessment
Score exploitability × patient-harm; classify controlled vs uncontrolled risk (FDA postmarket).
## Remediation & notification
Critical patch ≤ 30 days; customer notice ≤ 30 days; OTA staged rollout with rollback.
## Metrics (Q1 2026)
MTTR 18 days; 99.2% fleet on supported firmware; 0 open critical vulns.
"""),
"premarket-cyber-checklist": dict(docs=["Each artifact below, attached to the eSTAR submission"],
 example="""# Premarket Cybersecurity Checklist — AcmeCardio (all satisfied)
- [x] Cyber-device determination → CSMP §1 (Wi-Fi/BLE/cloud)
- [x] Security risk management plan + file → SRM-RPT-007
- [x] Threat model + DFDs → TM v1.2
- [x] Architecture views (4) → ARCH-PKG-003
- [x] Controls matrix (8 categories) → CTRL-MTX-002
- [x] SBOM (machine+human) + known vulns → SBOM CycloneDX 1.5
- [x] Testing: SAST/DAST/SCA/fuzz/pen → TEST-RPT-011
- [x] Postmarket + CVD plan → PMS-CVD-004
- [x] Security labeling / MDS2 → LBL-MDS2-1
- [x] Interoperability + misconnection analysis → INT-RA-006
"""),
"pccp-ai": dict(docs=["PCCP (this doc)","Modification protocol","Performance/validation plan","Impact assessment","Transparency/labeling note"],
 example="""# Predetermined Change Control Plan — Acme ECG-AI (De Novo)
## 1. Description of modifications
(a) Periodic retraining on new labeled ECGs; (b) decision-threshold re-tuning within ±0.03; (c) added input lead aVR. No change to intended use.
## 2. Modification protocol
Data: ≥ 5,000 new ECGs, ≥ 30% from under-represented subgroups; independent test set frozen. Retrain → evaluate AUROC ≥ 0.95, sensitivity ≥ 0.90 overall and per subgroup. Versioned release with rollback.
## 3. Impact assessment
Risks: drift, subgroup degradation. Controls: locked acceptance gates, postmarket monitoring, halt criteria.
## 4. Transparency
Each release adds a version note (date, data summary, performance delta) to labeling.
"""),
"gmlp-checklist": dict(docs=["GMLP evidence pack","Data management plan","Train/test independence statement","Monitoring plan"],
 example="""# GMLP Checklist — Acme ECG-AI (satisfied with evidence)
- [x] 1 Multidisciplinary team → R&D + clinical + security sign-off
- [x] 2 Good SW & security → SDL-PROC-014; threat model
- [x] 3 Representative data → 42k ECGs, 5 sites, balanced demographics (DATA-PLAN-2)
- [x] 4 Independent train/test → frozen test set, no leakage (split audit)
- [x] 5 Reference standard → 2-cardiologist adjudication
- [x] 6 Model tailored to use → rhythm-classification CNN
- [x] 7 Human-AI team → reader study (+11% sensitivity with AI)
- [x] 8 Clinically relevant testing → prospective multi-site
- [x] 9 User info → model card MC-ECG-1
- [x] 10 Monitoring → drift dashboard + retrain triggers
"""),
"510k-cyber-section": dict(docs=["510(k) cybersecurity section (eSTAR)","All referenced cyber artifacts"],
 example="""# 510(k) Cybersecurity Section — AcmeCardio (summary)
1. Cyber device: Yes — Wi-Fi/BLE/cloud.
2. Security risk management → SRM-RPT-007 (residual risks accepted).
3. Threat model → TM v1.2 (STRIDE, DFDs).
4. Architecture views → ARCH-PKG-003.
5. Controls → 8 categories implemented (CTRL-MTX-002).
6. SBOM → CycloneDX 1.5, 0 critical CVEs.
7. Testing → SAST/DAST/SCA/fuzz/pen, findings closed (TEST-RPT-011).
8. Postmarket + CVD → PMS-CVD-004.
9. Labeling → MDS2 + hardening guide.
10. Conclusion: reasonable assurance of cybersecurity demonstrated.
"""),
"presub-request": dict(docs=["Pre-Sub cover letter","Specific questions","Draft cyber/PCCP strategy","Proposed test plan"],
 example="""# Pre-Submission — Acme ECG-AI
## Questions for FDA
1. Is the proposed PCCP modification protocol (retrain + threshold ±0.03) acceptable for De Novo?
2. Are the subgroup performance acceptance gates sufficient to characterize bias?
3. Is the cybersecurity test scope (SAST/DAST/SCA/fuzz/pen) adequate for a cloud-connected SaMD?
## Context
Rhythm-classification SaMD; cloud inference on AWS; intended for primary-care screening.
## Proposed strategy
GMLP-aligned data plan; CycloneDX SBOM; CVD policy; pen test by accredited lab pre-submission.
"""),
}
# attach example + evidence_docs to TEMPLATES via _TPL_META-style lookup used in emit

# ground the in-app worked examples in the same real cleared devices as the PDFs
_TPL_EX_GROUNDED = {
"cybersecurity-management-plan": """# Cybersecurity Management Plan — BD Alaris™ Infusion System
**Manufacturer:** Becton, Dickinson and Company  ·  **Status:** 510(k) cleared Jul 21, 2025-era update (2023) with enhanced cybersecurity + EMR interoperability
**Cyber device:** Yes (Wi-Fi + EMR interoperability, multi-module connected platform)
**Basis:** §524B; FDA Premarket Cybersecurity Guidance (2025); AAMI SW96; ISO 14971; IEC 81001-5-1

## 1. Scope & context
Connected acute-care infusion platform: Point-of-Care Unit (PCU) coordinates pump/syringe/PCA modules and exchanges programming with hospital EMRs. Related systems: device manager, EMR interface, signed update channel.
## 2. Governance / SPDF
Product Security Owner + PSIRT own the total product lifecycle; security activities run inside the SPDF integrated with the QMS.
## 3. Security risk management
Security risk file per SW96 + ISO 14971; threats scored on exploitability × patient-harm; residual risks formally accepted by Security + Quality.
## 4. Architecture views
Global system · multi-patient harm · updateability/patchability · security use-case views.
## 5. SBOM
CycloneDX, OS/networking/crypto components, support/EOL + known-vulnerability list, maintained postmarket.
## 6. Controls (8 categories)
Authentication, authorization, cryptography, code/data integrity, confidentiality, detection/logging, resiliency/recovery, signed updates.
## 7. Testing
SAST, SCA, DAST of network/EMR interfaces, independent pen test; coverage traced to threat model.
## 8. Postmarket & CVD
SBOM→CVE + CISA KEV monitoring; published CVD; severity-based patch timelines; 806/803 assessment.
## 9. Labeling
MDS2 + hardening guide; supported network configurations.

_Illustrative reconstruction grounded in the BD Alaris System (public FDA/BD 510(k) clearance, Jul 2023). Not actual confidential submission text._
""",
"security-risk-assessment": """# Security Risk Assessment — BD Alaris™ Infusion System (excerpt)
| ID | Asset | Threat (STRIDE) | Exploit. | Patient harm | Control | Residual |
|----|-------|-----------------|----------|--------------|---------|----------|
| S-01 | EMR interface | Spoofing | Med | Med (wrong auto-program) | Mutual auth, order validation | Low (accepted) |
| S-02 | Software update | Tampering | Low | High (malicious image) | Code signing, integrity check | Low |
| S-03 | Service interface | Elevation | Med | Med | RBAC, least privilege | Low |
| S-04 | PHI in transit | Info disclosure | Med | Low | TLS, key management | Low |
| S-05 | Network | Denial of service | Med | Med (delayed therapy) | Safe-state, local fallback | Low (accepted) |

Acceptance: S-01/S-05 accepted with compensating controls (segmentation, facility monitoring), reflected in labeling; signed by Security + Quality.
If a control can't be implemented: document the justification, compensating controls, residual risk + acceptance, and the labeling that discloses the limitation.

_Illustrative reconstruction grounded in the BD Alaris System (public sources). Not actual confidential submission text._
""",
"premarket-cyber-checklist": """# Premarket Cybersecurity Checklist — BD Alaris™ Infusion System (all satisfied)
- [x] Cyber-device determination → CSMP §1 (Wi-Fi + EMR interoperability)
- [x] Security risk management plan + file → SRM report (SW96/14971)
- [x] Threat model + DFDs → STRIDE model
- [x] Architecture views (4) → architecture package
- [x] Controls matrix (8 categories) → controls matrix
- [x] SBOM (machine+human) + known vulns → CycloneDX + vuln list
- [x] Testing: SAST/DAST/SCA/fuzz/pen → reports + coverage rationale
- [x] Postmarket + CVD plan → postmarket + CVD plan
- [x] Security labeling / MDS2 → labeling + MDS2
- [x] Interoperability + misconnection analysis → interoperability analysis

Since Oct 1, 2023 FDA refuses to accept cyber-device submissions missing §524B content — each unchecked box is a likely RTA.

_Illustrative reconstruction grounded in the BD Alaris System (public sources). Not actual confidential submission text._
""",
"pccp-ai": """# Predetermined Change Control Plan — LumineticsCore™ / IDx-DR (autonomous AI for diabetic retinopathy)
**Manufacturer:** Digital Diagnostics  ·  **Status:** De Novo DEN180001 (2018), first FDA-authorized autonomous diagnostic AI; later 510(k) on its own predicate (2021)
**AI structure:** image-quality AI + diagnostic AI → autonomous mtmDR result  ·  **Public thresholds:** 85% sensitivity / 82.5% specificity (900-patient pivotal trial)

## 1. Description of modifications
- Periodic re-training of the diagnostic algorithm on additional labeled fundus images (intended use unchanged)
- Bounded re-tuning of the operating threshold within pre-specified limits
- Support for additional compatible fundus cameras after equivalence testing
## 2. Modification protocol
Data: minimum size + demographic representativeness; independent frozen test set (no leakage).
Evaluation: maintain sensitivity/specificity ≥ cleared thresholds (85% / 82.5%) overall and per subgroup; no degradation on the locked test set.
Release: versioned with documented validation + rollback.
## 3. Impact assessment
Re-training → subgroup drift → locked acceptance gates + subgroup analysis. Threshold → sensitivity loss → bounded + re-validate. New camera → domain shift → equivalence testing.
## 4. Transparency
Each in-scope release adds a labeling version note (date, data summary, performance delta). Changes beyond this envelope require a new submission.

_Illustrative reconstruction grounded in IDx-DR / LumineticsCore (De Novo DEN180001; Abràmoff et al. 2018; FDA PCCP guidance 2024). Not actual confidential submission text._
""",
}
for _k, _v in _TPL_EX_GROUNDED.items():
    if _k in _TPL_EX:
        _TPL_EX[_k]["example"] = _v
_TPL_PDF = {
 "cybersecurity-management-plan": "cybersecurity-management-plan-example.pdf",
 "security-risk-assessment": "security-risk-assessment-example.pdf",
 "premarket-cyber-checklist": "premarket-cyber-checklist-example.pdf",
 "pccp-ai": "pccp-ai-example.pdf",
 "sbom-cyclonedx": "sbom-cyclonedx-example.pdf",
 "threat-model": "threat-model-example.pdf",
 "vulnerability-disclosure-policy": "vulnerability-disclosure-policy-example.pdf",
 "postmarket-cyber-plan": "postmarket-cyber-plan-example.pdf",
 "510k-cyber-section": "510k-cyber-section-example.pdf",
 "gmlp-checklist": "gmlp-checklist-example.pdf",
 "presub-request": "presub-request-example.pdf",
}

# additional grounded worked examples (non-BD devices for variety)
_TPL_EX["sbom-cyclonedx"]["example"] = """{
  "bomFormat": "CycloneDX", "specVersion": "1.5",
  "metadata": { "component": { "type": "application", "name": "alaris-pcu-fw", "version": "<cleared-version>" },
                "supplier": { "name": "Becton, Dickinson and Company" } },
  "components": [
    { "type": "library", "name": "openssl", "version": "3.0.x", "licenses": [{ "license": { "id": "Apache-2.0" } }],
      "properties": [{ "name": "support:level", "value": "supported" }] },
    { "type": "library", "name": "network-stack", "version": "x.y" },
    { "type": "operating-system", "name": "rtos", "version": "x.y" }
  ], "vulnerabilities": []
}

Illustrative reconstruction grounded in the BD Alaris System (public sources). Not actual confidential submission text."""

_TPL_EX["threat-model"]["example"] = """# Threat Model — Dexcom G7 (connected CGM + mobile app)  ·  STRIDE
**Status:** FDA-cleared iCGM (2022); Bluetooth Low Energy to the G7 app (iOS/Android) and Apple Watch; cloud (Clarity) + share.
## Decomposition
Entities: sensor/transmitter, mobile app, BLE link, Dexcom cloud, follower/share, Apple Watch. Trust boundaries: sensor↔phone (BLE), phone↔cloud (TLS), cloud↔followers.
## Key threats & mitigations
- Spoofing (BLE): bonded pairing, session keys → BLE security tests
- Tampering (readings/alerts): integrity checks, validated ranges → fuzz + unit tests
- Info disclosure (glucose/PHI): TLS 1.2+, mobile secure storage (Keychain/Keystore) → MobSF, network capture
- DoS (alert suppression): local alerting independent of cloud → fault-injection
- Elevation (cloud/API): least-privilege IAM, scoped tokens → IAM review
## Residual
RF jamming of BLE accepted; mitigated by on-device alerting and gap handling.

_Illustrative reconstruction grounded in Dexcom G7 (public clearance + connectivity facts). Not actual confidential submission text._"""

_TPL_EX["vulnerability-disclosure-policy"]["example"] = """# Coordinated Vulnerability Disclosure Policy — (modeled on Medtronic's public product-security program)
**Contact:** a public security page + security@ intake; PGP key published.  **Scope:** marketed products + connected services.
## Reporting & safe harbor
Good-faith research welcomed; acknowledgment within a stated window; no legal action for testing within policy.
## Coordination
Triage and validate; assign/track CVEs (as a CNA or via a CNA); coordinate with CISA/ICS-CERT; publish security bulletins/advisories.
## Timelines
Severity-based remediation targets; interim mitigations communicated to customers; advisory at fix availability.
## Regulator reporting
Assess 21 CFR 806 correction/removal and 803 MDR triggers; align to FDA postmarket cybersecurity guidance.

_Illustrative reconstruction modeled on Medtronic's publicly documented coordinated-disclosure/PSIRT program. Not actual confidential text._"""

_TPL_EX["postmarket-cyber-plan"]["example"] = """# Postmarket Cybersecurity Plan — (modeled on a large connected-device maker, e.g., Medtronic)
## Monitoring
SBOM→CVE matching daily, CISA KEV, vendor PSIRT feeds, researcher reports via CVD intake.
## Assessment
Score exploitability × patient-harm; classify controlled vs uncontrolled risk per FDA postmarket guidance; CVSS + clinical impact.
## Remediation & notification
Severity-based patch SLAs; signed OTA/staged deployment with rollback; customer security bulletins.
## Reporting
21 CFR 806/803 assessment; coordinate advisories with CISA.
## Metrics
MTTR, % fleet on supported versions, open critical vulnerabilities.

_Illustrative reconstruction grounded in publicly documented PSIRT practice. Not actual confidential text._"""

_TPL_EX["510k-cyber-section"]["example"] = """# 510(k) Cybersecurity Section — Dexcom G7 (connected mobile iCGM)  ·  summary
1. Cyber device: Yes — BLE + mobile app (iOS/Android) + cloud (Clarity/share).
2. Security risk management → SRM file (SW96/14971), residual risks accepted.
3. Threat model → STRIDE across sensor/phone/cloud (see threat-model example).
4. Architecture views → global, multi-patient (cloud), updateability, use-case.
5. Controls (8 categories) → BLE bonding, TLS, mobile secure storage, signed app/firmware, logging.
6. SBOM → CycloneDX incl. mobile + embedded components; 0 critical CVEs.
7. Testing → SAST/DAST/SCA, BLE fuzzing, mobile (MobSF/MASVS), independent pen test.
8. Postmarket + CVD → monitoring + disclosure policy.
9. Labeling → security labeling + secure-setup guidance for the app.
10. Conclusion: reasonable assurance of cybersecurity for a connected CGM.

_Illustrative reconstruction grounded in Dexcom G7 (public facts). Not actual confidential submission text._"""

_TPL_EX["gmlp-checklist"]["example"] = """# GMLP Checklist — Viz.ai LVO (computer-aided triage AI for stroke)  ·  satisfied with evidence
**Status:** De Novo (2018), first FDA-authorized computer-aided triage & notification software; analyzes CTA, alerts the stroke team.
- [x] 1 Multidisciplinary expertise → clinical neuro + ML + security
- [x] 2 Good SW & security engineering → SDLC + threat model (HIPAA-compliant comms)
- [x] 3 Representative data → multi-site CTA across scanners/demographics
- [x] 4 Independent train/test → frozen test set, no leakage
- [x] 5 Reference standard → neuroradiologist adjudication of LVO
- [x] 6 Model tailored to use → LVO detection on CTA
- [x] 7 Human-AI team → notification augments, does not replace, the specialist read
- [x] 8 Clinically relevant testing → time-to-notification + detection performance
- [x] 9 User info → intended use, performance, limitations communicated
- [x] 10 Monitoring → real-world performance + drift monitoring

_Illustrative reconstruction grounded in Viz.ai LVO (public De Novo facts). Not actual confidential submission text._"""

_TPL_EX["presub-request"]["example"] = """# Pre-Submission (Q-Sub) — connected CGM (modeled on a Dexcom-class iCGM)
## Questions for FDA
1. Is the cybersecurity test scope (SAST/DAST/SCA, BLE fuzzing, mobile MASVS, pen test) adequate for a connected CGM + mobile app?
2. Are the proposed security architecture views sufficient given the cloud + follower-share ecosystem?
3. For mobile, is OWASP MASVS-based evidence acceptable to support the controls?
## Context
Integrated CGM (iCGM) with BLE to iOS/Android apps and cloud; interoperable with AID systems.
## Proposed strategy
SW96 risk management; CycloneDX SBOM; CVD policy; independent pen test pre-submission.

_Illustrative reconstruction grounded in a Dexcom-class connected CGM (public facts). Not actual confidential submission text._"""

# ================================================================ Security Requirements & V&V Tests
SECREQS = [
 dict(id="sr-authn", req="Unique user / entity authentication", mode="Automatable + Manual",
      desc="Authenticate users and connected entities before granting access to device functions, configuration, or data.",
      vv="Authentication test cases (valid/invalid/locked), session-management tests, penetration test of auth flows.",
      tech=["Software","Connected","Cloud","SaMD","Mobile-iOS","Mobile-Android"]),
 dict(id="sr-nodefault", req="No hardcoded or default credentials", mode="Automatable",
      desc="No shared, default, or hardcoded secrets/passwords/keys in firmware, app, or services.",
      vv="Secret scanning (gitleaks/trufflehog), SAST, firmware/app binary inspection.",
      tech=["Software","Firmware","Connected","Mobile-iOS","Mobile-Android","Cloud"]),
 dict(id="sr-mutualauth", req="Mutual authentication for device↔server", mode="Automatable + Manual",
      desc="Both endpoints authenticate (e.g., mutual TLS / certificate pinning) for device-to-cloud and device-to-app links.",
      vv="TLS handshake inspection, certificate-pinning bypass test, man-in-the-middle test.",
      tech=["Connected","Cloud","Mobile-iOS","Mobile-Android","AWS","Azure","GCP"]),
 dict(id="sr-authz", req="Authorization & least privilege (RBAC)", mode="Automatable + Manual",
      desc="Role-based access control; service and user accounts limited to least privilege.",
      vv="RBAC test matrix, privilege-escalation tests, IAM policy review.",
      tech=["Software","Connected","Cloud","AWS","Azure","GCP","SaMD"]),
 dict(id="sr-tls", req="Data-in-transit encryption (TLS 1.2+)", mode="Automatable",
      desc="All sensitive/PHI traffic encrypted with current TLS; no plaintext protocols.",
      vv="TLS scan (testssl.sh/sslyze), network capture, cipher-suite policy check.",
      tech=["Connected","Cloud","Mobile-iOS","Mobile-Android","AWS","Azure","GCP","SaMD"]),
 dict(id="sr-rest", req="Data-at-rest encryption & key management", mode="Automatable + Manual",
      desc="Sensitive data/credentials encrypted at rest; keys managed via KMS/HSM or platform keystore.",
      vv="Storage inspection, key-management design review, KMS/HSM configuration check.",
      tech=["Software","Cloud","Mobile-iOS","Mobile-Android","AWS","Azure","GCP"]),
 dict(id="sr-crypto", req="Approved cryptography (no weak algorithms)", mode="Automatable",
      desc="Use vetted, current cryptographic algorithms and libraries; no MD5/SHA-1/DES/ECB for security.",
      vv="Crypto/static analysis, dependency scan, cryptographic review.",
      tech=["Software","Firmware","Connected","Cloud","Mobile-iOS","Mobile-Android"]),
 dict(id="sr-signedupdate", req="Signed software/firmware updates + anti-rollback", mode="Automatable + Manual",
      desc="Updates are cryptographically signed and verified; downgrade/rollback to vulnerable versions prevented.",
      vv="Signature-verification test, tampered-image rejection test, anti-rollback test.",
      tech=["Firmware","Software","Connected","Mobile-iOS","Mobile-Android"]),
 dict(id="sr-secureboot", req="Secure boot / boot integrity", mode="Manual",
      desc="Device boots only verified firmware via a hardware/firmware root of trust.",
      vv="Boot-chain tamper test, secure-boot configuration review.",
      tech=["Hardware","Firmware"]),
 dict(id="sr-integrity", req="Code & data integrity protection", mode="Automatable + Manual",
      desc="Detect/prevent unauthorized modification of executable code and critical data.",
      vv="Integrity-check tests, tamper tests, runtime integrity verification.",
      tech=["Software","Firmware","Connected","SaMD"]),
 dict(id="sr-logging", req="Security audit logging", mode="Automatable + Manual",
      desc="Record security-relevant events (auth, config change, update) and make them available to the facility/SIEM.",
      vv="Log-generation tests, log-content review, SIEM ingestion test.",
      tech=["Software","Connected","Cloud","AWS","Azure","GCP"]),
 dict(id="sr-detect", req="Anomaly / intrusion detection", mode="Automatable + Manual",
      desc="Detect anomalous behavior or known-bad activity on the device or its services.",
      vv="Detection-rule tests, simulated-attack/replay tests.",
      tech=["Connected","Cloud","AWS","Azure","GCP"]),
 dict(id="sr-failsafe", req="Fail-safe / safe state under attack", mode="Manual",
      desc="Device maintains or reverts to a safe clinical state during cyber disruption (DoS, loss of connectivity).",
      vv="Fault injection, DoS/network-loss testing, safe-state verification.",
      tech=["Hardware","Firmware","Connected","SaMD"]),
 dict(id="sr-backup", req="Backup & recovery", mode="Automatable + Manual",
      desc="Recover configuration/data and restore service after a cyber event.",
      vv="Restore/recovery drills, backup-integrity verification.",
      tech=["Software","Cloud","AWS","Azure","GCP"]),
 dict(id="sr-ota", req="Remote update capability with rollback control", mode="Automatable + Manual",
      desc="Field-updatable to remediate vulnerabilities, with controlled, signed, reversible deployment.",
      vv="OTA update test (staged + rollback), update-failure handling test.",
      tech=["Connected","Firmware","Software","Mobile-iOS","Mobile-Android"]),
 dict(id="sr-sca", req="Software composition analysis (SCA)", mode="Automatable",
      desc="Continuously identify third-party/OSS components and their known vulnerabilities.",
      vv="SCA in CI (Grype/Dependabot/OWASP DC); fail build on critical CVEs.",
      tech=["Software","Firmware","Cloud","SaMD","Mobile-iOS","Mobile-Android"]),
 dict(id="sr-sbom", req="SBOM generation & maintenance", mode="Automatable",
      desc="Produce and maintain a machine-readable SBOM with support/EOL and known-vulnerability data.",
      vv="SBOM generation in CI (Syft); completeness/format validation (CycloneDX/SPDX).",
      tech=["Software","Firmware","Cloud","SaMD","Mobile-iOS","Mobile-Android"]),
 dict(id="sr-sast", req="Static application security testing (SAST)", mode="Automatable",
      desc="Analyze source/binaries for security weaknesses before release.",
      vv="SAST gate in CI (CodeQL/Semgrep/SonarQube); triage to closure.",
      tech=["Software","Firmware","SaMD","Mobile-iOS","Mobile-Android","Cloud"]),
 dict(id="sr-dast", req="Dynamic application security testing (DAST)", mode="Automatable",
      desc="Test running interfaces/APIs for exploitable vulnerabilities.",
      vv="DAST scan (OWASP ZAP/Burp) of services and APIs.",
      tech=["Connected","Cloud","SaMD","Mobile-iOS","Mobile-Android","AWS","Azure","GCP"]),
 dict(id="sr-fuzz", req="Fuzz / robustness testing of interfaces", mode="Automatable",
      desc="Send malformed inputs to protocols/parsers (BLE, network, file/DICOM) to find crashes/weaknesses.",
      vv="Protocol/API/file fuzzing with coverage tracking.",
      tech=["Connected","Firmware","Software","AI"]),
 dict(id="sr-pentest", req="Independent penetration test", mode="Manual",
      desc="Third-party adversarial assessment against the threat model before submission/release.",
      vv="Scoped penetration test; report with findings closed or risk-accepted.",
      tech=["Software","Connected","Cloud","SaMD","Hardware","Mobile-iOS","Mobile-Android"]),
 dict(id="sr-mobile-hardening", req="Mobile app hardening", mode="Automatable + Manual",
      desc="Jailbreak/root detection, certificate pinning, anti-tamper, no sensitive data in logs/backups.",
      vv="MobSF scan, OWASP MASVS/MASTG tests, runtime (Frida) checks.",
      tech=["Mobile-iOS","Mobile-Android","SaMD"]),
 dict(id="sr-mobile-storage", req="Mobile secure storage (Keychain/Keystore)", mode="Automatable + Manual",
      desc="Sensitive data/credentials stored in iOS Keychain / Android Keystore, not plaintext files.",
      vv="MobSF storage analysis, device-filesystem inspection.",
      tech=["Mobile-iOS","Mobile-Android"]),
 dict(id="sr-mobile-ats", req="No cleartext traffic (ATS / network security config)", mode="Automatable",
      desc="iOS App Transport Security enabled; Android network-security-config disallows cleartext.",
      vv="MobSF config check, traffic capture to confirm TLS-only.",
      tech=["Mobile-iOS","Mobile-Android"]),
 dict(id="sr-cloud-cspm", req="Cloud configuration baseline (CIS benchmark)", mode="Automatable",
      desc="Cloud accounts/resources hardened to a CIS benchmark; drift detected continuously.",
      vv="CSPM scan (Prowler/ScoutSuite/Defender for Cloud); CIS benchmark report.",
      tech=["Cloud","AWS","Azure","GCP"]),
 dict(id="sr-cloud-iam", req="Cloud IAM least privilege", mode="Automatable + Manual",
      desc="No wildcard/admin-by-default; scoped roles; no long-lived keys where avoidable.",
      vv="IAM policy analysis (Prowler/ScoutSuite/IAM Access Analyzer); access review.",
      tech=["Cloud","AWS","Azure","GCP"]),
 dict(id="sr-cloud-logging", req="Cloud audit logging & monitoring", mode="Automatable",
      desc="Account-level audit trail and threat detection enabled.",
      vv="Verify CloudTrail+GuardDuty (AWS) / Azure Monitor+Defender / GCP Cloud Audit Logs+SCC.",
      tech=["Cloud","AWS","Azure","GCP"]),
 dict(id="sr-container", req="Container/image vulnerability scanning", mode="Automatable",
      desc="Scan container images and IaC for vulnerabilities and misconfigurations before deploy.",
      vv="Image scan (Trivy/Grype) + IaC scan (Checkov/tfsec) in CI.",
      tech=["Cloud","AWS","Azure","GCP"]),
 dict(id="sr-segmentation", req="Network segmentation / least-exposure", mode="Automatable + Manual",
      desc="Restrict device/service network exposure; segment clinical networks; minimize open ports/services.",
      vv="Port/service scan, security-group/firewall review, segmentation test.",
      tech=["Connected","Cloud","Hardware","AWS","Azure","GCP"]),
 dict(id="sr-debug", req="Disable debug/maintenance interfaces", mode="Manual",
      desc="JTAG/UART/serial and debug services disabled or protected in production hardware.",
      vv="Hardware inspection, interface probing, production-image review.",
      tech=["Hardware","Firmware"]),
 dict(id="sr-exploit-mit", req="Binary exploit mitigations (ASLR/DEP/canaries)", mode="Automatable",
      desc="Compile/link with modern exploit mitigations enabled.",
      vv="Binary hardening check (checksec / platform equivalents).",
      tech=["Firmware","Software"]),
 dict(id="sr-ai-adversarial", req="AI adversarial robustness testing", mode="Automatable + Manual",
      desc="Evaluate model resilience to adversarial/perturbed inputs and out-of-distribution data.",
      vv="Adversarial test suite (e.g., ART), OOD/perturbation tests, performance bounds.",
      tech=["AI","SaMD"]),
 dict(id="sr-ai-dataintegrity", req="AI training-data integrity & provenance", mode="Automatable + Manual",
      desc="Protect against data poisoning; record data lineage; sign/verify datasets and models.",
      vv="Data-lineage audit, dataset/model signing verification, poisoning red-team.",
      tech=["AI","SaMD","Cloud"]),
 dict(id="sr-ai-input", req="AI inference input validation", mode="Automatable",
      desc="Validate/sanitize inputs (image format/range, metadata) before inference.",
      vv="Input fuzzing, range/format validation tests, malformed-DICOM tests.",
      tech=["AI","SaMD","Connected"]),
 dict(id="sr-ai-version", req="AI model versioning & rollback (PCCP-aligned)", mode="Automatable + Manual",
      desc="Version models, gate releases on acceptance criteria, and support rollback within the PCCP envelope.",
      vv="Release-gate tests against locked test set; rollback drill; version-traceability audit.",
      tech=["AI","SaMD","Cloud"]),
]

# ================================================================ Risk Assessment (cyber ↔ patient safety)
# Severity/Likelihood on 1–5 scales (ISO 14971 / AAMI TIR57 style); risk = S×L band.
RISK_ASSESSMENT = [
 dict(id="ra-01", cyber_issue="Unauthorized modification of infusion program / drug library", cia="I, A",
      inh_sev=5, inh_lik=3, control="Mutual authentication, signed configuration, server-side order validation, dose range limits",
      hazard="Over- or under-infusion of medication", patient="Overdose/underdose — serious harm or death",
      res_sev=5, res_lik=1, rec="Enforce signed config + order validation; segment clinical network; alert on anomalous programming",
      std="ISO 14971; AAMI SW96; FDA Premarket 2025"),
 dict(id="ra-02", cyber_issue="Unauthenticated wireless (BLE) command to insulin pump", cia="I",
      inh_sev=5, inh_lik=3, control="Bonded pairing, authenticated commands, max-dose sanity limits",
      hazard="Incorrect insulin delivery", patient="Hypo-/hyperglycemia — serious harm",
      res_sev=5, res_lik=1, rec="Require authenticated pairing; cap maximum dose; alert on anomalous commands",
      std="ISO 14971; FDA Premarket 2025"),
 dict(id="ra-03", cyber_issue="Unauthenticated RF telemetry to implant (pacemaker/ICD)", cia="I, C",
      inh_sev=5, inh_lik=2, control="Authenticated/encrypted telemetry, staged signed firmware",
      hazard="Altered pacing/defibrillation settings", patient="Inappropriate therapy — death",
      res_sev=5, res_lik=1, rec="Deploy authenticated telemetry; monitored firmware update via clinic",
      std="ISO 14971; IEC 81001-5-1"),
 dict(id="ra-04", cyber_issue="Network flood / ransomware / RF jamming (availability loss)", cia="A",
      inh_sev=4, inh_lik=4, control="Safe-state design, local fallback/buffering, resiliency, offline backups",
      hazard="Therapy interruption / device offline", patient="Delayed therapy or monitoring — harm",
      res_sev=4, res_lik=2, rec="Design fail-safe + local autonomy; segment networks; tested backups/restore",
      std="ISO 14971; FDA Postmarket; AAMI TIR97"),
 dict(id="ra-05", cyber_issue="Manipulated or suppressed clinical alert (monitor/CGM)", cia="I, A",
      inh_sev=4, inh_lik=3, control="Integrity checks, independent on-device alerting, validation",
      hazard="Missed or false clinical alert", patient="Undetected deterioration — harm",
      res_sev=4, res_lik=2, rec="Independent local alerting; integrity-verify alert path; anomaly detection",
      std="ISO 14971; AAMI TIR57"),
 dict(id="ra-06", cyber_issue="Adversarial/poisoned input or model-integrity loss (AI)", cia="I",
      inh_sev=4, inh_lik=3, control="Adversarial testing, input validation, data/model integrity, monitoring",
      hazard="AI misclassification (false negative)", patient="Missed diagnosis — delayed treatment",
      res_sev=4, res_lik=2, rec="Adversarial + OOD testing; sign datasets/models; monitor real-world performance",
      std="GMLP; NIST AI RMF; ISO 14971"),
 dict(id="ra-07", cyber_issue="Weak crypto / cloud misconfig / mobile data leakage", cia="C",
      inh_sev=2, inh_lik=4, control="TLS, encryption at rest, IAM least-privilege, secure mobile storage",
      hazard="Disclosure of PHI", patient="Privacy harm; indirect safety via loss of trust",
      res_sev=2, res_lik=2, rec="Enforce TLS + at-rest encryption; CSPM baseline; MASVS mobile storage",
      std="ISO 27001; HIPAA; GDPR Art. 32"),
 dict(id="ra-08", cyber_issue="Unsigned update / no anti-rollback (malicious firmware)", cia="I, A",
      inh_sev=5, inh_lik=2, control="Signed updates, secure boot, anti-rollback",
      hazard="Malicious firmware installed", patient="Arbitrary device behavior — severe harm",
      res_sev=5, res_lik=1, rec="Mandate code signing + secure boot + anti-rollback; verify on receipt",
      std="FDA Premarket 2025; IEC 81001-5-1"),
 dict(id="ra-09", cyber_issue="Unpatched OSS/third-party component (no SBOM/SCA)", cia="C, I, A",
      inh_sev=4, inh_lik=4, control="SBOM + SCA monitoring, patch SLAs, coordinated disclosure",
      hazard="Exploited known component vulnerability", patient="Compromise — varied patient harm",
      res_sev=4, res_lik=2, rec="Maintain SBOM; monitor CISA KEV; meet severity-based patch SLAs",
      std="§524B; AAMI TIR97; NIST 800-53"),
 dict(id="ra-10", cyber_issue="Shared/default/hardcoded credentials", cia="C, I",
      inh_sev=4, inh_lik=3, control="No default creds, unique authentication, secret scanning",
      hazard="Default/hardcoded credential abuse", patient="Unauthorized control — harm",
      res_sev=4, res_lik=1, rec="Remove defaults; provision unique credentials; scan builds for secrets",
      std="FDA Premarket 2025; OWASP"),
 dict(id="ra-11", cyber_issue="Open storage / over-broad IAM in AWS/Azure/GCP", cia="C, A",
      inh_sev=3, inh_lik=4, control="CIS baseline (CSPM), IAM least-privilege, audit logging",
      hazard="Cloud misconfiguration data exposure", patient="Mass PHI exposure; availability impact",
      res_sev=3, res_lik=2, rec="Apply CIS benchmark via CSPM; least-privilege IAM; enable audit logs",
      std="ISO 27001; NIST 800-53"),
 dict(id="ra-12", cyber_issue="Insecure mobile storage / no pinning / rooted device", cia="C, I",
      inh_sev=3, inh_lik=4, control="Keychain/Keystore, certificate pinning, root/jailbreak detection (MASVS)",
      hazard="Mobile app data leakage / tampering", patient="PHI exposure; manipulated readings",
      res_sev=3, res_lik=2, rec="Use platform secure storage + pinning; MASVS testing; integrity checks",
      std="OWASP MASVS; FDA Premarket 2025"),
]

# more "what good looks like" exemplars (new template types)
TEMPLATES["architecture-views"] = ("Security Architecture Views", "Cybersecurity", """# Security Architecture Views (FDA — 4 views)
**Device:** <name>  ·  **Basis:** FDA Premarket Cybersecurity Guidance (2025) §V.A.3

## 1. Global system view
All components, interfaces, data stores, external systems, and data flows with trust boundaries.

## 2. Multi-patient harm view
How a single compromise could scale to multiple patients (e.g., server/cloud), and the controls that prevent it.

## 3. Updateability / patchability view
How signed software/firmware updates reach the installed base; rollback/anti-rollback.

## 4. Security use case views
End-to-end flows for authentication, remote service, interoperability, and update — with controls per step.
""")
TEMPLATES["ai-model-card"] = ("AI Model Card / Transparency", "AI", """# AI Model Card / Transparency
**Device:** <name>  ·  **Basis:** FDA AI transparency principles; GMLP; EU AI Act

## Intended use & users
Indication, population, clinical workflow, autonomy level.
## Inputs / outputs
Data types, formats, output semantics, thresholds.
## Performance
Primary metrics with CIs; overall and per pre-defined subgroup; reference standard.
## Limitations
Out-of-scope use, known failure modes, edge cases.
## Data
Provenance, representativeness, train/test independence.
## Monitoring & change control
Real-world monitoring, drift triggers, PCCP envelope.
""")
TEMPLATES["pentest-summary"] = ("Penetration Test Summary", "Cybersecurity", """# Penetration Test Summary
**Device:** <name>  ·  **Tester:** <independent lab>  ·  **Dates:** <range>  ·  **Scope:** device, app, cloud, interfaces

## Methodology
Threat-model-driven; OWASP/MITRE ATT&CK; black/grey-box; tools + manual.
## Findings (by severity)
| ID | Severity | Finding | Status |
|----|----------|---------|--------|
| P-1 | High | <finding> | Closed |
| P-2 | Medium | <finding> | Risk-accepted |
## Coverage rationale
Mapping of tested attack surfaces to the threat model.
## Conclusion
Residual risk acceptable; retest evidence attached.
""")
_TPL_META["architecture-views"] = dict(guidance="Produce all four FDA views so reviewers can see the system, how harm could scale, how you patch, and how key flows are secured.",
   evidence=["Global system diagram", "Multi-patient harm analysis", "Updateability diagram", "Security use-case flows"])
_TPL_META["ai-model-card"] = dict(guidance="A concise, user-facing transparency artifact: intended use, performance (overall + subgroup), limitations, data, and how the model changes over time.",
   evidence=["Model card", "Subgroup performance table", "Data provenance summary", "Monitoring/PCCP reference"])
_TPL_META["pentest-summary"] = dict(guidance="Summarize an independent test tied to your threat model; show findings, closure/risk-acceptance, and coverage rationale.",
   evidence=["Pen test report", "Findings tracker with closure", "Coverage-to-threat-model mapping", "Retest evidence"])
_TPL_EX["architecture-views"] = dict(docs=["Global system view", "Multi-patient harm view", "Updateability view", "Security use-case views"], example="")
_TPL_EX["ai-model-card"] = dict(docs=["Model card", "Performance + subgroup tables", "Data provenance", "Monitoring plan"], example="")
_TPL_EX["pentest-summary"] = dict(docs=["Independent pen-test report", "Findings tracker", "Coverage rationale", "Retest evidence"], example="")
_TPL_PDF["architecture-views"] = "architecture-views-example.pdf"
_TPL_PDF["ai-model-card"] = "ai-model-card-example.pdf"
_TPL_PDF["pentest-summary"] = "pentest-summary-example.pdf"
_TPL_EX["architecture-views"]["example"] = """# Security Architecture Views — BD Alaris™ Infusion System
## 1. Global system view
PCU + pump/syringe/PCA/respiratory modules ↔ facility network ↔ EMR interface ↔ device manager ↔ signed update service. Trust boundaries at each hop.
## 2. Multi-patient harm view
A compromised server/EMR interface must NOT push unsafe programs fleet-wide — controls: signed/validated orders, server hardening, segmentation, rate/range limits.
## 3. Updateability / patchability view
Signed software distributed to the installed base; integrity verified on receipt; anti-rollback; staged rollout with monitoring.
## 4. Security use-case views
Clinician auth → program infusion → EMR auto-program (validated) → audit log; remote service (authenticated, logged); update (signed, verified).

_Illustrative reconstruction grounded in the BD Alaris System (public sources). Not actual confidential submission text._"""
_TPL_EX["ai-model-card"]["example"] = """# AI Model Card — LumineticsCore™ / IDx-DR (autonomous diabetic retinopathy AI)
**Intended use:** Autonomous detection of more-than-mild diabetic retinopathy (mtmDR) in adults with diabetes, in primary care.
**Inputs/outputs:** Fundus images (specified cameras) → mtmDR present / not detected (+ image-quality gate).
**Performance (public pivotal trial):** Sensitivity 87%+/specificity 90%+ region; FDA thresholds 85% sensitivity / 82.5% specificity.
**Limitations:** Not for patients with prior DR diagnosis; image-quality dependent; specified cameras only.
**Data:** 900-patient pivotal study across primary-care sites; independent reference standard.
**Monitoring/change control:** Real-world performance monitoring; PCCP governs retraining within bounds.

_Illustrative reconstruction grounded in IDx-DR / LumineticsCore (public De Novo facts). Not actual confidential text._"""
_TPL_EX["pentest-summary"]["example"] = """# Penetration Test Summary — Dexcom-class connected CGM (illustrative)
**Tester:** Independent accredited lab  ·  **Scope:** sensor/BLE, mobile app (iOS/Android), cloud APIs
## Methodology
Threat-model-driven; OWASP MASVS/MASTG + API testing; BLE protocol testing; grey-box.
## Findings
| ID | Severity | Finding | Status |
|----|----------|---------|--------|
| P-1 | Medium | Verbose API error leakage | Closed |
| P-2 | Low | Missing cert-pinning on one endpoint | Closed |
| P-3 | Info | Logging hygiene | Risk-accepted |
## Coverage
BLE, app storage/transport, API authz, cloud IAM mapped to the threat model.
## Conclusion
No high/critical open findings; residual risk acceptable; retest evidence attached.

_Illustrative reconstruction grounded in a Dexcom-class connected CGM (public facts). Not actual confidential text._"""

# primary device label per template + alternate-company exemplars (more "what good looks like")
_TPL_PRIMARY = {
 "cybersecurity-management-plan": "BD Alaris (infusion)", "security-risk-assessment": "BD Alaris",
 "premarket-cyber-checklist": "BD Alaris", "pccp-ai": "IDx-DR / LumineticsCore",
 "sbom-cyclonedx": "BD Alaris", "threat-model": "Dexcom G7", "vulnerability-disclosure-policy": "Medtronic",
 "postmarket-cyber-plan": "Medtronic", "510k-cyber-section": "Dexcom G7", "gmlp-checklist": "Viz.ai LVO",
 "presub-request": "Dexcom-class CGM", "architecture-views": "BD Alaris", "ai-model-card": "IDx-DR",
 "pentest-summary": "Dexcom-class CGM",
}
_TPL_ALT = {
 "cybersecurity-management-plan": [("Abbott FreeStyle Libre 3 Plus (CGM)", "csmp-abbott-example.pdf")],
 "threat-model": [("Insulet Omnipod 5 (AID pump)", "threat-model-omnipod-example.pdf")],
 "pccp-ai": [("Insulet Omnipod 5 (AID algorithm)", "pccp-omnipod-example.pdf")],
 "postmarket-cyber-plan": [("Abbott FreeStyle Libre (CGM)", "postmarket-abbott-example.pdf")],
 "sbom-cyclonedx": [("Insulet Omnipod 5 (AID pump)", "sbom-omnipod-example.pdf")],
}
def _example_pdfs(tid):
    out = []
    if _TPL_PDF.get(tid):
        out.append({"label": _TPL_PRIMARY.get(tid, "Example"), "file": _TPL_PDF[tid]})
    for label, f in _TPL_ALT.get(tid, []):
        out.append({"label": label, "file": f})
    return out

# ----------------------------------------------------------------- emit
def main():
    corpus = dict(regulations=REGULATIONS, submissions=SUBMISSIONS, requirements=REQUIREMENTS,
                  incidents=INCIDENTS, rta=RTA_FINES, ai=AI_REQS, secreqs=SECREQS, risk=RISK_ASSESSMENT,
                  templates=[{"id": k, "name": v[0], "category": v[1], "content": v[2],
                              "guidance": _TPL_META.get(k, {}).get("guidance", ""),
                              "evidence": _TPL_META.get(k, {}).get("evidence", []),
                              "evidence_docs": _TPL_EX.get(k, {}).get("docs", []),
                              "example": _TPL_EX.get(k, {}).get("example", ""),
                              "example_pdf": _TPL_PDF.get(k, ""),
                              "example_pdfs": _example_pdfs(k)} for k, v in TEMPLATES.items()])
    os.makedirs(HERE, exist_ok=True)
    for key, val in corpus.items():
        json.dump(val, open(os.path.join(HERE, f"{key}.json"), "w"), indent=2)
    # docs/data.js
    docs = os.path.join(ROOT, "docs")
    os.makedirs(docs, exist_ok=True)
    with open(os.path.join(docs, "data.js"), "w") as f:
        f.write("window.MEDREG = " + json.dumps(corpus, separators=(",", ":")) + ";")
    print("wrote", sum(len(v) for v in corpus.values()), "records across", len(corpus), "collections")
    for k, v in corpus.items():
        print(f"  {k}: {len(v)}")

if __name__ == "__main__":
    main()
