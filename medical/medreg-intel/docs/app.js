/* MedReg Intel — runs fully in the browser. Reference data from window.MEDREG; live data from openFDA. */
const D = window.MEDREG || {};
const $ = (s) => document.querySelector(s);
const esc = (s) => (s == null ? "" : String(s).replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])));
const REG = Object.fromEntries((D.regulations || []).map(r => [r.id, r]));
const subName = (id) => { const s = (D.submissions || []).find(x => x.id === id); return s ? s.name : id; };
// gold-standard PDF exemplars (served from the repo / Pages / full app)
const EX_BASE = (document.title || "").includes("standalone") ? "docs/examples/" : "examples/";
const EXAMPLE_PDFS = [
  { f: "01_premarket_cybersecurity_infusion_system.pdf", t: "Premarket Cybersecurity Package", g: "BD Alaris infusion system · 510(k) 2023" },
  { f: "02_security_risk_assessment_infusion_system.pdf", t: "Security Risk Assessment (SW96)", g: "BD Alaris infusion system" },
  { f: "03_pccp_gmlp_autonomous_ai.pdf", t: "PCCP + GMLP (AI)", g: "IDx-DR autonomous AI · De Novo DEN180001" },
  { f: "04_510k_cybersecurity_section_summary.pdf", t: "510(k) Cybersecurity Section", g: "BD Alaris infusion system" },
];
function templatesBanner() {
  return `<div class="exbanner">
    <div class="exb-head"><b>Gold-standard PDF examples — “what good looks like.”</b> Polished, professional exemplars grounded in the public record of real cleared devices (BD Alaris™, IDx-DR), with citations. Illustrative reconstructions of FDA-expected structure — not verbatim confidential filings.</div>
    <div class="exb-grid">${EXAMPLE_PDFS.map(p => `<a class="exb-card" href="${EX_BASE}${esc(p.f)}" target="_blank" rel="noopener"><span class="exb-t">${esc(p.t)}</span><span class="exb-g">${esc(p.g)}</span><span class="exb-pdf">Open PDF ↗</span></a>`).join("")}</div>
    <div class="exb-foot">The in-editor “Worked example” below uses a fictional device to show structure; these PDFs are the real-device-grounded versions. PDFs live in <code>docs/examples/</code> in the repo.</div>
  </div>`;
}

const TABS = [
  { id: "submissions", label: "Submissions", c: "c-sub", b: "b-sub", pip: "var(--mint)",
    facets: [{ f: "region", label: "Region" }] },
  { id: "templates", label: "Templates", c: "c-tpl", b: "b-tpl", pip: "var(--sage)",
    facets: [{ f: "category", label: "Category" }] },
  { id: "regulations", label: "Regulations", c: "c-reg", b: "b-reg", pip: "var(--periwinkle)",
    facets: [{ f: "region", label: "Region" }, { f: "type", label: "Type" }] },
  { id: "requirements", label: "Submission Requirements", c: "c-req", b: "b-req", pip: "var(--sky)",
    facets: [{ f: "cat", label: "Category" }, { f: "tech", label: "Technology", arr: true }, { f: "applies", label: "Submission", arr: true, map: subName }] },
  { id: "secreqs", label: "Security Requirements & V&V Tests", c: "c-sec", b: "b-req", pip: "#5fb6c9", facets: [] },
  { id: "ai", label: "AI requirements", c: "c-ai", b: "b-ai", pip: "var(--lavender)", facets: [] },
  { id: "risk", label: "Risk Assessment", c: "c-risk", b: "b-rta", pip: "#e89aae", facets: [] },
  { id: "incidents", label: "FDA & agency cyber incidents", c: "c-inc", b: "b-inc", pip: "var(--blush)",
    facets: [{ f: "agency", label: "Agency" }] },
  { id: "rta", label: "RTA & fines", c: "c-rta", b: "b-rta", pip: "var(--butter)", facets: [] },
];
let active = "submissions", query = "", facetVals = {};
let lensJuris = "All", lensTech = "All";
const TECH_PROFILES = ["All", "AI", "SaMD", "SiMD", "Software", "Hardware", "Firmware", "Connected", "Cloud", "AWS", "Azure", "GCP", "Mobile-iOS", "Mobile-Android"];

// ---------- lens bar ----------
function renderLens() {
  $("#lensJuris").innerHTML = ["All", "US", "International"].map(v =>
    `<button class="lchip ${v === lensJuris ? "on" : ""}" data-v="${v}">${v}</button>`).join("");
  $("#lensTech").innerHTML = TECH_PROFILES.map(v =>
    `<button class="lchip ${v === lensTech ? "on" : ""}" data-v="${v}">${v}</button>`).join("");
  $("#lensJuris").querySelectorAll(".lchip").forEach(c => c.addEventListener("click", () => { lensJuris = c.dataset.v; renderLens(); render(); }));
  $("#lensTech").querySelectorAll(".lchip").forEach(c => c.addEventListener("click", () => { lensTech = c.dataset.v; renderLens(); render(); }));
}
function passLens(r) {
  // jurisdiction
  if (lensJuris !== "All") {
    if ("us" in r || "intl" in r) { if (lensJuris === "US" && !r.us) return false; if (lensJuris === "International" && !r.intl) return false; }
    else if (r.region) { const isUS = String(r.region).includes("US"); if (lensJuris === "US" && !isUS) return false; if (lensJuris === "International" && r.region === "US") return false; }
  }
  // technology profile — only constrains rows that declare tech
  if (lensTech !== "All" && Array.isArray(r.tech) && r.tech.length && !r.tech.includes(lensTech)) return false;
  return true;
}

// ---------- nav ----------
$("#tabs").innerHTML = TABS.map(t =>
  `<button class="tab ${t.c}" data-id="${t.id}"><span class="pip" style="background:${t.pip}"></span>${t.label}</button>`).join("");
$("#tabs").querySelectorAll(".tab").forEach(b => b.addEventListener("click", () => { active = b.dataset.id; query = ""; facetVals = {}; $("#search").value = ""; render(); }));
$("#search").addEventListener("input", e => { query = e.target.value.toLowerCase().trim(); render(); });
$("#trackerPill").addEventListener("click", () => { const p = $("#trackerPanel"); p.classList.remove("hidden"); p.scrollIntoView({ behavior: "smooth" }); });

// ---------- Ask: client-side retrieval (RAG) over the embedded corpus ----------
function ragRank(q) {
  const terms = q.toLowerCase().split(/[^a-z0-9]+/).filter(t => t.length > 2);
  if (!terms.length) return [];
  const out = [];
  ["regulations", "submissions", "requirements", "incidents", "rta", "ai", "templates"].forEach(coll => {
    (D[coll] || []).forEach(r => {
      const blob = JSON.stringify(r).toLowerCase();
      const name = String(r.name || r.device || r.trigger || "").toLowerCase();
      let score = 0;
      terms.forEach(t => { score += blob.split(t).length - 1; if (name.includes(t)) score += 5; });
      if (score) out.push({ score, coll, r });
    });
  });
  return out.sort((a, b) => b.score - a.score).slice(0, 10);
}
const TABMAP = { regulations: "regulations", submissions: "submissions", requirements: "requirements", incidents: "incidents", rta: "rta", ai: "ai", templates: "templates" };
function runAsk() {
  const q = ($("#askInput").value || "").trim();
  const out = $("#askResults");
  if (!q) { out.innerHTML = ""; return; }
  const hits = ragRank(q);
  if (!hits.length) { out.innerHTML = `<div class="trow"><div class="tt">No matches</div><div class="tm">Try terms like SBOM, 524B, PCCP, mobile, cloud, RTA, or a device name.</div></div>`; return; }
  out.innerHTML = hits.map(({ coll, r }) => {
    const title = esc(r.name || r.device || r.trigger);
    const snip = esc(String(r.summary || r.desc || r.detail || r.what || r.guidance || "").slice(0, 190));
    return `<div class="trow askhit" data-tab="${coll}" data-q="${esc(title)}">
      <div class="tt">${title} <span class="nb rag">${coll}</span></div><div class="tm">${snip}</div></div>`;
  }).join("");
  out.querySelectorAll(".askhit").forEach(h => h.addEventListener("click", () => {
    active = TABMAP[h.dataset.tab]; facetVals = {}; query = ""; $("#search").value = "";
    render(); window.scrollTo({ top: 0, behavior: "smooth" });
  }));
}
$("#askBtn").addEventListener("click", runAsk);
$("#askInput").addEventListener("keydown", e => { if (e.key === "Enter") runAsk(); });
$("#pdfClose").addEventListener("click", closePdfViewer);
$("#pdfViewer").addEventListener("click", e => { if (e.target.id === "pdfViewer") closePdfViewer(); });
document.addEventListener("keydown", e => { if (e.key === "Escape" && !$("#pdfViewer").classList.contains("hidden")) closePdfViewer(); });

function facetValues(tab, fc) {
  const rows = D[tab.id] || [];
  const vals = new Set();
  rows.forEach(r => { const v = r[fc.f]; if (Array.isArray(v)) v.forEach(x => vals.add(x)); else if (v) vals.add(v); });
  return ["All", ...[...vals].sort()];
}
const matches = (o) => !query || JSON.stringify(o).toLowerCase().includes(query);

// ---------- render ----------
function render() {
  const tab = TABS.find(t => t.id === active);
  $("#tabs").querySelectorAll(".tab").forEach(b => b.classList.toggle("active", b.dataset.id === active));
  const fwrap = $("#filters");
  fwrap.innerHTML = (tab.facets || []).map((fc, i) => {
    const cur = facetVals[fc.f] || "All";
    const chips = facetValues(tab, fc).map(v =>
      `<button class="fchip ${v === cur ? "on" : ""}" data-f="${fc.f}" data-v="${esc(v)}">${esc(fc.map && v !== "All" ? fc.map(v) : v)}</button>`).join("");
    return `<div class="frow"><span class="flabel">${fc.label}</span>${chips}</div>`;
  }).join("");
  fwrap.querySelectorAll(".fchip").forEach(c => c.addEventListener("click", () => {
    facetVals[c.dataset.f] = c.dataset.v; render();
  }));
  let rows = (D[active] || []).filter(matches).filter(passLens);
  (tab.facets || []).forEach(fc => {
    const v = facetVals[fc.f];
    if (v && v !== "All") rows = rows.filter(r => fc.arr ? (r[fc.f] || []).includes(v) : r[fc.f] === v);
  });
  $("#count").textContent = rows.length + (rows.length === 1 ? " entry" : " entries");
  if (active === "secreqs") {
    $("#view").innerHTML = renderSecReqs(rows);
    const dx = $("#srDlXlsx"); if (dx) dx.onclick = () => downloadFile("security-requirements-vv.xlsx");
    const dc = $("#srDlCsv"); if (dc) dc.onclick = () => downloadSecreqCSV(rows);
    return;
  }
  if (active === "risk") {
    $("#view").innerHTML = renderRisk(rows);
    const rx = $("#riskDlXlsx"); if (rx) rx.onclick = () => downloadFile("risk-assessment-medical-device.xlsx");
    return;
  }
  if (active === "templates") {
    $("#view").innerHTML = templatesBanner() + renderTemplates(rows);
    $("#view").querySelectorAll(".tpl-head").forEach(h => h.addEventListener("click", () => h.parentElement.classList.toggle("open")));
    $("#view").querySelectorAll(".dl").forEach(b => b.addEventListener("click", e => { e.stopPropagation(); openEditor(b.dataset.id); }));
    $("#view").querySelectorAll(".pdfbtn").forEach(b => b.addEventListener("click", e => { e.stopPropagation(); openPdf(b.dataset.pdf); }));
    return;
  }
  $("#view").innerHTML =
    `<div class="grid ${active === "incidents" || active === "rta" ? "timeline" : ""}">${rows.map(r => CARD[active](r, tab)).join("") || empty()}</div>`;
  $("#view").querySelectorAll(".reglink").forEach(a => a.addEventListener("click", e => { e.preventDefault(); goToReg(a.dataset.reg); }));
}
const empty = () => `<div class="card" style="cursor:default"><p class="desc">No matches. Clear the search or pick another filter.</p></div>`;
function modeBadge(m) {
  const cls = m === "Automatable" ? "m-auto" : m === "Manual" ? "m-manual" : "m-both";
  return `<span class="modeb ${cls}">${esc(m)}</span>`;
}
function renderSecReqs(rows) {
  const note = lensTech === "All"
    ? `Showing security requirements across <b>all profiles</b>. Pick a <b>Profile</b> in the bar above (e.g., AI, Cloud, Mobile-iOS, Firmware) to focus the table.`
    : `Security requirements and V&amp;V tests for the <b>${esc(lensTech)}</b> profile.`;
  const bar = `<div class="dlbar"><span class="sr-note" style="margin:0;flex:1">${note}</span>
      <button class="btn" id="srDlCsv">Download CSV (current)</button>
      <button class="btn primary" id="srDlXlsx">Download Excel (all)</button></div>`;
  if (!rows.length) return bar + `<div class="card" style="cursor:default"><p class="desc">No security requirements for this profile.</p></div>`;
  const body = rows.map(r => `<tr>
      <td class="sr-req">${esc(r.req)}</td>
      <td class="sr-desc">${esc(r.desc)}</td>
      <td class="sr-mode">${modeBadge(r.mode)}</td>
      <td class="sr-vv">${esc(r.vv)}</td></tr>`).join("");
  return bar + `<div class="sr-wrap"><table class="sr-table">
      <thead><tr><th>Security requirement</th><th>Description</th><th>Automatable / Manual</th><th>V&amp;V test to validate</th></tr></thead>
      <tbody>${body}</tbody></table></div>`;
}
function riskColor(sxl) { return sxl >= 12 ? "rk-high" : sxl >= 6 ? "rk-med" : "rk-low"; }
function riskLevel(sxl) { return sxl >= 12 ? "High" : sxl >= 6 ? "Medium" : "Low"; }
function riskBadge(sev, lik) { const v = sev * lik; return `<span class="rk ${riskColor(v)}">${riskLevel(v)} · ${v}</span>`; }
function renderRisk(rows) {
  const bar = `<div class="dlbar"><span class="sr-note" style="margin:0;flex:1">Risk assessment flow: <b>cyber issue → C/I/A impact → inherent risk → mitigating control → hazardous situation → patient-safety impact → residual risk → recommendation → standards</b>. Inherent/residual = Severity × Likelihood (1–5). The Excel contains live formulas.</span>
      <button class="btn primary" id="riskDlXlsx">Download Excel (with formulas)</button></div>`;
  const body = rows.map(r => `<tr>
      <td class="sr-req">${esc(r.cyber_issue)}</td>
      <td style="text-align:center"><span class="cia">${esc(r.cia)}</span></td>
      <td style="text-align:center">${riskBadge(r.inh_sev, r.inh_lik)}</td>
      <td class="sr-desc">${esc(r.control)}</td>
      <td class="sr-desc">${esc(r.hazard)}</td>
      <td class="sr-desc">${esc(r.patient)}</td>
      <td style="text-align:center">${riskBadge(r.res_sev, r.res_lik)}</td>
      <td class="sr-desc">${esc(r.rec)}</td>
      <td class="sr-vv">${esc(r.std)}</td></tr>`).join("");
  return bar + `<div class="sr-wrap"><table class="sr-table risk">
      <thead><tr><th>Cyber issue</th><th>C/I/A</th><th>Inherent risk</th><th>Mitigating control</th><th>Hazardous situation</th>
        <th>Patient-safety impact</th><th>Residual risk</th><th>Recommendation to remediate</th><th>Standards</th></tr></thead>
      <tbody>${body}</tbody></table></div>
    <div class="sr-note" style="margin-top:14px">C = Confidentiality, I = Integrity, A = Availability. Risk band: Low (1–5) · Medium (6–11) · High (12–25). References: ISO 14971 · ISO/TR 24971 · AAMI TIR57 · ANSI/AAMI SW96 · FDA Premarket (2025) &amp; Postmarket (2016) · IEC 81001-5-1 · NIST 800-30 / AI RMF. The Excel has Risk Register (live formulas), Scoring Key, and References sheets.</div>`;
}
// ---- file downloads (embedded data-URI aware) ----
function fileUri(name) {
  if (window.MEDREG_XLSX && window.MEDREG_XLSX[name]) return window.MEDREG_XLSX[name];
  if (window.MEDREG_PDFS && window.MEDREG_PDFS[name]) return window.MEDREG_PDFS[name];
  return "examples/" + name;
}
function downloadFile(name) {
  const uri = fileUri(name); let url = uri;
  if (uri.startsWith("data:")) url = URL.createObjectURL(dataURItoBlob(uri));
  const a = document.createElement("a"); a.href = url; a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  if (uri.startsWith("data:")) setTimeout(() => URL.revokeObjectURL(url), 60000);
}
function csvEsc(s) { s = String(s == null ? "" : s); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; }
function downloadSecreqCSV(rows) {
  const head = ["ID", "Security requirement", "Description", "Automatable/Manual", "V&V test", "Profiles"];
  const lines = [head.join(",")].concat(rows.map(r => [r.id, r.req, r.desc, r.mode, r.vv, (r.tech || []).join("; ")].map(csvEsc).join(",")));
  const blob = new Blob(["\ufeff" + lines.join("\r\n")], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
  a.download = "security-requirements-" + (lensTech === "All" ? "all" : lensTech) + ".csv";
  document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 5000);
}
// ---- collapsible templates ----
function renderTemplates(rows) {
  return `<div class="tpl-list">` + rows.map(r => `<div class="tpl-row" data-id="${esc(r.id)}">
      <div class="tpl-head"><span class="tpl-name">${esc(r.name)}</span>
        <span class="badge b-tpl">${esc(r.category)}</span>${r.example_pdf ? `<span class="badge b-pdf">PDF</span>` : ""}
        <span class="tpl-car">▸</span></div>
      <div class="tpl-body">
        <p class="desc">${esc(r.guidance || "")}</p>
        ${(r.evidence_docs && r.evidence_docs.length) ? `<div class="kv"><b>Documents in an excellent submission:</b> ${(r.evidence_docs).map(esc).join(" · ")}</div>` : ""}
        <div class="links"><button class="dl" data-id="${esc(r.id)}">Edit &amp; download ↗</button>
          ${(r.example_pdfs && r.example_pdfs.length ? r.example_pdfs : (r.example_pdf ? [{ label: "Example", file: r.example_pdf }] : []))
            .map(e => `<button class="pdfbtn" data-pdf="${esc(e.file)}">View: ${esc(e.label)} ↗</button>`).join("")}</div>
      </div></div>`).join("") + `</div>`;
}
const link = (url, label) => url ? `<a href="${esc(url)}" target="_blank" rel="noopener">${label} ↗</a>` : "";
const regChips = (ids) => (ids || []).map(id => REG[id] ? `<a href="#" class="chip reglink" data-reg="${id}" title="${esc(REG[id].name)}">${esc(REG[id].name.split(" — ")[0])}</a>` : "").join("");
function goToReg(id) { const r = REG[id]; if (!r) return; active = "regulations"; facetVals = {}; query = r.name.toLowerCase(); $("#search").value = r.name; render(); window.scrollTo({ top: 0, behavior: "smooth" }); }

function pdfHref(file) { return (window.MEDREG_PDFS && window.MEDREG_PDFS[file]) || ("examples/" + file); }
function dataURItoBlob(uri) {
  const [meta, b64] = uri.split(","); const bin = atob(b64); const arr = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
  return new Blob([arr], { type: (meta.match(/:(.*?);/) || [])[1] || "application/pdf" });
}
let _pdfBlobUrl = null;
function showPdfViewer(url, name) {
  $("#pdfFrame").src = url;
  $("#pdfTitle").textContent = name;
  $("#pdfDownload").onclick = () => { const a = document.createElement("a"); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove(); };
  $("#pdfNewTab").onclick = () => window.open(url, "_blank");
  $("#pdfViewer").classList.remove("hidden");
}
function closePdfViewer() {
  $("#pdfViewer").classList.add("hidden"); $("#pdfFrame").src = "about:blank";
  if (_pdfBlobUrl) { URL.revokeObjectURL(_pdfBlobUrl); _pdfBlobUrl = null; }
}
function openPdf(file) {
  const h = pdfHref(file); let url = h;
  if (h.startsWith("data:")) { url = URL.createObjectURL(dataURItoBlob(h)); _pdfBlobUrl = url; }
  showPdfViewer(url, file);
}
const CARD = {
  submissions: (r, t) => `<div class="card ${t.c}">
    <div class="ct"><h3>${esc(r.name)}</h3></div>
    <div class="meta"><span class="badge ${t.b}">${esc(r.region)}</span><span class="badge b-ghost">${esc(r.pathway)}</span>
      ${/Required/i.test(r.cyber) ? `<span class="badge b-inc">Cyber required</span>` : ""}
      ${(r.tech || []).map(x => `<span class="badge b-tech">${esc(x)}</span>`).join("")}</div>
    <p class="desc">${esc(r.when)}</p>
    <div class="kv"><b>Form:</b> ${esc(r.form)} · <b>Review:</b> ${esc(r.review)} · <b>AI:</b> ${esc(r.ai)}</div>
    <ul class="reqlist">${(r.reqs || []).map(x => `<li>${esc(x)}</li>`).join("")}</ul>
    <div class="links">${link(r.url, "FDA / EU source")}</div></div>`,
  templates: (r, t) => `<div class="card ${t.c}">
    <div class="ct"><h3>${esc(r.name)}</h3></div>
    <div class="meta"><span class="badge ${t.b}">${esc(r.category)}</span>${r.example_pdf ? `<span class="badge b-pdf">Example PDF</span>` : ""}</div>
    <p class="desc">${esc(r.guidance || "Editable starting point with the fields FDA expects.")}</p>
    <div class="links"><button class="dl" data-id="${esc(r.id)}">Edit &amp; download ↗</button>
      ${r.example_pdf ? `<button class="pdfbtn" data-pdf="${esc(r.example_pdf)}">View example PDF ↗</button>` : ""}</div></div>`,
  regulations: (r, t) => `<div class="card ${t.c}">
    <div class="ct"><h3>${esc(r.name)}</h3></div>
    <div class="meta"><span class="badge ${t.b}">${esc(r.region)}</span><span class="badge b-ghost">${esc(r.type)}</span>
      ${r.cyber ? `<span class="badge b-inc">Cyber</span>` : ""}${r.ai ? `<span class="badge b-ai">AI</span>` : ""}
      ${(r.tech || []).slice(0, 4).map(x => `<span class="badge b-tech">${esc(x)}</span>`).join("")}</div>
    <p class="desc">${esc(r.summary)}</p>
    <div class="cite">${esc(r.citation)} · ${esc(r.authority)} · updated ${esc(r.last_updated)}</div>
    <div class="links">${link(r.url, "Source")}</div></div>`,
  requirements: (r, t) => `<div class="card ${t.c}">
    <div class="ct"><h3>${esc(r.name)}</h3></div>
    <div class="meta"><span class="badge ${t.b}">${esc(r.cat)}</span>
      ${(r.tech || []).map(x => `<span class="badge b-tech">${esc(x)}</span>`).join("")}</div>
    <p class="desc">${esc(r.desc)}</p>
    <div class="guide"><b>What to do.</b> ${esc(r.guidance)}</div>
    <div class="kv"><b>Evidence:</b> ${(r.evidence || []).map(esc).join(" · ")}</div>
    <div class="ifnot"><b>If you can't implement it.</b> ${esc(r.if_not_implementable)}</div>
    <div class="kv"><b>Applies to:</b> ${(r.applies || []).map(a => esc(subName(a))).join(", ")}</div>
    <div class="linkrow"><span class="ll">Regulations:</span> ${regChips(r.regs)}</div>
    <div class="cite">${esc(r.cite)}</div></div>`,
  ai: (r, t) => `<div class="card ${t.c}">
    <div class="ct"><h3>${esc(r.name)}</h3></div>
    <div class="meta"><span class="badge ${t.b}">AI</span></div>
    <p class="desc">${esc(r.detail)}</p>
    <div class="cite">${esc(r.cite)}</div></div>`,
  incidents: (r, t) => `<div class="card ${t.c} tl">
    <div class="tldate">${esc(r.date)}</div>
    <div class="ct"><h3>${esc(r.device)}</h3></div>
    <div class="meta"><span class="badge ${t.b}">${esc(r.agency)}</span><span class="badge b-ghost">${esc(r.maker)}</span>
      <span class="badge b-ghost">${esc(r.region)}</span>${r.cve && r.cve !== "—" ? `<span class="badge b-cve">${esc(r.cve.split(",")[0].split("(")[0].trim())}${r.cve.includes(",") || r.cve.includes("+") ? " +" : ""}</span>` : ""}</div>
    <div class="kv"><b>${esc(r.kind)}</b> — ${esc(r.impact)}</div>
    <p class="desc">${esc(r.summary)}</p>
    <div class="why"><b>Why reported.</b> ${esc(r.why)}</div>
    ${r.disclosure ? `<div class="kv"><b>Disclosure:</b> ${esc(r.disclosure)}</div>` : ""}
    ${r.mitigation ? `<div class="guide"><b>Mitigation.</b> ${esc(r.mitigation)}</div>` : ""}
    ${r.cve && r.cve !== "—" ? `<div class="cite">CVE: ${esc(r.cve)}</div>` : ""}
    <div class="links">${link(r.source, "Source")}</div></div>`,
  rta: (r, t) => `<div class="card ${t.c} tl">
    <div class="tldate">${esc(r.date)}</div>
    <div class="ct"><h3>${esc(r.trigger)}</h3></div>
    <div class="meta"><span class="badge ${t.b}">Since ${esc(r.since)}</span></div>
    <p class="desc">${esc(r.what)}</p>
    <div class="why"><b>Why it happens.</b> ${esc(r.why)}</div>
    <div class="kv"><b>Takeaway:</b> ${esc(r.lesson)}</div>
    <div class="links">${link(r.source, "Source")}</div></div>`,
};

// ---------- template editor (live, submission-aware, Word/PDF/MD) ----------
let edTpl = null, edMode = "blank";
function edRefresh() {
  if (!edTpl) return;
  if (edMode === "example") $("#edText").value = edTpl.example || edTpl.content;
  else $("#edText").value = buildPrefill(edTpl, $("#edSubmission").value);
}
function buildPrefill(tpl, subId) {
  let head = "";
  if (subId) {
    const sub = (D.submissions || []).find(s => s.id === subId);
    const reqs = (D.requirements || []).filter(r => (r.applies || []).includes(subId));
    head = `# ${tpl.name}\n_Prepared for: ${sub.name} (${sub.pathway})_\n\n`
      + `## Submission context\n- Pathway: ${sub.pathway}\n- Form: ${sub.form} — Review: ${sub.review}\n- Cybersecurity: ${sub.cyber}\n- AI: ${sub.ai}\n\n`
      + `## Evidence expected for this submission\n`
      + reqs.map(r => `- ${r.name} (${r.cat}) — ${(r.evidence || []).join("; ")}`).join("\n")
      + `\n\n---\n\n`;
  }
  return head + tpl.content;
}
function openEditor(id) {
  const t = (D.templates || []).find(x => x.id === id);
  if (!t) return;
  edTpl = t; edMode = "blank";
  $("#edTitle").textContent = t.name;
  $("#edCat").textContent = t.category;
  $("#edGuide").textContent = t.guidance || "";
  $("#edEvidence").innerHTML = (t.evidence || []).map(e => `<li>${esc(e)}</li>`).join("");
  $("#edDocs").innerHTML = (t.evidence_docs || []).map(e => `<li>${esc(e)}</li>`).join("");
  const pdfLink = $("#edPdfLink");
  if (t.example_pdf) { pdfLink.classList.remove("hidden"); pdfLink.onclick = () => openPdf(t.example_pdf); }
  else { pdfLink.classList.add("hidden"); pdfLink.onclick = null; }
  $("#edMode").querySelectorAll(".seg-btn").forEach(b => b.classList.toggle("on", b.dataset.mode === "blank"));
  const sel = $("#edSubmission");
  sel.innerHTML = `<option value="">— none (base template) —</option>` +
    (D.submissions || []).map(s => `<option value="${s.id}">${esc(s.name)}</option>`).join("");
  sel.value = "";
  edRefresh();
  $("#editor").classList.remove("hidden");
}
$("#edMode").querySelectorAll(".seg-btn").forEach(b => b.addEventListener("click", () => {
  edMode = b.dataset.mode;
  $("#edMode").querySelectorAll(".seg-btn").forEach(x => x.classList.toggle("on", x === b));
  $("#edSubmission").disabled = (edMode === "example");
  edRefresh();
}));
$("#edSubmission").addEventListener("change", () => { if (edMode === "blank") edRefresh(); });
$("#edClose").addEventListener("click", () => $("#editor").classList.add("hidden"));
$("#editor").addEventListener("click", e => { if (e.target.id === "editor") $("#editor").classList.add("hidden"); });

function fileBase() {
  const sub = $("#edSubmission").value;
  return edTpl.id + (edMode === "example" ? "-example" : (sub ? "-" + sub : ""));
}
function mdToHtml(md) {
  const lines = md.split("\n"); let html = "", inUl = false;
  const inline = s => esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
  for (let ln of lines) {
    if (/^### /.test(ln)) { if (inUl) { html += "</ul>"; inUl = false; } html += `<h3>${inline(ln.slice(4))}</h3>`; }
    else if (/^## /.test(ln)) { if (inUl) { html += "</ul>"; inUl = false; } html += `<h2>${inline(ln.slice(3))}</h2>`; }
    else if (/^# /.test(ln)) { if (inUl) { html += "</ul>"; inUl = false; } html += `<h1>${inline(ln.slice(2))}</h1>`; }
    else if (/^\s*[-*] /.test(ln)) { if (!inUl) { html += "<ul>"; inUl = true; } html += `<li>${inline(ln.replace(/^\s*[-*] /, ""))}</li>`; }
    else if (/^\s*\|/.test(ln)) { html += `<div style="font-family:monospace">${inline(ln)}</div>`; }
    else if (ln.trim() === "---") { html += "<hr/>"; }
    else if (ln.trim() === "") { if (inUl) { html += "</ul>"; inUl = false; } html += "<p></p>"; }
    else html += `<p>${inline(ln)}</p>`;
  }
  if (inUl) html += "</ul>";
  return html;
}
function download(blob, name) {
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name;
  document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 1500);
}
$("#dlMd").addEventListener("click", () => {
  const ext = edTpl.id.includes("sbom") ? "json" : "md";
  download(new Blob([$("#edText").value], { type: "text/plain;charset=utf-8" }), `${fileBase()}.${ext}`);
});
$("#dlWord").addEventListener("click", () => {
  const body = edTpl.id.includes("sbom") ? `<pre>${esc($("#edText").value)}</pre>` : mdToHtml($("#edText").value);
  const doc = `<html xmlns:w="urn:schemas-microsoft-com:office:word"><head><meta charset="utf-8">
    <style>body{font-family:Calibri,Arial,sans-serif;font-size:11pt;color:#222;line-height:1.4}
    h1{font-size:18pt}h2{font-size:14pt}h3{font-size:12pt}h1,h2,h3{font-family:Georgia,serif}
    ul{margin:4pt 0 8pt 18pt}li{margin:2pt 0}hr{border:0;border-top:1px solid #ccc}</style></head>
    <body>${body}</body></html>`;
  download(new Blob(["\ufeff" + doc], { type: "application/msword" }), `${fileBase()}.doc`);
});
$("#dlPdf").addEventListener("click", () => {
  const body = edTpl.id.includes("sbom") ? `<pre>${esc($("#edText").value)}</pre>` : mdToHtml($("#edText").value);
  const sub = $("#edSubmission").value ? (D.submissions || []).find(s => s.id === $("#edSubmission").value) : null;
  const mode = edMode === "example" ? "Worked example" : (sub ? "Pre-filled for " + sub.name : "Template");
  const w = window.open("", "_blank");
  if (!w) { alert("Allow pop-ups to export PDF, or use Download Word."); return; }
  w.document.write(`<html><head><meta charset="utf-8"><title>${esc(edTpl.name)}</title>
    <style>@page{margin:22mm 18mm}
    body{font-family:'Inter',Arial,sans-serif;font-size:11.5px;color:#2E3440;line-height:1.55;max-width:780px;margin:0 auto;padding:0 4px}
    .tb{border:1px solid #DCE4EF;border-top:3px solid #A9B8F0;border-radius:10px;padding:14px 16px;margin:0 0 18px}
    .tag{display:inline-block;font-size:9px;font-weight:700;letter-spacing:.04em;color:#4a5aa8;background:#EEF1FD;border:1px solid #A9B8F0;border-radius:999px;padding:2px 9px}
    .tb h1{font-family:Georgia,serif;font-size:21px;color:#2E3440;margin:9px 0 3px}
    .tb .m{font-size:11px;color:#566377}
    h1{font-size:19px}h2{font-size:14px}h3{font-size:12px}h1,h2,h3{font-family:Georgia,serif;color:#33384A}
    ul{margin:6px 0 10px 20px}hr{border:0;border-top:1px solid #ddd;margin:14px 0}
    pre{white-space:pre-wrap;font-size:10.5px;background:#FAFBFE;border:1px solid #E9EEF5;border-radius:8px;padding:10px}
    .ft{margin-top:22px;border-top:1px solid #E9EEF5;padding-top:8px;font-size:9px;color:#8A97AC}
    @media print{body{margin:0}}</style></head><body>
    <div class="tb"><span class="tag">MEDREG INTEL — ${esc(mode).toUpperCase()}</span>
      <h1>${esc(edTpl.name)}</h1><div class="m">Category: ${esc(edTpl.category)} · Generated ${new Date().toLocaleDateString()}</div></div>
    ${body}
    <div class="ft">Generated with MedReg Intel. Editable starting point reflecting FDA-expected structure — not legal advice or a verbatim cleared submission. Verify against current FDA/EU sources.</div>
    <script>window.onload=function(){window.print();}<\/script></body></html>`);
  w.document.close();
});

// ---------- live tracker: (1) regulation register watch, (2) openFDA device incidents ----------
const SNAP_KEY = "medreg_tracker_snapshot_v1", REG_SNAP_KEY = "medreg_reg_snapshot_v1";
const OF = "https://api.fda.gov/device";
const ofDate = (s) => (s && s.length === 8 ? `${s.slice(0,4)}-${s.slice(4,6)}-${s.slice(6,8)}` : (s || "—"));
const getJSON = (k) => { try { return JSON.parse(localStorage.getItem(k) || "null"); } catch (e) { return null; } };
const setJSON = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } };

function runRegisterWatch() {
  const regs = (D.regulations || []).slice().sort((a, b) => (b.last_updated || "").localeCompare(a.last_updated || ""));
  const cur = Object.fromEntries(regs.map(r => [r.id, r.last_updated || r.year || ""]));
  const prev = getJSON(REG_SNAP_KEY);
  const changed = prev ? Object.keys(cur).filter(id => !(id in prev) || prev[id] !== cur[id]) : [];
  const persisted = setJSON(REG_SNAP_KEY, cur);
  const nUS = regs.filter(r => r.us).length, nIntl = regs.filter(r => r.intl).length;
  const stamp = new Date().toLocaleString();
  $("#regStatus").textContent = `· checked ${regs.length}/${regs.length} regulations (${nUS} US · ${nIntl} international) at ${stamp} · ` +
    (prev == null ? `baseline set${persisted ? "" : " (not persisted here)"}` : `${changed.length} changed since last run`);
  $("#regRegister").innerHTML = regs.map(r => `<div class="trow ${changed.includes(r.id) ? "new" : ""}">
      <div class="tt">${esc(r.name.split(" — ")[0])}${changed.includes(r.id) ? `<span class="nb">CHANGED</span>` : `<span class="nb" style="color:#566377;background:#F1F5FA;border-color:#E1E7F0">checked</span>`}</div>
      <div class="tm"><b>${esc(r.type)}</b> · ${esc(r.region)} · updated ${esc(r.last_updated)}</div></div>`).join("");
}

async function ofTotal(path, search) {
  const r = await fetch(`${OF}/${path}.json?search=${encodeURIComponent(search)}&limit=1`);
  if (!r.ok) throw new Error(path + " " + r.status);
  const j = await r.json(); return (j.meta && j.meta.results && j.meta.results.total) || 0;
}
async function runTracker() {
  const btn = $("#runTracker"), status = $("#trkStatus"), out = $("#trkResults");
  btn.disabled = true; $("#trackerPill").classList.add("live");
  runRegisterWatch();
  status.textContent = "Querying openFDA…";
  try {
    const recallURL = `${OF}/recall.json?search=${encodeURIComponent("reason_for_recall:cybersecurity")}&sort=event_date_initiated:desc&limit=30`;
    const [recRes, cyberMaude, k510, recallTotal] = await Promise.all([
      fetch(recallURL).then(r => { if (!r.ok) throw new Error("recall " + r.status); return r.json(); }),
      ofTotal("event", "mdr_text.text:cybersecurity").catch(() => null),
      ofTotal("510k", "decision_date:[2025-01-01+TO+2026-12-31]").catch(() => null),
      ofTotal("recall", "reason_for_recall:cybersecurity").catch(() => null),
    ]);
    const recalls = (recRes.results || []).map(x => ({
      id: x.recall_number || (x.product_description || "").slice(0, 40),
      firm: x.recalling_firm || "—",
      device: (x.openfda && x.openfda.device_name) || (x.product_description || "").slice(0, 90),
      date: ofDate(x.event_date_initiated),
      reason: (x.reason_for_recall || "").slice(0, 160),
    }));
    const prev = getJSON(SNAP_KEY), ids = recalls.map(r => r.id);
    const newIds = prev == null ? [] : ids.filter(i => !prev.includes(i));
    const stored = setJSON(SNAP_KEY, ids);
    $("#pillDelta").textContent = prev == null ? "baseline set" : `${newIds.length ? "+" + newIds.length : "±0"} since last run`;
    $("#pillDelta").className = "delta-chip" + (newIds.length ? " up" : "");
    const summary = `<div class="trow"><div class="tt">Cybersecurity recalls (all time)</div><div class="tm">${recallTotal ?? "—"} device recalls citing cybersecurity</div></div>
      <div class="trow"><div class="tt">Cybersecurity MAUDE reports</div><div class="tm">${cyberMaude ?? "—"} adverse-event reports mention cybersecurity</div></div>
      <div class="trow"><div class="tt">510(k) clearances 2025–2026</div><div class="tm">${k510 ?? "—"} clearances in the window</div></div>`;
    const list = recalls.map(r => `<div class="trow ${newIds.includes(r.id) ? "new" : ""}">
        <div class="tt">${esc(r.device)}${newIds.includes(r.id) ? `<span class="nb">NEW</span>` : ""}</div>
        <div class="tm"><b>${esc(r.firm)}</b> · ${esc(r.date)} · ${esc(r.id)}<br>${esc(r.reason)}</div></div>`).join("");
    out.innerHTML = summary + list;
    const dtxt = prev == null ? "baseline set" : (newIds.length ? `+${newIds.length} new` : "no change");
    status.textContent = `Updated ${new Date().toLocaleString()} · ${recalls.length} recent cyber recalls · Δ ${dtxt}${stored ? "" : " · (delta not persisted here)"}`;
  } catch (e) {
    out.innerHTML = `<div class="trow"><div class="tt">Couldn't reach openFDA</div><div class="tm">${esc(e.message)}. openFDA may be momentarily unavailable, rate-limited, or blocked by your network. The regulation register above and the curated incidents tab still work offline.</div></div>`;
    status.textContent = "Live device feed failed — register still updated.";
  } finally {
    btn.disabled = false; $("#trackerPill").classList.remove("live");
  }
}
$("#runTracker").addEventListener("click", runTracker);
$("#clearSnap").addEventListener("click", () => {
  try { localStorage.removeItem(SNAP_KEY); localStorage.removeItem(REG_SNAP_KEY); } catch (e) {}
  $("#pillDelta").textContent = "baseline cleared"; $("#pillDelta").className = "delta-chip";
  $("#trkStatus").textContent = "Baselines reset — next run sets fresh baselines."; $("#regStatus").textContent = "";
});

renderLens();
render();
