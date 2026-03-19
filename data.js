// ════════════════════════════════════════════════════════════════
//  RESOURCE COMMAND ZAMBIA — Conference Prototype Data Layer
//  October 16-17 2026 Conference Edition
//  Built on real 2024-2025 statistics
// ════════════════════════════════════════════════════════════════
'use strict';

const ZD = {

  // ── COUNTRY INFO ─────────────────────────────────────────────
  country: {
    name: 'Republic of Zambia',
    capital: 'Lusaka',
    population: '20.1M',
    gdp: '$29.4B',
    gdpGrowth: '+5.8% (2025)',
    currency: 'Zambian Kwacha (ZMW)',
    flag: '🇿🇲',
    miningGDP: '~12%',
    exportShare: '~70% copper',
    copperTarget: '3M tonnes/yr by 2031',
    installed_capacity: 3871,
    actual_generation: 1469,
    peak_demand: 2800,
    deficit: 1600,
    hydro_share: 85,
    solar_target_mw: 500,
  },

  // ── ENERGY GRIDS / POWER ASSETS ──────────────────────────────
  grids: [
    {
      id: 'g1', name: 'Kariba North Bank Power Station',
      region: 'Southern Province', type: 'Hydro',
      operator: 'ZESCO Limited',
      out: 720, target: 1080, caidi: '186 min/yr', fo: '8.2%',
      roi: 6.1, capex: '$1.2B', shortfall: '$62M',
      lat: 74, lng: 36,
      status: 'Critical',
      note: 'CRITICAL: Kariba reservoir at 6% in Feb 2025. Significant drought impact — 40% below operating target.',
      rec: 'Emergency load-shedding in effect. Requires diversification to solar/gas immediately. Cabinet intervention required.'
    },
    {
      id: 'g2', name: 'Kafue Gorge Lower',
      region: 'Central Province', type: 'Hydro',
      operator: 'ZESCO Limited',
      out: 380, target: 750, caidi: '142 min/yr', fo: '6.4%',
      roi: 7.8, capex: '$2.0B', shortfall: '$28M',
      lat: 62, lng: 42,
      status: 'Warning',
      note: 'Kafue reservoir at 17% — below seasonal average. Seasonal efficiency -49%.',
      rec: 'Supplement with SAPP imports and accelerate Kafue Gorge Upper expansion.'
    },
    {
      id: 'g3', name: 'Maamba Collieries Thermal',
      region: 'Southern Province', type: 'Coal/Thermal',
      operator: 'Maamba Collieries Ltd',
      out: 270, target: 300, caidi: '38 min/yr', fo: '1.9%',
      roi: 12.4, capex: '$600M', shortfall: null,
      lat: 79, lng: 34,
      status: 'Optimal',
      note: 'Phase 2 (300 MW) commissioning expected mid-2026. Critical baseload during hydro deficit.',
      rec: 'Commission Phase 2 on schedule. Consider coal blending for emissions compliance.'
    },
    {
      id: 'g4', name: 'Chisamba Solar PV (100 MW)',
      region: 'Central Province', type: 'Solar',
      operator: 'ZESCO / Private',
      out: 78, target: 100, caidi: '12 min/yr', fo: '0.4%',
      roi: 14.2, capex: '$90M', shortfall: null,
      lat: 55, lng: 45,
      status: 'Optimal',
      note: 'First utility-scale solar. 78% avg output. Daytime supplement to hydro deficit.',
      rec: 'Replicate model. Phase 2 (200 MW) approved. Fast-track commissioning by Q4 2026.'
    },
    {
      id: 'g5', name: 'Mailo Solar PV (25 MW)',
      region: 'Central Province', type: 'Solar',
      operator: 'Greenco',
      out: 22, target: 25, caidi: '8 min/yr', fo: '0.3%',
      roi: 13.8, capex: '$22M', shortfall: null,
      lat: 53, lng: 48,
      status: 'Optimal',
      note: '88% utilization. IPP model proving commercially viable for Zambia.',
      rec: 'Replicate IPP structure. Enable net-metering for mining companies.'
    },
    {
      id: 'g6', name: 'Mumbwa Sunshare Solar (122 MW)',
      region: 'Central Province', type: 'Solar',
      operator: 'Sunshare Holdings',
      out: 0, target: 122, caidi: 'N/A', fo: 'N/A',
      roi: 15.1, capex: '$110M', shortfall: '$34M',
      lat: 57, lng: 36,
      status: 'Under Construction',
      note: 'Expected generation June 2026. Phase 2 (303 MW) by March 2027.',
      rec: 'Accelerate permitting. ERB license issued — ZEMA environmental clearance pending.'
    },
    {
      id: 'g7', name: 'SAPP Regional Import',
      region: 'Cross-Border', type: 'Import',
      operator: 'ZESCO / SAPP Pool',
      out: 133, target: 218, caidi: 'N/A', fo: '2.1%',
      roi: 8.9, capex: '$55M (Stanbic Facility)',
      shortfall: null,
      lat: 85, lng: 50,
      status: 'Warning',
      note: 'Avg 133 MW from SAPP. Emergency 218 MW from Eskom (SA) and ZPC (Zimbabwe) procured for 2024.',
      rec: 'Expand SAPP import capacity. Negotiate long-term contracts with Eskom and ZPC.'
    },
    {
      id: 'g8', name: 'Mansa Solar PV (50 MW ZESCO)',
      region: 'Luapula Province', type: 'Solar',
      operator: 'ZESCO Limited',
      out: 0, target: 50, caidi: 'N/A', fo: 'N/A',
      roi: 13.5, capex: '$47M', shortfall: '$12M',
      lat: 27, lng: 55,
      status: 'Under Construction',
      note: 'Part of 29 projects (2,510 MW total) under construction. State-financed.',
      rec: 'Prioritize commissioning. Rural electrification milestone.'
    },
  ],

  // ── MINES ────────────────────────────────────────────────────
  mines: [
    {
      id: 'm1', name: 'Kansanshi Copper-Gold Mine',
      company: 'First Quantum Minerals (80%) / ZCCM-IH (20%)',
      mineral: 'Copper + Gold', region: 'North-Western Province',
      location: 'Solwezi',
      output: '181,000 t/yr copper', royalty: '$720M+',
      gridId: 'g4', status: 'Optimal',
      lat: 40, lng: 22,
      investment: '$2.5B (S3 Expansion)',
      jobs: '6,000+ direct',
      note: 'S3 Expansion first concentrate Q3 2025. Now top-10 global copper mine. 6% production increase in 2025.',
      energyMW: 120,
      compliance: 94,
    },
    {
      id: 'm2', name: 'Lumwana Copper Mine (Super Pit)',
      company: 'Barrick Gold Corporation',
      mineral: 'Copper', region: 'North-Western Province',
      location: '100km west of Solwezi',
      output: '~150,000 t/yr copper', royalty: '$580M',
      gridId: 'g4', status: 'Optimal',
      lat: 37, lng: 16,
      investment: '$2.0B Super Pit Expansion (2025-2028)',
      jobs: '5,200+ direct',
      note: 'Super Pit expansion construction commenced 2025, completion 2028. Will double processing capacity.',
      energyMW: 110,
      compliance: 91,
    },
    {
      id: 'm3', name: 'Mopani Copper Mines',
      company: 'IRH-UAE (51%) / ZCCM-IH (49%)',
      mineral: 'Copper + Cobalt', region: 'Copperbelt Province',
      location: 'Kitwe & Mufulira',
      output: '70,000 t/yr target (2025)', royalty: '$210M',
      gridId: 'g1', status: 'Warning',
      lat: 34, lng: 48,
      investment: '$1.1B (Revival & Expansion)',
      jobs: '8,000+ direct',
      note: '40% boost in 2025 vs 2024. Full underground + smelting + refining. Power outages reducing output.',
      energyMW: 95,
      compliance: 72,
    },
    {
      id: 'm4', name: 'Konkola Copper Mines (KCM)',
      company: 'Vedanta Resources (Majority) / ZCCM-IH',
      mineral: 'Copper', region: 'Copperbelt Province',
      location: 'Chingola, Chililabombwe, Nampundwe',
      output: '~80,000 t/yr (revival phase)', royalty: '$160M',
      gridId: 'g1', status: 'Warning',
      lat: 29, lng: 45,
      investment: '$1.0B+ committed (5-yr plan)',
      jobs: '10,000+ direct',
      note: 'Vedanta regained control Aug 2024. 360% production increase YoY in 2025. Target: 300Kt by 2030.',
      energyMW: 80,
      compliance: 65,
    },
    {
      id: 'm5', name: 'Chambishi Copper Mine',
      company: 'CNMC (China)',
      mineral: 'Copper + Cobalt', region: 'Copperbelt Province',
      location: 'Chambishi',
      output: '45,000 t/yr copper', royalty: '$98M',
      gridId: 'g1', status: 'Optimal',
      lat: 31, lng: 52,
      investment: '$800M (ongoing)',
      jobs: '3,200+ direct',
      note: 'Chinese-invested. Cobalt refinery commissioned 2025 — Africa\'s first cobalt sulfate refinery.',
      energyMW: 55,
      compliance: 88,
    },
    {
      id: 'm6', name: 'Mimbula Copper Mine',
      company: 'Jubilee Metals (UK)',
      mineral: 'Copper', region: 'Copperbelt Province',
      location: 'Chingola',
      output: 'New production (2024)', royalty: '$42M',
      gridId: 'g1', status: 'Optimal',
      lat: 28, lng: 43,
      investment: '$280M',
      jobs: '800+ direct',
      note: 'New mine contributing to Zambia\'s 12% copper output growth in 2024.',
      energyMW: 30,
      compliance: 96,
    },
  ],

  // ── COMMODITIES ──────────────────────────────────────────────
  commodities: [
    { name: 'Copper',   symbol: '🔶', price: '$9,480/t',    change: '+3.2%', up: true,  desc: 'LME spot · Zambia #1 export' },
    { name: 'Cobalt',   symbol: '🔵', price: '$56,200/t',   change: '+130%', up: true,  desc: '2025 price surge · Africa refinery' },
    { name: 'Gold',     symbol: '🥇', price: '$2,340/oz',   change: '+1.1%', up: true,  desc: 'LBMA spot · Kansanshi by-product' },
    { name: 'Coal',     symbol: '⛏',  price: '$132/t',      change: '-0.6%', up: false, desc: 'Maamba thermal grade' },
    { name: 'Uranium',  symbol: '☢',  price: '$91/lb',      change: '+5.1%', up: true,  desc: 'Spot price · Zambia reserves' },
    { name: 'Manganese',symbol: '🪨', price: '$5.30/dmtu',  change: '+0.8%', up: true,  desc: 'Regional SADC spot' },
    { name: 'ZMW/USD',  symbol: '💱', price: '1 USD = 26.8 ZMW', change: 'Stable', up: true, desc: 'Bank of Zambia rate' },
    { name: 'Lithium',  symbol: '⚡',  price: '$12,400/t',  change: '+2.4%', up: true,  desc: 'Critical mineral · exploration' },
  ],

  // ── LICENSES / COMPLIANCE ─────────────────────────────────────
  licenses: [
    { id: 'l1', company: 'First Quantum Minerals',    type: 'Mining Concession (Copper+Gold)', ref: 'MRC/MC/2019/041', issued: 'Jun 2019', expiry: 'Jun 2044', score: 94, status: 'Compliant',     law: 'MRCA 2024' },
    { id: 'l2', company: 'Barrick Gold (Lumwana)',    type: 'Mining Concession (Copper)',      ref: 'MRC/MC/2004/007', issued: 'Jan 2004', expiry: 'Jan 2054', score: 91, status: 'Compliant',     law: 'MRCA 2024' },
    { id: 'l3', company: 'Mopani Copper Mines',       type: 'Mining + Env Auth',               ref: 'MRC/MC/2000/003', issued: 'Mar 2000', expiry: 'Dec 2040', score: 72, status: 'Under Review',  law: 'ZEMA EIS' },
    { id: 'l4', company: 'Konkola Copper Mines',      type: 'Mining Concession (Copper)',      ref: 'MRC/MC/1998/001', issued: 'Aug 1998', expiry: 'Aug 2038', score: 65, status: 'Under Review',  law: 'MRCA 2024' },
    { id: 'l5', company: 'CNMC Chambishi',            type: 'Mining Concession (Cu+Co)',       ref: 'MRC/MC/2003/012', issued: 'Apr 2003', expiry: 'Apr 2043', score: 88, status: 'Compliant',     law: 'MRCA 2024' },
    { id: 'l6', company: 'Maamba Collieries Ltd',     type: 'Mining + IPP Generation',         ref: 'ERB/EL/2013/004', issued: 'Jan 2013', expiry: 'Jan 2043', score: 86, status: 'Compliant',     law: 'MRCA + ERB' },
    { id: 'l7', company: 'Greenco / Mailo Solar',     type: 'Generation (Solar IPP)',           ref: 'ERB/EL/2020/019', issued: 'Nov 2020', expiry: 'Nov 2045', score: 97, status: 'Compliant',     law: 'ERB' },
    { id: 'l8', company: 'ZESCO Limited',             type: 'National Utility License',         ref: 'ERB/EL/1995/001', issued: 'Jan 1995', expiry: 'Ongoing', score: 78, status: 'Under Review',   law: 'ERB Act' },
    { id: 'l9', company: 'Mimbula Mine (Jubilee)',    type: 'Mining Concession (Copper)',       ref: 'MRC/MC/2022/088', issued: 'Oct 2022', expiry: 'Oct 2042', score: 96, status: 'Compliant',     law: 'MRCA 2024' },
  ],

  // ── INVESTMENTS ──────────────────────────────────────────────
  investments: [
    { id: 'i1', project: 'Lumwana Super Pit Expansion', investor: 'Barrick Gold Corp',        committed: '$2.0B',  deployed: '$380M', roi: '18%',   status: 'On Track',  type: 'Mining' },
    { id: 'i2', project: 'Kansanshi S3 Expansion',       investor: 'First Quantum Minerals',  committed: '$2.5B',  deployed: '$1.8B', roi: '16%',   status: 'On Track',  type: 'Mining' },
    { id: 'i3', project: 'KCM Revival Plan',              investor: 'Vedanta Resources',       committed: '$1.0B',  deployed: '$210M', roi: '14%',   status: 'On Track',  type: 'Mining' },
    { id: 'i4', project: 'Mopani Rehabilitation',         investor: 'IRH (UAE)',               committed: '$1.1B',  deployed: '$340M', roi: '13%',   status: 'Delayed',   type: 'Mining' },
    { id: 'i5', project: 'Mumbwa Sunshare Solar (Phase1)',investor: 'Sunshare Holdings',       committed: '$110M',  deployed: '$88M',  roi: '15%',   status: 'On Track',  type: 'Energy' },
    { id: 'i6', project: 'Chisamba Solar Ph.2 (200 MW)', investor: 'ZESCO / AfDB',            committed: '$180M',  deployed: '$42M',  roi: '14%',   status: 'On Track',  type: 'Energy' },
    { id: 'i7', project: 'SAPP Power Import Facility',   investor: 'Stanbic Bank Zambia',     committed: '$55.5M', deployed: '$55.5M',roi: '10%',   status: 'Completed', type: 'Finance' },
    { id: 'i8', project: 'Mining SME Finance Portfolio', investor: 'Zanaco Bank',             committed: '$247M',  deployed: '$180M', roi: 'Social', status: 'On Track',  type: 'Finance' },
    { id: 'i9', project: 'Cobalt Sulfate Refinery',      investor: 'CNMC / AfDB',             committed: '$320M',  deployed: '$290M', roi: '22%',   status: 'Completed', type: 'Mining' },
  ],

  // ── REGULATORY BODIES ─────────────────────────────────────────
  regulators: [
    {
      id: 'r1', name: 'Minerals Regulation Commission (MRC)',
      formerly: 'Ministry of Mines & Minerals Development',
      role: 'Mining rights, concessions, royalties, health & safety',
      law: 'Minerals Regulation Commission Act No.14 of 2024 (MRCA)',
      head: 'Commissioner of Mines',
      contact: 'mmmd.gov.zm',
      color: 'var(--primary)',
    },
    {
      id: 'r2', name: 'Energy Regulation Board (ERB)',
      formerly: null,
      role: 'Electricity and petroleum sector regulation, tariffs, licensing',
      law: 'Energy Regulation Act',
      head: 'Director General',
      contact: 'erb.org.zm',
      color: 'var(--warning)',
    },
    {
      id: 'r3', name: 'Zambia Environmental Management Agency (ZEMA)',
      formerly: 'Environmental Council of Zambia',
      role: 'Environmental Impact Assessments, compliance monitoring',
      law: 'Environmental Management Act No.12 of 2011',
      head: 'Director General',
      contact: 'zema.org.zm',
      color: 'var(--success)',
    },
    {
      id: 'r4', name: 'ZCCM Investments Holdings (ZCCM-IH)',
      formerly: 'Zambia Consolidated Copper Mines',
      role: 'State equity in major mines; strategic oversight of mining investment',
      law: 'ZCCM-IH Act',
      head: 'CEO / Board Chair',
      contact: 'zccm-ih.com.zm',
      color: 'var(--purple)',
    },
    {
      id: 'r5', name: 'Zambia Revenue Authority (ZRA)',
      formerly: null,
      role: 'Tax collection, royalty verification, transfer pricing audits',
      law: 'Income Tax Act + Mineral Royalty Act',
      head: 'Commissioner General',
      contact: 'zra.org.zm',
      color: 'var(--danger)',
    },
  ],

  // ── BANKING PARTNERS ─────────────────────────────────────────
  banks: [
    {
      name: 'Zanaco Bank',
      type: 'Commercial Bank (State-Linked)',
      mining_exposure: '$247M (2023-2025)',
      specialty: 'Mining value chain, SME supplier finance',
      rating: 'A-',
      risk_score: 82,
      compliance_link: true,
    },
    {
      name: 'Stanbic Bank Zambia',
      type: 'Commercial Bank (Standard Bank Group)',
      mining_exposure: '$55.5M (power imports 2024)',
      specialty: 'Project finance, risk management, cross-border trade',
      rating: 'A',
      risk_score: 88,
      compliance_link: true,
    },
    {
      name: 'African Development Bank (AfDB)',
      type: 'Development Finance Institution',
      mining_exposure: '$180M (energy + mining)',
      specialty: 'Sovereign guarantees, infrastructure, rural electrification',
      rating: 'AAA',
      risk_score: 95,
      compliance_link: true,
    },
    {
      name: 'World Bank / IFC',
      type: 'Multilateral DFI',
      mining_exposure: '$150M (pipeline)',
      specialty: 'Energy transition, governance reform, climate finance',
      rating: 'AAA',
      risk_score: 96,
      compliance_link: true,
    },
    {
      name: 'Eastern & Southern Africa TDB',
      type: 'Regional DFI',
      mining_exposure: '$2M SME (2023)',
      specialty: 'SME supply chain, trade finance',
      rating: 'AA',
      risk_score: 88,
      compliance_link: true,
    },
  ],

  // ── STRATEGIC TARGETS ─────────────────────────────────────────
  targets: [
    { title: 'Copper Production Target (800Kt→3Mt/yr)',  pct: 30,  color: 'var(--warning)', deadline: 'Dec 2031', meta: '890,346 t achieved in 2025 vs 3M t ambition' },
    { title: 'Solar Diversification (85% hydro → 50%)',  pct: 18,  color: 'var(--danger)',  deadline: 'Dec 2030', meta: 'Critical: 85% hydro dependency must drop to 50%' },
    { title: 'New Generation Commissioned (2,510 MW)',    pct: 34,  color: 'var(--primary)', deadline: 'Dec 2026', meta: '29 projects under construction, 862 MW commissioned' },
    { title: 'ERB Power Quality Compliance (81%→100%)',  pct: 81,  color: 'var(--success)', deadline: 'Dec 2027', meta: 'Q1 2025 compliance rate: 81%' },
    { title: 'Mining Digital Reporting (MRCA 2024)',      pct: 44,  color: 'var(--warning)', deadline: 'Jun 2026', meta: '44% of operators filing digitally under new MRCA' },
    { title: 'ZEMA Environmental Authorization Rate',     pct: 78,  color: 'var(--success)', deadline: 'Ongoing', meta: '96 projects approved in 2026 (42 mining, 20 energy)' },
    { title: 'Royalty Revenue Growth ($15M→$70M)',        pct: 100, color: 'var(--success)', deadline: 'Achieved!', meta: 'Transparency reforms delivered 367% royalty revenue growth' },
    { title: 'Rural Electrification Coverage',            pct: 52,  color: 'var(--warning)', deadline: 'Dec 2030', meta: 'Target 75% rural coverage by 2030' },
  ],

  // ── BLOCKCHAIN SEED ──────────────────────────────────────────
  chainSeed: [
    { h:1,  action:'SYSTEM_INIT',         actor:'SYSTEM',                  payload:'Resource Command Zambia — Genesis block. MRCA 2024 compliance framework initialised.',                                     ts:'2026-01-01T08:00:00Z' },
    { h:2,  action:'LICENSE_ISSUED',      actor:'MRC (MRCA 2024)',          payload:'MRC/MC/2022/088 issued to Mimbula Mine (Jubilee Metals) — 20yr mining concession, copper, Chingola.',                   ts:'2026-01-10T09:14:22Z' },
    { h:3,  action:'ROYALTY_RECEIVED',    actor:'ZRA Treasury',            payload:'Q4 2025 copper royalty: $72M received — First Quantum Minerals (Kansanshi). BURS ref ZRA-2026-0041.',                  ts:'2026-01-22T11:30:44Z' },
    { h:4,  action:'ENERGY_EMERGENCY',    actor:'ERB / ZESCO',             payload:'Emergency load management declared — Kariba at 6% capacity. Grid deficit 1,600 MW. National crisis.',                  ts:'2026-02-01T06:00:00Z' },
    { h:5,  action:'POWER_IMPORT',        actor:'ZESCO Grid Ops',          payload:'218 MW emergency import from Eskom (SA) and ZPC (ZW) commenced — Stanbic $55.5M facility utilised.',                   ts:'2026-02-05T08:30:33Z' },
    { h:6,  action:'MINE_PENALTY',        actor:'ZEMA Compliance',         payload:'KCM Chingola fined $1.2M — environmental breach, tailings pond overflow. ZEMA File CHG-2026-011.',                     ts:'2026-02-10T07:45:00Z' },
    { h:7,  action:'INVESTMENT_LOGGED',   actor:'Min. Finance',            payload:'Barrick Gold Super Pit Expansion: $380M deployed, on track. ZCCM-IH equity participation confirmed.',                   ts:'2026-02-15T09:00:00Z' },
    { h:8,  action:'LICENSE_UPGRADE',     actor:'MRC (MRCA 2024)',         payload:'FQM Kansanshi S3 expansion environmental clearance — ZEMA EIS approved. MRC Amendment MRC/EA/2026/004.',              ts:'2026-02-20T15:30:00Z' },
    { h:9,  action:'TARIFF_APPROVED',     actor:'ERB',                     payload:'Emergency ZESCO tariff adjustment approved Oct 2024. Net-metering guidelines effective Jan 2025.',                      ts:'2026-03-01T08:10:00Z' },
    { h:10, action:'COBALT_MILESTONE',    actor:'CNMC / MRC',              payload:'Africa\'s first cobalt sulfate refinery commissioned — Chambishi. Cobalt price +130% YoY. Strategic asset recorded.',  ts:'2026-03-05T09:00:00Z' },
    { h:11, action:'ROYALTY_REFORM',       actor:'ZRA / Govt',              payload:'Mineral royalty revenue confirmed: $70M achieved (prev $15M). Transparency reforms +367% growth.',                      ts:'2026-03-10T10:00:00Z' },
    { h:12, action:'SOLAR_COMMISSIONED',  actor:'ERB / Sunshare',          payload:'Mumbwa Sunshare Phase 1 (122 MW) commissioning approved. June 2026 generation start.',                                 ts:'2026-03-12T14:00:00Z' },
  ],

  // ── PRIVACY TIERS ─────────────────────────────────────────────
  privacyTiers: {
    company: {
      shared:  ['License status', 'Royalty amount paid', 'Production volume (aggregated)', 'Grid energy drawn (kWh)', 'ZEMA compliance status', 'Safety incidents (count only)'],
      private: ['Mine-level operational data', 'Ore grade & reserve estimates', 'Internal processing methods', 'Equipment specifications', 'Cost structure & margins', 'Employee personal data', 'Client contracts', 'Geological survey raw data'],
      label: 'What Energy/Mining Companies Share vs. Protect'
    }
  },

  // ── PLATFORM TIERS (Business Model) ───────────────────────────
  tiers: [
    {
      name: 'Government Core',
      price: 'Mandate-Based',
      color: 'var(--primary)',
      icon: 'fa-landmark',
      audience: 'MRC, ERB, ZEMA, ZRA, ZCCM-IH',
      features: [
        '✅ National compliance dashboard',
        '✅ Real-time royalty tracking',
        '✅ License registry (MRCA 2024)',
        '✅ Blockchain audit trail',
        '✅ ZEMA environmental monitoring',
        '✅ Resource map (national)',
        '✅ Policy simulation tools',
        '✅ Parliamentary reporting',
      ],
      cta: 'Sovereign Deployment'
    },
    {
      name: 'Finance & Risk',
      price: '$180K/yr',
      color: 'var(--warning)',
      icon: 'fa-bank',
      audience: 'Zanaco, Stanbic, AfDB, IFC, Pension Funds',
      features: [
        '✅ Compliance-linked credit scoring',
        '✅ Mine production dashboards',
        '✅ Royalty payment verification',
        '✅ Environmental risk flags',
        '✅ Cross-border SAPP data',
        '✅ Portfolio risk analytics',
        '✅ Regulatory change alerts',
        '⚙️ Custom risk model API',
      ],
      cta: 'Get Finance License'
    },
    {
      name: 'Industry Professional',
      price: '$95K/yr',
      color: 'var(--success)',
      icon: 'fa-gem',
      audience: 'FQM, Barrick, Vedanta, Mopani, CNMC, Jubilee',
      features: [
        '✅ Internal operational dashboard',
        '✅ MRCA filing automation',
        '✅ ZEMA EIS submission portal',
        '✅ ERB license renewal tracking',
        '✅ Energy cost optimizer',
        '✅ Supplier compliance tracker',
        '✅ Blockchain receipt generation',
        '🔒 Data never shared externally',
      ],
      cta: 'Start Industry Trial'
    },
  ],
};
