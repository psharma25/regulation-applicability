// Static build — everything runs in the browser from window.SECINTEL_DATA. No backend.
const $ = (s) => document.querySelector(s);
const fmt = (n) => n >= 1e9 ? (n/1e9).toFixed(2)+"B" : n >= 1e6 ? (n/1e6).toFixed(1)+"M" : n >= 1e3 ? (n/1e3).toFixed(0)+"K" : (n||0).toLocaleString();
const DATA = (window.SECINTEL_DATA && window.SECINTEL_DATA.incidents) || [];
const STATE_NAMES = { CA:"California", TX:"Texas", NY:"New York", WA:"Washington", MA:"Massachusetts",
  ME:"Maine", FL:"Florida", IL:"Illinois", NJ:"New Jersey", PA:"Pennsylvania", OH:"Ohio", NC:"North Carolina" };

const state = { domain:"All domains", product_id:"All products", sector:"All sectors",
  stateCode:"All states", yearFrom:null, yearTo:null, sec:false, nation:false, stateAgOnly:false, sortByImpact:false };

const py = (i) => parseInt((i.year || "0").slice(0, 4), 10) || 0;
function domains() { return [...new Set(DATA.flatMap(i => i.domains))].sort(); }
function sectors() { return [...new Set(DATA.map(i => i.sector))].sort(); }
function statesList() { return [...new Set(DATA.flatMap(i => i.states))].sort(); }
function years() { return [...new Set(DATA.map(py).filter(Boolean))].sort((a, b) => a - b); }
function productsByDomain() {
  const out = {};
  DATA.forEach(i => i.domains.forEach(d => { (out[d] ||= []).push({ id: i.id, entity: i.entity }); }));
  Object.values(out).forEach(a => a.sort((x, y) => x.entity.localeCompare(y.entity)));
  return out;
}
function filterRows() {
  return DATA.filter(i => {
    if (state.domain !== "All domains" && !i.domains.includes(state.domain)) return false;
    if (state.product_id !== "All products" && i.id !== state.product_id) return false;
    if (state.sector !== "All sectors" && i.sector !== state.sector) return false;
    if (state.stateCode !== "All states" && !i.states.includes(state.stateCode)) return false;
    if (state.sec && !i.reported_sec) return false;
    if (state.nation && !i.nation_state) return false;
    if (state.stateAgOnly && !i.reported_state_ag) return false;
    const y = py(i);
    if (state.yearFrom && y < state.yearFrom) return false;
    if (state.yearTo && y > state.yearTo) return false;
    return true;
  });
}
function statsOf(rows) {
  const unit = new Set(["individuals", "records"]);
  const by_domain = {}, by_threat = {};
  rows.forEach(i => { i.domains.forEach(d => by_domain[d] = (by_domain[d]||0)+1); by_threat[i.threat_category] = (by_threat[i.threat_category]||0)+1; });
  return {
    incidents: rows.length,
    records_impacted: rows.reduce((s, i) => s + (unit.has(i.unit) ? i.impacted_num : 0), 0),
    nation_state: rows.filter(i => i.nation_state).length,
    reported_sec: rows.filter(i => i.reported_sec).length,
    reported_state_ag: rows.filter(i => i.reported_state_ag).length,
    by_domain: Object.fromEntries(Object.entries(by_domain).sort((a, b) => b[1]-a[1])),
    by_threat: Object.fromEntries(Object.entries(by_threat).sort((a, b) => b[1]-a[1])),
  };
}

function opt(v, label, sel) { return `<option value="${v}"${sel===v?" selected":""}>${label||v}</option>`; }
function buildDomains() { $("#domainSel").innerHTML = opt("All domains") + domains().map(d => opt(d)).join(""); }
function buildSectors() { $("#sectorSel").innerHTML = opt("All sectors") + sectors().map(s => opt(s)).join(""); }
function buildStates() { $("#stateSel").innerHTML = opt("All states") + statesList().map(c => opt(c, STATE_NAMES[c] ? `${c} — ${STATE_NAMES[c]}` : c)).join(""); }
function buildYears() {
  const ys = years(); const lo = ys[0], hi = ys[ys.length - 1];
  state.yearFrom = lo; state.yearTo = hi;
  $("#yearFrom").innerHTML = ys.map(y => opt(String(y), String(y), String(lo))).join("");
  $("#yearTo").innerHTML = ys.map(y => opt(String(y), String(y), String(hi))).join("");
}
function buildProducts() {
  const sel = $("#productSel"); const pbd = productsByDomain();
  let items = state.domain === "All domains"
    ? Object.values(pbd).flat().filter((p, idx, arr) => arr.findIndex(q => q.id === p.id) === idx)
    : (pbd[state.domain] || []);
  items.sort((a, b) => a.entity.localeCompare(b.entity));
  sel.innerHTML = opt("All products") + items.map(p => `<option value="${p.id}">${p.entity}</option>`).join("");
  state.product_id = "All products";
}

function countUp(el, target) {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) { el.textContent = fmt(target); return; }
  const t0 = performance.now(), dur = 600;
  const step = (t) => { const k = Math.min(1, (t-t0)/dur); el.textContent = fmt(Math.round(target*k)); if (k<1) requestAnimationFrame(step); else el.textContent = fmt(target); };
  requestAnimationFrame(step);
}
function paintStats(s) {
  countUp($("#s_incidents"), s.incidents); countUp($("#s_records"), s.records_impacted);
  countUp($("#s_nation"), s.nation_state); countUp($("#s_sec"), s.reported_sec); countUp($("#s_ag"), s.reported_state_ag);
  const e = Object.entries(s.by_domain), max = Math.max(1, ...e.map(x => x[1]));
  $("#domainBars").innerHTML = e.slice(0, 5).map(([d, n]) =>
    `<div class="bar"><span title="${d}">${d}</span><div class="track"><div class="fill" style="width:${(n/max*100).toFixed(0)}%"></div></div><b>${n}</b></div>`).join("")
    || `<span style="color:var(--faint);font-size:12px">No matches</span>`;
}
function paintFeed(rows) {
  $("#feedCount").textContent = rows.length + " shown";
  if (!rows.length) { $("#feed").innerHTML = `<div class="card" style="cursor:default;color:var(--muted)">No incidents match these filters. Widen the year range or reset.</div>`; return; }
  $("#feed").innerHTML = rows.map(i => {
    const tags = [
      `<span class="tag threat">${i.threat_category}</span>`,
      `<span class="tag">${i.sector}</span>`,
      i.reported_sec ? `<span class="tag sec">SEC ${i.sec_item || "8-K"}</span>` : "",
      i.reported_state_ag ? `<span class="tag ag">State AG</span>` : "",
      i.reported_hhs ? `<span class="tag ag">HHS OCR</span>` : "",
      i.nation_state ? `<span class="tag nat">Nation-state</span>` : "",
    ].join("");
    const states = i.states && i.states.length ? `<div class="row"><span class="k">States</span>${i.states.join(", ")}</div>` : "";
    const feed = i.source_feed ? `<div class="row"><span class="k">Feed</span>${i.source_feed}</div>` : "";
    return `<div class="card" data-id="${i.id}">
      <div class="top"><span class="ent">${i.entity}</span><span class="yr">${i.year}</span></div>
      <div class="meta">${tags}</div>
      <div class="impact">${i.impacted}</div>
      <div class="detail">
        ${i.summary ? `<div class="row summary"><span class="k">Summary</span>${i.summary}</div>` : ""}
        <div class="row"><span class="k">Product</span>${i.product}</div>
        <div class="row"><span class="k">Domains</span>${i.domains.join(", ")}</div>
        <div class="row"><span class="k">Threat</span>${i.threat_type}</div>
        ${states}${feed}
        ${i.nation_state ? `<div class="row"><span class="k">Attribution</span>${i.attribution}</div>` : ""}
        <div class="row"><span class="k">Financial</span>${i.financial_loss || "Not disclosed"}</div>
        <div class="row"><span class="k">Data</span>${i.data_types}</div>
        <div class="row"><span class="k">Reputation</span>${i.reputational_impact || "—"}</div>
        <div class="row"><span class="k">Source</span>${(i.source||"").startsWith("http") ? `<a href="${i.source}" target="_blank" rel="noopener">open ↗</a>` : i.source}</div>
      </div></div>`;
  }).join("");
  $("#feed").querySelectorAll(".card").forEach(c => c.addEventListener("click", () => c.classList.toggle("open")));
}
function refresh() {
  let rows = filterRows();
  if (state.sortByImpact) rows = rows.slice().sort((a, b) => (b.impacted_num || 0) - (a.impacted_num || 0));
  paintStats(statsOf(rows)); paintFeed(rows); reflectStats();
}
function reflectStats() {
  const map = { nation: state.nation, sec: state.sec, ag: state.stateAgOnly, records: state.sortByImpact };
  document.querySelectorAll(".stat.clickable").forEach(el => {
    const act = el.getAttribute("data-act");
    el.classList.toggle("active", !!map[act]);
  });
}
function applyStatAct(act) {
  if (act === "all") {
    Object.assign(state, { sec:false, nation:false, stateAgOnly:false, sortByImpact:false });
  } else if (act === "records") {
    state.sortByImpact = !state.sortByImpact;
  } else if (act === "nation") {
    state.nation = !state.nation; const b = document.getElementById("nationToggle"); if (b) b.setAttribute("aria-pressed", state.nation);
  } else if (act === "sec") {
    state.sec = !state.sec; const b = document.getElementById("secToggle"); if (b) b.setAttribute("aria-pressed", state.sec);
  } else if (act === "ag") {
    state.stateAgOnly = !state.stateAgOnly;
  }
  refresh();
}

function renderAgencyStats() {
  const S = window.SECINTEL_STATS;
  const panel = document.getElementById("agencyStats");
  if (!S || !S.sources) { if (panel) panel.style.display = "none"; return; }
  const grid = document.getElementById("sgrid");
  const fnum = (n) => n == null ? "—" : n.toLocaleString();
  grid.innerHTML = S.sources.map((src, si) => {
    const years = (src.rows || []).map((r, ri) => {
      const detail = `<div class="sdetail" id="d_${si}_${ri}">
          <span>${r.note || ""}</span>
          ${r.url ? `<a href="${r.url}" target="_blank" rel="noopener">source ↗</a>` : ""}
        </div>`;
      return `<div class="syear" data-d="d_${si}_${ri}">
          <span class="yr">${r.year}</span>
          <span class="v">${fnum(r.breaches)}</span>
          <span class="v">${fnum(r.affected)}</span>
          <span class="car">▸</span>
        </div>${detail}`;
    }).join("");
    const live = src.live ? `<span class="slive">● live feed</span>` : "";
    return `<div class="scard" data-s="${si}">
      <div class="sh">
        <div class="sh-main"><span class="st-name">${src.label}</span> ${live}<div class="ssum">${src.summary || src.unit}</div></div>
        <span class="car">▸</span>
      </div>
      <div class="sbody">
        <div class="syear syear-head"><span class="yr">Year</span><span class="v">Breaches</span><span class="v">${src.unit.includes("KEV") ? "Total" : "Affected"}</span><span class="car"></span></div>
        ${years}
        <a class="ssrc" href="${src.url}" target="_blank" rel="noopener">Open ${src.label} source ↗</a>
      </div>
    </div>`;
  }).join("");
  // level 1: expand/collapse the card
  grid.querySelectorAll(".scard .sh").forEach(h => h.addEventListener("click", () => h.parentElement.classList.toggle("open")));
  // level 2: expand/collapse a year's detail
  grid.querySelectorAll(".syear[data-d]").forEach(y => y.addEventListener("click", (e) => {
    e.stopPropagation();
    document.getElementById(y.getAttribute("data-d")).classList.toggle("open");
    y.classList.toggle("open");
  }));
}

function analyze(q) {
  const low = q.toLowerCase();
  let domain = state.domain !== "All domains" ? state.domain : null;
  domains().forEach(d => { if (low.includes(d.toLowerCase())) domain = d; });
  const nation = /nation.?state|china|russia|espionage|apt/.test(low) ? true : null;
  const tmap = { ransomware:"Ransomware", credential:"Credential theft", espionage:"Nation-state espionage", device:"Device vulnerability", wiper:"Wiper / destructive", social:"Social engineering", misconfig:"Cloud misconfiguration" };
  let threat = null; Object.keys(tmap).forEach(k => { if (low.includes(k)) threat = tmap[k]; });
  let rows = DATA;
  if (domain) rows = rows.filter(i => i.domains.includes(domain));
  if (nation) rows = rows.filter(i => i.nation_state);
  if (threat) rows = rows.filter(i => i.threat_category === threat);
  if (/how many|statistic|stats|total|count|aggregate/.test(low)) {
    const s = statsOf(rows), scope = domain || "all domains";
    return `Across ${scope}${nation ? " (nation-state only)" : ""}: **${s.incidents} incidents**, ~**${s.records_impacted.toLocaleString()} individuals** impacted, **${s.nation_state}** nation-state, **${s.reported_sec}** reported to the SEC, **${s.reported_state_ag}** to a state AG. Top threats: ${Object.keys(s.by_threat).slice(0,3).join(", ")}.`;
  }
  if (!rows.length) return "No incidents match. Try a domain like 'AI', 'Manufacturing', or 'FDA / Medical Device', or ask for nation-state incidents.";
  return `${rows.length} matching incident(s)${domain ? " in "+domain : ""}${nation ? ", nation-state only" : ""}:\n` +
    rows.slice(0, 8).map(i => {
      const tag = i.nation_state ? ` — nation-state: ${i.attribution.split(";")[0]}` : "";
      const sec = i.reported_sec ? `, SEC ${i.sec_item}` : "";
      return `• ${i.entity} (${i.year}) — ${i.threat_category}, ${i.impacted}${sec}${tag}`;
    }).join("\n");
}
const SUGGEST = ["How many nation-state incidents and who's behind them?", "Summarize the AI risk", "Which incidents were reported to the SEC?", "Compare Manufacturing vs FDA / Medical Device"];
function renderSuggest() {
  $("#suggest").innerHTML = SUGGEST.map(s => `<span class="chip">${s}</span>`).join("");
  $("#suggest").querySelectorAll(".chip").forEach(c => c.addEventListener("click", () => { $("#prompt").value = c.textContent; send(); }));
}
function mdLite(t) { return t.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/\*\*(.+?)\*\*/g,"<strong>$1</strong>").replace(/\n/g,"<br>"); }
function addMsg(role, html) { const d = document.createElement("div"); d.className = "msg "+role; d.innerHTML = html; $("#chat").appendChild(d); $("#chat").scrollTop = $("#chat").scrollHeight; }
function send() {
  const p = $("#prompt"), text = p.value.trim(); if (!text) return;
  addMsg("user", mdLite(text)); p.value = "";
  setTimeout(() => addMsg("bot", mdLite(analyze(text)) + `<div class="trace">mode: in-browser heuristic (static build)</div>`), 120);
}

function init() {
  buildDomains(); buildSectors(); buildStates(); buildYears(); buildProducts();
  $("#domainSel").addEventListener("change", e => { state.domain = e.target.value; buildProducts(); refresh(); });
  $("#sectorSel").addEventListener("change", e => { state.sector = e.target.value; refresh(); });
  $("#stateSel").addEventListener("change", e => { state.stateCode = e.target.value; refresh(); });
  $("#productSel").addEventListener("change", e => { state.product_id = e.target.value; refresh(); });
  $("#yearFrom").addEventListener("change", e => { state.yearFrom = parseInt(e.target.value, 10); refresh(); });
  $("#yearTo").addEventListener("change", e => { state.yearTo = parseInt(e.target.value, 10); refresh(); });
  $("#secToggle").addEventListener("click", e => { state.sec = !state.sec; e.target.setAttribute("aria-pressed", state.sec); refresh(); });
  $("#nationToggle").addEventListener("click", e => { state.nation = !state.nation; e.target.setAttribute("aria-pressed", state.nation); refresh(); });
  $("#resetBtn").addEventListener("click", () => {
    Object.assign(state, { domain:"All domains", product_id:"All products", sector:"All sectors", stateCode:"All states", sec:false, nation:false, stateAgOnly:false, sortByImpact:false });
    $("#domainSel").value="All domains"; $("#sectorSel").value="All sectors"; $("#stateSel").value="All states";
    $("#secToggle").setAttribute("aria-pressed",false); $("#nationToggle").setAttribute("aria-pressed",false);
    buildYears(); $("#yearFrom").value=String(state.yearFrom); $("#yearTo").value=String(state.yearTo);
    buildProducts(); refresh();
  });
  $("#sendBtn").addEventListener("click", send);
  $("#prompt").addEventListener("keydown", e => { if (e.key==="Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
  document.querySelectorAll(".stat.clickable").forEach(el =>
    el.addEventListener("click", () => applyStatAct(el.getAttribute("data-act"))));
  renderSuggest(); renderAgencyStats(); refresh();
}
init();
