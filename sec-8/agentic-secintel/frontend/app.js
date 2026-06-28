const $ = (s) => document.querySelector(s);
const fmt = (n) => n >= 1e9 ? (n/1e9).toFixed(2)+"B" : n >= 1e6 ? (n/1e6).toFixed(1)+"M" : n >= 1e3 ? (n/1e3).toFixed(0)+"K" : (n||0).toLocaleString();

let META = null;
let history = [];
const state = { domain: "All domains", product_id: "All products", sector: "All sectors",
  stateCode: "All states", yearFrom: null, yearTo: null, sec: false, nation: false,
  stateAgOnly: false, sortByImpact: false };

async function api(path, opts) {
  const r = await fetch(path, opts);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
function qs() {
  const p = new URLSearchParams();
  if (state.domain !== "All domains") p.set("domain", state.domain);
  if (state.product_id !== "All products") p.set("product_id", state.product_id);
  if (state.sector !== "All sectors") p.set("sector", state.sector);
  if (state.stateCode !== "All states") p.set("state", state.stateCode);
  if (state.yearFrom != null) p.set("year_from", state.yearFrom);
  if (state.yearTo != null) p.set("year_to", state.yearTo);
  if (state.sec) p.set("reported_sec", "true");
  if (state.nation) p.set("nation_state", "true");
  if (state.stateAgOnly) p.set("reported_state_ag", "true");
  return p.toString() ? "?" + p.toString() : "";
}
const STATE_NAMES = { CA:"California", TX:"Texas", NY:"New York", WA:"Washington", MA:"Massachusetts",
  ME:"Maine", FL:"Florida", IL:"Illinois", NJ:"New Jersey", PA:"Pennsylvania", OH:"Ohio", NC:"North Carolina" };

async function loadMeta(preserveDomain) {
  META = await api("/api/meta");
  const badge = $("#modeBadge");
  badge.classList.remove("live", "heur");
  if (META.ollama) { badge.classList.add("live"); $("#modeText").textContent = "ollama · " + META.model; }
  else { badge.classList.add("heur"); $("#modeText").textContent = "heuristic (Ollama offline)"; }

  const dsel = $("#domainSel");
  const keep = preserveDomain && META.domains.includes(state.domain) ? state.domain : "All domains";
  dsel.innerHTML = `<option>All domains</option>` + META.domains.map(d => `<option>${d}</option>`).join("");
  dsel.value = keep; state.domain = keep;

  $("#sectorSel").innerHTML = `<option>All sectors</option>` + (META.sectors||[]).map(s => `<option>${s}</option>`).join("");
  $("#sectorSel").value = (preserveDomain && state.sector) || "All sectors";
  $("#stateSel").innerHTML = `<option value="All states">All states</option>` +
    (META.states||[]).map(c => `<option value="${c}">${STATE_NAMES[c] ? c+" — "+STATE_NAMES[c] : c}</option>`).join("");
  $("#stateSel").value = (preserveDomain && state.stateCode) || "All states";

  const ys = META.years || [];
  if (ys.length) {
    const lo = ys[0], hi = ys[ys.length-1];
    if (state.yearFrom == null || !preserveDomain) state.yearFrom = lo;
    if (state.yearTo == null || !preserveDomain) state.yearTo = hi;
    $("#yearFrom").innerHTML = ys.map(y => `<option${y===state.yearFrom?" selected":""}>${y}</option>`).join("");
    $("#yearTo").innerHTML = ys.map(y => `<option${y===state.yearTo?" selected":""}>${y}</option>`).join("");
  }
  buildProducts();
  renderSynced(META.live);
}

function renderSynced(liveMeta) {
  const el = $("#syncedText");
  if (liveMeta && liveMeta.fetched_at) {
    const when = new Date(liveMeta.fetched_at);
    const ok = (liveMeta.sources || []).filter(s => s.status === "ok").length;
    el.textContent = `tracker run ${timeAgo(when)} · ${liveMeta.count} records · ${ok} live sources`;
    el.classList.add("fresh");
  } else {
    el.textContent = "tracker not run yet"; el.classList.remove("fresh");
  }
  renderProvenance(liveMeta);
}
function renderProvenance(liveMeta) {
  const panel = $("#provenance"), grid = $("#provGrid");
  if (!liveMeta || !liveMeta.sources || !liveMeta.sources.length) { panel.hidden = true; return; }
  panel.hidden = false;
  $("#provWindow").textContent = liveMeta.window ? "window " + liveMeta.window : "";
  grid.innerHTML = liveMeta.sources.map(s => {
    const st = (s.status || "manual");
    const link = s.source_url ? `<a href="${s.source_url}" target="_blank" rel="noopener" title="${s.note||""}">${s.label}</a>` : `<span>${s.label}</span>`;
    return `<div class="psrc"><span class="st ${st}"></span><span class="pl">${link}<span class="pn">${st}${s.note ? " · "+s.note : ""}</span></span><span class="pc">${s.count||0}</span></div>`;
  }).join("");
}
function timeAgo(d) {
  const s = Math.max(1, Math.round((Date.now() - d.getTime()) / 1000));
  if (s < 60) return s + "s ago";
  if (s < 3600) return Math.round(s / 60) + "m ago";
  if (s < 86400) return Math.round(s / 3600) + "h ago";
  return d.toLocaleDateString();
}

async function runLiveRefresh() {
  const btn = $("#liveBtn");
  btn.classList.add("loading"); btn.disabled = true;
  $("#liveLabel").textContent = "Running…";
  try {
    const res = await api("/api/tracker/run", { method: "POST" });
    if (!res.ok) {
      $("#syncedText").textContent = "tracker failed — " + (res.hint || res.error || "check connection");
    } else {
      await loadMeta(true);   // picks up new live domains (SEC 8-K/10-K, HHS, State AG)
      await refresh();
    }
  } catch (e) {
    $("#syncedText").textContent = "tracker failed — is the server running?";
  } finally {
    btn.classList.remove("loading"); btn.disabled = false; $("#liveLabel").textContent = "Run tracker";
  }
}

async function init() {
  await loadMeta(false);
  const dsel = $("#domainSel");
  dsel.addEventListener("change", () => { state.domain = dsel.value; state.product_id = "All products"; buildProducts(); refresh(); });
  $("#productSel").addEventListener("change", (e) => { state.product_id = e.target.value; refresh(); });
  $("#sectorSel").addEventListener("change", (e) => { state.sector = e.target.value; refresh(); });
  $("#stateSel").addEventListener("change", (e) => { state.stateCode = e.target.value; refresh(); });
  $("#yearFrom").addEventListener("change", (e) => { state.yearFrom = parseInt(e.target.value, 10); refresh(); });
  $("#yearTo").addEventListener("change", (e) => { state.yearTo = parseInt(e.target.value, 10); refresh(); });
  $("#secToggle").addEventListener("click", (e) => { state.sec = !state.sec; e.target.setAttribute("aria-pressed", state.sec); refresh(); });
  $("#nationToggle").addEventListener("click", (e) => {
    state.nation = !state.nation; e.target.setAttribute("aria-pressed", state.nation); refresh();
  });
  $("#resetBtn").addEventListener("click", () => {
    Object.assign(state, { domain:"All domains", product_id:"All products", sector:"All sectors", stateCode:"All states", sec:false, nation:false, stateAgOnly:false, sortByImpact:false });
    dsel.value = "All domains"; $("#sectorSel").value = "All sectors"; $("#stateSel").value = "All states";
    $("#secToggle").setAttribute("aria-pressed", false); $("#nationToggle").setAttribute("aria-pressed", false);
    const ys = META.years || [];
    if (ys.length) { state.yearFrom = ys[0]; state.yearTo = ys[ys.length-1]; $("#yearFrom").value = String(ys[0]); $("#yearTo").value = String(ys[ys.length-1]); }
    buildProducts(); refresh();
  });
  $("#liveBtn").addEventListener("click", runLiveRefresh);
  $("#sendBtn").addEventListener("click", send);
  $("#prompt").addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
  document.querySelectorAll(".stat.clickable").forEach(el =>
    el.addEventListener("click", () => applyStatAct(el.getAttribute("data-act"))));
  renderSuggest();
  loadAgencyStats();
  refresh();
}

async function loadAgencyStats() {
  try {
    const S = await api("/api/agency-stats");
    const panel = $("#agencyStats");
    if (!S || !S.sources || !S.sources.length) { panel.style.display = "none"; return; }
    const fnum = (n) => n == null ? "—" : n.toLocaleString();
    $("#sgrid").innerHTML = S.sources.map((src, si) => {
      const years = (src.rows || []).map((r, ri) => {
        const detail = `<div class="sdetail" id="d_${si}_${ri}"><span>${r.note || ""}</span>${r.url ? `<a href="${r.url}" target="_blank" rel="noopener">source ↗</a>` : ""}</div>`;
        return `<div class="syear" data-d="d_${si}_${ri}"><span class="yr">${r.year}</span><span class="v">${fnum(r.breaches)}</span><span class="v">${fnum(r.affected)}</span><span class="car">▸</span></div>${detail}`;
      }).join("");
      const live = src.live ? `<span class="slive">● live feed</span>` : "";
      return `<div class="scard" data-s="${si}">
        <div class="sh"><div class="sh-main"><span class="st-name">${src.label}</span> ${live}<div class="ssum">${src.summary || src.unit}</div></div><span class="car">▸</span></div>
        <div class="sbody">
          <div class="syear syear-head"><span class="yr">Year</span><span class="v">Breaches</span><span class="v">${src.unit.includes("KEV") ? "Total" : "Affected"}</span><span class="car"></span></div>
          ${years}
          <a class="ssrc" href="${src.url}" target="_blank" rel="noopener">Open ${src.label} source ↗</a>
        </div></div>`;
    }).join("");
    $("#sgrid").querySelectorAll(".scard .sh").forEach(h => h.addEventListener("click", () => h.parentElement.classList.toggle("open")));
    $("#sgrid").querySelectorAll(".syear[data-d]").forEach(y => y.addEventListener("click", (e) => {
      e.stopPropagation();
      document.getElementById(y.getAttribute("data-d")).classList.toggle("open");
      y.classList.toggle("open");
    }));
  } catch (e) { $("#agencyStats").style.display = "none"; }
}

function buildProducts() {
  const sel = $("#productSel");
  let items = [];
  if (state.domain === "All domains") {
    const seen = new Set();
    Object.values(META.products_by_domain).flat().forEach(p => { if (!seen.has(p.id)) { seen.add(p.id); items.push(p); } });
  } else {
    items = META.products_by_domain[state.domain] || [];
  }
  items.sort((a, b) => a.entity.localeCompare(b.entity));
  sel.innerHTML = `<option value="All products">All products</option>` +
    items.map(p => `<option value="${p.id}">${p.entity}</option>`).join("");
}

async function refresh() {
  const [stats, list] = await Promise.all([api("/api/stats" + qs()), api("/api/incidents" + qs())]);
  let rows = list.incidents;
  if (state.sortByImpact) rows = rows.slice().sort((a, b) => (b.impacted_num || 0) - (a.impacted_num || 0));
  paintStats(stats);
  paintFeed(rows);
  reflectStats();
}
function reflectStats() {
  const map = { nation: state.nation, sec: state.sec, ag: state.stateAgOnly, records: state.sortByImpact };
  document.querySelectorAll(".stat.clickable").forEach(el => el.classList.toggle("active", !!map[el.getAttribute("data-act")]));
}
function applyStatAct(act) {
  if (act === "all") Object.assign(state, { sec:false, nation:false, stateAgOnly:false, sortByImpact:false });
  else if (act === "records") state.sortByImpact = !state.sortByImpact;
  else if (act === "nation") { state.nation = !state.nation; const b=$("#nationToggle"); if(b) b.setAttribute("aria-pressed", state.nation); }
  else if (act === "sec") { state.sec = !state.sec; const b=$("#secToggle"); if(b) b.setAttribute("aria-pressed", state.sec); }
  else if (act === "ag") state.stateAgOnly = !state.stateAgOnly;
  refresh();
}

function countUp(el, target) {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) { el.textContent = fmt(target); return; }
  const start = 0, dur = 600, t0 = performance.now();
  const step = (t) => {
    const k = Math.min(1, (t - t0) / dur);
    el.textContent = fmt(Math.round(target * (0.2 + 0.8 * k) * (k === 1 ? 1 : 1)));
    if (k < 1) requestAnimationFrame(step); else el.textContent = fmt(target);
  };
  requestAnimationFrame(step);
}

function paintStats(s) {
  countUp($("#s_incidents"), s.incidents);
  countUp($("#s_records"), s.records_impacted);
  countUp($("#s_nation"), s.nation_state);
  countUp($("#s_sec"), s.reported_sec);
  countUp($("#s_ag"), s.reported_state_ag);
  const entries = Object.entries(s.by_domain);
  const max = Math.max(1, ...entries.map(e => e[1]));
  $("#domainBars").innerHTML = entries.slice(0, 5).map(([d, n]) =>
    `<div class="bar"><span title="${d}">${d}</span><div class="track"><div class="fill" style="width:${(n/max*100).toFixed(0)}%"></div></div><b>${n}</b></div>`
  ).join("") || `<span style="color:var(--faint);font-size:12px">No matches</span>`;
}

function paintFeed(rows) {
  $("#feedCount").textContent = rows.length + " shown";
  if (!rows.length) { $("#feed").innerHTML = `<div class="card" style="cursor:default;color:var(--muted)">No incidents match this selection. Try another domain or clear filters.</div>`; return; }
  $("#feed").innerHTML = rows.map(i => {
    const tags = [
      `<span class="tag threat">${i.threat_category}</span>`,
      i.sector ? `<span class="tag">${i.sector}</span>` : "",
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
        <div class="row"><span class="k">Threat</span>${i.threat_type}</div>
        ${states}${feed}
        ${i.nation_state ? `<div class="row"><span class="k">Attribution</span>${i.attribution}</div>` : (i.attribution ? `<div class="row"><span class="k">Actor</span>${i.attribution}</div>` : "")}
        <div class="row"><span class="k">Financial</span>${i.financial_loss || "Not disclosed"}</div>
        <div class="row"><span class="k">Data</span>${i.data_types}</div>
        <div class="row"><span class="k">Reputation</span>${i.reputational_impact || "—"}</div>
        <div class="row"><span class="k">Source</span><a href="${i.source}" target="_blank" rel="noopener">${(i.source||"").startsWith("http") ? "open source ↗" : i.source}</a></div>
      </div></div>`;
  }).join("");
  $("#feed").querySelectorAll(".card").forEach(c =>
    c.addEventListener("click", () => c.classList.toggle("open")));
}

const SUGGEST = [
  "How many nation-state incidents and who's behind them?",
  "Summarize the risk for this domain",
  "Which incidents were reported to the SEC?",
  "Compare Manufacturing vs FDA / Medical Device",
];
function renderSuggest() {
  $("#suggest").innerHTML = SUGGEST.map(s => `<span class="chip">${s}</span>`).join("");
  $("#suggest").querySelectorAll(".chip").forEach(c =>
    c.addEventListener("click", () => { $("#prompt").value = c.textContent; send(); }));
}

function addMsg(role, html) {
  const d = document.createElement("div");
  d.className = "msg " + role; d.innerHTML = html;
  $("#chat").appendChild(d); $("#chat").scrollTop = $("#chat").scrollHeight;
  return d;
}
function mdLite(t) {
  return t.replace(/&/g,"&amp;").replace(/</g,"&lt;")
          .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
          .replace(/\n/g, "<br>");
}

async function send() {
  const p = $("#prompt"); const text = p.value.trim();
  if (!text) return;
  addMsg("user", mdLite(text)); p.value = "";
  history.push({ role: "user", content: text });
  $("#sendBtn").disabled = true;
  const wait = addMsg("bot", `<span class="typing"><span></span><span></span><span></span></span>`);
  try {
    const res = await api("/api/agent", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, filters: state, history })
    });
    let html = mdLite(res.reply);
    if (res.trace && res.trace.length) {
      html += `<div class="trace">▸ ${res.trace.map(t => t.tool + "(" + JSON.stringify(t.args).slice(0,60) + ") → " + t.result_summary).join("<br>▸ ")}</div>`;
    }
    html += `<div class="trace">mode: ${res.mode}</div>`;
    wait.innerHTML = html;
    history.push({ role: "assistant", content: res.reply });
  } catch (e) {
    wait.innerHTML = "Couldn't reach the analyst service. Is the server running?";
  } finally {
    $("#sendBtn").disabled = false; $("#chat").scrollTop = $("#chat").scrollHeight;
  }
}

init();
