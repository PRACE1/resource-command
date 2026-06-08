// Resource Command V1 — Main Application
'use strict';

// ── STATE ──────────────────────────────────────────────────
const S = {
  role: null, view: 'dashboard',
  liveOut: {}, // grid id → current output
  chain: [],   // blockchain blocks
  alerts: [],  // notification queue
  fieldReports: [],
  charts: {},
};

// ── BLOCKCHAIN (SHA-256) ───────────────────────────────────
const BC = {
  async hash(str) {
    const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
    return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2,'0')).join('');
  },
  async build(seeds) {
    S.chain = [];
    let prev = '0'.repeat(64);
    for (const s of seeds) {
      const h = await this.hash(`${prev}|${s.h}|${s.action}|${s.actor}|${s.payload}|${s.ts}`);
      S.chain.push({ ...s, prev, hash: h });
      prev = h;
    }
  },
  async add(action, actor, payload) {
    const prev = S.chain.length ? S.chain[S.chain.length-1].hash : '0'.repeat(64);
    const h2 = S.chain.length + 1;
    const ts = new Date().toISOString();
    const hash = await this.hash(`${prev}|${h2}|${action}|${actor}|${payload}|${ts}`);
    const block = { h: h2, action, actor, payload, ts, prev, hash };
    S.chain.push(block);
    return block;
  },
  async verify() {
    let prev = '0'.repeat(64);
    const res = [];
    for (const b of S.chain) {
      const exp = await this.hash(`${prev}|${b.h}|${b.action}|${b.actor}|${b.payload}|${b.ts}`);
      res.push({ h: b.h, ok: exp === b.hash && b.prev === prev });
      prev = b.hash;
    }
    return res;
  },
};

// ── AUTH ───────────────────────────────────────────────────
const Auth = {
  login(role) {
    S.role = role;
    sessionStorage.setItem('rc_role', role);
    $('login-screen').classList.add('hidden');
    $('app-shell').classList.remove('hidden');
    UI.buildNav();
    UI.updateTopbar();
    Router.go('dashboard');
    Live.start();
    BC.build(D.chainSeed).then(() => {});
    const saved = sessionStorage.getItem('rc_reports');
    if (saved) S.fieldReports = JSON.parse(saved);
  },
  logout() {
    S.role = null;
    sessionStorage.clear();
    $('app-shell').classList.add('hidden');
    $('login-screen').classList.remove('hidden');
    Live.stop();
    Object.values(S.charts).forEach(c => c.destroy());
    S.charts = {};
    S.alerts = [];
    S.chain = [];
  },
  init() {
    const r = sessionStorage.getItem('rc_role');
    if (r && ROLES[r]) { Auth.login(r); } else { $('login-screen').classList.remove('hidden'); }
  },
};

// ── UTILITIES ──────────────────────────────────────────────
function $(id) { return document.getElementById(id); }
function eff(g) { return Math.round(((S.liveOut[g.id]??g.out)/g.target)*100); }
function effColor(e) { return e>=100?'var(--success)':e>=70?'var(--warning)':'var(--danger)'; }
function statusClass(g) {
  const e=eff(g);
  return e>=90?'badge-optimal':e>=60?'badge-warning':'badge-critical';
}
function statusLabel(g) {
  const e=eff(g);
  return e>=90?'Optimal':e>=60?'Warning':'Critical';
}
function toast(msg, type='info') {
  const t=$('toast'); t.textContent=msg; t.className=`toast ${type}`;
  t.classList.remove('hidden');
  setTimeout(()=>t.classList.add('hidden'),4000);
}
function skeleton(h=180) { return `<div class="skeleton" style="height:${h}px;border-radius:14px"></div>`; }
function delay(ms) { return new Promise(r=>setTimeout(r,ms)); }

// ── LIVE DATA TICKER ───────────────────────────────────────
const Live = {
  _t: null,
  start() {
    D.grids.forEach(g => { S.liveOut[g.id] = g.out; });
    this._t = setInterval(() => this.tick(), 30000);
    setInterval(() => {
      const now = new Date();
      $('sync-time').textContent = `Last synced: ${now.toLocaleTimeString()}`;
    }, 1000);
  },
  stop() { clearInterval(this._t); },
  tick() {
    D.grids.forEach(g => {
      const prev = S.liveOut[g.id];
      const delta = (Math.random()-0.5)*0.06;
      const next = Math.max(1, Math.round(prev*(1+delta)));
      const prevEff = Math.round((prev/g.target)*100);
      const nextEff = Math.round((next/g.target)*100);
      S.liveOut[g.id] = next;
      // fire alert if status changes
      if ((prevEff>=90) !== (nextEff>=90) || (prevEff>=60) !== (nextEff>=60)) {
        const label = nextEff<60?'Critical':nextEff<90?'Warning':'Optimal';
        const type  = nextEff<60?'danger':nextEff<90?'warning':'success';
        const alertObj = { title:`${g.name} → ${label}`, desc:`Output changed to ${next} MW (${nextEff}% of target)`, type, ts: new Date() };
        S.alerts.unshift(alertObj);
        $('notif-count').textContent = S.alerts.length;
        toast(`⚡ ${g.name}: ${label} (${nextEff}%)`, type==='success'?'success':type);
      }
    });
    if (S.view==='dashboard') Views.dashboard();
    if (S.view==='grids')     Views.grids();
  },
};

// ── ROUTER ────────────────────────────────────────────────
const Router = {
  go(id) {
    const role = ROLES[S.role];
    const allowed = role.nav.flatMap(c=>c.items).map(i=>i.id);
    if (!allowed.includes(id)) { toast('Access restricted for your portal','danger'); return; }
    S.view = id;
    document.querySelectorAll('.view').forEach(v=>v.classList.remove('active'));
    const el = $(`view-${id}`);
    if (el) el.classList.add('active');
    document.querySelectorAll('.nav-links li').forEach(li=>{
      li.classList.toggle('active', li.dataset.view===id);
    });
    const titles = {
      dashboard:'Overview Dashboard', nexus:'Energy–Mine Nexus', map:'Resource Map',
      grids:'Grid Status', investments:'Investments', targets:'Strategic Targets',
      mining:'Mining Module', compliance:'Compliance & BERA', blockchain:'Blockchain Audit Trail',
      fieldreports:'Field Reports', reports:'Reports & Documents',
    };
    $('view-title').textContent = titles[id]||id;
    $('breadcrumb-page').textContent = titles[id]||id;
    const fn = Views[id];
    if (fn) fn();
  },
};

// ── UI HELPERS ────────────────────────────────────────────
const UI = {
  buildNav() {
    const role = ROLES[S.role];
    const ul = $('nav-links'); ul.innerHTML='';
    role.nav.forEach(cat=>{
      const div=document.createElement('div');
      div.className='nav-category'; div.textContent=cat.cat; ul.appendChild(div);
      cat.items.forEach(item=>{
        const li=document.createElement('li'); li.dataset.view=item.id;
        li.innerHTML=`<a href="#" onclick="Router.go('${item.id}');return false"><i class="fa-solid ${item.icon}"></i>${item.label}</a>`;
        ul.appendChild(li);
      });
    });
  },
  updateTopbar() {
    const role=ROLES[S.role];
    $('portal-label-text').textContent=role.label;
    $('user-name-display').textContent=S.role==='minister'?'Hon. Min. Moyo':S.role==='investor'?'Ms. O. Thebe':'Public User';
    $('user-role-display').textContent=role.label;
  },
  toggleNotifPanel() {
    const p=$('notif-panel'); p.classList.toggle('hidden');
    if (!p.classList.contains('hidden')) this.renderNotifs();
  },
  renderNotifs() {
    const list=$('notif-list'); list.innerHTML='';
    if (!S.alerts.length) { list.innerHTML='<div style="padding:20px;color:var(--text-muted);font-size:13px">No alerts yet.</div>'; return; }
    S.alerts.slice(0,20).forEach(a=>{
      const c=a.type==='danger'?'var(--danger)':a.type==='warning'?'var(--warning)':'var(--success)';
      list.innerHTML+=`<div class="notif-item">
        <div class="notif-item-icon" style="background:${c}22;color:${c}"><i class="fa-solid fa-bolt"></i></div>
        <div class="notif-item-body">
          <div class="notif-item-title">${a.title}</div>
          <div class="notif-item-desc">${a.desc}</div>
          <div class="notif-item-time">${a.ts.toLocaleTimeString()}</div>
        </div></div>`;
    });
  },
  closeModal() { $('modal-overlay').classList.add('hidden'); },
  openModal(title, html) {
    $('modal-title').textContent=title;
    $('modal-body').innerHTML=html;
    $('modal-overlay').classList.remove('hidden');
  },
  toggleSidebar() {
    $('sidebar').classList.toggle('open');
    $('sidebar-overlay').classList.toggle('hidden');
  },
  closeSidebar() {
    $('sidebar').classList.remove('open');
    $('sidebar-overlay').classList.add('hidden');
  },
  chart(id, config) {
    if (S.charts[id]) { S.charts[id].destroy(); delete S.charts[id]; }
    const el=$(id); if(!el) return;
    S.charts[id]=new Chart(el,config);
  },
};

$('modal-overlay').addEventListener('click',e=>{ if(e.target===$('modal-overlay')) UI.closeModal(); });

// ── VIEWS ─────────────────────────────────────────────────
const Views = {

  // ── DASHBOARD ──
  async dashboard() {
    const el=$('view-dashboard');
    el.innerHTML=`<div class="view-scroll">
      <div class="page-header"><h1>National Resource Overview</h1><p>Real-time energy grid and extractive sector performance — Botswana</p></div>
      <div class="kpi-grid" id="dash-kpis"></div>
      <div class="dashboard-grid">
        <div class="card col-span-2">
          <div class="card-header"><h3>Energy Production Trend (MW/Month)</h3></div>
          <canvas id="prodChart" height="90"></canvas>
        </div>
        <div class="card">
          <div class="card-header"><h3>Energy Mix</h3></div>
          <canvas id="mixChart" height="200"></canvas>
        </div>
        <div class="card col-span-3" style="padding:0;overflow:hidden">
          <div class="card-header" style="padding:16px 20px"><h3>Live Grid Status</h3>
            <button class="btn btn-primary" onclick="Views.exportCSV()"><i class="fa-solid fa-file-arrow-down"></i> Export CSV</button>
          </div>
          <table class="premium-table" style="padding:0">
            <thead><tr><th>Grid</th><th>Region</th><th>Type</th><th>Status</th><th>Output</th><th>Target</th><th>Efficiency</th><th></th></tr></thead>
            <tbody id="dash-grid-tbody"></tbody>
          </table>
        </div>
      </div>
    </div>`;
    // KPIs
    const totalOut = D.grids.reduce((a,g)=>a+(S.liveOut[g.id]??g.out),0);
    const kpis=[
      { title:'Total Investments', value:'P 45.2M', trend:'+5.2% vs last month', up:true,  icon:'fa-money-bill-trend-up', color:'var(--primary)', bg:'rgba(56,189,248,0.1)' },
      { title:'Live Production',  value:`${totalOut} MW`, trend:`${D.grids.length} active grids`, up:true, icon:'fa-bolt', color:'var(--warning)', bg:'rgba(245,158,11,0.1)' },
      { title:'Royalties (YTD)',  value:'P 3.9B',   trend:'Diamonds + Mining', up:true, icon:'fa-gem',  color:'var(--purple)', bg:'rgba(168,85,247,0.1)' },
      { title:'Critical Alerts',  value:S.alerts.filter(a=>a.type==='danger').length||'2', trend:'Require intervention', up:false, icon:'fa-triangle-exclamation', color:'var(--danger)', bg:'rgba(239,68,68,0.1)' },
    ];
    $('dash-kpis').innerHTML=kpis.map((k,i)=>`<div class="card kpi-card animate-in" style="animation-delay:${i*0.07}s">
      <div class="kpi-info"><h4>${k.title}</h4><div class="value">${k.value}</div>
      <div class="trend ${k.up?'text-success':'text-danger'}"><i class="fa-solid ${k.up?'fa-arrow-trend-up':'fa-arrow-trend-down'}"></i> ${k.trend}</div></div>
      <div class="kpi-icon" style="color:${k.color};background:${k.bg}"><i class="fa-solid ${k.icon}"></i></div>
    </div>`).join('');
    // Grid table
    $('dash-grid-tbody').innerHTML=D.grids.map((g,i)=>{
      const e=eff(g); const ec=effColor(e);
      return `<tr class="animate-in" style="animation-delay:${0.2+i*0.05}s">
        <td style="font-weight:700;color:#fff">${g.name}</td>
        <td style="color:var(--text-muted)">${g.region}</td>
        <td><span style="padding:3px 8px;background:rgba(255,255,255,0.05);border-radius:5px;font-size:11px">${g.type}</span></td>
        <td><span class="badge ${statusClass(g)}">${statusLabel(g)}</span></td>
        <td>${S.liveOut[g.id]??g.out} MW</td>
        <td style="color:var(--text-muted)">${g.target} MW</td>
        <td><div style="display:flex;align-items:center;gap:8px">
          <div style="flex:1;height:5px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden">
            <div style="width:${Math.min(e,100)}%;height:100%;background:${ec};border-radius:3px"></div></div>
          <span style="font-size:11px;font-weight:700;color:${ec};width:32px">${e}%</span></div></td>
        <td><button class="btn-action" onclick="Views.gridModal(${i})">Details</button></td>
      </tr>`;
    }).join('');
    // Charts
    await delay(50);
    UI.chart('prodChart',{type:'line',data:{labels:['Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar'],datasets:[
      {label:'Solar',data:[620,590,550,480,460,510,570,630],borderColor:'#38BDF8',backgroundColor:'rgba(56,189,248,0.08)',tension:0.4,fill:true,pointRadius:3},
      {label:'Biogas',data:[130,140,125,100,95,85,90,85],borderColor:'#A855F7',backgroundColor:'rgba(168,85,247,0.06)',tension:0.4,fill:true,pointRadius:3},
      {label:'Wind',data:[45,70,85,80,60,55,50,60],borderColor:'#F59E0B',backgroundColor:'rgba(245,158,11,0.05)',tension:0.4,fill:true,pointRadius:3},
    ]},options:{responsive:true,plugins:{legend:{position:'top',labels:{boxWidth:10,padding:16,font:{family:'Inter',size:11}}}},scales:{x:{grid:{color:'rgba(255,255,255,0.04)'}},y:{grid:{color:'rgba(255,255,255,0.04)'},ticks:{callback:v=>v+' MW'}}}}});
    UI.chart('mixChart',{type:'doughnut',data:{labels:['Coal','Solar','Biogas','Wind','Hydro','Imports'],datasets:[{data:[48,24,8,6,2,12],backgroundColor:['#EF4444','#38BDF8','#A855F7','#F59E0B','#06B6D4','#64748B'],borderWidth:3,borderColor:'#10141E',hoverOffset:6}]},options:{cutout:'65%',plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:10,font:{size:11}}}}}});
  },

  gridModal(i) {
    const g=D.grids[i]; const e=eff(g); const ec=effColor(e);
    UI.openModal(`Grid — ${g.name}`,`
      <span class="badge ${statusClass(g)}" style="margin-bottom:16px;display:inline-flex">${statusLabel(g)}</span>
      ${[['Region',g.region],['Type',g.type],['Output',(S.liveOut[g.id]??g.out)+' MW'],['Target',g.target+' MW'],['Efficiency',e+'%'],['CAIDI',g.caidi],['Forced Outage',g.fo],['ROI',g.roi+'%'],['CapEx',g.capex],['Shortfall',g.shortfall||'None']].map(([l,v])=>`<div class="modal-stat"><span class="modal-stat-label">${l}</span><span class="modal-stat-value">${v}</span></div>`).join('')}
      <div style="margin-top:16px;padding:14px;background:rgba(255,255,255,0.03);border-radius:10px;border-left:3px solid ${ec}">
        <div style="font-size:11px;text-transform:uppercase;color:var(--text-muted);margin-bottom:4px">Recommendation</div>
        <div style="font-size:13px;line-height:1.6">${g.rec}</div>
      </div>
      <div class="modal-actions">
        <button class="btn btn-primary" onclick="Views.exportCSV();UI.closeModal()"><i class="fa-solid fa-download"></i> Export</button>
        ${g.shortfall?`<button class="btn btn-danger" onclick="toast('Escalation submitted to Cabinet Office','warning');UI.closeModal()"><i class="fa-solid fa-bell"></i> Escalate</button>`:''}
      </div>`);
  },

  exportCSV() {
    const rows=[['Grid','Region','Type','Status','Output MW','Target MW','Eff%','ROI','Shortfall'],...D.grids.map(g=>[g.name,g.region,g.type,statusLabel(g),S.liveOut[g.id]??g.out,g.target,eff(g)+'%',g.roi,g.shortfall||'None'])];
    const csv=rows.map(r=>r.join(',')).join('\n');
    const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'})); a.download='ResourceCommand_GridExport.csv'; a.click();
    toast('CSV exported','success');
  },

  // ── ENERGY-MINE NEXUS ──
  nexus() {
    const el=$('view-nexus');
    el.innerHTML=`<div class="view-scroll">
      <div class="page-header">
        <h1><i class="fa-solid fa-link" style="color:var(--primary)"></i> Energy–Mine Nexus</h1>
        <p>The invisible loop that powers Botswana's economy — made visible. Every diamond mine depends on a substation. Every substation failure is a royalty risk.</p>
      </div>
      <div class="loop-card">
        <div class="loop-title"><i class="fa-solid fa-rotate"></i> The Botswana Resource Loop</div>
        <div class="loop-steps">
          <div class="loop-step">⛏ Morupule Coal</div><div class="loop-arrow">→</div>
          <div class="loop-step">⚡ Power Stations</div><div class="loop-arrow">→</div>
          <div class="loop-step">💎 Diamond Mines</div><div class="loop-arrow">→</div>
          <div class="loop-step">💰 Royalties (P3.5B/yr)</div><div class="loop-arrow">→</div>
          <div class="loop-step">🏗 Infrastructure Funding</div><div class="loop-arrow">→</div>
          <div class="loop-step">⚡ Power Stations</div>
        </div>
      </div>
      <div style="margin-bottom:24px">
        <h3 style="font-size:14px;font-weight:700;margin-bottom:16px">Mine ↔ Grid Dependencies</h3>
        ${D.mines.map(mine=>{
          const grid=D.grids.find(g=>g.id===mine.gridId);
          const e=grid?eff(grid):0; const ec=effColor(e);
          const risk=e<60?'HIGH RISK':e<90?'MODERATE':'LOW RISK';
          const riskColor=e<60?'var(--danger)':e<90?'var(--warning)':'var(--success)';
          return `<div style="display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:0;margin-bottom:16px">
            <div class="nexus-entity ${e<60?'critical':e>=90?'optimal':''}">
              <div class="nexus-entity-icon">${mine.mineral==='Diamonds'?'💎':mine.mineral==='Coal'?'⛏':mine.mineral==='Copper'?'🔶':mine.mineral==='Nickel'?'🔩':'🧪'}</div>
              <div class="nexus-entity-name">${mine.name}</div>
              <div class="nexus-entity-sub">${mine.company} · ${mine.mineral}</div>
              <div class="nexus-metrics">
                <div class="nexus-metric"><span>Annual Output</span><span>${mine.output}</span></div>
                <div class="nexus-metric"><span>Royalty Value</span><span style="color:var(--success)">${mine.royalty}</span></div>
                <div class="nexus-metric"><span>Status</span><span class="${mine.status==='Optimal'?'text-success':mine.status==='Offline'?'text-danger':'text-warning'}">${mine.status}</span></div>
              </div>
            </div>
            <div class="nexus-connector">
              <div style="font-size:10px;color:var(--text-muted);text-align:center;margin-bottom:4px">Grid Supply</div>
              <div style="font-size:22px;color:${riskColor}">⚡</div>
              <div style="font-size:10px;font-weight:700;color:${riskColor};text-align:center">${risk}</div>
              ${grid?`<div style="font-size:10px;color:var(--text-muted);text-align:center">${e}% capacity</div>`:''}
            </div>
            ${grid?`<div class="nexus-entity ${e<60?'critical':e>=90?'optimal':''}">
              <div class="nexus-entity-icon">⚡</div>
              <div class="nexus-entity-name">${grid.name}</div>
              <div class="nexus-entity-sub">${grid.region} · ${grid.type}</div>
              <div class="nexus-metrics">
                <div class="nexus-metric"><span>Output</span><span>${S.liveOut[grid.id]??grid.out} MW / ${grid.target} MW target</span></div>
                <div class="nexus-metric"><span>Efficiency</span><span style="color:${ec}">${e}%</span></div>
                <div class="nexus-metric"><span>Grid ROI</span><span>${grid.roi}%</span></div>
              </div>
            </div>`:'<div class="nexus-entity"><div style="color:var(--text-muted);font-size:13px">No grid assigned</div></div>'}
          </div>`;
        }).join('')}
      </div>
    </div>`;
  },

  // ── RESOURCE MAP ──
  map() {
    const el=$('view-map');
    el.innerHTML=`<div class="view-scroll">
      <div class="page-header"><h1><i class="fa-solid fa-map" style="color:var(--primary)"></i> Resource Map</h1><p>All active energy grids and mining concessions — live status overlay</p></div>
      <div style="display:grid;grid-template-columns:1fr 300px;gap:20px">
        <div class="map-wrapper">
          <div class="map-svg-container">
            <svg id="botswana-svg" viewBox="0 0 100 110" xmlns="http://www.w3.org/2000/svg">
              <!-- Botswana simplified border -->
              <path d="M 20,5 L 75,5 L 80,15 L 85,20 L 90,30 L 88,45 L 85,55 L 78,65 L 72,75 L 65,82 L 58,88 L 50,95 L 42,98 L 35,95 L 28,88 L 20,80 L 15,68 L 12,55 L 10,42 L 12,28 L 15,15 Z"
                fill="rgba(56,189,248,0.04)" stroke="rgba(56,189,248,0.25)" stroke-width="1" stroke-linejoin="round"/>
              <!-- Grid pins -->
              ${D.grids.map(g=>{
                const e=eff(g); const col=e>=90?'#10B981':e>=60?'#F59E0B':'#EF4444';
                return `<g class="grid-pin" onclick="Views.gridModal(${D.grids.indexOf(g)})" title="${g.name}">
                  <circle cx="${g.lng}" cy="${g.lat}" r="5" fill="${col}" fill-opacity="0.25" stroke="${col}" stroke-width="1.5"/>
                  <circle cx="${g.lng}" cy="${g.lat}" r="3" fill="${col}"/>
                  <circle cx="${g.lng}" cy="${g.lat}" r="8" fill="${col}" fill-opacity="0.08" class="pulse-ring"/>
                  <text x="${g.lng+7}" y="${g.lat+1}" class="pin-label" fill="#E2E8F0" font-size="5" dy="0.3em">${g.name.split(' ')[0]}</text>
                </g>`;
              }).join('')}
              <!-- Mine pins (diamonds) -->
              ${D.mines.filter(m=>m.status!=='Offline').map(m=>{
                const col=m.status==='Optimal'?'#A855F7':m.status==='Warning'?'#F59E0B':'#EF4444';
                return `<g onclick="toast('${m.name} — ${m.output} output','info')" style="cursor:pointer">
                  <polygon points="${m.lng},${m.lat-5} ${m.lng+4},${m.lat} ${m.lng},${m.lat+5} ${m.lng-4},${m.lat}" fill="${col}" fill-opacity="0.8" stroke="${col}" stroke-width="0.5"/>
                </g>`;
              }).join('')}
            </svg>
          </div>
          <div class="map-legend">
            <div class="legend-item"><div class="legend-dot" style="background:#10B981"></div>Grid Optimal</div>
            <div class="legend-item"><div class="legend-dot" style="background:#F59E0B"></div>Grid Warning</div>
            <div class="legend-item"><div class="legend-dot" style="background:#EF4444"></div>Grid Critical</div>
            <div class="legend-item"><div style="width:10px;height:10px;background:#A855F7;clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%)"></div>Mine</div>
          </div>
        </div>
        <div>
          <div class="card" style="margin-bottom:16px">
            <div class="card-header"><h3>Active Concessions</h3></div>
            ${D.concessions.map(c=>{
              const sc=c.status==='Active'?'badge-optimal':c.status==='Suspended'?'badge-critical':c.status==='Exploration'?'badge-info':'badge-warning';
              return `<div style="display:flex;justify-content:space-between;align-items:flex-start;padding:10px 0;border-bottom:1px solid var(--border)">
                <div><div style="font-size:12px;font-weight:700">${c.name}</div>
                <div style="font-size:11px;color:var(--text-muted)">${c.mineral} · ${c.size}</div>
                <div style="font-size:11px;color:var(--text-muted)">${c.company}</div></div>
                <span class="badge ${sc}" style="font-size:10px">${c.status}</span>
              </div>`;
            }).join('')}
          </div>
        </div>
      </div>
    </div>`;
  },

  // ── GRIDS ──
  grids() {
    const el=$('view-grids');
    el.innerHTML=`<div class="view-scroll">
      <div class="page-header"><h1>Grid Status</h1><p>Detailed performance metrics for all national energy grid nodes</p></div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px">
        ${D.grids.map((g,i)=>{
          const e=eff(g); const ec=effColor(e);
          return `<div class="card animate-in" style="animation-delay:${i*0.06}s">
            <div class="card-header">
              <div><div style="font-size:14px;font-weight:800">${g.name}</div>
              <div style="font-size:11px;color:var(--text-muted);margin-top:2px"><i class="fa-solid fa-location-dot"></i> ${g.region} · ${g.type}</div></div>
              <span class="badge ${statusClass(g)}">${statusLabel(g)}</span>
            </div>
            ${[['Output',(S.liveOut[g.id]??g.out)+' MW'],['Target',g.target+' MW'],['CAIDI',g.caidi],['Forced Outage',g.fo],['ROI',g.roi+'%'],['CapEx',g.capex]].map(([l,v])=>`<div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:12px"><span style="color:var(--text-muted)">${l}</span><span style="font-weight:600">${v}</span></div>`).join('')}
            ${g.shortfall?`<div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:12px"><span style="color:var(--text-muted)">Shortfall</span><span style="font-weight:700;color:var(--danger)">${g.shortfall}</span></div>`:''}
            <div style="margin-top:14px"><div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:4px"><span>Capacity Utilization</span><span style="color:${ec};font-weight:700">${e}%</span></div>
            <div class="progress-track"><div class="progress-fill" style="width:${Math.min(e,100)}%;background:${ec}"></div></div></div>
            <div style="display:flex;gap:8px;margin-top:14px">
              <button class="btn" style="flex:1;justify-content:center" onclick="Views.gridModal(${i})"><i class="fa-solid fa-chart-simple"></i> Diagnostics</button>
              ${g.shortfall?`<button class="btn btn-danger" onclick="toast('Escalation submitted to Cabinet','warning')"><i class="fa-solid fa-bell"></i></button>`:''}
            </div>
          </div>`;
        }).join('')}
      </div>
    </div>`;
  },

  // ── MINING MODULE ──
  mining() {
    const el=$('view-mining');
    el.innerHTML=`<div class="view-scroll">
      <div class="page-header"><h1><i class="fa-solid fa-gem" style="color:var(--purple)"></i> Mining Module</h1><p>Botswana's extractive sector — live commodity prices, mine output, and concession registry</p></div>
      <h3 style="font-size:13px;font-weight:700;margin-bottom:14px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px">Commodity Tracker</h3>
      <div class="commodity-grid" style="margin-bottom:28px">
        ${D.commodities.map((c,i)=>`<div class="commodity-card animate-in" style="animation-delay:${i*0.05}s">
          <div class="commodity-icon">${c.symbol}</div>
          <div class="commodity-name">${c.name}</div>
          <div class="commodity-price">${c.price}</div>
          <div class="commodity-change ${c.up?'text-success':'text-danger'}">${c.up?'▲':'▼'} ${c.change}</div>
          <div style="font-size:10px;color:var(--text-muted);margin-top:4px">${c.desc}</div>
        </div>`).join('')}
      </div>
      <h3 style="font-size:13px;font-weight:700;margin-bottom:14px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px">Active Mines</h3>
      <div class="card" style="padding:0;overflow:hidden">
        <table class="premium-table">
          <thead><tr><th>Mine</th><th>Company</th><th>Mineral</th><th>Region</th><th>Annual Output</th><th>Royalty</th><th>Grid Supply</th><th>Status</th></tr></thead>
          <tbody>
            ${D.mines.map((m,i)=>{
              const grid=D.grids.find(g=>g.id===m.gridId);
              const e=grid?eff(grid):0; const ec=effColor(e);
              const sc=m.status==='Optimal'?'badge-optimal':m.status==='Offline'?'badge-critical':'badge-warning';
              return `<tr class="animate-in" style="animation-delay:${i*0.06}s">
                <td style="font-weight:700">${m.name}</td>
                <td style="color:var(--text-muted);font-size:12px">${m.company}</td>
                <td>${m.mineral}</td>
                <td style="font-size:12px;color:var(--text-muted)">${m.region}</td>
                <td style="font-weight:600">${m.output}</td>
                <td style="font-weight:700;color:var(--success)">${m.royalty}</td>
                <td>${grid?`<span style="font-size:11px;color:${ec}">${e}% (${grid.name.split(' ')[0]})</span>`:'<span style="color:var(--text-muted);font-size:11px">N/A</span>'}</td>
                <td><span class="badge ${sc}">${m.status}</span></td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>
    </div>`;
  },

  // ── INVESTMENTS ──
  async investments() {
    const el=$('view-investments');
    el.innerHTML=`<div class="view-scroll">
      <div class="page-header"><h1>Investment Tracker</h1><p>Capital deployment, ROI performance, and parastatal financial health</p></div>
      <div class="kpi-grid">
        ${[{t:'Capital Committed',v:'P 45.2M',icon:'fa-handshake',color:'var(--primary)',bg:'rgba(56,189,248,0.1)'},
           {t:'Capital Deployed',v:'P 28.0M',icon:'fa-chart-pie',color:'var(--success)',bg:'rgba(16,185,129,0.1)'},
           {t:'Avg Projected ROI',v:'14.2%',icon:'fa-percent',color:'var(--purple)',bg:'rgba(168,85,247,0.1)'},
           {t:'Funding Gap',v:'P 2.1M',icon:'fa-circle-exclamation',color:'var(--danger)',bg:'rgba(239,68,68,0.1)'}]
          .map(k=>`<div class="card kpi-card"><div class="kpi-info"><h4>${k.t}</h4><div class="value">${k.v}</div></div><div class="kpi-icon" style="color:${k.color};background:${k.bg}"><i class="fa-solid ${k.icon}"></i></div></div>`).join('')}
      </div>
      <div class="dashboard-grid">
        <div class="card col-span-2"><div class="card-header"><h3>ROI Performance — Projected vs Actual</h3></div><canvas id="roiChart" height="100"></canvas></div>
        <div class="card"><div class="card-header"><h3>By Investor Source</h3></div><canvas id="srcChart" height="200"></canvas></div>
        <div class="card col-span-3" style="padding:0;overflow:hidden">
          <div class="card-header" style="padding:16px 20px"><h3>Active Investment Projects</h3></div>
          <table class="premium-table">
            <thead><tr><th>Project</th><th>Investor</th><th>Committed</th><th>Deployed</th><th>ROI Target</th><th>Status</th></tr></thead>
            <tbody>${D.investments.map(inv=>{
              const sc=inv.status==='On Track'?'badge-optimal':inv.status==='Delayed'?'badge-warning':'badge-critical';
              return `<tr><td style="font-weight:700">${inv.project}</td><td style="color:var(--text-muted)">${inv.investor}</td><td>${inv.committed}</td><td>${inv.deployed}</td><td style="color:var(--success);font-weight:700">${inv.roi}</td><td><span class="badge ${sc}">${inv.status}</span></td></tr>`;
            }).join('')}</tbody>
          </table>
        </div>
      </div>
    </div>`;
    await delay(50);
    UI.chart('roiChart',{type:'bar',data:{labels:D.investments.map(i=>i.project.substring(0,18)+'…'),datasets:[{label:'Projected %',data:[16.1,11,8,12,9,13],backgroundColor:'rgba(56,189,248,0.6)',borderRadius:5},{label:'Actual %',data:[16.1,6.8,2.1,8.2,10.5,11.9],backgroundColor:'rgba(16,185,129,0.6)',borderRadius:5}]},options:{responsive:true,plugins:{legend:{position:'top',labels:{font:{family:'Inter',size:11},boxWidth:10}}},scales:{x:{grid:{display:false}},y:{ticks:{callback:v=>v+'%'},grid:{color:'rgba(255,255,255,0.04)'}}}}});
    UI.chart('srcChart',{type:'doughnut',data:{labels:['GoB','BPOPF','AfDB','World Bank','ABSA','AIIM'],datasets:[{data:[9,12,7,5.1,6.5,5.6],backgroundColor:['#38BDF8','#10B981','#A855F7','#F59E0B','#EF4444','#64748B'],borderWidth:3,borderColor:'#10141E'}]},options:{cutout:'65%',plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:10,font:{size:11}}}}}});
  },

  // ── TARGETS ──
  targets() {
    $('view-targets').innerHTML=`<div class="view-scroll">
      <div class="page-header"><h1>Strategic Targets</h1><p>Government mandates, national energy goals, and resource sector milestones</p></div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:16px">
        ${D.targets.map((t,i)=>`<div class="card animate-in" style="animation-delay:${i*0.07}s">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px">
            <div style="font-size:14px;font-weight:700;flex:1;padding-right:12px">${t.title}</div>
            <div style="font-size:22px;font-weight:900;color:${t.color}">${t.pct}%</div>
          </div>
          <div style="font-size:11px;color:var(--text-muted);margin-bottom:10px"><i class="fa-solid fa-calendar-days"></i> ${t.deadline} · ${t.meta}</div>
          <div class="progress-track"><div class="progress-fill" style="width:${t.pct}%;background:${t.color}"></div></div>
        </div>`).join('')}
      </div>
    </div>`;
  },

  // ── COMPLIANCE ──
  compliance() {
    const el=$('view-compliance');
    el.innerHTML=`<div class="view-scroll">
      <div class="page-header"><h1>Compliance & BERA Registry</h1><p>License status, SLA enforcement, penalties, and accountability scorecards</p></div>
      <div class="card col-span-3 animate-in" style="padding:0;overflow:hidden;margin-bottom:20px">
        <div class="card-header" style="padding:16px 20px"><h3>BERA & Mining License Registry</h3>
          <button class="btn btn-primary" onclick="Views.exportCompCSV()"><i class="fa-solid fa-download"></i> Export</button></div>
        <table class="premium-table">
          <thead><tr><th>Company</th><th>Type</th><th>Ref No.</th><th>Issued</th><th>Expiry</th><th>Score</th><th>Status</th><th></th></tr></thead>
          <tbody>${D.licenses.map(l=>{
            const sc=l.status==='Compliant'?'badge-optimal':l.status==='Under Review'?'badge-warning':l.status==='Non-Compliant'||l.status==='Renewal Overdue'?'badge-critical':'badge-info';
            const sc2=l.score>=80?'var(--success)':l.score>=60?'var(--warning)':'var(--danger)';
            return `<tr>
              <td style="font-weight:700">${l.company}</td><td style="font-size:11px;color:var(--text-muted)">${l.type}</td>
              <td style="font-family:monospace;font-size:11px;color:var(--primary)">${l.ref}</td>
              <td style="font-size:12px;color:var(--text-muted)">${l.issued}</td><td>${l.expiry}</td>
              <td><div style="display:flex;align-items:center;gap:8px"><div style="flex:1;height:5px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden"><div style="width:${l.score}%;height:100%;background:${sc2};border-radius:3px"></div></div><span style="color:${sc2};font-size:11px;font-weight:700">${l.score}</span></div></td>
              <td><span class="badge ${sc}">${l.status}</span></td>
              <td><button class="btn-action" onclick="toast('Viewing BERA file: ${l.ref}','info')">View</button></td>
            </tr>`;
          }).join('')}</tbody>
        </table>
      </div>
    </div>`;
  },
  exportCompCSV() {
    const rows=[['Company','Type','Ref','Issued','Expiry','Score','Status'],...D.licenses.map(l=>[l.company,l.type,l.ref,l.issued,l.expiry,l.score,l.status])];
    const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([rows.map(r=>r.join(',')).join('\n')],{type:'text/csv'})); a.download='BERA_Registry.csv'; a.click();
    toast('Registry exported','success');
  },

  // ── BLOCKCHAIN ──
  async blockchain() {
    const el=$('view-blockchain');
    el.innerHTML=`<div class="view-scroll">
      <div class="page-header">
        <h1><i class="fa-solid fa-cubes" style="color:var(--primary)"></i> Blockchain Audit Trail</h1>
        <p>Every government action, payment, and grid change permanently recorded with SHA-256 cryptographic hashing. Tamper-proof. Independently verifiable.</p>
      </div>
      <div class="kpi-grid" style="margin-bottom:24px">
        ${[{t:'Chain Height',v:S.chain.length,icon:'fa-layer-group',color:'var(--primary)',bg:'rgba(56,189,248,0.1)'},
           {t:'Latest Hash',v:S.chain.length?(S.chain[S.chain.length-1].hash.slice(0,8)+'…'):'—',icon:'fa-fingerprint',color:'var(--success)',bg:'rgba(16,185,129,0.1)'},
           {t:'Chain Status',v:'Verified',icon:'fa-shield-check',color:'var(--success)',bg:'rgba(16,185,129,0.1)'},
           {t:'Immutable Records',v:S.chain.length,icon:'fa-lock',color:'var(--purple)',bg:'rgba(168,85,247,0.1)'}]
          .map(k=>`<div class="card kpi-card"><div class="kpi-info"><h4>${k.t}</h4><div class="value" style="font-size:${k.v.toString().length>8?'14px':'24px'};font-family:monospace">${k.v}</div></div><div class="kpi-icon" style="color:${k.color};background:${k.bg}"><i class="fa-solid ${k.icon}"></i></div></div>`).join('')}
      </div>
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
        <button class="btn btn-primary" id="verify-btn" onclick="Views.verifyChain()"><i class="fa-solid fa-circle-check"></i> Verify Entire Chain</button>
        <div id="verify-result" style="font-size:12px"></div>
      </div>
      <div id="chain-blocks">
        ${S.chain.slice().reverse().map(b=>`<div class="chain-block verified animate-in">
          <div class="block-header">
            <div style="display:flex;align-items:center;gap:10px">
              <span class="block-height">#${b.h}</span>
              <span class="block-action">${b.action}</span>
            </div>
            <div class="chain-status ok"><i class="fa-solid fa-check-circle"></i> Verified</div>
          </div>
          <div style="font-size:12px;color:var(--text-sub);margin-bottom:8px">${b.payload}</div>
          <div class="block-meta">
            <span><i class="fa-solid fa-user"></i> ${b.actor}</span>
            <span><i class="fa-solid fa-clock"></i> ${new Date(b.ts).toLocaleString()}</span>
          </div>
          <div class="block-hash"><span style="color:var(--text-muted)">Hash: </span>${b.hash}</div>
          <div class="block-hash" style="margin-top:4px"><span style="color:var(--text-muted)">Prev: </span>${b.prev}</div>
        </div>`).join('')}
      </div>
    </div>`;
  },
  async verifyChain() {
    const btn=$('verify-btn'); const res=$('verify-result');
    btn.disabled=true; btn.innerHTML='<i class="fa-solid fa-spinner fa-spin"></i> Verifying…';
    const results=await BC.verify();
    btn.disabled=false; btn.innerHTML='<i class="fa-solid fa-circle-check"></i> Verify Entire Chain';
    const allOk=results.every(r=>r.ok);
    res.innerHTML=allOk
      ?`<span style="color:var(--success);font-weight:700"><i class="fa-solid fa-shield-check"></i> All ${results.length} blocks verified — chain integrity confirmed</span>`
      :`<span style="color:var(--danger);font-weight:700"><i class="fa-solid fa-triangle-exclamation"></i> Chain integrity FAILED — tamper detected</span>`;
    toast(allOk?'Chain verified — all blocks valid':'Chain integrity FAILED',allOk?'success':'danger');
  },

  // ── FIELD REPORTS ──
  fieldreports() {
    $('view-fieldreports').innerHTML=`<div class="view-scroll">
      <div class="page-header"><h1><i class="fa-solid fa-walkie-talkie" style="color:var(--warning)"></i> Field Reports</h1><p>Grid technicians submit real-time outage reports and site observations. All submissions recorded to blockchain.</p></div>
      <div class="advisor-layout">
        <div class="card"><h3 style="margin-bottom:16px"><i class="fa-solid fa-tower-cell" style="color:var(--warning)"></i> Submit Report</h3>
          ${[['Technician ID / Name','text','tech-id','e.g. T-2049 / Kagiso Molapo'],['GPS Coordinates','text','tech-gps','e.g. -24.6541, 25.9087']].map(([l,t,id,ph])=>`<div class="form-group"><label>${l}</label><input type="${t}" id="${id}" class="form-input" placeholder="${ph}"></div>`).join('')}
          <div class="form-group"><label>Grid / Site</label><select id="fr-grid" class="form-input">${D.grids.map(g=>`<option>${g.name}</option>`).join('')}</select></div>
          <div class="form-group"><label>Incident Type</label><select id="fr-type" class="form-input"><option value="outage">Unplanned Outage</option><option value="maintenance">Scheduled Maintenance</option><option value="equipment">Equipment Fault</option><option value="weather">Weather/Environmental</option><option value="security">Security/Vandalism</option><option value="normal">Normal Check-in</option></select></div>
          <div class="form-group"><label>MW Impact</label><input type="number" id="fr-mw" class="form-input" placeholder="e.g. 25" min="0"></div>
          <div class="form-group"><label>Observations</label><textarea id="fr-desc" class="form-input" rows="4" placeholder="Describe what you observed…"></textarea></div>
          <button class="btn btn-primary" style="width:100%;justify-content:center;padding:12px" onclick="Views.submitReport()"><i class="fa-solid fa-paper-plane"></i> Submit & Record to Blockchain</button>
        </div>
        <div>
          <h3 style="font-size:14px;font-weight:700;margin-bottom:14px">Recent Reports</h3>
          <div id="report-log">${S.fieldReports.length?S.fieldReports.map(r=>Views._reportItem(r)).join(''):'<div style="color:var(--text-muted);font-size:13px">No reports yet this session.</div>'}</div>
        </div>
      </div>
    </div>`;
  },
  _reportItem(r) {
    const tmap={outage:'danger',maintenance:'info',equipment:'warning',weather:'info',security:'danger',normal:'success'};
    const type=tmap[r.type]||'info';
    const tc={'danger':'var(--danger)','info':'var(--primary)','warning':'var(--warning)','success':'var(--success)'};
    return `<div class="report-log-item animate-in">
      <div class="report-log-header">
        <span class="report-log-tech"><i class="fa-solid fa-hard-hat" style="color:${tc[type]}"></i> ${r.tech}</span>
        <span class="report-log-time">${new Date(r.ts).toLocaleString()}</span>
      </div>
      <div style="font-size:11px;color:var(--text-muted);margin-bottom:4px">${r.grid} · ${r.type}${r.mw?' · '+r.mw+' MW impact':''}</div>
      <div class="report-log-desc">${r.desc||'No description provided.'}</div>
    </div>`;
  },
  async submitReport() {
    const tech=$('tech-id').value.trim()||'Unknown Tech';
    const grid=$('fr-grid').value;
    const type=$('fr-type').value;
    const mw=$('fr-mw').value;
    const desc=$('fr-desc').value.trim();
    if (!desc) { toast('Please add a description','danger'); return; }
    const r={tech,grid,type,mw,desc,ts:new Date().toISOString()};
    S.fieldReports.unshift(r);
    sessionStorage.setItem('rc_reports',JSON.stringify(S.fieldReports));
    await BC.add('FIELD_REPORT', tech, `${grid} — ${type}${mw?' ('+mw+' MW impact)':''}: ${desc.slice(0,80)}`);
    toast('Report submitted & recorded to blockchain','success');
    ['tech-id','fr-mw','fr-desc'].forEach(id=>$(id).value='');
    $('report-log').innerHTML=S.fieldReports.map(r=>Views._reportItem(r)).join('');
  },

  // ── REPORTS ──
  reports() {
    const rpts=[
      {title:'Q1 2026 Performance Report',desc:'Full parastatal performance, investment ROI, and grid reliability review.',icon:'fa-chart-bar',color:'var(--primary)',date:'1 Mar 2026',size:'2.4 MB'},
      {title:'Resource Royalty Audit 2025',desc:'Verified diamond, copper, and coal royalty flows from all active concessions.',icon:'fa-gem',color:'var(--purple)',date:'15 Jan 2026',size:'4.8 MB'},
      {title:'National Grid Audit Report',desc:'Independent technical audit of all 16 national grid nodes.',icon:'fa-magnifying-glass-chart',color:'var(--success)',date:'11 Dec 2025',size:'6.1 MB'},
      {title:'Sustainability Progress Report',desc:'Carbon avoidance metrics and clean energy transition status.',icon:'fa-leaf',color:'var(--success)',date:'30 Nov 2025',size:'3.2 MB'},
      {title:'Maun Hydro Crisis Briefing',desc:'Emergency assessment — water levels, ROI impact, remediation plan.',icon:'fa-triangle-exclamation',color:'var(--danger)',date:'5 Feb 2026',size:'1.8 MB'},
      {title:'Budget vs Expenditure Summary',desc:'Capital budgets vs actual expenditure across all projects.',icon:'fa-file-invoice-dollar',color:'var(--warning)',date:'14 Feb 2026',size:'2.0 MB'},
    ];
    $('view-reports').innerHTML=`<div class="view-scroll">
      <div class="page-header"><h1>Reports & Documents</h1><p>Download accountability reports, audit logs, and quarterly summaries</p>
        <button class="btn" onclick="window.print()" style="margin-top:12px"><i class="fa-solid fa-print"></i> Print / Export PDF</button>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px">
        ${rpts.map((r,i)=>`<div class="card animate-in" style="animation-delay:${i*0.06}s;display:flex;flex-direction:column;gap:12px">
          <div style="display:flex;gap:14px;align-items:flex-start">
            <div style="width:44px;height:44px;border-radius:10px;background:${r.color}1a;color:${r.color};display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0"><i class="fa-solid ${r.icon}"></i></div>
            <div><div style="font-size:14px;font-weight:700;margin-bottom:4px">${r.title}</div><div style="font-size:12px;color:var(--text-muted)">${r.desc}</div></div>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;padding-top:10px;border-top:1px solid var(--border)">
            <span style="font-size:11px;color:var(--text-muted)"><i class="fa-solid fa-calendar"></i> ${r.date} · ${r.size}</span>
            <button class="btn btn-primary" onclick="toast('Downloading: ${r.title}','success')"><i class="fa-solid fa-download"></i> Download</button>
          </div>
        </div>`).join('')}
      </div>
    </div>`;
  },
};

// ── BOOT ──────────────────────────────────────────────────
Chart.defaults.color = '#64748B';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = 'Inter';

// Expose to HTML
window.RC = { auth: Auth, ui: UI };
window.Router = Router;
window.Views = Views;
window.toast = toast;

Auth.init();
