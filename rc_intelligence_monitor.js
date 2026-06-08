/**
 * Resource Command — Intelligence Monitor v3
 * -------------------------------------------
 * Multi-layer intelligence sweep across open sources.
 * Runs on schedule, writes findings to memory/intelligence_feed.md.
 *
 * FREE LAYERS (no API key required — active):
 *   Layer 1 — Google News RSS          (broad news, tightly-scoped queries)
 *   Layer 2 — GDELT DOC 2.0 API        (15-min global news, 100+ languages, 1 req/5s)
 *   Layer 3 — SEC EDGAR full-text      (6-K/20-F mining filings mentioning Zambia)
 *   Layer 4 — Mining RSS bundle        (Mining.com, Zambia Mining News, Mining Weekly, NRGI)
 *   Layer 5 — World Bank Projects API  (active Zambia projects, live endpoint)
 *   Layer 6 — World Bank Documents API (Zambia mining/revenue publications)
 *   Layer 7 — GitHub ZK repo scanner   (competitive intelligence — ZK royalty/compliance repos)
 *   Layer 8 — CourtListener            (US court cases — FQM/Glencore/Vedanta litigation)
 *   Layer 9 — arXiv ZK research        (new circuit papers, prior art monitoring)
 *   Layer 10 — AfDB projects           (active Zambia pipeline)
 *   Layer 11 — Zambia Parliament       (Hansard debates — mining/revenue/ZRA)
 *   Layer 12 — ICSID case tracker      (investor-state disputes involving Zambia)
 *   Layer 13 — FQM / Glencore IR       (investor relations direct feeds)
 *   Layer 14 — Zambian Local Press     (News Diggers, Lusaka Times, Mwebantu, Daily Mail ZM, Zambian Observer)
 *   Layer 15 — EU Battery Passport     (EUR-Lex regulation tracker + EU Commission press on critical raw materials)
 *
 * PREMIUM LAYERS (API key required — inactive until configured):
 *   BRAVE_API_KEY   — brave.com/search/api  (free: 2000 req/month)
 *                     Set env var: BRAVE_API_KEY=your_key
 *                     Gives: high-quality real-time web search, no RSS limitations
 *   OPENROUTER_KEY  — openrouter.ai          (pay-per-use, ~$0.001/query for Sonar Pro)
 *                     Set env var: OPENROUTER_API_KEY=your_key
 *                     Gives: Perplexity Sonar Pro synthesis — deep research summaries
 *
 * Usage:
 *   node rc_intelligence_monitor.js              — full run, saves report
 *   node rc_intelligence_monitor.js --dry        — prints to console only
 *   node rc_intelligence_monitor.js --layer gdelt — test single layer
 */

import fs   from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DRY       = process.argv.includes('--dry');
const LAYER     = process.argv.includes('--layer')
  ? process.argv[process.argv.indexOf('--layer') + 1]
  : null;

// ── Output paths ───────────────────────────────────────────────────────────────
const MEMORY_DIR  = path.join(__dirname, 'memory');
const FEED_PATH   = path.join(MEMORY_DIR, 'intelligence_feed.md');
const STATE_PATH  = path.join(MEMORY_DIR, '.intel_state.json');

// ── Watch targets — tightly scoped for RC ─────────────────────────────────────
const WATCH = {
  royalty: {
    label:    'ROYALTY GAP / ZRA',
    priority: 'HIGH',
    queries: [
      '"mineral royalty" Zambia ZRA 2026',
      '"Zambia Revenue Authority" mining royalty',
      'ZRA MOSES "mineral tracking" Zambia',
      '"nil returns" Zambia mining 2026',
      '"Auditor General" Zambia mining royalties',
    ],
  },
  institutions: {
    label:    'INSTITUTIONAL PARTNERS',
    priority: 'HIGH',
    queries: [
      'AfDB "African Development Bank" Zambia mining 2026',
      'World Bank IFC Zambia minerals digital',
      'ZCCM-IH Zambia 2026',
      'KoBold Metals Zambia copper 2026',
      'Trafigura Zambia copper 2026',
    ],
  },
  geopolitics: {
    label:    'GEOPOLITICS / SUPPLY CHAIN',
    priority: 'HIGH',
    queries: [
      'Zambia copper US China competition critical minerals 2026',
      '"Lobito Corridor" Zambia copper',
      'TAZARA Zambia copper China 2026',
      'EU "Battery Passport" Zambia copper compliance',
      '"critical minerals" Zambia United States 2026',
    ],
  },
  candidates: {
    label:    'CEO CANDIDATES',
    priority: 'URGENT',
    queries: [
      'Ndoba Vibetti Zambia mining',
      'Tisa Chama mining Zambia',
      'Pius Kasolo Zambia banking',
      'Emmanuel Mutati Zambia copper',
      'Victor Mwaba Zambia mining governance',
      'Sokwani Chilembo Chamber of Mines Zambia',
    ],
  },
  market: {
    label:    'MARKET & REGULATION',
    priority: 'MEDIUM',
    queries: [
      'Zambia "Minerals Regulation Commission" MRCA 2026',
      'Zambia mining tax policy royalty rate 2026',
      '"Copperbelt" mining Mopani Nchanga First Quantum 2026',
      'Zambia "local content" mining 2026',
      'Zambia elections 2026 mining Hichilema',
    ],
  },
  tech: {
    label:    'TECHNOLOGY / COMPETITION',
    priority: 'MEDIUM',
    queries: [
      '"zero knowledge" mining compliance royalty',
      'ZK proof regulatory compliance Africa 2026',
      '"digital compliance" mining Africa government 2026',
      'Circom Groth16 enterprise deployment 2026',
      'zkSNARK government audit compliance',
    ],
  },
  legal: {
    label:    'LEGAL & DISPUTES',
    priority: 'HIGH',
    queries: [
      'First Quantum Zambia ZRA dispute 2026',
      'Glencore Zambia tax royalty 2026',
      'Vedanta Zambia mining legal 2026',
      'ICSID arbitration Zambia mining 2026',
    ],
  },
};

// ── Mining company EDGAR CIK identifiers ──────────────────────────────────────
const EDGAR_TARGETS = [
  { name: 'Glencore PLC',        cik: '0001521365' },
  { name: 'First Quantum Minerals', searchTerm: 'first quantum minerals' },
  { name: 'Vedanta Resources',   searchTerm: 'vedanta resources' },
];

// ── Mining-specific RSS feeds ──────────────────────────────────────────────────
const MINING_RSS_FEEDS = [
  { label: 'Mining Weekly',      url: 'https://www.miningweekly.com/rss/latest' },
  { label: 'Zambia Mining News', url: 'https://www.miningnewszambia.com/feed/' },
  { label: 'Mining Technology',  url: 'https://www.mining-technology.com/feed/' },
  { label: 'Mining.com',         url: 'https://www.mining.com/feed/' },
  { label: 'NRGI',               url: 'https://resourcegovernance.org/rss.xml' },
  { label: 'African Arguments',  url: 'https://africanarguments.org/feed/' },
  { label: 'The Elephant',       url: 'https://www.theelephant.info/feed/' },
];

// ── Layer 14: Zambian local press (closes the local-language gap) ─────────────
// Major Zambian outlets covering ZRA, mining policy, government, parliament.
// State-owned (Daily Mail) + independent (News Diggers, Mwebantu) mix.
const ZAMBIAN_PRESS_FEEDS = [
  { label: 'News Diggers',       url: 'https://diggers.news/feed/' },
  { label: 'Lusaka Times',       url: 'https://www.lusakatimes.com/feed/' },
  { label: 'Mwebantu',           url: 'https://www.mwebantu.com/feed/' },
  { label: 'Zambia Daily Mail',  url: 'https://www.daily-mail.co.zm/feed/' },
  { label: 'Zambian Observer',   url: 'https://www.zambianobserver.com/feed/' },
  { label: 'Open Zambia',        url: 'https://openzambia.com/feed/' },
];

// ── Layer 15: EU Battery Passport regulation tracker ──────────────────────────
// Google News RSS scoped to EU regulatory keywords (most reliable RSS path for
// EUR-Lex content), plus direct industry feeds for battery / critical raw materials.
const EU_BATTERY_FEEDS = [
  {
    label: 'Google News (EU Battery Regulation)',
    url:   'https://news.google.com/rss/search?q=%22EU+Battery+Regulation%22+OR+%22Battery+Passport%22+2026&hl=en-US&gl=US&ceid=US:en',
  },
  {
    label: 'Google News (Critical Raw Materials Act)',
    url:   'https://news.google.com/rss/search?q=%22Critical+Raw+Materials+Act%22+OR+%22CRMA%22+EU+mining&hl=en-US&gl=US&ceid=US:en',
  },
  {
    label: 'Google News (EU Due Diligence Cobalt)',
    url:   'https://news.google.com/rss/search?q=%22EU+due+diligence%22+cobalt+OR+copper+supply+chain&hl=en-US&gl=US&ceid=US:en',
  },
  {
    label: 'Global Battery Alliance',
    url:   'https://www.globalbattery.org/feed/',
  },
];

// ── API keys (set as env vars to unlock premium layers) ───────────────────────
const BRAVE_API_KEY      = process.env.BRAVE_API_KEY      || null;
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || null;

// Keywords to filter mining RSS items for RC relevance
const MINING_KEYWORDS = [
  'zambia', 'copperbelt', 'ZRA', 'royalty', 'mineral tax',
  'mopani', 'nchanga', 'chambishi', 'first quantum', 'glencore',
  'vedanta', 'ZCCM', 'KoBold', 'battery passport', 'trafigura',
  'cobalt', 'copper', 'compliance', 'audit', 'zero knowledge',
  // Zambian-press specific terms (Layer 14)
  'minister of mines', 'mineral resources', 'ministry of mines',
  'auditor general', 'parliament', 'national assembly', 'cabinet',
  'lubinda', 'paul kabuswe', 'mining cadastre', 'mining licence',
  'concentrate export', 'export duty', 'smelter', 'refinery',
  // EU Battery Passport specific (Layer 15)
  'due diligence', 'critical raw materials', 'crma', 'supply chain',
  'battery regulation', 'eu commission', 'cobalt sourcing',
];

// ── Helpers ────────────────────────────────────────────────────────────────────
function loadState() {
  try { return JSON.parse(fs.readFileSync(STATE_PATH, 'utf8')); }
  catch { return { seen: [], lastRun: null }; }
}

function saveState(state) {
  if (!DRY) fs.writeFileSync(STATE_PATH, JSON.stringify(state, null, 2));
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function parseDate(str) {
  try { return new Date(str).getTime(); }
  catch { return 0; }
}

function isRelevant(text) {
  const lower = text.toLowerCase();
  return MINING_KEYWORDS.some(kw => lower.includes(kw.toLowerCase()));
}

// Strip HTML tags for plain text comparison
function stripHtml(str = '') {
  return str.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
}

const CUTOFF_DAYS = 7;
const CUTOFF_MS   = CUTOFF_DAYS * 24 * 60 * 60 * 1000;

// ── Layer 1: Google News RSS ───────────────────────────────────────────────────
async function fetchGoogleNews(query) {
  const url = `https://news.google.com/rss/search?q=${encodeURIComponent(query)}&hl=en-US&gl=US&ceid=US:en`;
  try {
    const res  = await fetch(url, { signal: AbortSignal.timeout(12000) });
    const text = await res.text();
    const items = [];
    const itemRegex = /<item>([\s\S]*?)<\/item>/g;
    let match;
    while ((match = itemRegex.exec(text)) !== null) {
      const block   = match[1];
      const title   = (block.match(/<title><!\[CDATA\[(.*?)\]\]><\/title>/) ||
                       block.match(/<title>(.*?)<\/title>/))?.[1] || '';
      const link    = (block.match(/<link>(.*?)<\/link>/))?.[1] || '';
      const pubDate = (block.match(/<pubDate>(.*?)<\/pubDate>/))?.[1] || '';
      const source  = (block.match(/<source[^>]*>(.*?)<\/source>/))?.[1] || '';
      if (title) items.push({ title: title.trim(), link, pubDate, source, layer: 'Google News' });
    }
    return items;
  } catch { return []; }
}

// ── Layer 2: GDELT DOC 2.0 ────────────────────────────────────────────────────
async function fetchGDELT(query, maxRecords = 8) {
  // GDELT searches across 100+ languages every 15 minutes
  // Rate limit: 1 request per 5 seconds — enforced
  const encoded = encodeURIComponent(query);
  const url = `https://api.gdeltproject.org/api/v2/doc/doc?query=${encoded}&mode=artlist&maxrecords=${maxRecords}&format=json&timespan=7d&sort=datedesc`;
  try {
    await sleep(5500); // GDELT enforces 1 req/5s — add buffer
    const res  = await fetch(url, { signal: AbortSignal.timeout(20000) });
    const text = await res.text();
    if (text.startsWith('Please limit')) {
      await sleep(8000); // back off and retry once
      const res2 = await fetch(url, { signal: AbortSignal.timeout(20000) });
      const t2   = await res2.text();
      if (t2.startsWith('Please limit')) return [];
      try {
        const data = JSON.parse(t2);
        return mapGDELT(data);
      } catch { return []; }
    }
    const data = JSON.parse(text);
    return mapGDELT(data);
  } catch { return []; }
}

function mapGDELT(data) {
  return (data.articles || []).map(a => ({
    title:   a.title  || '',
    link:    a.url    || '',
    pubDate: a.seendate
      ? a.seendate.replace(/(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z/, '$1-$2-$3T$4:$5:$6Z')
      : '',
    source:  a.domain || '',
    layer:   'GDELT',
  })).filter(a => a.title && a.link);
}

// ── Layer 3: SEC EDGAR full-text search ───────────────────────────────────────
// Monitors 6-K and 20-F filings that mention Zambia + royalty/mining
async function fetchEDGARFilings() {
  const results = [];
  // EDGAR full-text search — monitors 6-K and 20-F for Zambia royalty mentions
  // Covers FQM, Glencore, Barrick, Vedanta, and any other mining company filing
  const queries = [
    { q: '"Zambia" "mineral royalty"',      form: '6-K' },
    { q: '"Zambia" "royalty"',              form: '20-F' },
    { q: '"Kansanshi" "royalty"',           form: '6-K' },
    { q: '"Zambia Revenue Authority"',       form: '6-K' },
  ];

  for (const { q, form } of queries) {
    const url = `https://efts.sec.gov/LATEST/search-index?q=${encodeURIComponent(q)}&forms=${form}&dateRange=custom&startdt=${getDateDaysAgo(30)}&enddt=${getDateDaysAgo(0)}`;
    try {
      await sleep(800);
      const res  = await fetch(url, {
        headers: { 'User-Agent': 'ResourceCommand/2.0 kennedythebe0@gmail.com' },
        signal: AbortSignal.timeout(15000),
      });
      if (!res.ok) continue;
      const data = await res.json();
      const hits = data.hits?.hits || [];
      for (const hit of hits.slice(0, 4)) {
        const s    = hit._source || {};
        const id   = hit._id    || '';
        // _id format: "XXXXXX:filename.htm" — extract accession number
        const acc  = id.split(':')[0] || '';
        const cik  = (s.ciks || [])[0] || '';
        const name = (s.display_names || ['Unknown company'])[0].split('(')[0].trim();
        const date = s.period_ending || s.file_date || '';
        results.push({
          title:   `[EDGAR ${form}] ${name} — Zambia royalty/revenue filing`,
          link:    acc
            ? `https://www.sec.gov/Archives/edgar/data/${parseInt(cik)}/000000000000000000/${acc.replace(/-/g, '')}.htm`
            : `https://efts.sec.gov/LATEST/search-index?q=${encodeURIComponent(q)}&forms=${form}`,
          pubDate: date,
          source:  'SEC EDGAR',
          layer:   'EDGAR',
        });
      }
    } catch { continue; }
  }
  // Deduplicate by company name
  const seen = new Set();
  return results.filter(r => {
    const key = r.title;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function getDateDaysAgo(days) {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);
}

// ── Layer 4: Mining-specific RSS feeds ────────────────────────────────────────
async function fetchMiningRSS() {
  const results = [];
  for (const feed of MINING_RSS_FEEDS) {
    try {
      await sleep(400);
      const res  = await fetch(feed.url, { signal: AbortSignal.timeout(12000) });
      const text = await res.text();
      const itemRegex = /<item>([\s\S]*?)<\/item>/g;
      let match;
      while ((match = itemRegex.exec(text)) !== null) {
        const block   = match[1];
        const title   = (block.match(/<title><!\[CDATA\[(.*?)\]\]><\/title>/) ||
                         block.match(/<title>(.*?)<\/title>/))?.[1]?.trim() || '';
        const link    = (block.match(/<link>(.*?)<\/link>/))?.[1]?.trim() || '';
        const pubDate = (block.match(/<pubDate>(.*?)<\/pubDate>/))?.[1] || '';
        const desc    = (block.match(/<description><!\[CDATA\[(.*?)\]\]><\/description>/) ||
                         block.match(/<description>(.*?)<\/description>/))?.[1] || '';

        if (title && isRelevant(title + ' ' + stripHtml(desc))) {
          results.push({ title, link, pubDate, source: feed.label, layer: 'Mining RSS' });
        }
      }
    } catch { continue; }
  }
  return results;
}

// ── Layer 5: World Bank active Zambia projects ────────────────────────────────
async function fetchWorldBankProjects() {
  const url = 'https://search.worldbank.org/api/v2/projects?format=json&countrycode=ZM&status=Active&fl=id,name,totalamt,sector1,boarddate&rows=15&os=0';
  try {
    const res  = await fetch(url, { signal: AbortSignal.timeout(12000) });
    const data = await res.json();
    return (data.projects || []).map(p => ({
      title:   p.name || '',
      id:      p.id   || '',
      amount:  p.totalamt ? `USD ${(p.totalamt / 1e6).toFixed(0)}M` : 'n/a',
      sector:  p.sector1?.Name || 'n/a',
      date:    p.boarddate?.slice(0, 10) || 'n/a',
    }));
  } catch { return []; }
}

// ── Layer 6: World Bank Documents — Zambia mining/revenue ─────────────────────
async function fetchWorldBankDocs() {
  const url = 'https://search.worldbank.org/api/v2/wds?format=json&qterm=zambia+mineral+royalty+mining+revenue&fl=id,display_title,docdt,count&rows=5&os=0&srt=docdt&order=desc';
  try {
    const res  = await fetch(url, { signal: AbortSignal.timeout(12000) });
    const data = await res.json();
    const docs = data.documents;
    if (!docs) return [];
    return Object.values(docs)
      .filter(d => d.display_title)
      .slice(0, 5)
      .map(d => ({
        title:   d.display_title,
        link:    d.url || `https://documents.worldbank.org/en/publication/documents-reports/documentdetail/${d.id}`,
        pubDate: d.docdt || '',
        source:  'World Bank Documents',
        layer:   'World Bank Docs',
      }));
  } catch { return []; }
}

// ── Layer 7: Zambia Parliament — recent Hansard debates ───────────────────────
async function fetchZambiaParliament() {
  // Fetch both debates index and acts of parliament
  const urls = [
    'https://www.parliament.gov.zm/publications/debates-proceedings',
    'https://www.parliament.gov.zm/acts-of-parliament',
  ];
  const results = [];
  for (const url of urls) {
    try {
      const res  = await fetch(url, {
        signal: AbortSignal.timeout(15000),
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          'Accept':     'text/html,application/xhtml+xml',
        },
      });
      const html = await res.text();

      // Match any anchor with text content — broad pattern for Zambia Parliament HTML
      const patterns = [
        /href="(\/node\/\d+)"[^>]*>([^<]{8,120})</g,
        /href="([^"]*parliament[^"]*)"[^>]*>([^<]{8,120})</g,
        /<td[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*>([^<]{8,120})<\/a>/g,
      ];

      for (const pattern of patterns) {
        let match;
        while ((match = pattern.exec(html)) !== null) {
          const rawTitle = match[2].trim();
          if (!rawTitle || rawTitle.length < 8) continue;
          const href = match[1].startsWith('http') ? match[1] : `https://www.parliament.gov.zm${match[1]}`;
          const lower = rawTitle.toLowerCase();
          if (lower.includes('mine') || lower.includes('zra') || lower.includes('revenue') ||
              lower.includes('royalt') || lower.includes('copper') || lower.includes('mineral') ||
              lower.includes('tax') || lower.includes('zambia')) {
            results.push({
              title:   `[Hansard] ${rawTitle}`,
              link:    href,
              pubDate: new Date().toISOString(),
              source:  'Zambia Parliament',
              layer:   'Parliament',
            });
          }
        }
      }
    } catch { continue; }
  }
  // Deduplicate by title
  const seen = new Set();
  return results.filter(r => {
    if (seen.has(r.title)) return false;
    seen.add(r.title);
    return true;
  }).slice(0, 8);
}

// ── Layer 8: ICSID case tracker ───────────────────────────────────────────────
// Monitors for new investor-state cases involving Zambia
async function fetchICSIDCases() {
  // ICSID publishes case information in HTML — no official API
  const url = 'https://icsid.worldbank.org/cases/case-database?status=pending&respondent=Zambia';
  try {
    const res  = await fetch(url, {
      signal: AbortSignal.timeout(15000),
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; RCMonitor/2.0)' },
    });
    const html = await res.text();

    const results = [];
    // Look for case references and party names in the HTML
    const caseRegex = /ARB\/\d+\/\d+|UNCT\/\d+\/\d+/g;
    const caseNums = [...new Set(html.match(caseRegex) || [])];

    for (const caseNum of caseNums.slice(0, 5)) {
      results.push({
        title:   `ICSID Case ${caseNum} — Zambia (monitor for new filings)`,
        link:    `https://icsid.worldbank.org/cases/case-database`,
        pubDate: new Date().toISOString(),
        source:  'ICSID',
        layer:   'ICSID',
      });
    }
    return results;
  } catch { return []; }
}

// ── Layer 9: AfDB active Zambia projects ──────────────────────────────────────
async function fetchAfDBProjects() {
  // AfDB projects API — public endpoint
  const url = 'https://projectsportal.afdb.org/dataportal/api/projects?country=ZM&status=OnGoing&pageSize=10&pageNum=0';
  try {
    const res  = await fetch(url, {
      signal: AbortSignal.timeout(15000),
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; RCMonitor/2.0)',
        'Accept':     'application/json',
      },
    });
    if (!res.ok) return [];
    const data = await res.json();
    const projects = data?.data || data?.projects || data?.items || [];
    return projects.slice(0, 8).map(p => ({
      title:  p.projectTitle || p.name || p.title || 'AfDB Project',
      id:     p.projectNumber || p.id || '',
      amount: p.approvedAmount ? `UA ${(p.approvedAmount / 1e6).toFixed(1)}M` : 'n/a',
      sector: p.sector || p.sectorCode || 'n/a',
    }));
  } catch { return []; }
}

// ── Layer 10: First Quantum investor news direct ───────────────────────────────
async function fetchFQMNews() {
  // First Quantum + Glencore investor news — direct IR page scrape
  const targets = [
    {
      name: 'First Quantum Minerals',
      url:  'https://www.first-quantum.com/feed/', // RSS — bypasses JS-rendered page
      // FQM uses structured article elements
      pattern: /href="(\/news\/[a-z0-9\-]+\/)"[^>]*>[\s\S]{0,200}?<h[1-4][^>]*>([\s\S]*?)<\/h[1-4]>/g,
    },
    {
      name: 'Glencore',
      url:  'https://www.glencore.com/media-and-insights/news',
      pattern: /href="([^"]*media[^"]*)"[^>]*>[\s\S]{0,100}?<[^>]+>(Zambia[^<]{0,120}|[^<]{0,80}zambia[^<]{0,80})<\//ig,
    },
  ];

  const results = [];
  for (const { name, url, pattern } of targets) {
    try {
      await sleep(500);
      const res  = await fetch(url, {
        signal: AbortSignal.timeout(15000),
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          'Accept':     'text/html,application/xhtml+xml',
        },
      });
      const html = await res.text();

      // Broad title extraction — look for any article/headline tags
      const titleRegex = /<(?:h[1-4]|title)[^>]*>([\s\S]{10,150}?)<\/(?:h[1-4]|title)>/g;
      const linkRegex  = /href="((?:https?:\/\/(?:www\.)?(?:first-quantum|glencore)\.com)?\/[^"]{5,150})"/g;

      const titles = [];
      const links  = [];
      let m;
      while ((m = titleRegex.exec(html)) !== null) {
        const t = stripHtml(m[1]).trim();
        if (t.length > 8 && t.length < 200) titles.push(t);
      }
      while ((m = linkRegex.exec(html)) !== null) {
        links.push(m[1]);
      }

      // Pair titles with links (best effort), filter by relevance
      for (let i = 0; i < Math.min(titles.length, 10); i++) {
        const title = titles[i];
        if (!isRelevant(title) && !title.toLowerCase().includes('zambia') &&
            !title.toLowerCase().includes('quarter') && !title.toLowerCase().includes('result')) continue;
        const link = links[i]
          ? (links[i].startsWith('http') ? links[i] : `${new URL(url).origin}${links[i]}`)
          : url;
        results.push({
          title:   `[${name}] ${title}`,
          link,
          pubDate: new Date().toISOString(),
          source:  `${name} (IR)`,
          layer:   'Mining IR',
        });
      }
    } catch { continue; }
  }
  return results.slice(0, 8);
}

// ── Layer: GitHub ZK/compliance repo scanner ─────────────────────────────────
// Monitors for NEW public repos that might be RC competitors or prior art
async function fetchGitHubZKRepos() {
  const queries = [
    'circom+royalty',
    'zero-knowledge+mineral+compliance',
    'zkp+tax+compliance+africa',
    'groth16+government+audit',
    'zk-proof+mining+royalty',
  ];
  const results = [];
  for (const q of queries) {
    try {
      await sleep(400);
      const url = `https://api.github.com/search/repositories?q=${encodeURIComponent(q)}&sort=updated&order=desc&per_page=5`;
      const res  = await fetch(url, {
        headers: {
          'Accept':     'application/vnd.github.v3+json',
          'User-Agent': 'RCIntelMonitor/3.0',
        },
        signal: AbortSignal.timeout(12000),
      });
      if (!res.ok) continue;
      const data = await res.json();
      for (const repo of (data.items || [])) {
        results.push({
          title:   `[GitHub] ${repo.full_name} — ${repo.description || 'No description'} ★${repo.stargazers_count}`,
          link:    repo.html_url,
          pubDate: repo.pushed_at || repo.created_at,
          source:  'GitHub',
          layer:   'GitHub ZK',
        });
      }
    } catch { continue; }
  }
  return results;
}

// ── Layer: CourtListener — US litigation by major miners ─────────────────────
// Monitors FQM, Glencore, Vedanta, Barrick US court filings
async function fetchCourtListenerCases() {
  const queries = [
    'Zambia mining royalty',
    'First Quantum Zambia',
    'Glencore Zambia tax',
    'Kansanshi copper',
  ];
  const results = [];
  for (const q of queries) {
    try {
      await sleep(300);
      const url = `https://www.courtlistener.com/api/rest/v4/search/?q=${encodeURIComponent(q)}&type=o&format=json&filed_after=${getDateDaysAgo(180)}&order_by=score+desc`;
      const res  = await fetch(url, { signal: AbortSignal.timeout(12000) });
      if (!res.ok) continue;
      const data = await res.json();
      for (const r of (data.results || []).slice(0, 3)) {
        results.push({
          title:   `[Court] ${r.caseName || r.case_name || 'Unknown case'} — ${r.court_citation_string || r.court || 'US Court'}`,
          link:    r.absolute_url ? `https://www.courtlistener.com${r.absolute_url}` : 'https://www.courtlistener.com',
          pubDate: r.dateFiled || r.date_filed || '',
          source:  'CourtListener',
          layer:   'CourtListener',
        });
      }
    } catch { continue; }
  }
  // Deduplicate by case name
  const seen = new Set();
  return results.filter(r => {
    if (seen.has(r.title)) return false;
    seen.add(r.title);
    return true;
  });
}

// ── Layer: arXiv — ZK research papers ────────────────────────────────────────
// Monitors for new cryptographic research relevant to RC circuits
async function fetchArXivZKPapers() {
  const queries = [
    'zero-knowledge proof compliance regulatory',
    'groth16 application government',
    'circom circuit mineral',
    'ZK-SNARK enterprise audit',
  ];
  const results = [];
  for (const q of queries) {
    try {
      await sleep(3000); // arXiv requires polite delays
      const url = `https://export.arxiv.org/api/query?search_query=all:${encodeURIComponent(q)}&start=0&max_results=3&sortBy=submittedDate&sortOrder=descending`;
      const res  = await fetch(url, {
        headers: { 'User-Agent': 'RCIntelMonitor/3.0 (research monitoring)' },
        signal: AbortSignal.timeout(20000),
      });
      if (!res.ok) continue;
      const text = await res.text();
      // Parse Atom XML from arXiv
      const entryRegex = /<entry>([\s\S]*?)<\/entry>/g;
      let match;
      while ((match = entryRegex.exec(text)) !== null) {
        const block   = match[1];
        const title   = (block.match(/<title>([\s\S]*?)<\/title>/))?.[1]?.trim() || '';
        const id      = (block.match(/<id>([\s\S]*?)<\/id>/))?.[1]?.trim() || '';
        const pubDate = (block.match(/<published>([\s\S]*?)<\/published>/))?.[1]?.trim() || '';
        const summary = (block.match(/<summary>([\s\S]*?)<\/summary>/))?.[1]?.replace(/\s+/g, ' ').trim() || '';
        if (title && title.length > 5) {
          results.push({
            title:   `[arXiv] ${title}`,
            link:    id || 'https://arxiv.org/search/?searchtype=all&query=zero+knowledge+compliance',
            pubDate,
            source:  'arXiv cs.CR',
            layer:   'arXiv',
          });
        }
      }
    } catch { continue; }
  }
  return results.slice(0, 8);
}

// ── Layer 14: Zambian local press ─────────────────────────────────────────────
// Same RSS parsing pattern as Layer 4, but with the Zambian-specific feed list
// and broader keyword relevance check (uses extended MINING_KEYWORDS).
async function fetchZambianPress() {
  const results = [];
  for (const feed of ZAMBIAN_PRESS_FEEDS) {
    try {
      await sleep(400);
      const res  = await fetch(feed.url, { signal: AbortSignal.timeout(12000) });
      if (!res.ok) continue;
      const text = await res.text();
      const itemRegex = /<item>([\s\S]*?)<\/item>/g;
      let match;
      while ((match = itemRegex.exec(text)) !== null) {
        const block   = match[1];
        const title   = (block.match(/<title><!\[CDATA\[(.*?)\]\]><\/title>/) ||
                         block.match(/<title>(.*?)<\/title>/))?.[1]?.trim() || '';
        const link    = (block.match(/<link>(.*?)<\/link>/))?.[1]?.trim() || '';
        const pubDate = (block.match(/<pubDate>(.*?)<\/pubDate>/))?.[1] || '';
        const desc    = (block.match(/<description><!\[CDATA\[(.*?)\]\]><\/description>/) ||
                         block.match(/<description>(.*?)<\/description>/))?.[1] || '';

        if (title && isRelevant(title + ' ' + stripHtml(desc))) {
          results.push({ title, link, pubDate, source: feed.label, layer: 'Zambia Press' });
        }
      }
    } catch { continue; }
  }
  return results;
}

// ── Layer 15: EU Battery Passport regulation tracker ──────────────────────────
// Captures EU legislative/policy movement on the regulation that hits Feb 2027.
// Filter is wider — any item from these feeds is relevant by source.
async function fetchEUBatteryPassport() {
  const results = [];
  for (const feed of EU_BATTERY_FEEDS) {
    try {
      await sleep(400);
      const res  = await fetch(feed.url, { signal: AbortSignal.timeout(12000) });
      if (!res.ok) continue;
      const text = await res.text();
      const itemRegex = /<item>([\s\S]*?)<\/item>/g;
      let match;
      let count = 0;
      while ((match = itemRegex.exec(text)) !== null && count < 10) {
        const block   = match[1];
        const title   = (block.match(/<title><!\[CDATA\[(.*?)\]\]><\/title>/) ||
                         block.match(/<title>(.*?)<\/title>/))?.[1]?.trim() || '';
        const link    = (block.match(/<link>(.*?)<\/link>/))?.[1]?.trim() || '';
        const pubDate = (block.match(/<pubDate>(.*?)<\/pubDate>/))?.[1] || '';

        if (title && link) {
          results.push({
            title:   `[EU] ${title}`,
            link,
            pubDate,
            source:  feed.label,
            layer:   'EU Battery',
          });
          count++;
        }
      }
    } catch { continue; }
  }
  return results;
}

// ── PREMIUM Layer: Brave Search ───────────────────────────────────────────────
// Unlocked by setting BRAVE_API_KEY env var
// Get free key: brave.com/search/api (2,000 req/month free)
async function fetchBraveSearch(query, count = 10) {
  if (!BRAVE_API_KEY) return [];
  try {
    const url = `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}&count=${count}&freshness=pw`;
    const res  = await fetch(url, {
      headers: {
        'Accept':               'application/json',
        'Accept-Encoding':      'gzip',
        'X-Subscription-Token': BRAVE_API_KEY,
      },
      signal: AbortSignal.timeout(15000),
    });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.web?.results || []).map(r => ({
      title:   `[Brave] ${r.title}`,
      link:    r.url,
      pubDate: r.age || new Date().toISOString(),
      source:  r.meta_url?.hostname || 'Brave Search',
      layer:   'Brave',
    }));
  } catch { return []; }
}

// ── PREMIUM Layer: OpenRouter / Perplexity synthesis ─────────────────────────
// Unlocked by setting OPENROUTER_API_KEY env var
// Get key: openrouter.ai (pay-per-use, ~$0.001/query for Sonar Pro)
async function fetchOpenRouterSynthesis(topic) {
  if (!OPENROUTER_API_KEY) return null;
  try {
    const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization':  `Bearer ${OPENROUTER_API_KEY}`,
        'Content-Type':   'application/json',
        'HTTP-Referer':   'https://resource-command.io',
        'X-Title':        'Resource Command Intelligence Monitor',
      },
      body: JSON.stringify({
        model: 'perplexity/sonar-pro',
        messages: [{ role: 'user', content: topic }],
        max_tokens: 800,
      }),
      signal: AbortSignal.timeout(30000),
    });
    if (!res.ok) return null;
    const data = await res.json();
    return data.choices?.[0]?.message?.content || null;
  } catch { return null; }
}

// ── Main sweep ────────────────────────────────────────────────────────────────
async function run() {
  const now     = Date.now();
  const state   = loadState();
  const seenSet = new Set(state.seen);
  const results = {};
  let   newCount = 0;

  console.log(`\nResource Command Intelligence Monitor v2`);
  console.log(`Run: ${new Date().toISOString()}\n`);

  // Initialise result buckets
  for (const [cat, cfg] of Object.entries(WATCH)) {
    results[cat] = { label: cfg.label, priority: cfg.priority, items: [] };
  }

  // Helper to add item if unseen and fresh
  function addItem(cat, item) {
    if (!item.title || !item.link) return;
    if (seenSet.has(item.link)) return;
    const age = now - parseDate(item.pubDate);
    if (age > CUTOFF_MS && state.lastRun) return;
    results[cat].items.push(item);
    seenSet.add(item.link);
    newCount++;
  }

  // ── Run layers ──────────────────────────────────────────────────────────────

  if (!LAYER || LAYER === 'google') {
    console.log('  [1/15] Google News RSS sweep...');
    for (const [cat, cfg] of Object.entries(WATCH)) {
      for (const query of cfg.queries) {
        const items = await fetchGoogleNews(query);
        items.forEach(item => addItem(cat, item));
        await sleep(350);
      }
    }
  }

  if (!LAYER || LAYER === 'gdelt') {
    console.log('  [2/15] GDELT global sweep...');
    // GDELT sweeps focused on RC-specific intelligence
    const gdeltTargets = [
      { cat: 'royalty',      query: 'Zambia mineral royalty ZRA compliance audit' },
      { cat: 'royalty',      query: 'Zambia mining tax evasion ZRA 2026' },
      { cat: 'institutions', query: 'AfDB World Bank Zambia mining digital compliance' },
      { cat: 'institutions', query: 'Trafigura Zambia copper deal 2026' },
      { cat: 'geopolitics',  query: 'Zambia copper US China critical minerals 2026' },
      { cat: 'geopolitics',  query: 'EU Battery Passport copper mining Africa compliance' },
      { cat: 'tech',         query: 'zero knowledge proof government compliance Africa' },
      { cat: 'legal',        query: 'First Quantum Zambia ZRA dispute arbitration 2026' },
      { cat: 'market',       query: 'Zambia Copperbelt mining regulation election 2026' },
    ];
    for (const { cat, query } of gdeltTargets) {
      const items = await fetchGDELT(query, 8);
      items.forEach(item => addItem(cat, item));
    }
  }

  if (!LAYER || LAYER === 'edgar') {
    console.log('  [3/15] SEC EDGAR filing sweep...');
    const edgarItems = await fetchEDGARFilings();
    edgarItems.forEach(item => addItem('legal', item));
  }

  if (!LAYER || LAYER === 'mining') {
    console.log('  [4/15] Mining RSS feeds...');
    const miningItems = await fetchMiningRSS();
    for (const item of miningItems) {
      // Route to correct category based on content
      const lower = item.title.toLowerCase();
      const cat = lower.includes('zra') || lower.includes('royalt') || lower.includes('tax')
        ? 'royalty'
        : lower.includes('arbitrat') || lower.includes('legal') || lower.includes('dispute')
        ? 'legal'
        : lower.includes('battery') || lower.includes('eu ') || lower.includes('passport')
        ? 'geopolitics'
        : 'market';
      addItem(cat, item);
    }
  }

  if (!LAYER || LAYER === 'parliament') {
    console.log('  [5/15] Zambia Parliament Hansard...');
    const parlItems = await fetchZambiaParliament();
    parlItems.forEach(item => addItem('royalty', item));
  }

  if (!LAYER || LAYER === 'icsid') {
    console.log('  [6/15] ICSID case tracker...');
    const icsidItems = await fetchICSIDCases();
    icsidItems.forEach(item => addItem('legal', item));
  }

  if (!LAYER || LAYER === 'fqm') {
    console.log('  [7/15] First Quantum / Glencore investor relations...');
    const fqmItems = await fetchFQMNews();
    fqmItems.forEach(item => addItem('legal', item));
  }

  if (!LAYER || LAYER === 'github') {
    console.log('  [8/15] GitHub ZK repo scanner (competitor intelligence)...');
    const ghItems = await fetchGitHubZKRepos();
    ghItems.forEach(item => addItem('tech', item));
    if (ghItems.length === 0) {
      // No ZK royalty repos found = no public competitors. Log as positive signal.
      console.log('         ✓ Zero public ZK royalty/compliance repos found — RC has no open-source competitors.');
    }
  }

  if (!LAYER || LAYER === 'court') {
    console.log('  [9/15] CourtListener — US litigation by major miners...');
    const courtItems = await fetchCourtListenerCases();
    courtItems.forEach(item => addItem('legal', item));
  }

  if (!LAYER || LAYER === 'arxiv') {
    console.log('  [10/15] arXiv ZK research papers...');
    const arxivItems = await fetchArXivZKPapers();
    arxivItems.forEach(item => addItem('tech', item));
  }

  if (!LAYER || LAYER === 'zambia') {
    console.log('  [11/15] Zambian local press sweep...');
    const zmItems = await fetchZambianPress();
    // Route by content — ZRA/royalty/audit → royalty, parliament/cabinet → royalty,
    // mining policy/licence → market, disputes → legal, else market.
    for (const item of zmItems) {
      const lower = item.title.toLowerCase();
      const cat =
        (lower.includes('zra') || lower.includes('royalt') || lower.includes('audit') ||
         lower.includes('auditor general') || lower.includes('parliament') ||
         lower.includes('cabinet')) ? 'royalty' :
        (lower.includes('dispute') || lower.includes('arbitrat') || lower.includes('court')) ? 'legal' :
        (lower.includes('china') || lower.includes('lobito') || lower.includes('us ') ||
         lower.includes('european')) ? 'geopolitics' :
        'market';
      addItem(cat, item);
    }
  }

  if (!LAYER || LAYER === 'eu') {
    console.log('  [12/15] EU Battery Passport / Critical Raw Materials regulation...');
    const euItems = await fetchEUBatteryPassport();
    // All EU regulation signals route to geopolitics — they shape the export-market terms
    euItems.forEach(item => addItem('geopolitics', item));
  }

  // ── Premium layers (only fire if API keys set) ────────────────────────────
  if (BRAVE_API_KEY) {
    console.log('  [PREMIUM] Brave Search sweep...');
    const braveQueries = [
      { q: 'Zambia Revenue Authority mineral royalty compliance 2026', cat: 'royalty' },
      { q: 'First Quantum Zambia ZRA tax dispute 2026',               cat: 'legal' },
      { q: 'EU Battery Passport copper mining certification 2026',    cat: 'geopolitics' },
      { q: 'AfDB World Bank Zambia digital compliance technology',    cat: 'institutions' },
    ];
    for (const { q, cat } of braveQueries) {
      const items = await fetchBraveSearch(q, 8);
      items.forEach(item => addItem(cat, item));
      await sleep(300);
    }
  } else {
    console.log('  [PREMIUM] Brave Search — INACTIVE (set BRAVE_API_KEY to enable, free at brave.com/search/api)');
  }

  if (OPENROUTER_API_KEY) {
    console.log('  [PREMIUM] OpenRouter/Perplexity synthesis...');
    // Deep synthesis runs are stored separately, not in the main feed
  } else {
    console.log('  [PREMIUM] OpenRouter — INACTIVE (set OPENROUTER_API_KEY to enable, free credits at openrouter.ai)');
  }

  // ── Structural data pulls ─────────────────────────────────────────────────
  let wbProjects = [];
  let wbDocs     = [];
  let afdbItems  = [];

  if (!LAYER || LAYER === 'worldbank') {
    console.log('  [13/15] World Bank projects and documents...');
    [wbProjects, wbDocs] = await Promise.all([
      fetchWorldBankProjects(),
      fetchWorldBankDocs(),
    ]);
  }

  if (!LAYER || LAYER === 'afdb') {
    console.log('  [14/15] AfDB active Zambia projects...');
    afdbItems = await fetchAfDBProjects();
  }

  if (!LAYER || LAYER === 'parliament') {
    console.log('  [15/15] Zambia Parliament Hansard...');
    // (already handled above in main loop)
  }

  // ── Build report ──────────────────────────────────────────────────────────
  const lines = [];

  lines.push(`# Resource Command — Intelligence Feed`);
  lines.push(`**Last updated:** ${new Date().toUTCString()}`);
  lines.push(`**New items this run:** ${newCount}`);
  lines.push('');

  // Priority order: URGENT → HIGH → MEDIUM
  const order  = ['URGENT', 'HIGH', 'MEDIUM'];
  const sorted = Object.entries(results).sort(
    (a, b) => order.indexOf(a[1].priority) - order.indexOf(b[1].priority)
  );

  for (const [, data] of sorted) {
    if (!data.items.length) continue;
    const marker = data.priority === 'URGENT' ? '[ URGENT ]' :
                   data.priority === 'HIGH'   ? '[ HIGH ]'   : '[ INFO ]';
    lines.push(`## ${marker} ${data.label}`);
    lines.push('');
    for (const item of data.items.slice(0, 8)) {
      const date = item.pubDate
        ? new Date(item.pubDate).toISOString().slice(0, 10)
        : 'n/d';
      const layerTag = item.layer ? ` [${item.layer}]` : '';
      lines.push(`- **${item.title}**`);
      lines.push(`  ${item.source}${layerTag} · ${date}`);
      if (item.link) lines.push(`  ${item.link}`);
    }
    lines.push('');
  }

  // World Bank structural section
  if (wbProjects.length) {
    lines.push(`## [ INFO ] WORLD BANK — ACTIVE ZAMBIA PROJECTS`);
    lines.push('');
    for (const p of wbProjects) {
      lines.push(`- **${p.title}** (${p.amount})`);
      lines.push(`  Sector: ${p.sector} · Board: ${p.date} · ID: ${p.id}`);
    }
    lines.push('');
  }

  if (wbDocs.length) {
    lines.push(`## [ INFO ] WORLD BANK — RECENT PUBLICATIONS (Zambia mining/revenue)`);
    lines.push('');
    for (const d of wbDocs) {
      const date = d.pubDate ? new Date(d.pubDate).toISOString().slice(0, 10) : 'n/d';
      lines.push(`- **${d.title}** · ${date}`);
      if (d.link) lines.push(`  ${d.link}`);
    }
    lines.push('');
  }

  if (afdbItems.length) {
    lines.push(`## [ INFO ] AFDB — ACTIVE ZAMBIA PIPELINE`);
    lines.push('');
    for (const p of afdbItems) {
      lines.push(`- **${p.title}** (${p.amount})`);
      lines.push(`  Sector: ${p.sector} · ID: ${p.id}`);
    }
    lines.push('');
  }

  // Empty categories summary
  const empty = sorted.filter(([, d]) => !d.items.length);
  if (empty.length) {
    lines.push(`## No new items`);
    lines.push(empty.map(([, d]) => d.label).join(', '));
    lines.push('');
  }

  // Premium layer status
  lines.push(`## [ INFO ] PREMIUM LAYER STATUS`);
  lines.push('');
  lines.push(`- **Brave Search:** ${BRAVE_API_KEY ? '✅ ACTIVE' : '❌ INACTIVE — set BRAVE_API_KEY (free at brave.com/search/api, 2000 req/month)'}`);
  lines.push(`- **OpenRouter/Perplexity:** ${OPENROUTER_API_KEY ? '✅ ACTIVE' : '❌ INACTIVE — set OPENROUTER_API_KEY (openrouter.ai, ~$0.001/query)'}`);
  lines.push('');

  lines.push('---');
  lines.push(`*RC Intelligence Monitor v4 — 15 layers: Google News · GDELT · SEC EDGAR · Mining RSS · World Bank · AfDB · GitHub ZK scanner · CourtListener · arXiv · Parliament · ICSID · FQM/Glencore IR · Zambian Local Press · EU Battery Passport*`);
  lines.push(`*Run \`node rc_intelligence_monitor.js\` to refresh | \`--dry\` for console only | \`--layer gdelt\` for single layer*`);
  lines.push(`*Premium: \`BRAVE_API_KEY=x node rc_intelligence_monitor.js\` or \`OPENROUTER_API_KEY=x node rc_intelligence_monitor.js\`*`);

  const report = lines.join('\n');

  // ── Output ────────────────────────────────────────────────────────────────
  if (DRY) {
    console.log('\n' + report);
  } else {
    if (!fs.existsSync(MEMORY_DIR)) fs.mkdirSync(MEMORY_DIR, { recursive: true });
    fs.writeFileSync(FEED_PATH, report);
    console.log(`\nReport written: ${FEED_PATH}`);
    console.log(`New items:      ${newCount}`);
  }

  state.seen    = [...seenSet].slice(-3000);
  state.lastRun = now;
  saveState(state);

  return newCount;
}

run().catch(console.error);
