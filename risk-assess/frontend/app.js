const $ = (s) => document.querySelector(s);
const messages = $("#messages");
const SUGGESTIONS = [
  "How does ISO 14971 estimate probability of harm?",
  "What is Expected Annual Loss in finance risk?",
  "Explain reputation, financial and IP loss scoring",
  "Download the medical template",
];

function addMsg(html, who) {
  const div = document.createElement("div");
  div.className = `msg ${who}`;
  div.innerHTML = html;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return div;
}

function esc(s) {
  return (s || "").replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

async function loadHealth() {
  try {
    const r = await fetch("/api/health");
    const d = await r.json();
    const el = $("#status");
    el.textContent = `● ${d.retrieval_mode} · ${d.llm} · ${d.knowledge_chunks} chunks`;
    el.classList.add("ok");
  } catch {
    $("#status").textContent = "API offline";
  }
}

async function loadForms() {
  const r = await fetch("/api/domains");
  const d = await r.json();
  const wrap = $("#forms");
  wrap.innerHTML = "";
  d.domains.forEach((dom) => {
    const card = document.createElement("div");
    card.className = "form-card";
    card.innerHTML = `<h3>${esc(dom.label)}</h3><p>${esc(dom.description)}</p>
      <a href="/api/forms/${dom.id}/download">⬇ Download Excel</a>`;
    wrap.appendChild(card);
  });
}

function renderSuggestions() {
  const box = $("#suggestions");
  SUGGESTIONS.forEach((s) => {
    const c = document.createElement("span");
    c.className = "chip";
    c.textContent = s;
    c.onclick = () => { $("#chat-input").value = s; $("#chat-form").requestSubmit(); };
    box.appendChild(c);
  });
}

async function send(message) {
  addMsg(esc(message), "user");
  const thinking = addMsg("…", "bot");
  try {
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const d = await r.json();
    let html = esc(d.message || "");
    if (d.action === "download" && d.download_url) {
      html += `<a class="dl" href="${d.download_url}">⬇ Download ${esc(d.label)}</a>`;
    }
    if (d.sources && d.sources.length) {
      html += `<span class="src">sources: ${d.sources.map(esc).join(", ")} · engine: ${esc(d.engine || "")}</span>`;
    }
    thinking.innerHTML = html;
    messages.scrollTop = messages.scrollHeight;
  } catch (e) {
    thinking.textContent = "Error contacting the API.";
  }
}

$("#chat-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const v = $("#chat-input").value.trim();
  if (!v) return;
  $("#chat-input").value = "";
  send(v);
});

async function loadMapping(domain) {
  const r = await fetch(`/api/library/${domain}`);
  const d = await r.json();
  $("#mapping-title").textContent = d.title;
  const t = $("#mapping-table");
  t.innerHTML =
    "<thead><tr>" + d.columns.map((c) => `<th>${esc(c)}</th>`).join("") + "</tr></thead>" +
    "<tbody>" + d.rows.map((row) =>
      "<tr>" + row.map((cell) => `<td>${esc(String(cell))}</td>`).join("") + "</tr>").join("") +
    "</tbody>";
}

$("#mapping-domain").addEventListener("change", (e) => loadMapping(e.target.value));

renderSuggestions();
loadHealth();
loadForms();
loadMapping("medical");
