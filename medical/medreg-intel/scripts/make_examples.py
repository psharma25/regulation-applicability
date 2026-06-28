"""Generate polished 'what good looks like' PDF exemplars into docs/examples/.

Each document is an ILLUSTRATIVE EXEMPLAR modeled on (a) the FDA-expected structure
(§524B / 2025 premarket cybersecurity guidance, PCCP & GMLP guidance) and (b) the
PUBLIC record of a real, successfully cleared device. FDA does not release the
confidential cybersecurity content of cleared submissions, so the detailed content
here is a faithful reconstruction of structure and expectations, not a verbatim filing.
Grounding devices and public citations are stated in each document's provenance box.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, ListFlowable, ListItem, HRFlowable, KeepTogether)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "examples")
os.makedirs(OUT, exist_ok=True)

# palette (matches the app's pastel system, tuned for print)
INK = colors.HexColor("#2E3440"); MUTED = colors.HexColor("#566377"); FAINT = colors.HexColor("#8A97AC")
PERI = colors.HexColor("#A9B8F0"); PERI_BG = colors.HexColor("#EEF1FD")
MINT = colors.HexColor("#8FD4C1"); MINT_BG = colors.HexColor("#E7F7F2")
BLUSH = colors.HexColor("#F2AEBE"); BUTTER_BG = colors.HexColor("#FBF4DE")
LINE = colors.HexColor("#DCE4EF")

S = getSampleStyleSheet()
def style(name, **kw):
    base = kw.pop("parent", S["Normal"]); return ParagraphStyle(name, parent=base, **kw)
H1 = style("H1", fontName="Times-Bold", fontSize=14, textColor=INK, spaceBefore=14, spaceAfter=5, leading=17)
H2 = style("H2", fontName="Helvetica-Bold", fontSize=10.5, textColor=colors.HexColor("#4a5aa8"), spaceBefore=10, spaceAfter=3)
BODY = style("BODY", fontName="Helvetica", fontSize=9.5, textColor=INK, leading=13.5, spaceAfter=4, alignment=TA_LEFT)
SMALL = style("SMALL", fontName="Helvetica", fontSize=8, textColor=MUTED, leading=11)
TITLE = style("TITLE", fontName="Times-Bold", fontSize=22, textColor=INK, leading=25)
SUB = style("SUB", fontName="Helvetica", fontSize=10.5, textColor=MUTED, leading=14)
CELL = style("CELL", fontName="Helvetica", fontSize=8.3, textColor=INK, leading=11)
CELLH = style("CELLH", fontName="Helvetica-Bold", fontSize=8.3, textColor=INK, leading=11)

DOC_META = {"title": "MedReg Intel — Exemplar", "device": ""}

def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = letter
    # top hairline + running title
    canvas.setStrokeColor(LINE); canvas.setLineWidth(0.5)
    canvas.line(0.9 * inch, h - 0.62 * inch, w - 0.9 * inch, h - 0.62 * inch)
    canvas.setFont("Helvetica", 7.5); canvas.setFillColor(FAINT)
    canvas.drawString(0.9 * inch, h - 0.55 * inch, "MedReg Intel · Illustrative exemplar")
    canvas.drawRightString(w - 0.9 * inch, h - 0.55 * inch, DOC_META["device"])
    # footer
    canvas.line(0.9 * inch, 0.7 * inch, w - 0.9 * inch, 0.7 * inch)
    canvas.setFont("Helvetica", 7); canvas.setFillColor(FAINT)
    canvas.drawString(0.9 * inch, 0.55 * inch,
                      "Illustrative exemplar — modeled on FDA guidance + public record, not a verbatim confidential submission.")
    canvas.drawRightString(w - 0.9 * inch, 0.55 * inch, "Page %d" % doc.page)
    canvas.restoreState()

def title_block(title, subtitle, grounding, basis):
    el = []
    # pastel tag
    tag = Table([[Paragraph('<font color="#4a5aa8"><b>ILLUSTRATIVE EXEMPLAR — “what good looks like”</b></font>', SMALL)]],
                colWidths=[6.7 * inch])
    tag.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PERI_BG), ("BOX", (0, 0), (-1, -1), 0.5, PERI),
                             ("LEFTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    el += [tag, Spacer(1, 12), Paragraph(title, TITLE), Spacer(1, 4), Paragraph(subtitle, SUB), Spacer(1, 10)]
    box = Table([[Paragraph("<b>Grounded in (public record):</b> " + grounding, SMALL)],
                 [Paragraph("<b>Regulatory basis:</b> " + basis, SMALL)]], colWidths=[6.7 * inch])
    box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), MINT_BG), ("BOX", (0, 0), (-1, -1), 0.5, MINT),
                             ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                             ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    el += [box, Spacer(1, 6), HRFlowable(width="100%", thickness=0.6, color=LINE), Spacer(1, 2)]
    return el

def bullets(items):
    return ListFlowable([ListItem(Paragraph(i, BODY), leftIndent=10, value="•") for i in items],
                        bulletType="bullet", start="•", leftIndent=12)

def table(rows, widths, header=True):
    data = [[Paragraph(c, CELLH if (header and r == 0) else CELL) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=[x * inch for x in widths], repeatRows=1 if header else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
          ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
          ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, colors.HexColor("#FAFBFE")])]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), PERI_BG), ("LINEBELOW", (0, 0), (-1, 0), 0.6, PERI)]
    t.setStyle(TableStyle(st)); return t

def build(filename, device_short, blocks):
    DOC_META["device"] = device_short
    doc = BaseDocTemplate(os.path.join(OUT, filename), pagesize=letter,
                          leftMargin=0.9 * inch, rightMargin=0.9 * inch, topMargin=0.8 * inch, bottomMargin=0.85 * inch)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=_header_footer)])
    doc.build(list(blocks))
    print("wrote", os.path.join("docs/examples", filename))

def sec(title, *flow):
    out = [Paragraph(title, H1)]; out.extend(flow); return out

# =================================================================== 1) Premarket cyber package
def doc_cyber():
    b = title_block(
        "Premarket Cybersecurity Documentation",
        "Modular, EMR-connected infusion system (Class II, 510(k))",
        'BD Alaris™ Infusion System — FDA 510(k) cleared July 2023 (updated software with enhanced cybersecurity + EMR interoperability; remediated the 2020 Class I recall of ~774,000 devices). Public source: BD press release, news.bd.com (2023-07-21).',
        "FD&C Act §524B; FDA Premarket Cybersecurity Guidance (final, 2025-06-27); AAMI SW96; ISO 14971; IEC 81001-5-1.")
    b += sec("1. Cyber-device determination",
             Paragraph("The system is a <b>cyber device</b> under §524B: a modular point-of-care unit (PCU) with large-volume, syringe, and PCA pump modules, wired/wireless network connectivity, and bidirectional EMR interoperability. Connectivity (Wi-Fi + wired Ethernet + maintenance USB) brings it within scope of the 2025 guidance.", BODY))
    b += sec("2. Security risk management (AAMI SW96 / ISO 14971)",
             Paragraph("Security risk is managed in a dedicated file integrated with the safety risk file. Risks are scored on exploitability and patient-harm independently; residual risks are formally accepted by Quality and Product Security.", BODY),
             Spacer(1, 4),
             table([["ID", "Asset / interface", "Threat (STRIDE)", "Control", "Residual"],
                    ["S-01", "Wireless module link", "Spoofing", "Mutual-TLS, device certificates, 802.1X", "Low (accepted)"],
                    ["S-02", "Drug library / DERS update", "Tampering", "Signed packages, integrity verification", "Low"],
                    ["S-03", "EMR interoperability (HL7/FHIR)", "Information disclosure", "TLS 1.2+, scoped interfaces, audit logging", "Low"],
                    ["S-04", "Maintenance USB port", "Elevation of privilege", "Port lockdown, signed service tools, RBAC", "Low (accepted)"],
                    ["S-05", "PCU availability", "Denial of service", "Local autonomy, watchdog, safe-state on fault", "Medium (accepted)"]],
                   [0.45, 1.7, 1.35, 2.3, 0.9]))
    b += sec("3. Threat model",
             Paragraph("A STRIDE model spans the PCU, pump modules, wireless/wired networking, the maintenance interface, the drug-library/DERS update path, and EMR integration. Each threat traces to a control and a verification test (see §6).", BODY))
    b += sec("4. Security architecture views",
             bullets(["<b>Global system view</b> — PCU, modules, network, server-side drug-library service, EMR gateway, trust boundaries.",
                      "<b>Multi-patient harm view</b> — blast radius if a shared server or drug library is compromised.",
                      "<b>Updateability / patchability view</b> — signed software and drug-library update path with rollback.",
                      "<b>Security use-case views</b> — clinician auth, service access, EMR association, key/cert management."]))
    b += sec("5. Security controls (eight categories)",
             table([["Category", "Implementation (summary)"],
                    ["Authentication", "Role-based clinician/service auth; device-to-server mutual-TLS"],
                    ["Authorization", "Least-privilege roles; service functions gated"],
                    ["Cryptography", "TLS in transit; signed firmware/drug library; keys in hardware-backed store"],
                    ["Code &amp; data integrity", "Secure boot, signed images, anti-rollback"],
                    ["Confidentiality", "Encryption of PHI in transit; minimized data at rest"],
                    ["Event detection / logging", "Security event logs exported to hospital SIEM"],
                    ["Resiliency / recovery", "Local infusion autonomy; safe-state; restore from signed image"],
                    ["Firmware / software updates", "Authenticated, staged updates with verification and rollback"]],
                   [1.8, 4.9]))
    b += sec("6. Cybersecurity testing",
             table([["Activity", "Scope", "Result"],
                    ["SAST", "Full firmware + app source", "Findings triaged; criticals resolved"],
                    ["SCA / SBOM analysis", "All third-party components", "0 known critical CVEs at submission"],
                    ["DAST", "Network services + EMR interface", "No unauthenticated exposure"],
                    ["Fuzzing", "Protocol parsers (HL7/FHIR, update)", "No exploitable crashes"],
                    ["Penetration test", "Independent accredited lab", "All findings closed or risk-accepted"]],
                   [1.3, 3.4, 2.0]))
    b += sec("7. SBOM (excerpt)",
             table([["Component", "Version", "Support / EOL", "Known vulns"],
                    ["Embedded RTOS", "x.y", "Supported", "0 critical"],
                    ["TLS library", "x.y.z", "Supported (LTS)", "0 critical"],
                    ["HL7/FHIR parser", "x.y", "Supported", "0 critical"],
                    ["Logging library", "x.y", "Supported", "0 critical"]],
                   [2.4, 1.0, 1.9, 1.4]),
             Spacer(1, 3), Paragraph("Delivered as machine-readable CycloneDX 1.5 with supplier, license, support level, and end-of-support per component.", SMALL))
    b += sec("8. Postmarket management &amp; CVD",
             bullets(["Continuous SBOM→CVE and CISA KEV monitoring; vendor PSIRT feeds.",
                      "Coordinated Vulnerability Disclosure policy with safe-harbor and SLAs; CVEs via CNA.",
                      "Patch SLAs by severity; customer notification ≤ 30 days; 21 CFR 806/803 assessment triggers defined."]))
    b += sec("9. Labeling",
             Paragraph("Security labeling and an MDS2 form describe supported configurations, network requirements, controls, update mechanism, and known limitations; a hardening guide ships with the device.", BODY))
    b += sec("10. Conclusion",
             Paragraph("The documentation demonstrates a <b>reasonable assurance of cybersecurity</b> for a connected infusion system consistent with §524B and the 2025 premarket guidance.", BODY))
    build("01_premarket_cybersecurity_infusion_system.pdf", "Infusion system (BD Alaris-grounded)", b)

# =================================================================== 2) Security Risk Assessment
def doc_sra():
    b = title_block(
        "Security Risk Assessment (SW96 / ISO 14971)",
        "Excerpt — connected infusion system",
        'BD Alaris™ Infusion System (510(k) cleared July 2023). Public source: BD press release, news.bd.com (2023-07-21).',
        "AAMI SW96:2023; ISO 14971:2019; FDA Premarket Cybersecurity Guidance (2025).")
    b += sec("Method",
             Paragraph("Assets and interfaces are enumerated, threats derived via STRIDE, and each risk scored on <b>exploitability</b> and <b>patient-harm</b> separately. Controls are selected; residual risk is compared to acceptance criteria and formally accepted.", BODY))
    b += sec("Risk register (excerpt)",
             table([["ID", "Asset", "Threat", "Exploit.", "Harm", "Control(s)", "Residual"],
                    ["S-01", "Wireless link", "Spoofing", "Med", "Med", "Mutual-TLS, 802.1X, cert pinning", "Low ✓"],
                    ["S-02", "Drug library update", "Tampering", "Low", "High", "Signed packages, anti-rollback", "Low ✓"],
                    ["S-03", "EMR interface", "Info disclosure", "Med", "Low", "TLS, scoped API, audit logs", "Low ✓"],
                    ["S-04", "Service/USB", "Elevation", "Low", "High", "Port lockdown, signed tools, RBAC", "Low ✓"],
                    ["S-05", "PCU availability", "DoS", "Med", "Med", "Local autonomy, watchdog, safe-state", "Med ✓*"],
                    ["S-06", "Audit log", "Repudiation", "Low", "Low", "Tamper-evident logging to SIEM", "Low ✓"]],
                   [0.4, 1.05, 1.0, 0.55, 0.5, 2.2, 0.85]))
    b += sec("Acceptance",
             Paragraph("All residual risks meet acceptance criteria. * S-05 accepted on the basis that the pump retains local infusion autonomy and enters a safe state independent of the network; compensating controls and monitoring apply. Accepted by Quality + Product Security, with rationale recorded in the risk file.", BODY))
    b += sec("If a control cannot be implemented",
             Paragraph("Where a control is infeasible (e.g., per-user authentication on a shared bedside device during a code), the file records the justification, the compensating controls (physical access control, network segmentation, audit logging), the residual risk and its acceptance, and the user-facing limitation in labeling — the approach FDA expects in lieu of the control.", BODY))
    build("02_security_risk_assessment_infusion_system.pdf", "Infusion system (BD Alaris-grounded)", b)

# =================================================================== 3) PCCP + GMLP (AI)
def doc_pccp():
    b = title_block(
        "Predetermined Change Control Plan (PCCP) &amp; GMLP",
        "Autonomous AI diagnostic — diabetic retinopathy detection (Class II, De Novo)",
        'IDx-DR / LumineticsCore (Digital Diagnostics) — FDA De Novo DEN180001, April 2018, first autonomous AI diagnostic. Pivotal trial: 900 patients across 10 primary-care sites; 87.2% sensitivity, 90.7% specificity vs the Wisconsin Fundus Photograph Reading Center. Public sources: FDA De Novo DEN180001; University of Iowa / Digital Diagnostics announcements (2018).',
        "FDA PCCP final guidance (2024); GMLP guiding principles (2021); FDA AI lifecycle draft (2025).")
    b += sec("1. Device &amp; intended use",
             Paragraph("Software-only autonomous AI that analyzes fundus images from a non-mydriatic camera at the point of care and returns a screening result for more-than-mild diabetic retinopathy (mtmDR), without specialist over-read. The reconstruction below illustrates how a PCCP would be structured for such a device under current guidance.", BODY))
    b += sec("2. Description of modifications (bounded)",
             bullets(["Periodic <b>re-training</b> on additional labeled fundus images (same indication and population).",
                      "<b>Operating-point</b> re-tuning within a pre-specified bound to maintain the sensitivity/specificity trade-off.",
                      "Support for <b>additional compatible cameras</b> validated to the image-quality specification.",
                      "<b>No change</b> to intended use, target population, or output categories."]))
    b += sec("3. Modification protocol",
             table([["Step", "Requirement"],
                    ["Data", "≥ N new images; representative across age, sex, race/ethnicity, and disease severity; independent frozen test set; documented provenance"],
                    ["Reference standard", "Reading-center grading (ETDRS) by certified graders, as in the pivotal study"],
                    ["Re-training", "Versioned pipeline; no test-set leakage; change log"],
                    ["Acceptance gates", "Sensitivity ≥ 85% and specificity ≥ 82.5% overall <b>and</b> within each subgroup; no regression vs prior version"],
                    ["Release", "Versioned, signed model artifact with rollback; labeling/version note updated"]],
                   [1.4, 5.3]))
    b += sec("4. Reference performance (pivotal, public)",
             table([["Metric", "Result", "Reference"],
                    ["Sensitivity (mtmDR)", "87.2%", "Wisconsin Fundus Photograph Reading Center (ETDRS)"],
                    ["Specificity (mtmDR)", "90.7%", "Wisconsin Fundus Photograph Reading Center (ETDRS)"],
                    ["Study", "900 patients, 10 primary-care sites", "Prospective pivotal trial (2018)"]],
                   [1.9, 2.3, 2.5]))
    b += sec("5. Impact assessment",
             Paragraph("Risks of the bounded changes — performance drift and subgroup degradation — are controlled by locked acceptance gates (including per-subgroup), independent test data, postmarket monitoring, and explicit halt/rollback criteria. Any change outside this envelope (e.g., new indication, new output) falls <b>outside the PCCP</b> and requires a new marketing submission.", BODY))
    b += sec("6. GMLP evidence (10 principles)",
             table([["#", "Principle", "Evidence (illustrative)"],
                    ["1", "Multidisciplinary expertise", "Clinical + ML + security across lifecycle"],
                    ["2", "Good software &amp; security practice", "SDLC + security risk file"],
                    ["3", "Representative data", "Multi-site, demographically balanced cohort"],
                    ["4", "Train/test independence", "Frozen, audited test set"],
                    ["5", "Reference standard", "Reading-center ETDRS adjudication"],
                    ["6", "Model tailored to use", "Lesion-based pipeline for mtmDR"],
                    ["7", "Human-AI team", "Autonomous use validated for primary care"],
                    ["8", "Clinically relevant testing", "Prospective primary-care trial"],
                    ["9", "Clear user information", "Image-quality feedback + result labeling"],
                    ["10", "Deployed monitoring", "Real-world performance + drift triggers"]],
                   [0.3, 2.5, 3.9]))
    b += sec("7. Transparency",
             Paragraph("Each authorized release adds a dated version note (data summary, performance delta, affected configurations) to labeling so users understand what changed and the validated population.", BODY))
    build("03_pccp_gmlp_autonomous_ai.pdf", "Autonomous AI (IDx-DR-grounded)", b)

# =================================================================== 4) 510(k) cyber section
def doc_510k():
    b = title_block(
        "510(k) Cybersecurity Section — Summary",
        "Connected infusion system (eSTAR)",
        'BD Alaris™ Infusion System (510(k) cleared July 2023). Public source: BD press release, news.bd.com (2023-07-21).',
        "FD&C Act §524B; FDA Premarket Cybersecurity Guidance (2025); eSTAR.")
    b += sec("Section contents",
             table([["#", "Item", "Reference artifact"],
                    ["1", "Cyber-device determination &amp; connectivity", "CSMP §1"],
                    ["2", "Security risk management summary", "SRM report (SW96/14971)"],
                    ["3", "Threat model summary", "Threat model (STRIDE) + DFDs"],
                    ["4", "Architecture views", "Architecture package (4 views)"],
                    ["5", "Security controls (8 categories)", "Controls matrix + design evidence"],
                    ["6", "SBOM", "CycloneDX 1.5 + known-vuln list"],
                    ["7", "Cybersecurity testing", "SAST/DAST/SCA/fuzz/pen reports"],
                    ["8", "Postmarket management + CVD", "Postmarket plan + CVD policy"],
                    ["9", "Security labeling", "MDS2 + hardening guide"],
                    ["10", "Reasonable-assurance conclusion", "Summary statement"]],
                   [0.3, 3.4, 3.0]))
    b += sec("Conclusion",
             Paragraph("Each artifact above is summarized in the section and attached to the eSTAR submission; the section concludes with an explicit statement of <b>reasonable assurance of cybersecurity</b>, the standard FDA reviewers look for in a cyber-device 510(k).", BODY))
    build("04_510k_cybersecurity_section_summary.pdf", "Infusion system (BD Alaris-grounded)", b)

if __name__ == "__main__":
    doc_cyber(); doc_sra(); doc_pccp(); doc_510k()
    print("done →", OUT)
