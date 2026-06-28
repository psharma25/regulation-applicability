/* BitSense Blog — frontend logic (vanilla JS, no build step). */
const App = (() => {
  const state = { posts: [], tags: [], tag: null, q: "", config: {}, editing: null };
  const $ = (s) => document.querySelector(s);

  // ---- auth -------------------------------------------------------------
  const tokenKey = "bitsense_admin_token";
  const getToken = () => localStorage.getItem(tokenKey) || "";
  function authHeaders() {
    const t = getToken();
    return t ? { Authorization: "Bearer " + t } : {};
  }
  async function ensureToken() {
    if (!state.config.auth_required) return true;
    if (getToken()) return true;
    const t = prompt("Admin token required to publish:");
    if (!t) return false;
    localStorage.setItem(tokenKey, t.trim());
    return true;
  }

  // ---- api --------------------------------------------------------------
  async function api(path, opts = {}) {
    const res = await fetch(path, opts);
    if (!res.ok) {
      let msg = res.statusText;
      try { msg = (await res.json()).detail || msg; } catch {}
      if (res.status === 401) localStorage.removeItem(tokenKey);
      throw new Error(msg);
    }
    return res.status === 204 ? null : res.json();
  }

  // ---- markdown (compact renderer) -------------------------------------
  function esc(s){return s.replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));}
  function isVideo(url){return /\.(mp4|webm|mov|ogv|ogg)(\?|#|$)/i.test(url);}
  function inline(s){
    return esc(s)
      .replace(/`([^`]+)`/g,(_,c)=>`<code>${c}</code>`)
      .replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g,(_,a,u)=>
        isVideo(u)?`<video controls src="${u}"></video>`:`<img alt="${a}" src="${u}">`)
      .replace(/@\[video\]\(([^)\s]+)\)/g,(_,u)=>`<video controls src="${u}"></video>`)
      .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g,(_,t,u)=>`<a href="${u}" target="_blank" rel="noopener">${t}</a>`)
      .replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>")
      .replace(/(^|[^*])\*([^*]+)\*/g,"$1<em>$2</em>")
      .replace(/_([^_]+)_/g,"<em>$1</em>");
  }
  function markdown(src){
    const lines=(src||"").replace(/\r\n/g,"\n").split("\n");
    let html="", i=0, para=[], list=null;
    const flushP=()=>{ if(para.length){ html+=`<p>${inline(para.join(" "))}</p>`; para=[]; } };
    const flushL=()=>{ if(list){ html+=`</${list}>`; list=null; } };
    while(i<lines.length){
      let ln=lines[i];
      if(/^```/.test(ln)){ flushP(); flushL(); let buf=[]; i++;
        while(i<lines.length&&!/^```/.test(lines[i])){buf.push(lines[i]);i++;}
        html+=`<pre><code>${esc(buf.join("\n"))}</code></pre>`; i++; continue; }
      if(/^\s*$/.test(ln)){ flushP(); flushL(); i++; continue; }
      let m;
      if((m=ln.match(/^(#{1,4})\s+(.*)/))){ flushP(); flushL();
        const h=m[1].length; html+=`<h${h}>${inline(m[2])}</h${h}>`; i++; continue; }
      if(/^>\s?/.test(ln)){ flushP(); flushL();
        let buf=[]; while(i<lines.length&&/^>\s?/.test(lines[i])){buf.push(lines[i].replace(/^>\s?/,""));i++;}
        html+=`<blockquote>${inline(buf.join(" "))}</blockquote>`; continue; }
      if((m=ln.match(/^[-*]\s+(.*)/))){ flushP(); if(list!=="ul"){flushL();list="ul";html+="<ul>";}
        html+=`<li>${inline(m[1])}</li>`; i++; continue; }
      if((m=ln.match(/^\d+\.\s+(.*)/))){ flushP(); if(list!=="ol"){flushL();list="ol";html+="<ol>";}
        html+=`<li>${inline(m[1])}</li>`; i++; continue; }
      // standalone media line
      if(/^!\[/.test(ln)||/^@\[video\]/.test(ln)){ flushP(); flushL(); html+=inline(ln); i++; continue; }
      para.push(ln); i++;
    }
    flushP(); flushL();
    return html;
  }

  // ---- helpers ----------------------------------------------------------
  function fmtDate(iso){
    try{ return new Date(iso).toLocaleDateString(undefined,{year:"numeric",month:"short",day:"numeric"});}
    catch{ return iso; }
  }
  function readTime(body){
    const words=(body||"").split(/\s+/).filter(Boolean).length;
    return Math.max(1,Math.round(words/220))+" min read";
  }
  function postUrl(slug){ return `${location.origin}${location.pathname}#/post/${slug}`; }

  // ---- sharing ----------------------------------------------------------
  function shareRow(post){
    const url=encodeURIComponent(postUrl(post.slug));
    const title=encodeURIComponent(post.title);
    const sum=encodeURIComponent(post.summary||post.title);
    const targets=[
      ["LinkedIn",`https://www.linkedin.com/sharing/share-offsite/?url=${url}`],
      ["X",`https://twitter.com/intent/tweet?text=${title}&url=${url}`],
      ["Bluesky",`https://bsky.app/intent/compose?text=${title}%20${url}`],
      ["Reddit",`https://www.reddit.com/submit?url=${url}&title=${title}`],
      ["Email",`mailto:?subject=${title}&body=${sum}%0A%0A${url}`],
    ];
    const btns=targets.map(([n,h])=>`<button onclick="window.open('${h}','_blank','noopener,width=640,height=620')">${n}</button>`).join("");
    return `<div class="share"><span class="lbl">Share</span>${btns}
      <button onclick="App.copyLink('${post.slug}')">Copy link</button></div>`;
  }
  function copyLink(slug){
    navigator.clipboard.writeText(postUrl(slug)).then(()=>toast("Link copied"),()=>toast("Copy failed"));
  }

  // ---- rendering: feed --------------------------------------------------
  function renderTags(){
    const el=$("#taglist");
    if(!state.tags.length){ el.innerHTML='<span style="font-family:var(--mono);font-size:12px;color:var(--text-dim)">no tags yet</span>'; return; }
    el.innerHTML=state.tags.map(t=>`
      <button class="${state.tag===t.tag?"active":""}" onclick="App.selectTag('${t.tag}')">
        <span>#${t.tag}</span><span class="n">${t.count}</span>
      </button>`).join("");
  }
  function renderFeed(){
    const feed=$("#feed");
    $("#scope").textContent = state.tag ? `#${state.tag}` : (state.q ? "Search" : "Latest");
    $("#count").textContent = `${state.posts.length} post${state.posts.length===1?"":"s"}`;
    $("#clear").style.display = (state.tag||state.q) ? "" : "none";
    if(!state.posts.length){
      feed.innerHTML=`<div class="empty"><b>Nothing here yet.</b>${state.tag||state.q?"Try clearing the filter.":'Hit "＋ New post" to publish the first one.'}</div>`;
      return;
    }
    feed.innerHTML=state.posts.map(p=>{
      const cover=p.cover?(isVideo(p.cover)
        ?`<div class="cover"><video muted src="${p.cover}"></video></div>`
        :`<div class="cover"><img src="${p.cover}" alt=""></div>`):"";
      const chips=(p.tags||[]).map(t=>`<span class="chip" onclick="event.stopPropagation();App.selectTag('${t}')">${t}</span>`).join("");
      const draft=p.status==="draft"?`<span class="draft">draft</span>`:"";
      return `<article class="card">
        ${cover}
        <div class="pad">
          <div class="meta">${draft}<span>${fmtDate(p.created_at)}</span><span>${readTime(p.body)}</span></div>
          <h3 onclick="App.openPost('${p.slug}')">${esc(p.title)}</h3>
          ${p.summary?`<p class="summary">${esc(p.summary)}</p>`:""}
          <div class="chips">${chips}</div>
          ${shareRow(p)}
        </div>
      </article>`;
    }).join("");
  }

  // ---- rendering: single post ------------------------------------------
  function renderPost(p){
    const hero=p.cover?(isVideo(p.cover)
      ?`<div class="hero"><video controls src="${p.cover}"></video></div>`
      :`<div class="hero"><img src="${p.cover}" alt=""></div>`):"";
    const chips=(p.tags||[]).map(t=>`<span class="chip" onclick="App.selectTag('${t}')">${t}</span>`).join("");
    $("#feed-view").style.display="none";
    const pv=$("#post-view"); pv.style.display="";
    pv.innerHTML=`
      <a class="back" href="#/" onclick="App.home();return false">← all posts</a>
      <article class="post">
        ${hero}
        <div class="body">
          <div class="meta">
            ${p.status==="draft"?'<span style="color:var(--danger)">DRAFT</span>':""}
            <span>${fmtDate(p.created_at)}</span><span>${readTime(p.body)}</span>
            <button style="font-family:var(--mono);font-size:12px;background:none;border:0;color:var(--signal-ink);padding:0" onclick="App.editPost('${p.slug}')">edit</button>
          </div>
          <h1>${esc(p.title)}</h1>
          ${p.summary?`<p style="font-size:21px;color:#3a4654;margin:0 0 22px">${esc(p.summary)}</p>`:""}
          <div class="prose">${markdown(p.body)}</div>
          <div class="chips" style="margin-top:28px">${chips}</div>
          ${shareRow(p)}
        </div>
      </article>`;
    window.scrollTo(0,0);
  }

  // ---- data load --------------------------------------------------------
  async function load(){
    const params=new URLSearchParams({include_drafts:"true"});
    if(state.tag) params.set("tag",state.tag);
    if(state.q) params.set("q",state.q);
    try{
      const [posts,tags]=await Promise.all([
        api(`/api/posts?${params}`), api(`/api/tags`)
      ]);
      state.posts=posts.posts; state.tags=tags.tags;
      renderTags(); renderFeed();
    }catch(e){ $("#feed").innerHTML=`<div class="empty"><b>Couldn't load posts.</b>${esc(e.message)}</div>`; }
  }

  // ---- editor -----------------------------------------------------------
  function openEditor(post=null){
    state.editing=post;
    $("#editor-title").textContent=post?"Edit post":"New post";
    $("#save-btn").textContent=post?"Save changes":"Publish";
    $("#del-btn").style.display=post?"":"none";
    $("#f-title").value=post?.title||"";
    $("#f-summary").value=post?.summary||"";
    $("#f-body").value=post?.body||"";
    $("#f-tags").value=(post?.tags||[]).join(", ");
    $("#f-status").value=post?.status||"published";
    $("#f-cover").value=post?.cover||"";
    $("#thumbs").innerHTML="";
    $("#overlay").classList.add("open");
    setTimeout(()=>$("#f-title").focus(),50);
  }
  function closeEditor(){ $("#overlay").classList.remove("open"); state.editing=null; }

  function insertAtCursor(text){
    const ta=$("#f-body"); const s=ta.selectionStart, e=ta.selectionEnd;
    ta.value=ta.value.slice(0,s)+text+ta.value.slice(e);
    ta.selectionStart=ta.selectionEnd=s+text.length; ta.focus();
  }
  function addThumb(url,kind){
    const div=document.createElement("div"); div.className="thumb";
    div.innerHTML=(kind==="video"?`<video src="${url}"></video>`:`<img src="${url}">`)+
      `<button title="Set as cover" onclick="App.setCover('${url}')">cover</button>`;
    $("#thumbs").appendChild(div);
  }
  async function uploadFiles(files){
    if(!(await ensureToken())) return;
    for(const file of files){
      const fd=new FormData(); fd.append("file",file);
      toast(`Uploading ${file.name}…`);
      try{
        const r=await api("/api/upload",{method:"POST",body:fd,headers:authHeaders()});
        if(r.kind==="video") insertAtCursor(`\n@[video](${r.url})\n`);
        else insertAtCursor(`\n![${file.name.replace(/\.[^.]+$/,"")}](${r.url})\n`);
        if(!$("#f-cover").value){ $("#f-cover").value=r.url; }
        addThumb(r.url,r.kind);
        toast("Uploaded");
      }catch(e){ toast("Upload failed: "+e.message); }
    }
  }
  function setCover(url){ $("#f-cover").value=url; toast("Cover set"); }

  async function save(){
    const title=$("#f-title").value.trim();
    if(!title){ toast("A title is required."); $("#f-title").focus(); return; }
    if(!(await ensureToken())) return;
    const payload={
      title, summary:$("#f-summary").value.trim(),
      body:$("#f-body").value, tags:$("#f-tags").value,
      status:$("#f-status").value, cover:$("#f-cover").value||null,
    };
    const btn=$("#save-btn"); btn.disabled=true; btn.textContent="Saving…";
    try{
      const editing=state.editing;
      const saved=editing
        ? await api(`/api/posts/${editing.slug}`,{method:"PUT",headers:{...authHeaders(),"Content-Type":"application/json"},body:JSON.stringify(payload)})
        : await api(`/api/posts`,{method:"POST",headers:{...authHeaders(),"Content-Type":"application/json"},body:JSON.stringify(payload)});
      closeEditor(); toast(editing?"Saved":"Published");
      location.hash=`#/post/${saved.slug}`; await load(); openPost(saved.slug);
    }catch(e){ toast("Save failed: "+e.message); }
    finally{ btn.disabled=false; btn.textContent=state.editing?"Save changes":"Publish"; }
  }
  async function deleteCurrent(){
    if(!state.editing) return;
    if(!confirm(`Delete "${state.editing.title}"? This can't be undone.`)) return;
    if(!(await ensureToken())) return;
    try{
      await api(`/api/posts/${state.editing.slug}`,{method:"DELETE",headers:authHeaders()});
      closeEditor(); toast("Deleted"); home(); await load();
    }catch(e){ toast("Delete failed: "+e.message); }
  }

  // ---- navigation -------------------------------------------------------
  async function openPost(slug){
    try{ const p=await api(`/api/posts/${slug}`); location.hash=`#/post/${slug}`; renderPost(p); }
    catch(e){ toast(e.message); home(); }
  }
  async function editPost(slug){
    try{ openEditor(await api(`/api/posts/${slug}`)); }catch(e){ toast(e.message); }
  }
  function home(){
    location.hash="#/"; $("#post-view").style.display="none"; $("#feed-view").style.display="";
    window.scrollTo(0,0);
  }
  function selectTag(t){
    state.tag=(state.tag===t)?null:t; state.q=""; $("#search").value="";
    home(); load();
  }
  function clearFilters(){ state.tag=null; state.q=""; $("#search").value=""; load(); }

  function route(){
    const m=location.hash.match(/#\/post\/(.+)/);
    if(m) openPost(decodeURIComponent(m[1])); else home();
  }

  // ---- misc -------------------------------------------------------------
  let toastT;
  function toast(msg){
    const el=$("#toast"); el.textContent=msg; el.classList.add("show");
    clearTimeout(toastT); toastT=setTimeout(()=>el.classList.remove("show"),2600);
  }

  // ---- init -------------------------------------------------------------
  async function init(){
    try{ state.config=await api("/api/config"); }catch{}
    // search (debounced)
    let st; $("#search").addEventListener("input",e=>{
      clearTimeout(st); st=setTimeout(()=>{ state.q=e.target.value.trim(); state.tag=null; renderTags(); load(); },250);
    });
    // dropzone
    const dz=$("#dropzone"), fi=$("#file-input");
    dz.addEventListener("click",()=>fi.click());
    fi.addEventListener("change",e=>{ uploadFiles([...e.target.files]); fi.value=""; });
    ["dragenter","dragover"].forEach(ev=>dz.addEventListener(ev,e=>{e.preventDefault();dz.classList.add("drag");}));
    ["dragleave","drop"].forEach(ev=>dz.addEventListener(ev,e=>{e.preventDefault();dz.classList.remove("drag");}));
    dz.addEventListener("drop",e=>uploadFiles([...e.dataTransfer.files]));
    // esc closes editor
    document.addEventListener("keydown",e=>{ if(e.key==="Escape"&&$("#overlay").classList.contains("open")) closeEditor(); });
    $("#overlay").addEventListener("click",e=>{ if(e.target===$("#overlay")) closeEditor(); });
    window.addEventListener("hashchange",route);
    await load(); route();
  }

  return { init, home, openPost, editPost, selectTag, clearFilters,
           openEditor, closeEditor, save, deleteCurrent, setCover, copyLink };
})();
document.addEventListener("DOMContentLoaded", App.init);
