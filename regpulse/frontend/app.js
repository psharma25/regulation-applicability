// RegPulse frontend — talks to the FastAPI backend at same origin.
let regs=[], controls=[], regFilter="all", regSearch="", ctrlFilter="all", ctrlSearch="";
let token=localStorage.getItem("rp_token")||"", lastApplicable=null, lastProfile=null, authMode="login";

// ----- example scenarios & known company/product presets -----
const EXAMPLES=[
 {name:"Insulin pump + cloud (US+EU)",org:"Acme MedTech",prod:"Connected insulin pump",markets:["United States","EU"],product_types:["medical_device"],data_types:["phi","eu_personal"],flags:["software","connected","ai"]},
 {name:"AI diagnostic SaaS (EU)",org:"Cortex Diagnostics",prod:"AI imaging triage",markets:["EU"],product_types:["samd"],data_types:["eu_personal"],flags:["software","connected","ai"]},
 {name:"B2B SaaS (US+EU, PII)",org:"Northwind",prod:"Workflow SaaS",markets:["United States","EU"],product_types:["saas"],data_types:["pii"],flags:["software","connected"]},
 {name:"Fintech payments app (US+EU)",org:"PayForge",prod:"Payments platform",markets:["United States","EU"],product_types:["fintech"],data_types:["payment","financial","pii"],flags:["software","connected"]},
 {name:"EdTech for K-12 (US)",org:"LearnLoop",prod:"Classroom SaaS",markets:["United States"],product_types:["edtech"],data_types:["children","pii"],flags:["software","connected"]},
 {name:"US-government cloud SaaS (FedRAMP)",org:"GovStack",prod:"Agency platform",markets:["United States"],product_types:["saas"],data_types:["pii"],flags:["software","connected","us_gov"]},
];
const COMPANIES=[
 {label:"Medtronic — MiniMed insulin pump",org:"Medtronic",prod:"MiniMed insulin pump",markets:["United States","EU"],product_types:["medical_device"],data_types:["phi","eu_personal"],flags:["software","connected"]},
 {label:"Philips — IntelliVue patient monitor",org:"Philips",prod:"IntelliVue monitor",markets:["United States","EU","Japan"],product_types:["medical_device"],data_types:["phi","eu_personal"],flags:["software","connected"]},
 {label:"Salesforce — CRM SaaS",org:"Salesforce",prod:"CRM platform",markets:["United States","EU","United Kingdom"],product_types:["saas"],data_types:["pii"],flags:["software","connected","ai"]},
 {label:"Workday — HR & finance SaaS",org:"Workday",prod:"HR/Finance SaaS",markets:["United States","EU"],product_types:["saas"],data_types:["pii","financial"],flags:["software","connected"]},
 {label:"Stripe — payments platform",org:"Stripe",prod:"Payments platform",markets:["United States","EU","United Kingdom"],product_types:["fintech"],data_types:["payment","financial","pii"],flags:["software","connected"]},
 {label:"Plaid — fintech data network",org:"Plaid",prod:"Financial data API",markets:["United States"],product_types:["fintech"],data_types:["financial","pii"],flags:["software","connected"]},
 {label:"Datadog — observability SaaS",org:"Datadog",prod:"Observability platform",markets:["United States","EU"],product_types:["saas"],data_types:["pii"],flags:["software","connected"]},
 {label:"Snowflake — data cloud",org:"Snowflake",prod:"Data cloud",markets:["United States","EU"],product_types:["saas"],data_types:["pii","financial"],flags:["software","connected","ai"]},
 {label:"Coursera — EdTech platform",org:"Coursera",prod:"Online learning",markets:["United States","EU"],product_types:["edtech"],data_types:["pii","children"],flags:["software","connected"]},
 {label:"Tempus — AI precision-medicine SaaS",org:"Tempus",prod:"Precision-medicine AI",markets:["United States"],product_types:["healthcare_saas"],data_types:["phi"],flags:["software","connected","ai"]},
]

const $=s=>document.querySelector(s);
function show(el){el.classList.add("on")} function hide(el){el.classList.remove("on")}
function go(id){document.getElementById(id).scrollIntoView({behavior:"smooth"})}
function tog(el){el.classList.toggle("on")}
function picked(id){return [...document.querySelectorAll('#'+id+' .pill.on')].map(p=>p.dataset.v)}
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function dl(name,text,type){const b=new Blob([text],{type});const u=URL.createObjectURL(b);const a=document.createElement('a');a.href=u;a.download=name;a.click();URL.revokeObjectURL(u);}

async function api(path,opts={}){
  opts.headers=Object.assign({"Content-Type":"application/json"},opts.headers||{});
  if(token) opts.headers["Authorization"]="Bearer "+token;
  const r=await fetch(path,opts);
  if(!r.ok) throw new Error((await r.json().catch(()=>({}))).detail||r.statusText);
  return r;
}

// ---- HTML + Excel export helpers ----
function saveHTML(filename,title,bodyHTML){
  const css="body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#1a1917;max-width:1000px;margin:32px auto;padding:0 24px;line-height:1.55}h1{font-size:26px;margin:0 0 4px}h2{font-size:15px;text-transform:uppercase;letter-spacing:.05em;color:#1a3a5c;border-bottom:2px solid #e2e0d8;padding-bottom:6px;margin:26px 0 10px}table{border-collapse:collapse;width:100%;font-size:13px;margin-top:8px}th,td{border:1px solid #e2e0d8;padding:8px 10px;text-align:left;vertical-align:top}th{background:#1a3a5c;color:#fff}tr:nth-child(even) td{background:#f7f6f3}.muted{color:#9c9a8e}a{color:#1a3a5c}.foot{margin-top:30px;font-size:11px;color:#9c9a8e;border-top:1px solid #e2e0d8;padding-top:12px}";
  const doc=`<!DOCTYPE html><html><head><meta charset="utf-8"><title>${esc(title)}</title><style>${css}</style></head><body>${bodyHTML}<div class="foot">Generated by RegPulse Intelligence on ${new Date().toLocaleString()}. Planning intelligence only — not legal, regulatory or audit advice. Validate against the official source for each regulation.</div></body></html>`;
  dl(filename,doc,'text/html');
}
function saveXLSX(filename,sheets){
  if(window.XLSX){
    const wb=XLSX.utils.book_new();
    sheets.forEach(([name,rows])=>{XLSX.utils.book_append_sheet(wb,XLSX.utils.aoa_to_sheet(rows),name.slice(0,31));});
    XLSX.writeFile(wb,filename);
  }else{
    let html='<html xmlns:x="urn:schemas-microsoft-com:office:excel"><head><meta charset="utf-8"></head><body>';
    sheets.forEach(([name,rows])=>{html+=`<h3>${esc(name)}</h3><table border="1">`+rows.map(r=>'<tr>'+r.map(c=>`<td>${esc(String(c==null?'':c)).replace(/\n/g,'<br>')}</td>`).join('')+'</tr>').join('')+'</table>';});
    html+='</body></html>';
    dl(filename.replace(/\.xlsx$/,'.xls'),html,'application/vnd.ms-excel');
  }
}
function savePDF(filename,title,meta,sections,table){
  const J=window.jspdf&&window.jspdf.jsPDF;
  if(J){
    const doc=new J({unit:'pt',format:'a4'});
    const W=doc.internal.pageSize.getWidth(),H=doc.internal.pageSize.getHeight(),M=42;let y=50;
    function setColor(c){if(Array.isArray(c))doc.setTextColor(c[0],c[1],c[2]);else doc.setTextColor(c==null?20:c);}
    function text(t,fs,bold,color){doc.setFont('helvetica',bold?'bold':'normal');doc.setFontSize(fs);setColor(color);
      doc.splitTextToSize(String(t||''),W-2*M).forEach(ln=>{if(y>H-50){doc.addPage();y=50;}doc.text(ln,M,y);y+=fs+4;});}
    text(title,16,true,20);y+=2;doc.setDrawColor(200);doc.line(M,y,W-M,y);y+=14;
    text(meta,9,false,120);y+=8;
    sections.forEach(([h,t])=>{if(y>H-90){doc.addPage();y=50;}text(h,11,true,[26,58,92]);text(t,10,false,60);y+=6;});
    if(table&&doc.autoTable){doc.autoTable({startY:Math.min(y+4,H-60),head:[table.head],body:table.rows,
      styles:{fontSize:8,cellPadding:3,valign:'top',overflow:'linebreak'},headStyles:{fillColor:[26,58,92]},
      alternateRowStyles:{fillColor:[247,246,243]},margin:{left:M,right:M}});}
    doc.save(filename);
  }else{
    let html='<h1>'+esc(title)+'</h1><p style="color:#888">'+esc(meta)+'</p>';
    sections.forEach(([h,t])=>{html+='<h2>'+esc(h)+'</h2><p>'+esc(t)+'</p>';});
    if(table){html+='<table><thead><tr>'+table.head.map(x=>'<th>'+esc(x)+'</th>').join('')+'</tr></thead><tbody>'+table.rows.map(r=>'<tr>'+r.map(c=>'<td>'+esc(String(c==null?'':c)).replace(/\n/g,'<br>')+'</td>').join('')+'</tr>').join('')+'</tbody></table>';}
    const css='body{font-family:Arial,sans-serif;max-width:900px;margin:24px auto;line-height:1.5;color:#1a1917}h1{font-size:22px}h2{font-size:14px;color:#1a3a5c;border-bottom:1px solid #ccc;margin-top:18px}table{border-collapse:collapse;width:100%;font-size:12px}th,td{border:1px solid #ccc;padding:6px;text-align:left;vertical-align:top}th{background:#1a3a5c;color:#fff}';
    const w=window.open('','_blank');
    if(w){w.document.write('<!DOCTYPE html><html><head><meta charset="utf-8"><title>'+esc(filename)+'</title><style>'+css+'</style></head><body>'+html+'<scr'+'ipt>window.onload=function(){setTimeout(function(){window.print();},250);}</scr'+'ipt></body></html>');w.document.close();}
    else{alert('Allow pop-ups to print to PDF, or use the HTML / Excel download instead.');}
  }
}
function downloadRegPDF(r){
  const bf=r.briefing||{};
  const rows=controls.filter(c=>(c.regulations||[]).includes(r.id)).sort((a,b)=>b.score-a.score);
  const meta=(r.body||'')+' · '+(r.jurisdictions||[]).join(', ')+' · '+(r.emerging?'Emerging':'In force');
  const sections=[
    ['What it is',bf.what_it_is||r.summary],
    ['Why it is important',bf.why_important||''],
    ['Detailed description',bf.detail||''],
    ['What changed ('+(bf.change_date||'')+', '+(bf.change_impact||'low')+' impact)',(bf.delta||'')+'  Impact: '+(bf.change_note||'')],
    ['Official source',r.url]
  ];
  const table={head:['#','Control','Why it matters','Priority','Severity'],
    rows:rows.map((c,i)=>[i+1,c.title,c.explanation,c.priority,c.severity+' · '+c.score])};
  savePDF(r.id+'_briefing.pdf',r.name+' ('+r.id+')',meta,sections,table);
}

// ----- init -----
async function init(){
  try{ regs=await(await api("/api/regulations")).json(); $("#sRegs").textContent=regs.length; renderRegs(); }catch(e){console.error(e);}
  try{ controls=await(await api("/api/controls")).json(); $("#sCtrls").textContent=controls.length; renderCtrls(); }catch(e){console.error(e);}
  try{ renderDelta(await(await api("/api/scan/delta")).json()); }catch(e){ $("#scanStatus").textContent="No scan yet — run one."; }
  // presets
  const sel=$("#companyPreset"); COMPANIES.forEach((c,i)=>{const o=document.createElement("option");o.value=i;o.textContent=c.label;sel.appendChild(o);});
  $("#exampleBtns").innerHTML=EXAMPLES.map((e,i)=>`<button class="btn ghost sm" onclick="loadExample(${i})">${e.name}</button>`).join("");
  refreshAuthUI();
}

// ----- presets -----
function setPills(group,vals){document.querySelectorAll('#'+group+' .pill').forEach(p=>p.classList.toggle('on',(vals||[]).includes(p.dataset.v)));}
function applyProfile(p){
  $("#pName").value=p.org?`${p.org} — ${p.prod}`:'';
  setPills("ptypes",p.product_types);setPills("markets",p.markets);setPills("datatypes",p.data_types);setPills("flags",p.flags);
  runApply();
}
function loadCompany(i){if(i==='')return;applyProfile(COMPANIES[+i]);}
function loadExample(i){applyProfile(EXAMPLES[+i]);}

// ----- regulations -----
function setRegFilter(el){document.querySelectorAll('#regChips .chip').forEach(c=>c.classList.remove('active'));el.classList.add('active');regFilter=el.dataset.d;renderRegs();}
function renderRegs(){
  let list=regs.filter(r=>regFilter==="all"||r.domain===regFilter);
  if(regSearch){const q=regSearch.toLowerCase();list=list.filter(r=>(r.name+r.summary+r.id).toLowerCase().includes(q));}
  $("#regGrid").innerHTML=list.map(r=>`
    <div class="card" onclick="showReg('${r.id}')">
      <h4>${r.id}</h4><div class="title">${r.name}</div>
      <div class="desc">${(r.summary||'').slice(0,120)}…</div>
      <div class="foot"><span class="muted">${(r.jurisdictions||[]).slice(0,2).join(', ')}</span>
        <span>${r.emerging?'<span class="badge b-emerging">Emerging</span> ':''}${r.change_type?`<span class="badge b-${r.change_type}">${r.change_type}</span>`:''}</span></div>
    </div>`).join("");
}
async function showReg(id){
  const r=await(await api("/api/regulations/"+id)).json();
  const bf=r.briefing||{};
  const chg=`<span class="badge b-${bf.change||'unchanged'}">${bf.change||'unchanged'}</span> <span class="tag t-${bf.change_impact==='high'?'Critical':bf.change_impact==='medium'?'High':'Low'}">${bf.change_impact||'low'} impact</span>`;
  $("#modalInner").innerHTML=`
    <div class="modal-head"><div><div class="muted" style="font-family:'DM Mono',monospace;color:var(--accent)">${r.id} · ${r.body||''} · ${(r.jurisdictions||[]).join(', ')}</div><h3>${esc(r.name)}</h3></div><button class="modal-x" onclick="closeModal()">✕</button></div>
    <div class="modal-body">
      <div class="mlabel">What it is</div><div style="font-size:13.5px;color:var(--text-2)">${esc(bf.what_it_is||r.summary)}</div>
      <div class="mlabel">Why it is important</div><div style="font-size:13.5px;color:var(--text-2)">${esc(bf.why_important||'')}</div>
      <div class="mlabel">Detailed description</div><div style="font-size:13.5px;color:var(--text-2)">${esc(bf.detail||'')}</div>
      <div class="mlabel">What changed · ${bf.change_date||''}</div><div class="ob-b" style="display:block;border:none;padding:12px 14px;background:var(--off);border-radius:8px">${chg}<p style="margin-top:8px">${esc(bf.delta||r.latest_delta||'No scan yet.')}</p><p style="margin-top:6px"><b>Impact:</b> ${esc(bf.change_note||'')}</p></div>
      <div class="mlabel">Official source</div><div style="font-size:13px"><a href="${esc(r.url)}" target="_blank" rel="noopener" style="color:var(--accent);font-weight:500">${esc(r.url)||'—'} ↗</a></div>
      <div class="mlabel">Mapped controls (${(r.mapped_controls||[]).length})</div><div style="font-size:13px;color:var(--text-2)">${(r.mapped_controls||[]).join(', ')||'—'}</div>
    </div>
    <div class="modal-foot"><button class="btn ghost sm" onclick="closeModal()">Close</button>
      <button class="btn ghost sm" onclick='downloadRegPDF(${JSON.stringify(r)})'>Briefing (PDF)</button>
      <button class="btn ghost sm" onclick='downloadRegHTML(${JSON.stringify(r)})'>Briefing (HTML)</button>
      <button class="btn sm" onclick="window.location='/api/regulations/${r.id}/roadmap.xlsx'">Roadmap (Excel)</button></div>`;
  show($("#modal"));
}
function downloadRegHTML(r){
  const bf=r.briefing||{};
  const rows=controls.filter(c=>(c.regulations||[]).includes(r.id)).sort((a,b)=>b.score-a.score);
  const body=`<h1>${esc(r.name)} <span class="muted">(${r.id})</span></h1>
    <p class="muted">${r.body||''} · ${(r.jurisdictions||[]).join(', ')} · ${r.emerging?'Emerging':'In force'}</p>
    <h2>What it is</h2><p>${esc(bf.what_it_is||r.summary)}</p>
    <h2>Why it is important</h2><p>${esc(bf.why_important||'')}</p>
    <h2>Detailed description</h2><p>${esc(bf.detail||'')}</p>
    <h2>What changed (${bf.change_date||''}, ${bf.change_impact||'low'} impact)</h2><p>${esc(bf.delta||'')}</p><p><b>Impact:</b> ${esc(bf.change_note||'')}</p>
    <h2>Official source</h2><p><a href="${esc(r.url)}">${esc(r.url)}</a></p>
    <h2>Prioritized roadmap (${rows.length} controls)</h2>
    <table><thead><tr><th>#</th><th>Control</th><th>Why it matters</th><th>Action steps</th><th>Priority</th><th>Severity</th></tr></thead><tbody>
    ${rows.map((c,i)=>`<tr><td>${i+1}</td><td><b>${esc(c.title)}</b></td><td>${esc(c.explanation)}</td><td>${(c.actions||[]).map(a=>esc(a)).join('<br>')}</td><td>${c.priority}</td><td>${c.severity} · ${c.score}</td></tr>`).join('')}
    </tbody></table>`;
  saveHTML(`${r.id}_briefing.html`,`${r.name} — Briefing & Roadmap`,body);
}
function closeModal(){hide($("#modal"));}

// ----- weekly scan / delta -----
async function runScan(){
  show($("#overlay"));
  const steps=["Crawling sources…","Embedding into local vector store…","Summarizing with local LLM…","Diffing vs last snapshot…","Scoring impact…"];
  let i=0;const t=setInterval(()=>{$("#ovText").textContent=steps[i%steps.length];i++;},700);
  try{ await api("/api/scan/run",{method:"POST"}); renderDelta(await(await api("/api/scan/delta")).json()); }
  catch(e){ alert("Scan failed: "+e.message); }
  finally{ clearInterval(t); hide($("#overlay")); }
}
let lastDelta=null;
function renderDelta(d){
  lastDelta=d;
  if(!d.run){ $("#scanStatus").textContent="No scan yet — run one."; return; }
  $("#scanStatus").innerHTML=`Last scan #${d.run.id} · <b>${d.run.new}</b> new · <b>${d.run.updated}</b> updated · ${d.run.unchanged} unchanged`;
  const hi=d.items.filter(x=>x.impact==="high"&&x.change_type!=="unchanged").length;
  $("#deltaSummary").innerHTML=`
    <div class="ds new"><div class="n">${d.run.new}</div><div class="l muted">New</div></div>
    <div class="ds up"><div class="n">${d.run.updated}</div><div class="l muted">Updated</div></div>
    <div class="ds hi"><div class="n">${hi}</div><div class="l muted">High impact</div></div>
    <div class="ds"><div class="n">${d.run.unchanged}</div><div class="l muted">Unchanged</div></div>`;
  $("#deltaFeed").innerHTML=d.items.map(x=>`
    <div class="ob" onclick="this.classList.toggle('open')">
      <div class="ob-h"><span class="badge b-${x.change_type}">${x.change_type}</span>
        <span class="ob-id">${x.reg_id}</span><span class="ob-t">${esc(x.name)}</span>
        <span class="tag t-${x.impact==='high'?'Critical':x.impact==='medium'?'High':'Low'}">${x.impact}</span></div>
      <div class="ob-b"><p>${esc(x.delta)}</p><p class="muted" style="margin-top:8px">Source: <a href="${esc(x.url)}" target="_blank">${esc(x.url)}</a></p></div>
    </div>`).join("");
}
function downloadDelta(fmt){
  if(!lastDelta||!lastDelta.run){alert("Run a scan first.");return;}
  if(fmt==='xlsx'){
    const rows=[['Change','ID','Regulation','Impact','What changed','Official source']].concat(lastDelta.items.map(x=>[x.change_type,x.reg_id,x.name,x.impact,x.delta,x.url]));
    saveXLSX('regpulse_weekly_delta.xlsx',[['Weekly Delta',rows]]);
  }else{
    const body=`<h1>Weekly Regulatory Delta</h1><p class="muted">New ${lastDelta.run.new} · Updated ${lastDelta.run.updated} · Unchanged ${lastDelta.run.unchanged}</p>
      <table><thead><tr><th>Change</th><th>Regulation</th><th>Impact</th><th>What changed</th><th>Source</th></tr></thead><tbody>
      ${lastDelta.items.map(x=>`<tr><td>${x.change_type}</td><td><b>${esc(x.name)}</b><br><span class="muted">${x.reg_id}</span></td><td>${x.impact}</td><td>${esc(x.delta)}</td><td><a href="${esc(x.url)}">source ↗</a></td></tr>`).join('')}
      </tbody></table>`;
    saveHTML('regpulse_weekly_delta.html','Weekly Regulatory Delta',body);
  }
}

// ----- applicability -----
async function runApply(){
  const profile={name:$("#pName").value||"My platform",markets:picked("markets"),product_types:picked("ptypes"),data_types:picked("datatypes"),flags:picked("flags")};
  if(!profile.markets.length&&!profile.product_types.length){alert("Pick at least a market or product type.");return;}
  lastProfile=profile; show($("#overlay")); $("#ovText").textContent="Evaluating applicability…";
  try{
    const res=await(await api("/api/applicability",{method:"POST",body:JSON.stringify(profile)})).json();
    lastApplicable=res.applicable; renderApply(res); renderRoadmapBox(res.applicable.map(a=>a.reg_id));
    $("#saveBtn").style.display=token?"inline-block":"none";
  }catch(e){ alert("Failed: "+e.message); }
  finally{ hide($("#overlay")); }
}
function renderApply(res){
  $("#applyResults").innerHTML=`
    <div class="section-label" style="margin-bottom:10px">${res.count} regulations in scope · ${esc(lastProfile.name)}</div>
    ${res.applicable.map(a=>`
      <div class="ob" onclick="this.classList.toggle('open')">
        <div class="ob-h"><span class="dot p-${a.priority}"></span><span class="ob-id">${a.reg_id}</span><span class="ob-t">${esc(a.name)}</span>
          ${a.emerging?'<span class="badge b-emerging">Emerging</span>':''}<span class="tag t-${a.priority}">${a.priority}</span></div>
        <div class="ob-b"><p>${esc(a.why)}</p><p class="muted" style="margin-top:8px">Domain: ${a.domain} · <a href="${esc(a.url)}" target="_blank">Official source ↗</a></p></div>
      </div>`).join("")}
    <div class="hero-actions" style="margin-top:14px">
      <button class="btn ghost sm" onclick="downloadApply('html')">Download analysis (HTML)</button>
      <button class="btn ghost sm" onclick="downloadApply('xlsx')">Download analysis (Excel)</button>
    </div>`;
  go("apply");
}
function downloadApply(fmt){
  if(!lastApplicable)return;
  if(fmt==='xlsx'){
    const rows=[['ID','Regulation','Priority','Why it applies','Official source']].concat(lastApplicable.map(a=>[a.reg_id,a.name,a.priority,a.why,a.url]));
    saveXLSX('regpulse_applicability.xlsx',[['Applicable Regulations',rows]]);
  }else{
    const body=`<h1>Applicable Regulations</h1><p class="muted">${esc(lastProfile.name)} · markets: ${esc((lastProfile.markets||[]).join(', '))} · ${lastApplicable.length} in scope</p>
      <table><thead><tr><th>Priority</th><th>Regulation</th><th>Why it applies</th><th>Official source</th></tr></thead><tbody>
      ${lastApplicable.map(a=>`<tr><td>${a.priority}</td><td><b>${esc(a.name)}</b><br><span class="muted">${a.reg_id}</span></td><td>${esc(a.why)}</td><td><a href="${esc(a.url)}">source ↗</a></td></tr>`).join('')}
      </tbody></table>`;
    saveHTML('regpulse_applicability.html','Applicable Regulations',body);
  }
}

// ----- roadmap -----
function renderRoadmapBox(regIds){
  $("#roadmapBox").innerHTML=`
    <div class="section-label">Capability · Roadmap</div>
    <h2>Combined Implementation Roadmap</h2>
    <p class="sub">A single prioritized, de-duplicated roadmap across all ${regIds.length} applicable regulations — overlapping controls implemented once, tagged with every regulation they satisfy.</p>
    <div class="hero-actions">
      <button class="btn" onclick='downloadRoadmap(${JSON.stringify(regIds)},"xlsx")'>Combined roadmap (Excel) ↓</button>
      <button class="btn ghost" onclick='downloadRoadmap(${JSON.stringify(regIds)},"html")'>Combined roadmap (HTML) ↓</button>
      <button class="btn ghost" onclick="previewRoadmap()">Preview inline</button>
    </div>
    <div id="roadmapPreview" style="margin-top:20px"></div>`;
}
async function downloadRoadmap(regIds,fmt){
  if(fmt==='xlsx'){
    // use the backend's openpyxl-generated workbook (formatted, 2 sheets)
    const r=await fetch("/api/roadmap.xlsx",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({reg_ids:regIds,profile_name:(lastProfile&&lastProfile.name)||"My platform"})});
    const b=await r.blob();const u=URL.createObjectURL(b);const a=document.createElement('a');a.href=u;a.download="regpulse_roadmap.xlsx";a.click();URL.revokeObjectURL(u);
  }else{
    const res=await(await api("/api/roadmap",{method:"POST",body:JSON.stringify({reg_ids:regIds})})).json();
    const body=`<h1>Combined Implementation Roadmap</h1><p class="muted">${esc((lastProfile&&lastProfile.name)||'My platform')} · ${regIds.length} regulations · ${res.rows.length} controls</p>
      <table><thead><tr><th>#</th><th>Phase</th><th>Control</th><th>Why it matters</th><th>Action steps</th><th>Priority</th><th>Severity</th><th>Regulations</th></tr></thead><tbody>
      ${res.rows.map(r=>`<tr><td>${r.seq}</td><td>P${r.phase}</td><td><b>${esc(r.title)}</b></td><td>${esc(r.explanation)}</td><td>${(r.actions||[]).map(a=>esc(a)).join('<br>')}</td><td>${r.priority}</td><td>${r.severity} · ${r.score}</td><td>${(r.regulations||[]).join(', ')}</td></tr>`).join('')}
      </tbody></table>`;
    saveHTML('regpulse_roadmap.html','Combined Implementation Roadmap',body);
  }
}
async function previewRoadmap(){
  const res=await(await api("/api/roadmap",{method:"POST",body:JSON.stringify({reg_ids:lastApplicable.map(a=>a.reg_id)})})).json();
  $("#roadmapPreview").innerHTML=res.rows.map(r=>`
    <div class="ob"><div class="ob-h"><span class="dot p-${r.priority}"></span><span class="ob-id">${r.id}</span><span class="ob-t">${esc(r.title)}</span>
      <span class="muted">P${r.phase} · ${r.effort}</span><span class="tag t-${r.priority}">${r.priority}</span></div></div>`).join("");
}

// ----- control library -----
function setCtrlFilter(el){document.querySelectorAll('#ctrlChips .chip').forEach(c=>c.classList.remove('active'));el.classList.add('active');ctrlFilter=el.dataset.d;renderCtrls();}
function renderCtrls(){
  let list=controls.filter(c=>ctrlFilter==="all"||c.priority===ctrlFilter);
  if(ctrlSearch){const q=ctrlSearch.toLowerCase();list=list.filter(c=>(c.title+c.domain+c.id+c.explanation).toLowerCase().includes(q));}
  $("#ctrlCount").textContent=`${list.length} of ${controls.length} controls`;
  $("#ctrlGrid").innerHTML=list.map(c=>{const i=controls.indexOf(c);return `
    <div class="card" onclick="showCtrl(${i})">
      <h4>${c.id} · ${c.priority}</h4><div class="title">${esc(c.title)}</div>
      <div class="desc">${esc((c.explanation||'').slice(0,110))}…</div>
      <div class="foot"><span class="muted">P${c.phase} · ${c.domain}</span><span class="tag t-${c.severity}">${c.severity} · ${c.score}</span></div>
    </div>`;}).join("");
}
function showCtrl(i){const c=controls[i];
  $("#modalInner").innerHTML=`
    <div class="modal-head"><div><div class="muted" style="font-family:'DM Mono',monospace;color:var(--accent)">${c.id} · phase ${c.phase} · ${c.effort}</div><h3>${esc(c.title)}</h3></div><button class="modal-x" onclick="closeModal()">✕</button></div>
    <div class="modal-body">
      <div class="mlabel">Explanation — why this control exists</div><div style="font-size:13.5px;color:var(--text-2)">${esc(c.explanation)}</div>
      <div class="mlabel">Actionable steps</div><ul style="margin-left:18px;font-size:13.5px;color:var(--text-2)">${(c.actions||[]).map(a=>`<li>${esc(a)}</li>`).join('')}</ul>
      <div class="mlabel">Priority / severity</div><div style="font-size:13px"><span class="tag t-${c.severity}">${c.severity} · ${c.score}</span> &nbsp; Priority: ${c.priority}</div>
      <div class="mlabel">Satisfies regulations</div><div style="font-size:13px;color:var(--text-2)">${(c.regulations||[]).join(', ')}</div>
    </div>
    <div class="modal-foot"><button class="btn ghost sm" onclick="closeModal()">Close</button>
      <button class="btn ghost sm" onclick="downloadCtrl(${i},'html')">Control (HTML)</button>
      <button class="btn sm" onclick="downloadCtrl(${i},'xlsx')">Control (Excel)</button></div>`;
  show($("#modal"));
}
const CHEAD=['ID','Control','Domain','Phase','Priority','Severity','Score','Explanation','Action steps','Regulations'];
function crow(c){return [c.id,c.title,c.domain,c.phase,c.priority,c.severity,c.score,c.explanation,(c.actions||[]).map((a,i)=>`${i+1}. ${a}`).join('\n'),(c.regulations||[]).join('; ')];}
function downloadCtrl(i,fmt){const c=controls[i];
  if(fmt==='xlsx'){saveXLSX(`${c.id}.xlsx`,[['Control',[CHEAD,crow(c)]]]);}
  else{saveHTML(`${c.id}.html`,c.title,`<h1>${esc(c.title)}</h1><p class="muted">${c.id} · ${c.domain} · phase ${c.phase}</p>
    <p><b>Priority:</b> ${c.priority} &nbsp; <b>Severity:</b> ${c.severity} (${c.score})</p>
    <h2>Explanation</h2><p>${esc(c.explanation)}</p>
    <h2>Actionable steps</h2><ol>${(c.actions||[]).map(a=>`<li>${esc(a)}</li>`).join('')}</ol>
    <h2>Satisfies regulations</h2><p>${(c.regulations||[]).join(', ')}</p>`);}
}
function downloadControls(fmt){
  if(fmt==='xlsx'){saveXLSX('regpulse_control_library.xlsx',[['Control Library',[CHEAD].concat(controls.map(crow))]]);}
  else{const body=`<h1>RegPulse Control Library</h1><p class="muted">${controls.length} explainable, actionable controls.</p>
    <table><thead><tr><th>ID</th><th>Control</th><th>Domain</th><th>Phase</th><th>Priority</th><th>Severity</th><th>Explanation</th><th>Action steps</th><th>Regulations</th></tr></thead><tbody>
    ${controls.map(c=>`<tr><td>${c.id}</td><td><b>${esc(c.title)}</b></td><td>${c.domain}</td><td>${c.phase}</td><td>${c.priority}</td><td>${c.severity} · ${c.score}</td><td>${esc(c.explanation)}</td><td>${(c.actions||[]).map(a=>esc(a)).join('<br>')}</td><td>${(c.regulations||[]).join(', ')}</td></tr>`).join('')}
    </tbody></table>`;
    saveHTML('regpulse_control_library.html','RegPulse Control Library',body);}
}

// ----- auth -----
function openAuth(){show($("#authModal"))} function closeAuth(){hide($("#authModal"))}
function toggleAuthMode(){authMode=authMode==="login"?"register":"login";
  $("#authTitle").textContent=authMode==="login"?"Log in":"Create account";
  $("#authSubmit").textContent=authMode==="login"?"Log in":"Create account";
  $("#authToggle").textContent=authMode==="login"?"Create account":"Have an account? Log in";}
async function doAuth(){
  const email=$("#authEmail").value,password=$("#authPass").value; $("#authErr").textContent="";
  try{
    let r;
    if(authMode==="register"){ r=await api("/api/auth/register",{method:"POST",body:JSON.stringify({email,password})}); }
    else{ const f=new URLSearchParams();f.set("username",email);f.set("password",password);
      r=await fetch("/api/auth/login",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:f});
      if(!r.ok) throw new Error("Incorrect email or password"); }
    token=(await r.json()).access_token; localStorage.setItem("rp_token",token); closeAuth(); refreshAuthUI();
  }catch(e){ $("#authErr").textContent=e.message; }
}
function logout(){token="";localStorage.removeItem("rp_token");refreshAuthUI();}
async function refreshAuthUI(){
  if(!token){ $("#navRight").innerHTML=`<button class="btn ghost sm" onclick="openAuth()">Log in</button>`; return; }
  try{ const me=await(await api("/api/auth/me")).json();
    $("#navRight").innerHTML=`<span class="muted">${esc(me.email)}</span><button class="btn ghost sm" onclick="logout()">Log out</button>`;
    if(lastApplicable) $("#saveBtn").style.display="inline-block";
  }catch(e){ logout(); }
}
async function saveAnalysis(){
  if(!token){ openAuth(); return; }
  try{
    await api("/api/profiles",{method:"POST",body:JSON.stringify(lastProfile)});
    await api("/api/analyses",{method:"POST",body:JSON.stringify({name:lastProfile.name,profile:lastProfile,applicable:lastApplicable})});
    alert("Saved to your account — it will be here next time you log in.");
  }catch(e){ alert("Save failed: "+e.message); }
}

init();
