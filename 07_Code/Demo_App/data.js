// Resource Command V1 — All Data
const D = {
  grids: [
    { id:'g1', name:'Gaborone Central Array', region:'South East', type:'Solar',  out:450, target:400, caidi:'12 min/yr', fo:'0.4%', roi:16.1, capex:'P8.2M', shortfall:null,    lat:69, lng:47, rec:'Performing 12.5% above target. Recommend Phase 2 expansion.' },
    { id:'g2', name:'Francistown Solar P1',   region:'North East', type:'Solar',  out:120, target:115, caidi:'18 min/yr', fo:'0.8%', roi:13.4, capex:'P4.1M', shortfall:null,    lat:27, lng:62, rec:'Stable performance. Scheduled maintenance due Q3.' },
    { id:'g3', name:'Palapye Biogas Node',    region:'Central',    type:'Biogas', out:85,  target:150, caidi:'86 min/yr', fo:'3.2%', roi:6.8,  capex:'P6.5M', shortfall:'P1.2M', lat:40, lng:55, rec:'43% below target. Additional biogas feedstock commitments needed.' },
    { id:'g4', name:'Maun Hydro-Ex',          region:'North West', type:'Hydro',  out:12,  target:80,  caidi:'220 min/yr',fo:'9.8%', roi:2.1,  capex:'P9.0M', shortfall:'P0.9M', lat:33, lng:21, rec:'CRITICAL: 15% of target. Drought impact. Cabinet review required.' },
    { id:'g5', name:'Jwaneng Expansion',      region:'Southern',   type:'Solar',  out:310, target:300, caidi:'8 min/yr',  fo:'0.2%', roi:17.5, capex:'P7.4M', shortfall:null,    lat:74, lng:32, rec:'Best performing grid — model for national expansion.' },
    { id:'g6', name:'Kanye Wind Farm',        region:'Southern',   type:'Wind',   out:60,  target:90,  caidi:'55 min/yr', fo:'1.9%', roi:8.2,  capex:'P5.6M', shortfall:null,    lat:67, lng:37, rec:'Seasonal wind reduction. Hybrid storage proposed.' },
    { id:'g7', name:'Serowe Community Grid',  region:'Central',    type:'Solar',  out:40,  target:38,  caidi:'22 min/yr', fo:'0.6%', roi:11.9, capex:'P1.8M', shortfall:null,    lat:41, lng:52, rec:'Meets electrification targets. Pilot success.' },
  ],
  investments: [
    { id:'i1', project:'Gaborone Solar Ph.2',     investor:'BPOPF',          committed:'P12.0M', deployed:'P9.6M',  roi:'15%',       status:'On Track' },
    { id:'i2', project:'Palapye Biogas Upgrade',  investor:'ABSA Botswana',  committed:'P6.5M',  deployed:'P3.1M',  roi:'11%',       status:'Delayed'  },
    { id:'i3', project:'Maun Hydro Remediation',  investor:'GoB Direct',     committed:'P9.0M',  deployed:'P2.4M',  roi:'8%',        status:'Critical' },
    { id:'i4', project:'Kanye Wind Storage',      investor:'AIIM Partners',  committed:'P5.6M',  deployed:'P4.2M',  roi:'12%',       status:'On Track' },
    { id:'i5', project:'Rural Electrification',   investor:'AfDB',           committed:'P7.0M',  deployed:'P5.8M',  roi:'Social',    status:'On Track' },
    { id:'i6', project:'Grid Modernization',      investor:'World Bank IFC', committed:'P5.1M',  deployed:'P3.0M',  roi:'13%',       status:'On Track' },
  ],
  mines: [
    { id:'m1', name:'Jwaneng Diamond Mine',    company:'Debswana',          mineral:'Diamonds', region:'Southern',   output:'15.3M carats/yr', royalty:'P2.1B', gridId:'g5', status:'Optimal',  lat:74, lng:31 },
    { id:'m2', name:'Orapa Diamond Mine',      company:'Debswana',          mineral:'Diamonds', region:'Central',    output:'11.9M carats/yr', royalty:'P1.4B', gridId:'g7', status:'Optimal',  lat:37, lng:33 },
    { id:'m3', name:'Morupule Colliery',       company:'Debswana',          mineral:'Coal',     region:'Central',    output:'3.5Mtpa',          royalty:'P180M', gridId:'g3', status:'Warning',  lat:41, lng:54 },
    { id:'m4', name:'Khoemacau Copper',        company:'Khoemacau Copper Mining', mineral:'Copper', region:'North West', output:'60Ktpa',        royalty:'P420M', gridId:'g4', status:'Warning',  lat:30, lng:24 },
    { id:'m5', name:'BCL Nickel (Mothballed)', company:'BCL Ltd (Gov)',     mineral:'Nickel',   region:'North East', output:'Paused',           royalty:'P0',    gridId:'g2', status:'Offline',  lat:26, lng:61 },
    { id:'m6', name:'Soda Ash (Botash)',       company:'Botash (State-Owned)',mineral:'Soda Ash',region:'North West', output:'300Ktpa',          royalty:'P95M',  gridId:'g4', status:'Optimal',  lat:35, lng:20 },
  ],
  commodities: [
    { name:'Diamonds', symbol:'💎', price:'$6,200/ct', change:'+2.1%', up:true,  desc:'Botswana #1 export' },
    { name:'Coal',     symbol:'⛏',  price:'$130/t',    change:'-0.8%', up:false, desc:'Morupule grade export' },
    { name:'Copper',   symbol:'🔶', price:'$9,450/t',  change:'+3.4%', up:true,  desc:'Khoemacau production' },
    { name:'Nickel',   symbol:'🔩', price:'$16,200/t', change:'+1.2%', up:true,  desc:'Spot price LME' },
    { name:'Soda Ash', symbol:'🧪', price:'$420/t',    change:'-1.5%', up:false, desc:'Botash FOB' },
    { name:'Gold',     symbol:'🥇', price:'$2,310/oz', change:'+0.9%', up:true,  desc:'Spot price LBMA' },
    { name:'Uranium',  symbol:'☢', price:'$91/lb',    change:'+5.2%', up:true,  desc:'Untapped reserves' },
    { name:'Manganese',symbol:'🪨', price:'$5.20/dmtu',change:'+0.4%', up:true,  desc:'Regional export' },
  ],
  licenses: [
    { id:'l1', company:'BPC Energy Ltd',       type:'Generation & Transmission', ref:'BERA/EL/2021/001', issued:'Jan 2021', expiry:'Jan 2036', score:94, status:'Compliant'      },
    { id:'l2', company:'Gaborone Solar Co.',   type:'Generation (Renewable)',    ref:'BERA/EL/2023/019', issued:'Mar 2023', expiry:'Mar 2038', score:89, status:'Compliant'      },
    { id:'l3', company:'Palapye Biogas Ltd',   type:'Generation (Biogas)',       ref:'BERA/EL/2022/008', issued:'Sep 2022', expiry:'Sep 2037', score:58, status:'Under Review'   },
    { id:'l4', company:'Maun Hydro Consortium',type:'Generation (Hydro)',        ref:'BERA/EL/2020/004', issued:'Apr 2020', expiry:'Apr 2035', score:32, status:'Non-Compliant'  },
    { id:'l5', company:'Kanye Wind Ops Pty',   type:'Generation (Wind)',         ref:'BERA/EL/2024/031', issued:'Jul 2024', expiry:'Jul 2039', score:76, status:'Compliant'      },
    { id:'l6', company:'NatFuel Petroleum',    type:'Petroleum Import',          ref:'BERA/PP/2024/056', issued:'Apr 2024', expiry:'Mar 2025', score:41, status:'Renewal Overdue'},
    { id:'l7', company:'Khoemacau Copper',     type:'Mining Concession (Copper)',ref:'MME/MC/2019/012',  issued:'Jun 2019', expiry:'Jun 2039', score:91, status:'Compliant'      },
    { id:'l8', company:'Debswana',             type:'Mining Concession (Diamonds)',ref:'MME/MC/1978/001',issued:'Jan 1978', expiry:'Jan 2049', score:97, status:'Compliant'      },
  ],
  concessions: [
    { id:'c1', name:'Block 9 — NW Copper Belt',  company:'Khoemacau / Sandfire', mineral:'Copper',   status:'Active',  size:'3,240 km²', lat:28, lng:23 },
    { id:'c2', name:'Jwaneng Kimberlite Pipe',   company:'Debswana',             mineral:'Diamonds', status:'Active',  size:'188 km²',   lat:74, lng:31 },
    { id:'c3', name:'Orapa-Letlhakane Cluster',  company:'Debswana',             mineral:'Diamonds', status:'Active',  size:'520 km²',   lat:37, lng:33 },
    { id:'c4', name:'Selebi-Phikwe Nickel Belt', company:'BCL Ltd',              mineral:'Nickel',   status:'Suspended',size:'890 km²',  lat:26, lng:62 },
    { id:'c5', name:'Morupule Coal Field',        company:'Debswana',             mineral:'Coal',     status:'Active',  size:'1,100 km²', lat:41, lng:54 },
    { id:'c6', name: 'Sua Pan Soda Ash',         company:'Botash',               mineral:'Soda Ash', status:'Active',  size:'1,600 km²', lat:35, lng:68 },
    { id:'c7', name:'Gcwihaba Uranium Zone',     company:'Exploration Stage',    mineral:'Uranium',  status:'Exploration',size:'2,400 km²',lat:22, lng:21 },
    { id:'c8', name:'Tati Nickel Belt Extension',company:'Tati Co. (Pending)',   mineral:'Nickel',   status:'Pending', size:'340 km²',   lat:24, lng:68 },
  ],
  chainSeed: [
    { h:1,  action:'SYSTEM_INIT',       actor:'SYSTEM',            payload:'Resource Command V1 blockchain initialised. Genesis block.',                    ts:'2026-01-01T08:00:00Z' },
    { h:2,  action:'LICENSE_ISSUED',    actor:'BERA Authority',    payload:'BERA/EL/2024/031 issued to Kanye Wind Ops Pty — 15yr generation license.',     ts:'2026-01-15T09:14:22Z' },
    { h:3,  action:'PAYMENT_LOGGED',    actor:'Treasury',          payload:'P9.6M disbursed for Gaborone Solar Ph.2. Ref: BPOPF/2026/003.',               ts:'2026-01-22T11:30:44Z' },
    { h:4,  action:'CONCESSION_GRANTED',actor:'Min. Minerals',     payload:'MME/MC/2026/019 granted to Tawana Copper JV — Block 12, NW District.',        ts:'2026-02-01T14:05:10Z' },
    { h:5,  action:'PENALTY_ISSUED',    actor:'BERA Authority',    payload:'P650,000 penalty to Maun Hydro — forced outage 9.8% exceeds 7.5% SLA.',       ts:'2026-02-05T16:20:33Z' },
    { h:6,  action:'SLA_BREACH',        actor:'Compliance Engine', payload:'Palapye Biogas Day 61 breach — auto-escalation triggered BERA s.55(2).',       ts:'2026-02-10T07:45:00Z' },
    { h:7,  action:'ROYALTY_RECEIVED',  actor:'Treasury',          payload:'P2.1B diamond royalty received from Debswana Q4 2025. BURS ref TRY-2026-041.', ts:'2026-02-15T09:00:00Z' },
    { h:8,  action:'INVESTMENT_APPROVED',actor:'Min. Finance',     payload:'AfDB P7.0M rural electrification tranche 2 approved and recorded.',           ts:'2026-02-20T15:30:00Z' },
    { h:9,  action:'FIELD_REPORT',      actor:'Tech T-1042',       payload:'Gaborone Central Array Q1 inspection — all systems nominal.',                  ts:'2026-03-01T08:10:00Z' },
    { h:10, action:'LICENSE_WARNING',   actor:'Compliance Engine', payload:'NatFuel BERA/PP/2024/056 expired — auto-suspension notice generated.',         ts:'2026-03-05T09:00:00Z' },
  ],
  targets: [
    { title:'Renewable Share (Target: 50%)',        pct:34, color:'var(--success)', deadline:'Dec 2030', meta:'National Energy Policy Mandate' },
    { title:'Rural Electrification Coverage',       pct:72, color:'var(--primary)', deadline:'Dec 2027', meta:'72% of rural households connected' },
    { title:'CAIDI Reliability Improvement',        pct:58, color:'var(--warning)', deadline:'Jun 2026', meta:'Outage duration -58% vs baseline' },
    { title:'Parastatal Efficiency Index',          pct:82, color:'var(--success)', deadline:'Ongoing',  meta:'Target ≥0.80 — Currently 0.82' },
    { title:'Biogas Feedstock Targets',             pct:42, color:'var(--danger)',  deadline:'Mar 2026', meta:'CRITICAL: Below trajectory' },
    { title:'Mining Digital Reporting Compliance',  pct:61, color:'var(--primary)', deadline:'Dec 2026', meta:'61% of operators filing digitally' },
  ],
  suppliers: [
    { name:'BPC Energy Ltd',       type:'Solar/Transmission',  region:'south-east', cap:450, comp:94, rel:97,  roi:16.1, local:true,  green:true,  desc:'National parastatal. Highest compliance, government-guaranteed.' },
    { name:'Jwaneng Expansion Ltd',type:'Solar (Premium)',      region:'southern',   cap:310, comp:96, rel:99,  roi:17.5, local:true,  green:true,  desc:'Best performing grid — 103% utilisation, model for expansion.' },
    { name:'Gaborone Solar Co.',   type:'Solar (Renewable)',   region:'south-east', cap:120, comp:89, rel:92,  roi:13.4, local:true,  green:true,  desc:'Private solar operator. Excellent renewable credentials.' },
    { name:'Kanye Wind Ops',       type:'Wind (Renewable)',    region:'southern',   cap:60,  comp:76, rel:78,  roi:8.2,  local:true,  green:true,  desc:'First commercial wind node. Seasonal fluctuations — storage needed.' },
    { name:'Scatec Solar (IPP)',   type:'Utility-Scale Solar', region:'any',        cap:500, comp:91, rel:94,  roi:14.5, local:false, green:true,  desc:'International IPP, strong Africa track record. Requires BERA license.' },
    { name:'Eskom (SA)',           type:'Base Load',           region:'any',        cap:2000,comp:85, rel:88,  roi:12.0, local:false, green:false, desc:'Via SAPP interconnect. High capacity, high carbon.' },
    { name:'NamPower (Namibia)',   type:'Hydro+Solar',         region:'any',        cap:350, comp:82, rel:86,  roi:11.0, local:false, green:true,  desc:'Clean cross-border supply via SADC Power Pool.' },
  ],
};

// Role definitions
const ROLES = {
  minister: { label:'National Command', icon:'fa-landmark', color:'var(--primary)',
    nav: [
      { cat:'Overview', items: [
        { id:'dashboard', label:'Dashboard', icon:'fa-grid-2' },
        { id:'nexus',     label:'Energy-Mine Nexus', icon:'fa-link' },
        { id:'map',       label:'Resource Map', icon:'fa-map' },
      ]},
      { cat:'Energy Grid', items: [
        { id:'grids',       label:'Grid Status', icon:'fa-bolt' },
        { id:'investments', label:'Investments', icon:'fa-money-bill-wave' },
        { id:'targets',     label:'Targets', icon:'fa-bullseye' },
      ]},
      { cat:'Mining & Resources', items: [
        { id:'mining', label:'Mining Module', icon:'fa-gem' },
      ]},
      { cat:'Governance', items: [
        { id:'compliance',   label:'Compliance & BERA', icon:'fa-scale-balanced' },
        { id:'blockchain',   label:'Blockchain Audit', icon:'fa-cubes' },
        { id:'fieldreports', label:'Field Reports', icon:'fa-walkie-talkie' },
      ]},
      { cat:'Documents', items: [
        { id:'reports', label:'Reports', icon:'fa-file-contract' },
      ]},
    ]
  },
  investor: { label:'Investor & Company', icon:'fa-chart-line', color:'var(--success)',
    nav: [
      { cat:'Overview', items: [
        { id:'dashboard', label:'Dashboard', icon:'fa-grid-2' },
        { id:'map',       label:'Resource Map', icon:'fa-map' },
      ]},
      { cat:'Performance', items: [
        { id:'grids',       label:'Grid Status',   icon:'fa-bolt' },
        { id:'investments', label:'Investments',   icon:'fa-money-bill-wave' },
        { id:'targets',     label:'Targets',       icon:'fa-bullseye' },
        { id:'mining',      label:'Mining Module', icon:'fa-gem' },
      ]},
      { cat:'Documents', items: [
        { id:'reports', label:'Reports', icon:'fa-file-contract' },
      ]},
    ]
  },
  public: { label:'Public Accountability', icon:'fa-users', color:'var(--purple)',
    nav: [
      { cat:'Transparency', items: [
        { id:'dashboard',  label:'Overview',         icon:'fa-grid-2' },
        { id:'map',        label:'Resource Map',     icon:'fa-map' },
        { id:'nexus',      label:'Energy-Mine Nexus',icon:'fa-link' },
        { id:'blockchain', label:'Audit Trail',      icon:'fa-cubes' },
        { id:'reports',    label:'Public Reports',   icon:'fa-file-contract' },
      ]},
    ]
  },
};
