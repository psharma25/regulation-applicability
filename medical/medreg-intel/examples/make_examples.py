"""Generate polished example PDFs ("what good looks like") for MedReg Intel templates.

These are ILLUSTRATIVE RECONSTRUCTIONS that follow FDA's recommended structure and are
grounded in REAL cleared devices using only PUBLIC facts (FDA decision summaries / press /
device security pages). The full confidential cybersecurity packages from actual submissions
are not public, so no proprietary submission text is reproduced.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable, ListFlowable, ListItem)

OUT = os.path.dirname(os.path.abspath(__file__))

# ---- palette (matches the app) ----
INK = colors.HexColor("#33384A"); MUTED = colors.HexColor("#566377"); FAINT = colors.HexColor("#8A97AC")
PERI = colors.HexColor("#A9B8F0"); MINT = colors.HexColor("#8FD4C1"); SKY = colors.HexColor("#A8D8EC")
BLUSH = colors.HexColor("#F2AEBE"); SAGE = colors.HexColor("#B6D4A8"); LINE = colors.HexColor("#E1E7F0")
PERIBG = colors.HexColor("#EEF1FD"); MINTBG = colors.HexColor("#E7F7F2"); BUTTERBG = colors.HexColor("#FBF4DE")

S = getSampleStyleSheet()
def style(name, **kw):
    base = kw.pop("parent", S["Normal"]); return ParagraphStyle(name, parent=base, **kw)
H_TITLE = style("t", fontName="Times-Bold", fontSize=22, leading=26, textColor=INK, spaceAfter=2)
H_SUB = style("s", fontName="Helvetica", fontSize=10.5, leading=14, textColor=MUTED, spaceAfter=2)
H1 = style("h1", fontName="Times-Bold", fontSize=14, leading=18, textColor=INK, spaceBefore=14, spaceAfter=4)
H2 = style("h2", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=colors.HexColor("#3f7e9e"), spaceBefore=8, spaceAfter=2)
BODY = style("b", fontName="Helvetica", fontSize=10, leading=14.5, textColor=INK, spaceAfter=5)
SMALL = style("sm", fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=MUTED)
BULLET = style("bul", parent=BODY, leftIndent=6, spaceAfter=2)
MONO = style("mono", fontName="Courier", fontSize=8.5, leading=11.5, textColor=INK)
CELL = style("cell", fontName="Helvetica", fontSize=8.5, leading=11, textColor=INK)
CELLH = style("cellh", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=colors.white)


def banner(text, fill):
    t = Table([[Paragraph(text, style("ban", fontName="Helvetica-Bold", fontSize=8.5, textColor=INK))]], colWidths=[6.9 * inch])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), fill), ("LEFTPADDING", (0, 0), (-1, -1), 9),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                           ("ROUNDEDCORNERS", [4, 4, 4, 4])]))
    return t


def rule(color=PERI):
    return HRFlowable(width="100%", thickness=2.5, color=color, spaceBefore=2, spaceAfter=8, lineCap="round")


def bullets(items):
    return ListFlowable([ListItem(Paragraph(i, BULLET), leftIndent=12, value="•") for i in items],
                        bulletType="bullet", start="•", leftIndent=10)


def kvtable(rows):
    data = [[Paragraph(f"<b>{k}</b>", CELL), Paragraph(v, CELL)] for k, v in rows]
    t = Table(data, colWidths=[1.7 * inch, 5.2 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -2), 0.5, LINE),
                           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    return t


def gridtable(header, rows, widths, header_fill=SKY):
    data = [[Paragraph(h, CELLH) for h in header]] + [[Paragraph(c, CELL) for c in r] for r in rows]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5f7e9e")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F9FC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]))
    return t


def make(filename, title, device, basis, accent, body_builder, sources):
    path = os.path.join(OUT, filename)
    doc = SimpleDocTemplate(path, pagesize=letter, topMargin=0.7 * inch, bottomMargin=0.8 * inch,
                            leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                            title=title, author="MedReg Intel")

    def footer(canvas, d):
        canvas.saveState()
        canvas.setStrokeColor(LINE); canvas.setLineWidth(0.5)
        canvas.line(0.8 * inch, 0.62 * inch, 7.7 * inch, 0.62 * inch)
        canvas.setFont("Helvetica", 7); canvas.setFillColor(FAINT)
        canvas.drawString(0.8 * inch, 0.46 * inch,
                          "Illustrative reconstruction — follows FDA guidance structure; device facts from public sources. Not an actual confidential submission.")
        canvas.drawRightString(7.7 * inch, 0.46 * inch, "MedReg Intel  ·  page %d" % d.page)
        canvas.restoreState()

    story = []
    story.append(banner("EXAMPLE — what good looks like  ·  illustrative reconstruction, grounded in a real cleared device", accent))
    story.append(Spacer(1, 12))
    story.append(Paragraph(title, H_TITLE))
    story.append(rule(accent))
    story.append(Paragraph(f"<b>Grounded in:</b> {device}", H_SUB))
    story.append(Paragraph(f"<b>Basis:</b> {basis}", H_SUB))
    story.append(Spacer(1, 8))
    body_builder(story)
    story.append(Spacer(1, 14))
    story.append(rule(LINE))
    story.append(Paragraph("Sources (public)", H2))
    story.append(bullets(sources))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("wrote", filename)


# ============================ 1. Cybersecurity Management Plan (BD Alaris) ============================
def csmp(story):
    story.append(kvtable([
        ("Manufacturer", "Becton, Dickinson and Company (BD)"),
        ("Device", "BD Alaris&#8482; Infusion System (Point-of-Care Unit + pump/syringe/PCA modules)"),
        ("Pathway / status", "510(k) — cleared July 21, 2023 (updated software with enhanced cybersecurity + EMR interoperability)"),
        ("Cyber device?", "Yes — Wi-Fi connectivity + EMR interoperability; multi-module connected platform"),
        ("Regulatory basis", "FD&amp;C Act &#167;524B; FDA Premarket Cybersecurity Guidance (2025); AAMI SW96; ISO 14971; IEC 81001-5-1"),
    ]))
    story.append(Paragraph("1. Scope &amp; system context", H1))
    story.append(Paragraph("A connected acute-care infusion platform: the Point-of-Care Unit (PCU) coordinates infusion modules and exchanges programming with hospital EMRs over the facility network. Related systems include the server-side device manager, the EMR interoperability interface, and the maintenance/update channel.", BODY))
    story.append(Paragraph("2. Governance &amp; SPDF", H1))
    story.append(Paragraph("Product Security Owner / PSIRT accountable for the total product lifecycle. Security activities are executed inside a Secure Product Development Framework integrated with the QMS (design controls).", BODY))
    story.append(Paragraph("3. Security risk management", H1))
    story.append(Paragraph("Security risk file maintained per AAMI SW96 and integrated with the ISO 14971 safety risk file. Threats scored on exploitability and patient-harm; residual risks formally accepted by Security and Quality.", BODY))
    story.append(Paragraph("4. Architecture views", H1))
    story.append(bullets(["Global system view — PCU, modules, EMR interface, device manager, update channel.",
                           "Multi-patient harm view — a unit/server compromise must not enable fleet-wide dosing changes.",
                           "Updateability/patchability view — signed software distribution to the installed base.",
                           "Security use-case views — clinician auth, EMR auto-programming, remote service."]))
    story.append(Paragraph("5. Software Bill of Materials (SBOM)", H1))
    story.append(Paragraph("Machine- and human-readable SBOM (CycloneDX) covering OS, networking, and crypto components, with support/EOL and a known-vulnerability list; maintained through postmarket.", BODY))
    story.append(Paragraph("6. Security controls (8 categories)", H1))
    story.append(gridtable(["Category", "Representative control"], [
        ["Authentication", "Authenticated access to PCU configuration and service interfaces"],
        ["Authorization", "Role-based access; least privilege for service accounts"],
        ["Cryptography", "Encrypted EMR/data-in-transit; protected credentials at rest"],
        ["Code &amp; data integrity", "Signed software/firmware; integrity checks on update"],
        ["Confidentiality", "Protection of PHI exchanged with the EMR"],
        ["Event detection / logging", "Security-relevant audit logging available to the facility"],
        ["Resiliency / recovery", "Safe-state behavior; recovery from network loss"],
        ["Firmware / software updates", "Controlled, signed distribution to the installed base"],
    ], [1.7 * inch, 5.2 * inch]))
    story.append(Paragraph("7. Verification &amp; validation (testing)", H1))
    story.append(bullets(["Static analysis (SAST) and software-composition analysis (SCA) in CI.",
                           "Dynamic analysis (DAST) of network/EMR interfaces.",
                           "Independent penetration test with findings closed or risk-accepted.",
                           "Coverage rationale traced to the threat model."]))
    story.append(Paragraph("8. Postmarket &amp; coordinated disclosure", H1))
    story.append(Paragraph("Continuous SBOM-to-CVE and CISA KEV monitoring; published CVD policy; severity-based patch timelines; field correction/removal assessed under 21 CFR 806 and MDR under 803.", BODY))
    story.append(Paragraph("9. Labeling", H1))
    story.append(Paragraph("Security labeling (MDS2) and a hardening/secure-configuration guide describing supported network configurations and operational controls for the deploying facility.", BODY))


# ============================ 2. Security Risk Assessment (BD Alaris) ============================
def sra(story):
    story.append(kvtable([
        ("Device", "BD Alaris&#8482; Infusion System"),
        ("Method", "AAMI SW96 / ISO 14971-aligned security risk assessment (STRIDE threats)"),
        ("Note", "Illustrative rows showing the expected structure and reasoning, not BD's confidential file."),
    ]))
    story.append(Paragraph("Security risk register (excerpt)", H1))
    story.append(gridtable(["ID", "Asset", "Threat (STRIDE)", "Exploit.", "Patient harm", "Control", "Residual"], [
        ["S-01", "EMR interface", "Spoofing", "Med", "Med — wrong auto-program", "Mutual auth, validated orders", "Low (accepted)"],
        ["S-02", "Software update", "Tampering", "Low", "High — malicious image", "Code signing, integrity check", "Low"],
        ["S-03", "Service iface", "Elevation", "Med", "Med", "RBAC, least privilege", "Low"],
        ["S-04", "PHI in transit", "Info disclosure", "Med", "Low", "TLS, key management", "Low"],
        ["S-05", "Network", "Denial of service", "Med", "Med — delayed therapy", "Safe-state, local fallback", "Low (accepted)"],
    ], [0.5 * inch, 1.0 * inch, 1.15 * inch, 0.6 * inch, 1.35 * inch, 1.3 * inch, 1.0 * inch]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Risk acceptance", H2))
    story.append(Paragraph("Residual risks S-01 and S-05 accepted with compensating controls (network segmentation, facility monitoring) and reflected in labeling. Acceptance signed by Security and Quality with rationale recorded in the risk file.", BODY))
    story.append(Paragraph("If a control cannot be implemented", H2))
    story.append(Paragraph("Document a risk-based justification: why the control is infeasible, the compensating controls, the residual risk and its formal acceptance, and the user-facing labeling that describes the limitation — consistent with FDA's premarket cybersecurity guidance.", BODY))


# ============================ 3. Premarket Cybersecurity Checklist (BD Alaris) ============================
def checklist(story):
    story.append(kvtable([
        ("Device", "BD Alaris&#8482; Infusion System (connected Class II)"),
        ("Use", "Pre-submission acceptance gate — every item linked to an artifact in the eSTAR."),
    ]))
    story.append(Paragraph("Acceptance checklist (all satisfied)", H1))
    story.append(gridtable(["Item (&#167;524B / 2025 guidance)", "Artifact reference"], [
        ["Cyber-device determination &amp; rationale", "CSMP &#167;1 (Wi-Fi + EMR interoperability)"],
        ["Security risk management plan + file", "SRM report (SW96/14971)"],
        ["Threat model + data-flow diagrams", "Threat model (STRIDE)"],
        ["Security architecture views (4)", "Architecture package"],
        ["Security controls matrix (8 categories)", "Controls matrix"],
        ["SBOM (machine + human readable) + known vulns", "CycloneDX SBOM + vuln list"],
        ["Cybersecurity testing (SAST/DAST/SCA/fuzz/pen)", "Test reports + coverage rationale"],
        ["Postmarket vulnerability management + CVD plan", "Postmarket + CVD plan"],
        ["Security labeling / MDS2 / hardening guide", "Labeling + MDS2"],
        ["Interoperability + misconnection risk analysis", "Interoperability analysis"],
    ], [3.6 * inch, 3.3 * inch], header_fill=MINT))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Why this matters", H2))
    story.append(Paragraph("Since October 1, 2023, FDA refuses to accept (RTA) cyber-device submissions missing &#167;524B content. Each unchecked box above is a likely RTA; attaching the named artifact next to each item is what an excellent submission does.", BODY))


# ============================ 4. PCCP for AI (IDx-DR / LumineticsCore) ============================
def pccp(story):
    story.append(kvtable([
        ("Manufacturer", "Digital Diagnostics (formerly IDx)"),
        ("Device", "LumineticsCore&#8482; (formerly IDx-DR) — autonomous AI for diabetic retinopathy"),
        ("Pathway / status", "De Novo DEN180001 (2018) — first FDA-authorized autonomous diagnostic AI; later 510(k) on its own predicate (2021)"),
        ("AI structure", "Two algorithms: an image-quality AI and the diagnostic AI; outputs an autonomous mtmDR result"),
        ("Public performance", "Pivotal trial (900 patients); FDA performance thresholds 85% sensitivity / 82.5% specificity"),
        ("Basis", "PCCP per FDA final guidance (2024). Illustrative — shows how a PCCP could be structured for this device class."),
    ]))
    story.append(Paragraph("1. Description of modifications", H1))
    story.append(bullets(["Periodic re-training of the diagnostic algorithm on additional labeled fundus images (intended use unchanged).",
                           "Bounded re-tuning of the operating threshold within pre-specified limits.",
                           "Support for additional compatible fundus cameras after equivalence testing."]))
    story.append(Paragraph("2. Modification protocol", H1))
    story.append(Paragraph("<b>Data management.</b> Minimum dataset size and demographic representativeness defined; an independent, frozen test set with no leakage from training.", BODY))
    story.append(Paragraph("<b>Re-training &amp; evaluation.</b> Acceptance gates pre-specified — e.g., maintain sensitivity/specificity at or above the cleared thresholds (85% / 82.5%) overall and per pre-defined subgroup; no degradation on the locked test set.", BODY))
    story.append(Paragraph("<b>Release &amp; rollback.</b> Versioned release with documented validation and a rollback path.", BODY))
    story.append(Paragraph("3. Impact assessment", H1))
    story.append(gridtable(["Modification", "Risk", "Control / verification"], [
        ["Re-training", "Subgroup performance drift", "Locked acceptance gates + subgroup analysis on frozen test set"],
        ["Threshold re-tuning", "Sensitivity loss", "Bounded change; re-validate against thresholds"],
        ["New camera", "Image-domain shift", "Equivalence testing before enablement"],
    ], [1.7 * inch, 1.9 * inch, 3.3 * inch], header_fill=colors.HexColor("#C6B4E6")))
    story.append(Paragraph("4. Transparency", H1))
    story.append(Paragraph("Each release within the PCCP adds a version note to labeling (date, data summary, performance delta). Changes beyond this authorized envelope require a new marketing submission.", BODY))


SBOM_JSON = """{
  "bomFormat": "CycloneDX", "specVersion": "1.5",
  "metadata": {
    "component": { "type": "application", "name": "alaris-pcu-fw", "version": "<cleared-version>" },
    "supplier": { "name": "Becton, Dickinson and Company" }
  },
  "components": [
    { "type": "library", "name": "openssl", "version": "3.0.x",
      "licenses": [{ "license": { "id": "Apache-2.0" } }],
      "properties": [{ "name": "support:level", "value": "supported" }] },
    { "type": "library", "name": "network-stack", "version": "x.y" },
    { "type": "operating-system", "name": "rtos", "version": "x.y" }
  ],
  "vulnerabilities": []
}"""


def sbom(story):
    story.append(kvtable([
        ("Device", "BD Alaris&#8482; Infusion System (PCU software)"),
        ("Format", "CycloneDX 1.5 — machine + human readable; generated in CI"),
        ("Note", "Skeleton showing the expected structure/fields; component versions illustrative."),
    ]))
    story.append(Paragraph("SBOM structure (CycloneDX)", H1))
    for line in SBOM_JSON.split("\n"):
        story.append(Paragraph(line.replace(" ", "&nbsp;") or "&nbsp;", MONO))
    story.append(Spacer(1, 8))
    story.append(Paragraph("What an excellent SBOM adds", H2))
    story.append(bullets(["Supplier, license, version for every component (commercial, OSS, off-the-shelf).",
                           "Support level and end-of-support date per component.",
                           "A linked known-vulnerability list and a justification for any missing element.",
                           "Continuous regeneration so the SBOM stays current through postmarket."]))


ALARIS_SRC = [
    "FDA / BD — &ldquo;BD Receives FDA 510(k) Clearance for Updated BD Alaris Infusion System&rdquo; (Jul 21, 2023).",
    "FDA — Cybersecurity in Medical Devices: QMS Considerations and Content of Premarket Submissions (final, Jun 27, 2025).",
    "AAMI SW96; ISO 14971; IEC 81001-5-1.",
]
IDX_SRC = [
    "FDA De Novo DEN180001 (IDx-DR), 2018; Digital Diagnostics (LumineticsCore) public materials.",
    "Abr&agrave;moff et al., npj Digital Medicine (2018) — pivotal trial; thresholds 85% sensitivity / 82.5% specificity.",
    "FDA — Marketing Submission Recommendations for a PCCP for AI-Enabled Device Software Functions (final, 2024).",
]

make("cybersecurity-management-plan-example.pdf", "Cybersecurity Management Plan", "BD Alaris&#8482; Infusion System (cleared 510(k), 2023)",
     "FDA 2025 premarket cybersecurity guidance structure; device facts public.", PERIBG, csmp, ALARIS_SRC)
make("security-risk-assessment-example.pdf", "Security Risk Assessment", "BD Alaris&#8482; Infusion System",
     "AAMI SW96 / ISO 14971 structure; illustrative register.", PERIBG, sra, ALARIS_SRC)
make("premarket-cyber-checklist-example.pdf", "Premarket Cybersecurity Documentation Checklist", "BD Alaris&#8482; Infusion System",
     "FDA &#167;524B acceptance criteria.", MINTBG, checklist, ALARIS_SRC)
make("pccp-ai-example.pdf", "Predetermined Change Control Plan (AI)", "LumineticsCore&#8482; / IDx-DR (De Novo DEN180001, 2018)",
     "FDA PCCP final guidance (2024); device facts public.", colors.HexColor("#F3EEFA"), pccp, IDX_SRC)
make("sbom-cyclonedx-example.pdf", "Software Bill of Materials (CycloneDX)", "BD Alaris&#8482; Infusion System",
     "CycloneDX 1.5; NTIA minimum elements.", PERIBG, sbom, ALARIS_SRC)

print("done")


# ============================ NON-BD examples (Dexcom / Viz.ai / Medtronic) ============================
DEXCOM_SRC = [
    "FDA / Dexcom — Dexcom G7 510(k) clearance (Dec 2022); G6 first interoperable iCGM (2018, special controls).",
    "Public connectivity facts: Bluetooth Low Energy to the G7 app (iOS/Android) and Apple Watch; Dexcom Clarity cloud.",
    "FDA — Cybersecurity in Medical Devices premarket guidance (2025); OWASP MASVS for mobile.",
]
VIZ_SRC = [
    "FDA — De Novo for Viz.AI Contact (first computer-aided triage & notification software), 2018.",
    "FDA / Viz.ai public materials; analyzes CTA and alerts the stroke team via mobile.",
    "FDA-MHRA-Health Canada — Good Machine Learning Practice (10 principles), 2021.",
]
MDT_SRC = [
    "Medtronic — publicly documented Product Security / coordinated vulnerability disclosure (PSIRT) program.",
    "FDA — Postmarket Management of Cybersecurity in Medical Devices (2016); §524B(b)(1).",
    "AAMI TIR97 (postmarket security); CISA ICS medical advisory coordination.",
]

def threat_model(story):
    story.append(kvtable([
        ("Device", "Dexcom G7 — integrated CGM (iCGM)"),
        ("Connectivity", "Bluetooth Low Energy &rarr; G7 app (iOS/Android) &amp; Apple Watch; Dexcom Clarity cloud + share"),
        ("Method", "STRIDE over sensor, mobile app, BLE link, cloud, followers"),
        ("Note", "Illustrative — shows expected structure for a connected mobile SaMD; not Dexcom's confidential file."),
    ]))
    story.append(Paragraph("1. Decomposition &amp; trust boundaries", H1))
    story.append(bullets(["Entities: sensor/transmitter, mobile app, BLE link, Dexcom cloud, follower/share, Apple Watch.",
                           "Trust boundaries: sensor&harr;phone (BLE), phone&harr;cloud (TLS), cloud&harr;followers."]))
    story.append(Paragraph("2. Threats &amp; mitigations (STRIDE)", H1))
    story.append(gridtable(["Threat", "Example", "Mitigation", "V&amp;V"], [
        ["Spoofing", "Rogue BLE peer", "Bonded pairing, session keys", "BLE security tests"],
        ["Tampering", "Altered readings/alerts", "Integrity checks, range validation", "Fuzz + unit tests"],
        ["Info disclosure", "Glucose/PHI exposure", "TLS 1.2+, Keychain/Keystore", "MobSF, capture"],
        ["DoS", "Alert suppression", "On-device alerting independent of cloud", "Fault injection"],
        ["Elevation", "Cloud/API abuse", "Least-privilege IAM, scoped tokens", "IAM review"],
    ], [1.0 * inch, 1.7 * inch, 2.5 * inch, 1.7 * inch], header_fill=SKY))
    story.append(Spacer(1, 8))
    story.append(Paragraph("3. Residual risk", H2))
    story.append(Paragraph("RF jamming of the BLE link accepted; mitigated by on-device alerting and gap handling, disclosed in labeling.", BODY))

def cvd(story):
    story.append(kvtable([
        ("Basis", "Modeled on Medtronic's publicly documented coordinated-disclosure / product-security program"),
        ("Regulatory", "&#167;524B(b)(1); FDA Postmarket Cybersecurity guidance; AAMI TIR97"),
        ("Note", "Illustrative structure; not Medtronic's verbatim policy."),
    ]))
    story.append(Paragraph("1. Scope &amp; contact", H1))
    story.append(Paragraph("Marketed products and connected services. Public security page with a reporting form and a published PGP key; security@ intake.", BODY))
    story.append(Paragraph("2. Reporting &amp; safe harbor", H1))
    story.append(Paragraph("Good-faith research welcomed; acknowledgment within a stated window; no legal action for testing within the policy.", BODY))
    story.append(Paragraph("3. Coordination &amp; CVEs", H1))
    story.append(bullets(["Triage and validate reports; assign/track CVEs (CNA or via a CNA).",
                           "Coordinate with CISA / ICS-CERT; publish security bulletins/advisories.",
                           "Credit researchers per coordinated-disclosure norms."]))
    story.append(Paragraph("4. Timelines &amp; remediation", H1))
    story.append(gridtable(["Severity", "Target remediation", "Interim"], [
        ["Critical", "Expedited (e.g., &le; 30 days)", "Compensating controls / advisory"],
        ["High", "Defined window", "Mitigation guidance"],
        ["Medium/Low", "Scheduled release", "Tracked to closure"],
    ], [1.4 * inch, 2.6 * inch, 2.9 * inch], header_fill=MINT))
    story.append(Spacer(1, 8))
    story.append(Paragraph("5. Regulator reporting", H2))
    story.append(Paragraph("Assess 21 CFR 806 correction/removal and 803 MDR triggers; align to FDA postmarket cybersecurity guidance.", BODY))

def postmarket(story):
    story.append(kvtable([
        ("Basis", "Modeled on a large connected-device maker's PSIRT practice (e.g., Medtronic)"),
        ("Regulatory", "&#167;524B(b)(1); FDA Postmarket Cybersecurity guidance (2016)"),
    ]))
    story.append(Paragraph("1. Monitoring", H1))
    story.append(bullets(["SBOM&rarr;CVE matching (daily), CISA KEV, vendor PSIRT feeds, researcher reports via CVD intake."]))
    story.append(Paragraph("2. Assessment", H1))
    story.append(Paragraph("Score exploitability &times; patient-harm; classify controlled vs uncontrolled risk per FDA postmarket guidance (CVSS + clinical impact).", BODY))
    story.append(Paragraph("3. Remediation &amp; notification", H1))
    story.append(Paragraph("Severity-based patch SLAs; signed OTA / staged deployment with rollback; customer security bulletins; &le; 30-day notification for uncontrolled risk.", BODY))
    story.append(Paragraph("4. Reporting &amp; metrics", H1))
    story.append(gridtable(["Metric", "Example target"], [
        ["Mean time to remediate (critical)", "&le; 30 days"],
        ["% fleet on supported version", "&ge; 95%"],
        ["Open critical vulnerabilities", "0"],
    ], [3.5 * inch, 3.4 * inch], header_fill=PERI))

def k510(story):
    story.append(kvtable([
        ("Device", "Dexcom G7 — connected mobile iCGM"),
        ("Cyber device?", "Yes — BLE + mobile app (iOS/Android) + cloud (Clarity/share)"),
        ("Note", "Illustrative summary of an eSTAR cybersecurity section; not Dexcom's confidential content."),
    ]))
    story.append(Paragraph("Cybersecurity section (summary)", H1))
    story.append(gridtable(["#", "Element", "Evidence"], [
        ["1", "Cyber device determination", "BLE + app + cloud connectivity"],
        ["2", "Security risk management", "SRM file (SW96/14971)"],
        ["3", "Threat model", "STRIDE across sensor/phone/cloud"],
        ["4", "Architecture views", "Global, multi-patient (cloud), updateability, use-case"],
        ["5", "Controls (8 categories)", "BLE bonding, TLS, secure storage, signed updates, logging"],
        ["6", "SBOM", "CycloneDX incl. mobile + embedded; 0 critical CVEs"],
        ["7", "Testing", "SAST/DAST/SCA, BLE fuzzing, MobSF/MASVS, pen test"],
        ["8", "Postmarket + CVD", "Monitoring + disclosure policy"],
        ["9", "Labeling", "Security labeling + secure-setup guidance"],
    ], [0.4 * inch, 2.5 * inch, 4.0 * inch], header_fill=SKY))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Conclusion", H2))
    story.append(Paragraph("Reasonable assurance of cybersecurity for a connected CGM with a mobile app and cloud ecosystem.", BODY))

def gmlp(story):
    story.append(kvtable([
        ("Device", "Viz.ai LVO (Viz.AI Contact) — computer-aided triage AI for stroke"),
        ("Status", "De Novo (2018) — first FDA-authorized computer-aided triage &amp; notification software; analyzes CTA, alerts the stroke team"),
        ("Basis", "FDA/MHRA/Health Canada GMLP (10 principles). Illustrative evidence mapping."),
    ]))
    story.append(Paragraph("GMLP principles — satisfied with evidence", H1))
    story.append(gridtable(["#", "GMLP principle", "Evidence"], [
        ["1", "Multidisciplinary expertise", "Clinical neuro + ML + security across lifecycle"],
        ["2", "Good SW &amp; security engineering", "SDLC + threat model; HIPAA-compliant comms"],
        ["3", "Representative data", "Multi-site CTA across scanners/demographics"],
        ["4", "Independent train/test", "Frozen test set, no leakage"],
        ["5", "Reference standard", "Neuroradiologist adjudication of LVO"],
        ["6", "Model tailored to use", "LVO detection on CTA"],
        ["7", "Human-AI team", "Notification augments the specialist read"],
        ["8", "Clinically relevant testing", "Time-to-notification + detection performance"],
        ["9", "Clear user info", "Intended use, performance, limitations"],
        ["10", "Deployed monitoring", "Real-world performance + drift monitoring"],
    ], [0.4 * inch, 2.6 * inch, 3.9 * inch], header_fill=colors.HexColor("#C6B4E6")))

def presub(story):
    story.append(kvtable([
        ("Device", "Connected CGM (modeled on a Dexcom-class iCGM)"),
        ("Type", "Pre-Submission (Q-Sub)"),
        ("Note", "Illustrative — frames the questions an excellent Pre-Sub asks for a connected mobile SaMD."),
    ]))
    story.append(Paragraph("1. Questions for FDA", H1))
    story.append(bullets(["Is the cybersecurity test scope (SAST/DAST/SCA, BLE fuzzing, mobile MASVS, pen test) adequate for a connected CGM + mobile app?",
                           "Are the proposed security architecture views sufficient given the cloud + follower-share ecosystem?",
                           "Is OWASP MASVS-based evidence acceptable to support the mobile controls?"]))
    story.append(Paragraph("2. Device &amp; context", H1))
    story.append(Paragraph("Integrated CGM (iCGM) with BLE to iOS/Android apps and cloud; interoperable with automated insulin delivery systems.", BODY))
    story.append(Paragraph("3. Proposed strategy", H1))
    story.append(bullets(["SW96 security risk management; CycloneDX SBOM; published CVD policy.",
                           "Independent penetration test by an accredited lab before submission."]))

make("threat-model-example.pdf", "Threat Model", "Dexcom G7 — connected mobile iCGM (cleared 2022)",
     "STRIDE; FDA 2025 guidance structure; device facts public.", SKY, threat_model, DEXCOM_SRC)
make("vulnerability-disclosure-policy-example.pdf", "Coordinated Vulnerability Disclosure Policy", "Modeled on Medtronic's public product-security program",
     "§524B(b)(1); FDA postmarket guidance; AAMI TIR97.", MINTBG, cvd, MDT_SRC)
make("postmarket-cyber-plan-example.pdf", "Postmarket Cybersecurity Plan", "Modeled on a large connected-device maker (e.g., Medtronic)",
     "FDA Postmarket Cybersecurity guidance.", PERIBG, postmarket, MDT_SRC)
make("510k-cyber-section-example.pdf", "510(k) Cybersecurity Section", "Dexcom G7 — connected mobile iCGM",
     "eSTAR cybersecurity section; device facts public.", SKY, k510, DEXCOM_SRC)
make("gmlp-checklist-example.pdf", "GMLP Checklist (10 principles)", "Viz.ai LVO (De Novo 2018) — computer-aided triage AI",
     "FDA/MHRA/HC GMLP; device facts public.", colors.HexColor("#F3EEFA"), gmlp, VIZ_SRC)
make("presub-request-example.pdf", "Pre-Submission (Q-Sub) Request", "Connected CGM (Dexcom-class iCGM)",
     "FDA Q-Submission program.", MINTBG, presub, DEXCOM_SRC)
print("non-BD examples done")


# ============================ additional exemplars: architecture views, model card, pentest ============================
def archviews(story):
    story.append(kvtable([("Device", "BD Alaris&#8482; Infusion System"),
        ("Basis", "FDA Premarket Cybersecurity Guidance (2025) §V.A.3 — four architecture views"),
        ("Note", "Illustrative reconstruction; not BD's confidential file.")]))
    story.append(Paragraph("1. Global system view", H1))
    story.append(Paragraph("PCU + pump/syringe/PCA/respiratory modules &harr; facility network &harr; EMR interface &harr; device manager &harr; signed update service, with trust boundaries at each hop.", BODY))
    story.append(Paragraph("2. Multi-patient harm view", H1))
    story.append(Paragraph("A compromised server / EMR interface must not push unsafe programs fleet-wide. Controls: signed/validated orders, server hardening, network segmentation, rate/range limits.", BODY))
    story.append(Paragraph("3. Updateability / patchability view", H1))
    story.append(Paragraph("Signed software distributed to the installed base; integrity verified on receipt; anti-rollback; staged rollout with monitoring.", BODY))
    story.append(Paragraph("4. Security use-case views", H1))
    story.append(gridtable(["Use case", "Key controls"], [
        ["Clinician auth → program infusion", "Authentication, authorization, audit log"],
        ["EMR auto-program", "Mutual auth, order validation, range limits"],
        ["Remote service", "Authenticated, least-privilege, logged"],
        ["Software update", "Signed image, integrity check, anti-rollback"],
    ], [2.4 * inch, 4.5 * inch], header_fill=PERI))

def modelcard(story):
    story.append(kvtable([("Device", "LumineticsCore&#8482; / IDx-DR — autonomous diabetic retinopathy AI"),
        ("Status", "De Novo DEN180001 (2018); Class II; two algorithms (image-quality + diagnostic)"),
        ("Basis", "FDA AI transparency principles; GMLP; EU AI Act. Illustrative.")]))
    story.append(Paragraph("Intended use & users", H1))
    story.append(Paragraph("Autonomous detection of more-than-mild diabetic retinopathy (mtmDR) in adults with diabetes, in primary care, without a clinician interpreting the image.", BODY))
    story.append(Paragraph("Inputs / outputs", H1))
    story.append(Paragraph("Fundus images from specified cameras &rarr; image-quality gate &rarr; mtmDR detected / not detected.", BODY))
    story.append(Paragraph("Performance (public pivotal trial)", H1))
    story.append(gridtable(["Metric", "Value"], [
        ["FDA performance threshold — sensitivity", "85%"],
        ["FDA performance threshold — specificity", "82.5%"],
        ["Pivotal study", "900 patients, primary-care sites, independent reference standard"],
    ], [3.0 * inch, 3.9 * inch], header_fill=colors.HexColor("#C6B4E6")))
    story.append(Paragraph("Limitations", H1))
    story.append(bullets(["Not for patients previously diagnosed with DR.", "Image-quality dependent (built-in gate).", "Specified cameras only."]))
    story.append(Paragraph("Monitoring & change control", H1))
    story.append(Paragraph("Real-world performance monitoring; retraining governed by a Predetermined Change Control Plan.", BODY))

def pentest(story):
    story.append(kvtable([("Device", "Dexcom-class connected CGM (illustrative)"),
        ("Tester / scope", "Independent accredited lab — sensor/BLE, mobile app (iOS/Android), cloud APIs"),
        ("Basis", "Threat-model-driven; OWASP MASVS/MASTG + API + BLE testing.")]))
    story.append(Paragraph("Findings", H1))
    story.append(gridtable(["ID", "Severity", "Finding", "Status"], [
        ["P-1", "Medium", "Verbose API error leakage", "Closed"],
        ["P-2", "Low", "Missing cert-pinning on one endpoint", "Closed"],
        ["P-3", "Info", "Logging hygiene", "Risk-accepted"],
    ], [0.6 * inch, 1.0 * inch, 3.6 * inch, 1.7 * inch], header_fill=SKY))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Coverage & conclusion", H2))
    story.append(Paragraph("BLE, mobile storage/transport, API authorization, and cloud IAM mapped to the threat model. No high/critical open findings; residual risk acceptable; retest evidence attached.", BODY))

make("architecture-views-example.pdf", "Security Architecture Views", "BD Alaris&#8482; Infusion System",
     "FDA 2025 guidance — four views.", PERIBG, archviews, ALARIS_SRC)
make("ai-model-card-example.pdf", "AI Model Card / Transparency", "LumineticsCore&#8482; / IDx-DR (De Novo DEN180001)",
     "FDA AI transparency principles; GMLP.", colors.HexColor("#F3EEFA"), modelcard, IDX_SRC)
make("pentest-summary-example.pdf", "Penetration Test Summary", "Dexcom-class connected CGM (illustrative)",
     "Threat-model-driven; OWASP MASVS.", SKY, pentest, DEXCOM_SRC)
print("extra exemplars done")


# ============================ alternate-company exemplars (Abbott / Insulet) ============================
ABBOTT_SRC = [
    "Abbott — FreeStyle Libre 2 Plus / 3 Plus CGM; FDA-cleared for use with automated insulin delivery (Mar 2023).",
    "Public connectivity facts: Bluetooth to a mobile app; readings transmitted to phone; AID integration.",
    "FDA — Cybersecurity in Medical Devices premarket guidance (2025); OWASP MASVS.",
]
INSULET_SRC = [
    "Insulet — Omnipod 5, first FDA-cleared tubeless automated insulin delivery (AID) patch pump; smartphone-controlled.",
    "Public facts: integrated dosing algorithm adjusts insulin every 5 min using CGM input; 510(k) algorithm update (Dec 2025).",
    "FDA — Premarket Cybersecurity guidance (2025); PCCP final guidance (2024); GMLP.",
]

def csmp_abbott(story):
    story.append(kvtable([("Manufacturer", "Abbott"), ("Device", "FreeStyle Libre 3 Plus &mdash; connected CGM"),
        ("Connectivity", "Bluetooth &rarr; mobile app (iOS/Android); cleared for AID integration"),
        ("Basis", "FDA Premarket Cybersecurity guidance (2025); SW96; ISO 14971. Illustrative.")]))
    story.append(Paragraph("1. Scope & context", H1))
    story.append(Paragraph("Wearable CGM streaming readings over BLE to a mobile app and, when integrated, to an automated insulin delivery (AID) system. Related systems: mobile app, cloud, AID controller.", BODY))
    story.append(Paragraph("2. Security risk management", H1))
    story.append(Paragraph("SW96 + ISO 14971 security risk file; emphasis on integrity of glucose values feeding dosing decisions; residual risk accepted by Security + Quality.", BODY))
    story.append(Paragraph("3. Controls (8 categories)", H1))
    story.append(gridtable(["Category", "Representative control"], [
        ["Authentication", "Bonded BLE pairing to the app"],
        ["Integrity", "Validated/΅signed readings feeding AID"],
        ["Cryptography", "TLS to cloud; protected mobile storage"],
        ["Confidentiality", "PHI minimization in app + cloud"],
        ["Updates", "Signed app/sensor firmware updates"],
    ], [1.7 * inch, 5.2 * inch], header_fill=MINT))
    story.append(Paragraph("4. Postmarket & CVD", H1))
    story.append(Paragraph("SBOM&rarr;CVE monitoring; CVD policy; severity-based patch timelines; coordination with AID partners (e.g., pump makers).", BODY))

def threat_omnipod(story):
    story.append(kvtable([("Device", "Insulet Omnipod 5 &mdash; automated insulin delivery (AID) patch pump"),
        ("Connectivity", "Bluetooth to compatible smartphone / Controller; CGM input drives dosing every 5 min"),
        ("Method", "STRIDE over pod, CGM link, phone/controller, cloud"), ("Note", "Illustrative; safety-critical dosing.")]))
    story.append(Paragraph("Threats & mitigations (STRIDE)", H1))
    story.append(gridtable(["Threat", "Example", "Mitigation", "V&amp;V"], [
        ["Spoofing", "Rogue controller/CGM peer", "Bonded pairing, authenticated link", "BLE security tests"],
        ["Tampering", "Altered dose command / CGM value", "Signed commands, dose limits, value validation", "Fuzz + limit tests"],
        ["DoS", "Loss of CGM/controller link", "Safe fallback to basal; alerts", "Fault injection"],
        ["Elevation", "Cloud/app abuse", "Least-privilege, scoped tokens", "IAM review"],
    ], [1.0 * inch, 1.9 * inch, 2.4 * inch, 1.6 * inch], header_fill=SKY))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Residual risk", H2))
    story.append(Paragraph("Maximum-dose limits and safe-state basal bound worst-case harm if a link is degraded; disclosed in labeling.", BODY))

def pccp_omnipod(story):
    story.append(kvtable([("Device", "Insulet Omnipod 5 &mdash; AID dosing algorithm"),
        ("Status", "First FDA-cleared tubeless AID; algorithm enhancement 510(k) (Dec 2025)"),
        ("Basis", "FDA PCCP final guidance (2024). Illustrative — algorithm change control.")]))
    story.append(Paragraph("1. Description of modifications", H1))
    story.append(bullets(["Bounded changes to target-glucose options and control parameters (intended use unchanged).",
                           "Adding compatibility with additional cleared CGM sensors after equivalence testing."]))
    story.append(Paragraph("2. Modification protocol", H1))
    story.append(Paragraph("Pre-specified safety bounds (max dose, target ranges); in-silico + clinical validation; acceptance gates on time-in-range and safety (no increase in hypo events); versioned release with rollback.", BODY))
    story.append(Paragraph("3. Impact assessment", H1))
    story.append(gridtable(["Modification", "Risk", "Control / verification"], [
        ["Algorithm parameter change", "Hypo-/hyperglycemia", "Safety bounds + clinical acceptance gates"],
        ["New CGM compatibility", "Input domain shift", "Sensor equivalence testing before enablement"],
    ], [2.0 * inch, 2.0 * inch, 2.9 * inch], header_fill=colors.HexColor("#C6B4E6")))
    story.append(Paragraph("4. Transparency", H1))
    story.append(Paragraph("Labeling version notes per in-scope release; changes beyond the envelope require a new submission.", BODY))

def postmarket_abbott(story):
    story.append(kvtable([("Device", "Abbott FreeStyle Libre (connected CGM)"),
        ("Basis", "FDA Postmarket Cybersecurity guidance; &#167;524B(b)(1); AAMI TIR97. Illustrative.")]))
    story.append(Paragraph("1. Monitoring", H1))
    story.append(bullets(["SBOM&rarr;CVE matching, CISA KEV, mobile-platform advisories (iOS/Android), researcher reports via CVD."]))
    story.append(Paragraph("2. Assessment & remediation", H1))
    story.append(Paragraph("Exploitability &times; patient-harm scoring (glucose-value integrity prioritized); severity-based app/firmware update SLAs; staged rollout via app stores with rollback.", BODY))
    story.append(Paragraph("3. Reporting & metrics", H1))
    story.append(gridtable(["Metric", "Example target"], [
        ["Critical patch (app/firmware)", "&le; 30 days"],
        ["% users on supported app version", "&ge; 95%"],
        ["Open critical vulnerabilities", "0"],
    ], [3.5 * inch, 3.4 * inch], header_fill=PERI))

def sbom_omnipod(story):
    story.append(kvtable([("Device", "Insulet Omnipod 5 (controller/app + pod firmware)"),
        ("Format", "CycloneDX 1.5 — machine + human readable; generated in CI"), ("Note", "Illustrative structure.")]))
    story.append(Paragraph("SBOM structure (CycloneDX)", H1))
    for line in SBOM_JSON.replace("alaris-pcu-fw", "omnipod5-controller").replace("Becton, Dickinson and Company", "Insulet Corporation").split("\n"):
        story.append(Paragraph(line.replace(" ", "&nbsp;") or "&nbsp;", MONO))
    story.append(Spacer(1, 8))
    story.append(Paragraph("What an excellent SBOM adds", H2))
    story.append(bullets(["Mobile app + embedded pod components, each with supplier/license/version.",
                           "Support/EOL per component; linked known-vulnerability list; continuous regeneration."]))

make("csmp-abbott-example.pdf", "Cybersecurity Management Plan", "Abbott FreeStyle Libre 3 Plus (connected CGM)",
     "FDA 2025 guidance structure; device facts public.", MINTBG, csmp_abbott, ABBOTT_SRC)
make("threat-model-omnipod-example.pdf", "Threat Model", "Insulet Omnipod 5 (AID patch pump)",
     "STRIDE; device facts public.", SKY, threat_omnipod, INSULET_SRC)
make("pccp-omnipod-example.pdf", "Predetermined Change Control Plan (AID algorithm)", "Insulet Omnipod 5 (AID algorithm)",
     "FDA PCCP final guidance (2024).", colors.HexColor("#F3EEFA"), pccp_omnipod, INSULET_SRC)
make("postmarket-abbott-example.pdf", "Postmarket Cybersecurity Plan", "Abbott FreeStyle Libre (connected CGM)",
     "FDA Postmarket guidance; AAMI TIR97.", PERIBG, postmarket_abbott, ABBOTT_SRC)
make("sbom-omnipod-example.pdf", "Software Bill of Materials (CycloneDX)", "Insulet Omnipod 5 (AID patch pump)",
     "CycloneDX 1.5; NTIA minimum elements.", PERIBG, sbom_omnipod, INSULET_SRC)
print("alternate-company exemplars done")
