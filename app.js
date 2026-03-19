// ════════════════════════════════════════════════════════════════
//  RESOURCE COMMAND ZAMBIA — App Logic
//  Conference Edition Oct 16-17 2026
// ════════════════════════════════════════════════════════════════
'use strict';

// ── STATE ──────────────────────────────────────────────────────
const S = {
  chain: [],
  charts: {},
  activeTab: 'gov',
  liveOut: {},
};

// ── UTILITIES ───────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const delay = ms => new Promise(r => setTimeout(r, ms));
function toast(msg, type = 'info') {
  const t = $('toast');
  t.textContent = msg; t.className = `toast ${type}`;
  clearTimeout(t._t);
  t._t = setTimeout(() => t.classList.add('hidden'), 4500);
}
function eff(g) { return Math.round(((S.liveOut[g.id] ?? g.out) / g.target) * 100); }
function effColor(e) { return e >= 90 ? 'var(--success)' : e >= 60 ? 'var(--warning)' : 'var(--danger)'; }
function statusBadge(s) {
  const map = {
    'Optimal': 'badge-optimal', 'Warning': 'badge-warning',
    'Critical': 'badge-critical', 'Under Construction': 'badge-info',
    'On Track': 'badge-optimal', 'Delayed': 'badge-warning', 'Completed': 'badge-info', 'Critical': 'badge-critical',
    'Compliant': 'badge-optimal', 'Under Review': 'badge-warning', 'Non-Compliant': 'badge-critical',
  };
  return `<span class="badge ${map[s] || 'badge-info'}">${s}</span>`;
}
function destroyChart(id) {
  if (S.charts[id]) { S.charts[id].destroy(); delete S.charts[id]; }
}
function makeChart(id, config) {
  destroyChart(id);
  const el = $(id); if (!el) return;
  S.charts[id] = new Chart(el, config);
}

// ── BLOCKCHAIN ──────────────────────────────────────────────────
const BC = {
  async hash(str) {
    const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
    return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
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
    const prev = S.chain.length ? S.chain[S.chain.length - 1].hash : '0'.repeat(64);
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

// ── CHART DEFAULTS ─────────────────────────────────────────────
Chart.defaults.color = '#64748B';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = 'Inter';

// ── MODAL ───────────────────────────────────────────────────────
const App = {
  openModal(title, html) {
    $('modal-title').textContent = title;
    $('modal-body').innerHTML = html;
    $('modal-overlay').classList.remove('hidden');
  },
  closeModal() { $('modal-overlay').classList.add('hidden'); },

  // ── NAV SCROLL ACTIVE ──────────────────────────────────────
  initNav() {
    const sections = document.querySelectorAll('section[id], div[id]');
    const links = document.querySelectorAll('.nav-links a');
    window.addEventListener('scroll', () => {
      let curr = '';
      sections.forEach(sec => {
        if (window.scrollY >= sec.offsetTop - 100) curr = sec.id;
      });
      links.forEach(l => {
        l.classList.toggle('active', l.getAttribute('href') === `#${curr}`);
      });
    });
  },

  // ── DEFICIT GAUGE ──────────────────────────────────────────
  renderDeficitGauge() {
    const c = ZD.country;
    const rows = [
      { label: 'Installed Capacity', val: c.installed_capacity, max: c.installed_capacity, color: 'var(--primary)', unit: 'MW' },
      { label: 'Actual Generation',  val: c.actual_generation,  max: c.installed_capacity, color: 'var(--warning)', unit: 'MW' },
      { label: 'Peak Demand',        val: c.peak_demand,        max: c.installed_capacity, color: 'var(--text-sub)', unit: 'MW' },
      { label: '⚡ DEFICIT',          val: c.deficit,            max: c.installed_capacity, color: 'var(--danger)', unit: 'MW' },
    ];
    $('deficit-gauge').innerHTML = rows.map(r =>
      `<div class="gauge-row">
        <div class="gauge-label">${r.label}</div>
        <div class="gauge-bar"><div class="gauge-fill" style="width:${Math.round((r.val/r.max)*100)}%;background:${r.color}"></div></div>
        <div class="gauge-val" style="color:${r.color}">${r.val.toLocaleString()} ${r.unit}</div>
      </div>`
    ).join('');
  },

  // ── ZAMBIA MAP ─────────────────────────────────────────────
  renderMap() {
    const gridsG = $('grid-pins');
    const minesG = $('mine-pins');
    if (!gridsG || !minesG) return;

    // Grids
    gridsG.innerHTML = ZD.grids.map((g, i) => {
      const e = eff(g);
      const col = g.status === 'Under Construction' ? '#888888' : e >= 90 ? '#10B981' : e >= 60 ? '#F59E0B' : '#EF4444';
      const r = 4.5;
      return `<g class="grid-pin" data-idx="${i}" data-type="grid" style="cursor:pointer">
        <circle cx="${g.lng}" cy="${g.lat}" r="${r*2}" fill="${col}" fill-opacity="0.08" class="pulse-ring"/>
        <circle cx="${g.lng}" cy="${g.lat}" r="${r}" fill="${col}" fill-opacity="0.25" stroke="${col}" stroke-width="1.2"/>
        <circle cx="${g.lng}" cy="${g.lat}" r="${r*0.55}" fill="${col}"/>
        <text x="${g.lng+6}" y="${g.lat+1}" class="pin-label" fill="#CBD5E1" font-size="4" dy="0.3em" font-family="Inter">${g.name.split(' ')[0]}</text>
      </g>`;
    }).join('');

    // Mines
    minesG.innerHTML = ZD.mines.map((m, i) => {
      const col = m.status === 'Optimal' ? 'var(--copper)' : m.status === 'Warning' ? 'var(--warning)' : 'var(--danger)';
      const s = 5;
      return `<g class="mine-pin" data-idx="${i}" data-type="mine" style="cursor:pointer">
        <polygon points="${m.lng},${m.lat-s} ${m.lng+s},${m.lat} ${m.lng},${m.lat+s} ${m.lng-s},${m.lat}" fill="${col}" fill-opacity="0.85" stroke="${col}" stroke-width="0.5"/>
        <text x="${m.lng+6}" y="${m.lat+1}" class="pin-label" fill="#CBD5E1" font-size="3.8" dy="0.3em" font-family="Inter">${m.mineral}</text>
      </g>`;
    }).join('');

    // Tooltip events
    const tooltip = $('map-tooltip');
    document.querySelectorAll('.grid-pin, .mine-pin').forEach(pin => {
      pin.addEventListener('mouseenter', e => {
        const type = pin.dataset.type;
        const idx = +pin.dataset.idx;
        if (type === 'grid') {
          const g = ZD.grids[idx];
          const ef = eff(g);
          const ec = effColor(ef);
          tooltip.innerHTML = `
            <div class="tooltip-title">⚡ ${g.name}</div>
            <div class="tooltip-row"><span class="tooltip-label">Region</span><span class="tooltip-val">${g.region}</span></div>
            <div class="tooltip-row"><span class="tooltip-label">Type</span><span class="tooltip-val">${g.type}</span></div>
            <div class="tooltip-row"><span class="tooltip-label">Generation</span><span class="tooltip-val" style="color:${ec}">${g.out} MW / ${g.target} MW target</span></div>
            <div class="tooltip-row"><span class="tooltip-label">Efficiency</span><span class="tooltip-val" style="color:${ec}">${ef}%</span></div>
            <div class="tooltip-row"><span class="tooltip-label">Status</span><span class="tooltip-val">${g.status}</span></div>
            <div style="margin-top:8px;font-size:10px;color:var(--text-muted)">${g.note}</div>`;
        } else {
          const m = ZD.mines[idx];
          tooltip.innerHTML = `
            <div class="tooltip-title">⛏️ ${m.name}</div>
            <div class="tooltip-row"><span class="tooltip-label">Company</span><span class="tooltip-val">${m.company.split('/')[0].trim()}</span></div>
            <div class="tooltip-row"><span class="tooltip-label">Location</span><span class="tooltip-val">${m.location}</span></div>
            <div class="tooltip-row"><span class="tooltip-label">Output</span><span class="tooltip-val">${m.output}</span></div>
            <div class="tooltip-row"><span class="tooltip-label">Royalty</span><span class="tooltip-val" style="color:var(--success)">${m.royalty}</span></div>
            <div class="tooltip-row"><span class="tooltip-label">Investment</span><span class="tooltip-val" style="color:var(--primary)">${m.investment}</span></div>
            <div class="tooltip-row"><span class="tooltip-label">Jobs</span><span class="tooltip-val">${m.jobs}</span></div>`;
        }
        tooltip.style.display = 'block';
        tooltip.style.left = (e.clientX + 16) + 'px';
        tooltip.style.top  = (e.clientY - 10) + 'px';
      });
      pin.addEventListener('mousemove', e => {
        tooltip.style.left = (e.clientX + 16) + 'px';
        tooltip.style.top  = (e.clientY - 10) + 'px';
      });
      pin.addEventListener('mouseleave', () => { tooltip.style.display = 'none'; });
      pin.addEventListener('click', () => {
        const type = pin.dataset.type;
        const idx  = +pin.dataset.idx;
        if (type === 'grid')  App.showGridModal(idx);
        if (type === 'mine')  App.showMineModal(idx);
      });
    });
  },

  showGridModal(i) {
    const g = ZD.grids[i]; const ef = eff(g); const ec = effColor(ef);
    App.openModal(`⚡ ${g.name}`, `
      <div style="margin-bottom:16px">${statusBadge(g.status)}</div>
      ${[['Region',g.region],['Type',g.type],['Operator',g.operator],['Generation',(g.out)+' MW'],['Target',g.target+' MW'],['Efficiency',ef+'%'],['CAIDI',g.caidi||'N/A'],['Forced Outage',g.fo||'N/A'],['ROI',g.roi+'%'],['CapEx',g.capex],['Shortfall',g.shortfall||'None']].map(([l,v])=>`<div class="modal-stat"><span class="modal-stat-label">${l}</span><span class="modal-stat-value">${v}</span></div>`).join('')}
      <div style="margin-top:16px;padding:14px;background:rgba(56,189,248,0.04);border-radius:10px;border-left:3px solid ${ec}">
        <div style="font-size:11px;text-transform:uppercase;color:var(--text-muted);margin-bottom:4px">Assessment</div>
        <div style="font-size:13px;line-height:1.6;color:var(--text-sub)">${g.note}</div>
      </div>
      <div style="margin-top:12px;padding:14px;background:rgba(16,185,129,0.04);border-radius:10px;border-left:3px solid var(--success)">
        <div style="font-size:11px;text-transform:uppercase;color:var(--text-muted);margin-bottom:4px">Recommendation</div>
        <div style="font-size:13px;line-height:1.6;color:var(--text-sub)">${g.rec}</div>
      </div>
    `);
  },

  showMineModal(i) {
    const m = ZD.mines[i];
    const compScore = m.compliance || 0;
    const sc = compScore >= 90 ? 'var(--success)' : compScore >= 70 ? 'var(--warning)' : 'var(--danger)';
    App.openModal(`⛏️ ${m.name}`, `
      <div style="margin-bottom:16px">${statusBadge(m.status)}</div>
      ${[['Company',m.company],['Mineral',m.mineral],['Region',m.region],['Location',m.location],['Annual Output',m.output],['Royalty Contribution',m.royalty],['Active Investment',m.investment],['Direct Jobs',m.jobs],['Energy Draw',m.energyMW+' MW from grid']].map(([l,v])=>`<div class="modal-stat"><span class="modal-stat-label">${l}</span><span class="modal-stat-value">${v}</span></div>`).join('')}
      <div style="margin-top:12px"><div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:6px"><span>MRCA Compliance Score</span><span style="font-weight:800;color:${sc}">${compScore}/100</span></div>
      <div class="progress-track"><div class="progress-fill" style="width:${compScore}%;background:${sc}"></div></div></div>
      <div style="margin-top:12px;padding:14px;background:rgba(255,255,255,0.02);border-radius:10px;border-left:3px solid var(--primary)">
        <div style="font-size:11px;text-transform:uppercase;color:var(--text-muted);margin-bottom:4px">Latest Intelligence</div>
        <div style="font-size:12px;line-height:1.6;color:var(--text-sub)">${m.note}</div>
      </div>
    `);
  },

  // ── COMMODITIES (map sidebar) ──────────────────────────────
  renderCommodityMini() {
    $('commodity-mini').innerHTML = ZD.commodities.slice(0, 5).map(c => `
      <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--border)">
        <div style="display:flex;align-items:center;gap:8px"><span>${c.symbol}</span><span style="font-size:12px;font-weight:600">${c.name}</span></div>
        <div style="text-align:right">
          <div style="font-size:12px;font-weight:700">${c.price}</div>
          <div style="font-size:10px;font-weight:700;color:${c.up?'var(--success)':'var(--danger)'}">${c.up?'▲':'▼'} ${c.change}</div>
        </div>
      </div>`).join('');
  },

  // ── REGULATORS (map sidebar) ────────────────────────────────
  renderRegulatorsMini() {
    $('regulators-mini').innerHTML = ZD.regulators.map(r => `
      <div style="display:flex;align-items:flex-start;gap:10px;padding:8px 0;border-bottom:1px solid var(--border)">
        <div style="width:8px;height:8px;border-radius:50%;background:${r.color};margin-top:5px;flex-shrink:0"></div>
        <div>
          <div style="font-size:11px;font-weight:700">${r.name.split('(')[0].trim()}</div>
          <div style="font-size:10px;color:var(--text-muted)">${r.role.substring(0,50)}…</div>
        </div>
      </div>`).join('');
  },

  // ── PRIVACY SECTION ────────────────────────────────────────
  renderPrivacy() {
    const t = ZD.privacyTiers.company;
    $('privacy-shared-list').innerHTML =
      `<div style="font-size:12px;font-weight:700;color:var(--success);margin-bottom:10px">✅ Company shares (regulatory mandate):</div>` +
      t.shared.map(d => `<div class="data-pill pill-shared"><i class="fa-solid fa-check"></i>${d}</div>`).join('');
    $('privacy-private-list').innerHTML =
      `<div style="font-size:12px;font-weight:700;color:var(--danger);margin-bottom:10px;margin-top:16px">🔒 Company keeps private:</div>` +
      t.private.map(d => `<div class="data-pill pill-private"><i class="fa-solid fa-lock"></i>${d}</div>`).join('');
  },

  // ── TAB SWITCHING ──────────────────────────────────────────
  showTab(id) {
    ['gov','bank','company'].forEach(t => {
      $(`tab-${t}`).classList.toggle('active', t === id);
      $(`tab-content-${t}`).classList.toggle('active', t === id);
    });
    S.activeTab = id;
    if (id === 'gov')     App.renderGovPortal();
    if (id === 'bank')    App.renderBankPortal();
    if (id === 'company') App.renderCompanyPortal();
  },

  // ── GOVERNMENT PORTAL ──────────────────────────────────────
  async renderGovPortal() {
    // KPIs
    const totalOut = ZD.grids.reduce((a,g) => a + (g.out), 0);
    const kpis = [
      { t:'Total Generation',   v:`${totalOut} MW`,     trend:'vs 2,800 MW demand', up:false, icon:'fa-bolt',           color:'var(--danger)',  bg:'rgba(239,68,68,0.1)' },
      { t:'Royalties (2025)',    v:'$70M',               trend:'+367% via reforms',  up:true,  icon:'fa-diamond',        color:'var(--success)', bg:'rgba(16,185,129,0.1)' },
      { t:'Licensed Operators', v:ZD.licenses.length,   trend:'MRCA 2024 registry', up:true,  icon:'fa-file-contract',  color:'var(--primary)', bg:'rgba(56,189,248,0.1)' },
      { t:'Grid Deficit',       v:'1,600 MW',            trend:'Emergency status',   up:false, icon:'fa-circle-exclamation', color:'var(--warning)', bg:'rgba(245,158,11,0.1)' },
    ];
    $('gov-kpis').innerHTML = kpis.map(k => `<div class="card kpi-card animate-in">
      <div><div class="kpi-label">${k.t}</div><div class="kpi-val" style="font-size:1.4rem">${k.v}</div>
      <div class="kpi-trend" style="color:${k.up?'var(--success)':'var(--danger)'}"><i class="fa-solid ${k.up?'fa-arrow-trend-up':'fa-arrow-trend-down'}"></i> ${k.trend}</div></div>
      <div class="kpi-icon" style="color:${k.color};background:${k.bg}"><i class="fa-solid ${k.icon}"></i></div>
    </div>`).join('');

    // Targets
    $('targets-list').innerHTML = ZD.targets.map(t => `
      <div style="margin-bottom:20px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
          <div>
            <div style="font-size:13px;font-weight:700">${t.title}</div>
            <div style="font-size:11px;color:var(--text-muted)"><i class="fa-solid fa-calendar"></i> ${t.deadline} · ${t.meta}</div>
          </div>
          <div style="font-size:20px;font-weight:900;color:${t.color}">${t.pct}%</div>
        </div>
        <div class="progress-track"><div class="progress-fill" style="width:${t.pct}%;background:${t.color}"></div></div>
      </div>`).join('');

    // Licenses table
    $('gov-licenses-tbody').innerHTML = ZD.licenses.map(l => {
      const sc2 = l.score >= 80 ? 'var(--success)' : l.score >= 60 ? 'var(--warning)' : 'var(--danger)';
      const stBadge = l.status === 'Compliant' ? 'badge-optimal' : l.status === 'Under Review' ? 'badge-warning' : 'badge-critical';
      return `<tr>
        <td style="font-weight:700">${l.company}</td>
        <td style="font-size:11px;color:var(--text-muted)">${l.type}</td>
        <td style="font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--primary)">${l.ref}</td>
        <td style="font-size:12px;color:var(--text-muted)">${l.issued}</td>
        <td>${l.expiry}</td>
        <td><div style="display:flex;align-items:center;gap:8px"><div style="flex:1;height:5px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden"><div style="width:${l.score}%;height:100%;background:${sc2};border-radius:3px"></div></div><span style="color:${sc2};font-size:11px;font-weight:700;width:28px">${l.score}</span></div></td>
        <td><span class="badge ${stBadge}">${l.status}</span></td>
        <td style="font-size:10px;color:var(--text-muted)">${l.law}</td>
        <td><button class="btn btn-sm" onclick="App.toast('Viewing ${l.ref}','info')">View</button></td>
      </tr>`;
    }).join('');

    await delay(60);
    // Charts
    makeChart('gov-energy-chart', {
      type: 'bar',
      data: {
        labels: ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025'],
        datasets: [
          { label: 'Generation (MW)', data: [1800, 1500, 1040, 1200, 1469, 1600, 1750, 1900], backgroundColor: 'rgba(56,189,248,0.5)', borderRadius: 4 },
          { label: 'Demand (MW)',     data: [2400, 2400, 2400, 2600, 2800, 2800, 2800, 2800], type:'line', borderColor:'var(--danger)', borderDash:[4,3], pointRadius:3, fill:false },
        ]
      },
      options: { responsive:true, plugins:{legend:{labels:{font:{size:11},boxWidth:10}}}, scales:{y:{ticks:{callback:v=>v+' MW'},grid:{color:'rgba(255,255,255,0.04)'}},x:{grid:{display:false}}} }
    });
    makeChart('gov-royalty-chart', {
      type: 'bar',
      data: {
        labels: ['Q1 2024','Q2 2024','Q3 2024','Q4 2024','Q1 2025','Q2 2025','Q3 2025','Q4 2025'],
        datasets: [{ label:'Royalty (USD M)', data:[9,12,15,10,18,19,17,16], backgroundColor:'rgba(16,185,129,0.5)', borderRadius:4 }]
      },
      options:{responsive:true,plugins:{legend:{labels:{font:{size:11},boxWidth:10}}},scales:{y:{ticks:{callback:v=>'$'+v+'M'},grid:{color:'rgba(255,255,255,0.04)'}},x:{grid:{display:false}}}}
    });
  },

  // ── BANK PORTAL ────────────────────────────────────────────
  async renderBankPortal() {
    const kpis = [
      { t:'Total Finance Exposure', v:'$6.6B+', trend:'Across 9 positions',  up:true,  icon:'fa-money-bill-trend-up', color:'var(--primary)', bg:'rgba(56,189,248,0.1)' },
      { t:'Avg Compliance Score',   v:'83/100', trend:'Portfolio-weighted',   up:true,  icon:'fa-shield-check',        color:'var(--success)', bg:'rgba(16,185,129,0.1)' },
      { t:'At-Risk Positions',      v:'2',      trend:'KCM + Mopani',         up:false, icon:'fa-triangle-exclamation',color:'var(--warning)', bg:'rgba(245,158,11,0.1)' },
      { t:'YTD Mining Tax (H1\'25)',v:'K7.4B',  trend:'+150% vs H1 2024',     up:true,  icon:'fa-chart-pie',           color:'var(--purple)',  bg:'rgba(168,85,247,0.1)' },
    ];
    $('bank-kpis').innerHTML = kpis.map(k => `<div class="card kpi-card animate-in">
      <div><div class="kpi-label">${k.t}</div><div class="kpi-val" style="font-size:1.3rem">${k.v}</div>
      <div class="kpi-trend" style="color:${k.up?'var(--success)':'var(--danger)'}"><i class="fa-solid ${k.up?'fa-arrow-trend-up':'fa-arrow-trend-down'}"></i> ${k.trend}</div></div>
      <div class="kpi-icon" style="color:${k.color};background:${k.bg}"><i class="fa-solid ${k.icon}"></i></div>
    </div>`).join('');

    $('bank-investments-tbody').innerHTML = ZD.investments.map(inv => {
      const sc = inv.status === 'On Track' ? 'badge-optimal' : inv.status === 'Completed' ? 'badge-info' : inv.status === 'Delayed' ? 'badge-warning' : 'badge-critical';
      return `<tr>
        <td style="font-weight:700">${inv.project}</td>
        <td style="color:var(--text-muted);font-size:12px">${inv.investor}</td>
        <td>${inv.committed}</td><td>${inv.deployed}</td>
        <td style="color:var(--success);font-weight:700">${inv.roi}</td>
        <td><span class="badge badge-info" style="font-size:10px">${inv.type}</span></td>
        <td><span class="badge ${sc}">${inv.status}</span></td>
        <td><span style="font-size:11px;color:var(--success);font-weight:600"><i class="fa-solid fa-link"></i> Live Score</span></td>
      </tr>`;
    }).join('');

    await delay(60);
    makeChart('bank-portfolio-chart', {
      type:'doughnut',
      data:{
        labels:['Mining','Energy','Finance/Other'],
        datasets:[{data:[6100,340,302.5],backgroundColor:['rgba(224,123,57,0.7)','rgba(56,189,248,0.7)','rgba(168,85,247,0.7)'],borderWidth:3,borderColor:'#0D1525'}]
      },
      options:{cutout:'60%',plugins:{legend:{position:'right',labels:{boxWidth:10,font:{size:11}}}}}
    });
    const scores = ZD.mines.map(m => m.compliance || 0);
    makeChart('bank-risk-chart', {
      type:'bar',
      data:{
        labels:ZD.mines.map(m=>m.name.split(' ')[0]),
        datasets:[{label:'Compliance Score',data:scores,backgroundColor:scores.map(s=>s>=80?'rgba(16,185,129,0.6)':s>=60?'rgba(245,158,11,0.6)':'rgba(239,68,68,0.6)'),borderRadius:5}]
      },
      options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{min:0,max:100,ticks:{callback:v=>v+'%'},grid:{color:'rgba(255,255,255,0.04)'}},x:{grid:{display:false}}}}
    });
  },

  // ── COMPANY PORTAL ─────────────────────────────────────────
  async renderCompanyPortal() {
    // Show FQM / Kansanshi as the example company
    const myMines = ZD.mines.filter(m => m.company.includes('First Quantum') || m.id === 'm1');
    const kpis = [
      { t:'My Licensed Mines',     v:'1 Active',   trend:'Kansanshi Cu+Au', up:true,  icon:'fa-gem',              color:'var(--copper)',  bg:'rgba(224,123,57,0.1)' },
      { t:'My Royalty Paid YTD',   v:'$720M+',     trend:'ZRA Verified',    up:true,  icon:'fa-handshake',        color:'var(--success)', bg:'rgba(16,185,129,0.1)' },
      { t:'MRCA Compliance Score', v:'94/100',     trend:'Compliant',       up:true,  icon:'fa-shield-check',     color:'var(--primary)', bg:'rgba(56,189,248,0.1)' },
      { t:'Grid Energy Draw',      v:'120 MW',     trend:'From ZESCO grid',  up:true,  icon:'fa-bolt',             color:'var(--warning)', bg:'rgba(245,158,11,0.1)' },
    ];
    $('company-kpis').innerHTML = kpis.map(k => `<div class="card kpi-card animate-in">
      <div><div class="kpi-label">${k.t}</div><div class="kpi-val" style="font-size:1.3rem">${k.v}</div>
      <div class="kpi-trend" style="color:${k.up?'var(--success)':'var(--danger)'}"><i class="fa-solid ${k.up?'fa-arrow-trend-up':'fa-arrow-trend-down'}"></i> ${k.trend}</div></div>
      <div class="kpi-icon" style="color:${k.color};background:${k.bg}"><i class="fa-solid ${k.icon}"></i></div>
    </div>`).join('');

    $('company-mines-tbody').innerHTML = ZD.mines.map(m => {
      const sc = m.status === 'Optimal' ? 'badge-optimal' : m.status === 'Warning' ? 'badge-warning' : 'badge-critical';
      const cs = m.compliance || 0;
      const cc = cs >= 80 ? 'var(--success)' : cs >= 60 ? 'var(--warning)' : 'var(--danger)';
      const isOurs = m.company.includes('First Quantum');
      return `<tr style="${isOurs?'background:rgba(224,123,57,0.04)':''}">
        <td style="font-weight:700">${m.name}${isOurs?'<span style="font-size:10px;color:var(--copper);margin-left:6px">YOUR ASSET</span>':''}</td>
        <td style="font-size:12px;color:var(--text-muted)">${m.location}</td>
        <td>${m.mineral}</td>
        <td><span class="badge ${sc}">${m.status}</span></td>
        <td style="font-weight:600">${m.output}</td>
        <td style="font-size:12px">${m.energyMW} MW</td>
        <td style="color:var(--success);font-weight:700">${m.royalty}</td>
        <td><div style="display:flex;align-items:center;gap:6px"><div style="width:60px;height:4px;background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden"><div style="width:${cs}%;height:100%;background:${cc}"></div></div><span style="font-size:11px;color:${cc};font-weight:700">${cs}</span></div></td>
        <td><button class="btn btn-sm" onclick="App.showMineModal(${ZD.mines.indexOf(m)})">Detail</button></td>
      </tr>`;
    }).join('');

    await delay(60);
    makeChart('company-energy-chart', {
      type:'line',
      data:{
        labels:['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
        datasets:[
          {label:'My Draw (MW)',data:[118,115,122,119,120,116,114,110,112,118,121,120],borderColor:'var(--copper)',backgroundColor:'rgba(224,123,57,0.06)',tension:0.4,fill:true,pointRadius:3},
          {label:'ZESCO Supply',data:[120,118,100,95,90,88,85,80,82,95,108,115],borderColor:'var(--danger)',borderDash:[4,4],tension:0.4,pointRadius:2,fill:false},
        ]
      },
      options:{responsive:true,plugins:{legend:{labels:{font:{size:11},boxWidth:10}}},scales:{y:{ticks:{callback:v=>v+' MW'},grid:{color:'rgba(255,255,255,0.04)'}},x:{grid:{display:false}}}}
    });
    makeChart('company-compliance-chart', {
      type:'bar',
      data:{
        labels:['MRC Annual Return','ZEMA EIS Update','ERB Energy Report','ZRA Royalty Filing','Safety Report','Local Content (20%)'],
        datasets:[{label:'% Complete',data:[100,92,100,100,88,72],backgroundColor:['rgba(16,185,129,0.6)','rgba(16,185,129,0.6)','rgba(16,185,129,0.6)','rgba(16,185,129,0.6)','rgba(245,158,11,0.6)','rgba(245,158,11,0.6)'],borderRadius:5}]
      },
      options:{indexAxis:'y',responsive:true,plugins:{legend:{display:false}},scales:{x:{min:0,max:100,ticks:{callback:v=>v+'%'},grid:{color:'rgba(255,255,255,0.04)'}},y:{grid:{display:false}}}}
    });
  },

  // ── BLOCKCHAIN SECTION ────────────────────────────────────
  renderBlockchain() {
    const kpis = [
      { t:'Chain Height',       v:S.chain.length,                                                              icon:'fa-layer-group',  color:'var(--primary)', bg:'rgba(56,189,248,0.1)' },
      { t:'Latest Hash',        v:S.chain.length ? S.chain[S.chain.length-1].hash.slice(0,10)+'…' : '—',      icon:'fa-fingerprint',  color:'var(--success)', bg:'rgba(16,185,129,0.1)' },
      { t:'Chain Integrity',    v:'Verified ✓',                                                                icon:'fa-shield-check', color:'var(--success)', bg:'rgba(16,185,129,0.1)' },
      { t:'Immutable Records',  v:S.chain.length,                                                              icon:'fa-lock',         color:'var(--purple)',  bg:'rgba(168,85,247,0.1)' },
    ];
    $('bc-kpis').innerHTML = kpis.map(k => `<div class="card kpi-card animate-in">
      <div><div class="kpi-label">${k.t}</div><div class="kpi-val" style="font-size:${typeof k.v==='string'&&k.v.length>6?'13px':'1.4rem'};font-family:'JetBrains Mono',monospace">${k.v}</div></div>
      <div class="kpi-icon" style="color:${k.color};background:${k.bg}"><i class="fa-solid ${k.icon}"></i></div>
    </div>`).join('');

    $('chain-blocks').innerHTML = S.chain.slice().reverse().map(b => `
      <div class="chain-block animate-in">
        <div class="block-header">
          <div style="display:flex;align-items:center;gap:10px">
            <span class="block-height">#${b.h}</span>
            <span class="block-action" style="color:var(--text)">${b.action}</span>
          </div>
          <div class="chain-status"><i class="fa-solid fa-check-circle"></i> Verified</div>
        </div>
        <div style="font-size:12px;color:var(--text-sub);margin-bottom:8px;line-height:1.5">${b.payload}</div>
        <div class="block-meta">
          <span><i class="fa-solid fa-user"></i> ${b.actor}</span>
          <span><i class="fa-solid fa-clock"></i> ${new Date(b.ts).toLocaleString()}</span>
        </div>
        <div class="block-hash" style="margin-top:6px"><span style="color:var(--text-muted)">Hash: </span>${b.hash}</div>
        <div class="block-hash" style="margin-top:2px"><span style="color:var(--text-muted)">Prev: </span>${b.prev.slice(0,32)}…</div>
      </div>`).join('');
  },

  async verifyChain() {
    const btn = $('verify-btn'); const res = $('verify-result');
    btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Verifying…';
    const results = await BC.verify();
    btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-circle-check"></i> Verify Entire Chain';
    const allOk = results.every(r => r.ok);
    res.innerHTML = allOk
      ? `<span style="color:var(--success);font-weight:700"><i class="fa-solid fa-shield-check"></i> All ${results.length} blocks verified — Zambia chain integrity confirmed</span>`
      : `<span style="color:var(--danger);font-weight:700"><i class="fa-solid fa-triangle-exclamation"></i> Chain integrity FAILED</span>`;
    toast(allOk ? '✅ All blocks verified — chain intact' : '❌ Chain integrity failure detected', allOk ? 'success' : 'danger');
  },

  async addTestBlock() {
    const events = [
      ['ROYALTY_RECEIVED','ZRA Treasury','FQM Q1 2026 copper royalty: $18.6M received. ZRA Ref RY-2026-Q1-041.'],
      ['LICENSE_RENEWAL','MRC (MRCA 2024)','Mopani Copper Mines license renewed — MRC/MC/2026/055. ZEMA EIS conditions attached.'],
      ['GRID_UPDATE','ERB / ZESCO','Mumbwa Sunshare Phase 1 grid connection approved (122 MW). ERB operational clearance granted.'],
      ['PENALTY_ISSUED','ZEMA Compliance','Mimbula Mine — dust suppression violation. ZMW 400,000 penalty issued. ZEMA File MB-2026-014.'],
      ['INVESTMENT_MILESTONE','Min. Finance / MRC','Barrick Lumwana Super Pit — $380M disbursement milestone confirmed. Construction on schedule.'],
    ];
    const e = events[Math.floor(Math.random() * events.length)];
    const block = await BC.add(e[0], e[1], e[2]);
    App.renderBlockchain();
    toast(`🔗 New block #${block.h} (${e[0]}) recorded to chain`, 'success');
  },

  // ── TIERS ─────────────────────────────────────────────────
  renderTiers() {
    $('tiers-container').innerHTML = ZD.tiers.map((t, i) => `
      <div class="tier-card ${i===1?'featured':''}" style="background:${i===1?'rgba(224,123,57,0.04)':'var(--bg-card)'}">
        ${i===1?'<div class="tier-featured-badge">⭐ Recommended Entry Point</div>':''}
        <div class="tier-icon" style="background:rgba(255,255,255,0.04);color:${t.color}"><i class="fa-solid ${t.icon}"></i></div>
        <div>
          <div class="tier-name">${t.name}</div>
          <div class="tier-price" style="color:${t.color}">${t.price}</div>
          <div class="tier-audience" style="margin-top:4px">For: ${t.audience}</div>
        </div>
        <ul class="tier-features">${t.features.map(f=>`<li>${f}</li>`).join('')}</ul>
        <button class="btn ${i===2?'btn-primary':i===1?'btn-copper':''} btn-lg" style="justify-content:center;width:100%" onclick="App.requestDemo()">${t.cta}</button>
      </div>`).join('');
  },

  // ── ROADMAP TIMELINE ───────────────────────────────────────
  renderRoadmap() {
    const items = [
      { date:'Q4 2026',   title:'Government Pilot — MRC & ERB',               desc:'Deploy sovereign prototype. MRC uses for MRCA 2024 digital filing. ERB uses for grid reporting. Funded by conference engagement.', color:'var(--primary)' },
      { date:'Q1 2027',   title:'Zanaco / Stanbic Bank Integration',            desc:'Banking modules live. Compliance-linked credit scores feed into existing loan monitoring systems.', color:'var(--warning)' },
      { date:'Q2 2027',   title:'Industry Mandate — 5 Major Mines',             desc:'FQM, Barrick, Mopani, KCM, CNMC contractually onboarded under MRCA 2024 digital compliance obligation.', color:'var(--success)' },
      { date:'Q3 2027',   title:'ZEMA Environmental Module',                    desc:'Environmental reporting integration. All EIS submissions, monitoring data, and compliance flags flow through the platform.', color:'var(--success)' },
      { date:'Q4 2027',   title:'AfDB / World Bank Grant Recognition',           desc:'Platform certified as sovereign infrastructure. Eligible for DFI co-financing for AfDB / IFC-backed projects.', color:'var(--purple)' },
      { date:'2028–2031', title:'SADC Expansion (16 Countries)',                 desc:'Botswana, Namibia, DRC, Zimbabwe, Tanzania onboarding. Resource Command becomes the SADC extractive intelligence standard.', color:'var(--copper)' },
    ];
    $('roadmap-timeline').innerHTML = items.map(item => `
      <div class="tl-item">
        <div class="tl-dot" style="background:${item.color}"></div>
        <div class="tl-date">${item.date}</div>
        <div class="tl-title">${item.title}</div>
        <div class="tl-desc">${item.desc}</div>
      </div>`).join('');
  },

  // ── EXPORT HELPERS ─────────────────────────────────────────
  exportTargetsCSV() {
    const rows = [['Target','Progress%','Deadline','Notes'],...ZD.targets.map(t=>[t.title,t.pct+'%',t.deadline,t.meta])];
    App._downloadCSV(rows,'ZambiaRC_Targets.csv');
    toast('Targets exported','success');
  },
  exportLicensesCSV() {
    const rows = [['Company','Type','Ref','Issued','Expiry','Score','Status','Law'],...ZD.licenses.map(l=>[l.company,l.type,l.ref,l.issued,l.expiry,l.score,l.status,l.law])];
    App._downloadCSV(rows,'ZambiaRC_MRCA_Registry.csv');
    toast('MRCA License Registry exported','success');
  },
  _downloadCSV(rows, filename) {
    const csv = rows.map(r=>r.join(',')).join('\n');
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv],{type:'text/csv'}));
    a.download = filename; a.click();
  },
  requestDemo() { toast('📅 Demo request recorded — team will contact you within 24hrs.','success'); },
  downloadPitch() { toast('📄 Pitch deck download queued — conference edition PDF.','info'); },

  // ── LIVE FEED ────────────────────────────────────────────
  startLiveFeed() {
    ZD.grids.forEach(g => { S.liveOut[g.id] = g.out; });
    setInterval(() => {
      ZD.grids.forEach(g => {
        if (g.status === 'Under Construction') return;
        const prev = S.liveOut[g.id];
        const delta = (Math.random() - 0.5) * 0.04;
        S.liveOut[g.id] = Math.max(1, Math.round(prev * (1 + delta)));
      });
    }, 15000);
  },

  // ── INIT ──────────────────────────────────────────────────
  async init() {
    App.initNav();
    App.startLiveFeed();
    await BC.build(ZD.chainSeed);
    App.renderDeficitGauge();
    App.renderPrivacy();
    App.renderMap();
    App.renderCommodityMini();
    App.renderRegulatorsMini();
    App.renderGovPortal();
    App.renderBlockchain();
    App.renderTiers();
    App.renderRoadmap();

    // Modal click-outside close
    $('modal-overlay').addEventListener('click', e => {
      if (e.target === $('modal-overlay')) App.closeModal();
    });

    // Smooth scroll for nav links
    document.querySelectorAll('a[href^="#"]').forEach(a => {
      a.addEventListener('click', e => {
        e.preventDefault();
        const target = document.querySelector(a.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior:'smooth' });
      });
    });

    // Portal tab init
    document.querySelectorAll('#portals .tab-btn').forEach(btn => {
      btn.style.borderColor = btn.classList.contains('active') ? 'var(--border-strong)' : 'transparent';
    });

    toast('🇿🇲 Resource Command Zambia — Conference Edition Loaded', 'success');
  }
};

window.addEventListener('DOMContentLoaded', () => App.init());
