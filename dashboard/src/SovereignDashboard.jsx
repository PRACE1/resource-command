/**
 * SovereignDashboard.jsx — v2.2
 * Resource Command · Sovereign Mineral Audit Terminal
 *
 * v2.2 additions:
 *   1. Live simulated block counter (every 2.2 s in sim mode, real-time feel)
 *   2. Session proof counter — total proofs verified since mount
 *   3. Throughput badge — live ~N/min calculated from session start
 *   4. FlipNumber — subtle roll animation on any changing value
 *   5. Staggered validator dot pulse — each dot has its own phase offset
 *   6. Bloom post-processing (graceful no-op if package absent)
 *      → npm install @react-three/postprocessing postprocessing
 *
 * Backend: http://localhost:8000
 *   GET  /api/leads   GET  /api/status
 *   POST /api/leads/:id/approve-reply   WS ws://localhost:8000/ws/logs
 */

import { useRef, useMemo, useEffect, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { gsap } from 'gsap'

// ─── CONFIG ──────────────────────────────────────────────────────────────────

const API = 'http://localhost:8000'
const WS  = 'ws://localhost:8000/ws/logs'

const VIP_NAMES = new Set([
  'Jordi Baylina', 'Akshith Gunasekaran', 'Keegan Ryan', 'Kobi Gurkan', 'Ying Tong Lai',
])

// ─── COLOUR PALETTE ──────────────────────────────────────────────────────────

const C = {
  bg:          '#090e1a',
  bgCard:      '#0d1b2a',
  bgBorder:    '#1e293b',
  emerald:     '#10b981',
  emeraldDim:  '#059669',
  emeraldGlow: '#34d399',
  slate:       '#94a3b8',
  slateLight:  '#cbd5e1',
  white:       '#f8fafc',
  red:         '#ef4444',
  amber:       '#f59e0b',
  blue:        '#3b82f6',
  violet:      '#a78bfa',
  cyan:        '#22d3ee',
}

// ─── STATIC DATA ─────────────────────────────────────────────────────────────

const FALLBACK_LEADS = [
  { id: 'jordi',    name: 'Jordi Baylina',       role: 'Circom Creator · Polygon',  progress: 72, status: 'SENT'    },
  { id: 'akshith',  name: 'Akshith Gunasekaran', role: 'Security Researcher · ToB', progress: 89, status: 'OPENED'  },
  { id: 'keegan',   name: 'Keegan Ryan',          role: 'Cryptographer · ToB',       progress: 45, status: 'SENT'    },
  { id: 'kobi',     name: 'Kobi Gurkan',          role: 'ZK Researcher',             progress: 31, status: 'PENDING' },
  { id: 'yingtong', name: 'Ying Tong Lai',        role: 'Circom Contributor',        progress: 18, status: 'COLD'    },
]

const AUDIT_PACK = [
  { label: 'Circuit Design',          pct: 100, done: true  },
  { label: 'Red Team Exercise',       pct: 100, done: true  },
  { label: 'Corporate Architecture',  pct: 100, done: true  },
  { label: 'Legal Risk Architecture', pct: 100, done: true  },
  { label: 'ToB Engagement',          pct: 55,  done: false },
  { label: 'MPC Ceremony',            pct: 12,  done: false },
  { label: 'v2.0 Oracle',             pct: 8,   done: false },
]

const TICKER_ITEMS = [
  'PROOF VERIFIED — Chambishi Site A — Tonnage: 4,821t — Royalty: $284,130 — Hash: 0x3a7f…c291',
  'PROOF VERIFIED — Luanshya Site B — Tonnage: 3,102t — Royalty: $182,518 — Hash: 0x9d2e…a445',
  'VALIDATOR CONSENSUS — 5/5 Nodes — AfDB ✓  WB ✓  ZRA ✓  MRC ✓  MoF ✓ — Block: #00441',
  'PROOF VERIFIED — Kansanshi Site C — Tonnage: 6,340t — Royalty: $373,060 — Hash: 0xb1c4…7f83',
  'MPC CEREMONY — Phase 2 Contribution Accepted — Participant: MRC Zambia — Entropy: MIXED',
  'GOVERNANCE UPDATE — royalty_rate_bps: 600 — Signed: ZRA — Block: #00438 — HQR: SATISFIED',
  'PROOF VERIFIED — Lumwana Site D — Tonnage: 5,217t — Royalty: $307,203 — Hash: 0xf8a1…b334',
]

// ─── UTILITIES ───────────────────────────────────────────────────────────────

function rHex(len = 48) {
  const h = '0123456789abcdef'
  let s = '0x'
  for (let i = 0; i < len; i++) s += h[Math.random() * 16 | 0]
  return s
}

const PREFIXES = [
  'π.A:', 'π.B[0]:', 'π.B[1]:', 'π.C:', 'VK.alpha:', 'VK.beta:',
  'INPUT[0]:', 'INPUT[1]:', 'POSEIDON:', 'R1CS.wit:',
  'COMMIT.ρ:', 'WITNESS:', 'GROTH16:', 'PAIRING:',
]

function proofLine() {
  return PREFIXES[Math.random() * PREFIXES.length | 0] + '  ' + rHex(52)
}

function lineColor(text) {
  if (/GROTH16|PAIRING/.test(text))  return C.cyan
  if (/POSEIDON|COMMIT/.test(text))  return C.violet
  if (/WITNESS|R1CS/.test(text))     return C.amber
  return C.emerald
}

function leadStatusColor(status) {
  if (status === 'REPLIED') return C.emeraldGlow
  if (status === 'OPENED')  return C.cyan
  if (status === 'SENT')    return C.emerald
  if (status === 'PENDING') return C.amber
  return C.slate
}

// ─── 3D: BLOOM (graceful no-op if @react-three/postprocessing not installed) ─

function SceneBloom() {
  const [Mods, setMods] = useState(null)
  useEffect(() => {
    import('@react-three/postprocessing')
      .then(m => setMods(m))
      .catch(() => {})
  }, [])
  if (!Mods) return null
  const { EffectComposer, Bloom } = Mods
  return (
    <EffectComposer>
      <Bloom luminanceThreshold={0.15} luminanceSmoothing={0.9} intensity={1.6} mipmapBlur />
    </EffectComposer>
  )
}

// ─── 3D: KINETIC LATTICE ─────────────────────────────────────────────────────

const NODE_COUNT   = 260
const CONNECT_DIST = 3.6

export function KineticLattice() {
  const groupRef = useRef()

  const nodeData = useMemo(() => Array.from({ length: NODE_COUNT }, () => ({
    ox: (Math.random() - 0.5) * 22,  oy: (Math.random() - 0.5) * 12,  oz: (Math.random() - 0.5) * 6,
    ax: (Math.random() - 0.5) * 0.35, ay: (Math.random() - 0.5) * 0.35, az: (Math.random() - 0.5) * 0.18,
    px: Math.random() * Math.PI * 2,  py: Math.random() * Math.PI * 2,  pz: Math.random() * Math.PI * 2,
    fx: 0.07 + Math.random() * 0.11,  fy: 0.06 + Math.random() * 0.09,  fz: 0.04 + Math.random() * 0.07,
  })), [])

  const edgeIndices = useMemo(() => {
    const out = []
    const d2  = CONNECT_DIST * CONNECT_DIST
    for (let i = 0; i < NODE_COUNT; i++) {
      for (let j = i + 1; j < NODE_COUNT; j++) {
        const dx = nodeData[i].ox - nodeData[j].ox
        const dy = nodeData[i].oy - nodeData[j].oy
        const dz = nodeData[i].oz - nodeData[j].oz
        if (dx*dx + dy*dy + dz*dz < d2) out.push(i, j)
      }
    }
    return out
  }, [nodeData])

  const pointsGeo = useMemo(() => {
    const g   = new THREE.BufferGeometry()
    const pos = new Float32Array(NODE_COUNT * 3)
    const col = new Float32Array(NODE_COUNT * 3)
    nodeData.forEach((n, i) => { pos[i*3] = n.ox; pos[i*3+1] = n.oy; pos[i*3+2] = n.oz })
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3).setUsage(THREE.DynamicDrawUsage))
    g.setAttribute('color',    new THREE.BufferAttribute(col, 3).setUsage(THREE.DynamicDrawUsage))
    return g
  }, [nodeData])

  const linesGeo = useMemo(() => {
    const g   = new THREE.BufferGeometry()
    const pos = new Float32Array(edgeIndices.length * 3)
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3).setUsage(THREE.DynamicDrawUsage))
    return g
  }, [edgeIndices])

  const pointsMat = useMemo(() => new THREE.PointsMaterial({
    vertexColors: true, size: 0.14, transparent: true, opacity: 1.0, sizeAttenuation: true,
  }), [])

  const linesMat = useMemo(() => new THREE.LineBasicMaterial({
    color: 0x10b981, transparent: true, opacity: 0.18,
  }), [])

  const pos = useMemo(() => new Float32Array(NODE_COUNT * 3), [])

  useEffect(() => () => {
    pointsGeo.dispose(); linesGeo.dispose(); pointsMat.dispose(); linesMat.dispose()
  }, [pointsGeo, linesGeo, pointsMat, linesMat])

  useFrame(({ clock }) => {
    const t      = clock.getElapsedTime()
    const colArr = pointsGeo.attributes.color.array

    for (let i = 0; i < NODE_COUNT; i++) {
      const n = nodeData[i]
      pos[i*3]   = n.ox + Math.sin(t * n.fx + n.px) * n.ax
      pos[i*3+1] = n.oy + Math.sin(t * n.fy + n.py) * n.ay
      pos[i*3+2] = n.oz + Math.sin(t * n.fz + n.pz) * n.az
      // Depth-graded: bright emerald core → violet perimeter
      const d = Math.sqrt(pos[i*3]*pos[i*3] + pos[i*3+1]*pos[i*3+1] + pos[i*3+2]*pos[i*3+2])
      const f = Math.min(d / 13, 1)
      colArr[i*3]   = 0.204 + f * 0.184
      colArr[i*3+1] = 0.827 - f * 0.427
      colArr[i*3+2] = 0.600 + f * 0.345
    }

    pointsGeo.attributes.position.array.set(pos)
    pointsGeo.attributes.position.needsUpdate = true
    pointsGeo.attributes.color.needsUpdate    = true

    const lp = linesGeo.attributes.position.array
    for (let e = 0; e < edgeIndices.length; e++) {
      const ni = edgeIndices[e]
      lp[e*3] = pos[ni*3]; lp[e*3+1] = pos[ni*3+1]; lp[e*3+2] = pos[ni*3+2]
    }
    linesGeo.attributes.position.needsUpdate = true

    if (groupRef.current) {
      groupRef.current.rotation.y = t * 0.016
      groupRef.current.rotation.x = Math.sin(t * 0.006) * 0.07
    }
  })

  return (
    <group ref={groupRef}>
      <points       geometry={pointsGeo} material={pointsMat} />
      <lineSegments geometry={linesGeo}  material={linesMat}  />
    </group>
  )
}

// ─── UI: FLIP NUMBER ─────────────────────────────────────────────────────────
// Subtle roll animation whenever a displayed value changes.

function FlipNumber({ value, style = {} }) {
  const [shown,    setShown]    = useState(value)
  const [flipping, setFlipping] = useState(false)
  const prev = useRef(value)

  useEffect(() => {
    if (String(value) === String(prev.current)) return
    setFlipping(true)
    const t = setTimeout(() => { setShown(value); setFlipping(false); prev.current = value }, 130)
    return () => clearTimeout(t)
  }, [value])

  return (
    <span style={{
      ...style,
      display:    'inline-block',
      opacity:    flipping ? 0.25 : 1,
      transform:  flipping ? 'translateY(-5px)' : 'translateY(0)',
      transition: 'opacity 0.13s ease, transform 0.13s ease',
    }}>
      {shown}
    </span>
  )
}

// ─── UI: QUORUM RING ─────────────────────────────────────────────────────────

function QuorumRing({ v = {}, nodes = [], round = null }) {
  const active = v.active ?? 5
  const total  = v.total  ?? 5
  const hqr    = v.hqr_satisfied !== false
  const pct    = Math.round((active / total) * 100)

  const SIZE = 132, cx = 66, cy = 66, R = 48, SW = 7
  const circ       = 2 * Math.PI * R
  const activeDash = circ * (active / total)
  const ringColor  = hqr ? C.emerald : C.amber

  const vLabels = nodes.length >= total
    ? nodes.slice(0, total).map(n => n.id)
    : ['ZRA', 'MRC', 'AfDB', 'WB', 'MoF'].slice(0, total)

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '22px' }}>

      <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`} style={{ flexShrink: 0 }}>
        {/* Outer dashed decorative ring */}
        <circle cx={cx} cy={cy} r={R + 14} fill="none" stroke={C.bgBorder} strokeWidth="1" strokeDasharray="2 4" />
        {/* Track */}
        <circle cx={cx} cy={cy} r={R} fill="none" stroke={C.bgBorder} strokeWidth={SW} />
        {/* Active arc */}
        <circle cx={cx} cy={cy} r={R} fill="none"
          stroke={ringColor} strokeWidth={SW}
          strokeDasharray={`${activeDash} ${circ}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${cx} ${cy})`}
          style={{ filter: `drop-shadow(0 0 7px ${ringColor})`, transition: 'stroke-dasharray 0.8s ease' }}
        />
        {/* Centre pct */}
        <text x={cx} y={cy - 8} textAnchor="middle" fill={C.white}
          fontSize="22" fontWeight="700" fontFamily="JetBrains Mono, monospace"
          style={{ filter: `drop-shadow(0 0 5px ${ringColor})` }}>
          {pct}%
        </text>
        <text x={cx} y={cy + 8} textAnchor="middle" fill={C.slate}
          fontSize="7" fontFamily="Inter, sans-serif" letterSpacing="2.5">
          QUORUM
        </text>
        <text x={cx} y={cy + 20} textAnchor="middle" fill={ringColor}
          fontSize="6" fontFamily="Inter, sans-serif" fontWeight="700" letterSpacing="1.5">
          {hqr ? 'HQR SATISFIED' : 'HQR DEGRADED'}
        </text>

        {/* Validator dots — staggered pulse via animationDelay */}
        {vLabels.map((label, i) => {
          const angle = (i / total) * 2 * Math.PI - Math.PI / 2
          const nx    = cx + (R + 17) * Math.cos(angle)
          const ny    = cy + (R + 17) * Math.sin(angle)
          const ok    = i < active
          const col   = ok ? ringColor : C.slate
          return (
            <g key={label}>
              <circle cx={nx} cy={ny} r="4" fill="none" stroke={col} strokeWidth="1.5"
                style={ok ? {
                  filter: `drop-shadow(0 0 4px ${ringColor})`,
                  animation: `pulse-dot 2.2s ease-in-out ${(i * 0.44).toFixed(2)}s infinite`,
                } : {}} />
              <circle cx={nx} cy={ny} r="1.8" fill={col} />
              <text x={nx} y={ny + 12} textAnchor="middle" fill={col}
                fontSize="5.5" fontFamily="Inter, sans-serif" fontWeight="700" letterSpacing="0.5">
                {label}
              </text>
            </g>
          )
        })}
      </svg>

      {/* Stats column */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '13px', flex: 1 }}>
        <div>
          <div style={{ fontSize: '7.5px', color: C.slate, letterSpacing: '2px', textTransform: 'uppercase', fontFamily: 'Inter, sans-serif', marginBottom: '3px' }}>Validators</div>
          <div style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, color: C.white, textShadow: `0 0 12px ${ringColor}90` }}>
            <span style={{ fontSize: '28px' }}>{active}</span>
            <span style={{ fontSize: '13px', color: C.slate, fontWeight: 400 }}> / {total} online</span>
          </div>
        </div>
        <div>
          <div style={{ fontSize: '7.5px', color: C.slate, letterSpacing: '2px', textTransform: 'uppercase', fontFamily: 'Inter, sans-serif', marginBottom: '3px' }}>Block</div>
          <div style={{ fontSize: '22px', fontWeight: 700, color: C.white, fontFamily: "'JetBrains Mono', monospace", textShadow: `0 0 12px ${C.emerald}90` }}>
            {round != null
              ? <FlipNumber value={`#${String(round).padStart(5, '0')}`} />
              : '—'}
          </div>
        </div>
        <div style={{ fontSize: '8.5px', color: hqr ? C.emerald : C.amber, fontFamily: "'JetBrains Mono', monospace", fontWeight: 600, letterSpacing: '0.3px' }}>
          Q ∩ &#123;AfDB, WB&#125; {hqr ? '≠ ∅ ✓' : '= ∅ ✗'}
        </div>
      </div>

    </div>
  )
}

// ─── UI: HEX PROOF STREAM ────────────────────────────────────────────────────

function HexStream({ lines }) {
  return (
    <div style={{
      fontFamily:    "'JetBrains Mono', monospace",
      fontSize:      '10.5px',
      lineHeight:    '1.75',
      height:        '100%',
      overflow:      'hidden',
      maskImage:         'linear-gradient(to bottom, transparent 0%, black 10%, black 90%, transparent 100%)',
      WebkitMaskImage:   'linear-gradient(to bottom, transparent 0%, black 10%, black 90%, transparent 100%)',
    }}>
      {lines.map(({ id, text, live }, i) => (
        <div key={id} style={{
          opacity:      0.22 + (i / lines.length) * 0.78,
          whiteSpace:   'nowrap',
          overflow:     'hidden',
          textOverflow: 'ellipsis',
          color:        i === lines.length - 1 ? '#f0fdf4' : lineColor(text),
          fontWeight:   i === lines.length - 1 ? 700 : 400,
          transition:   'color 0.15s',
          textShadow:   i >= lines.length - 2 ? `0 0 8px ${lineColor(text)}` : 'none',
          letterSpacing: live && i === lines.length - 1 ? '0.2px' : 'normal',
        }}>
          {live ? '▸ ' : ''}{text}
        </div>
      ))}
    </div>
  )
}

// ─── UI: INBOX INTERCEPT MODAL ───────────────────────────────────────────────

function VipReplyModal({ reply, onClose }) {
  const [edited,  setEdited]  = useState('')
  const [sending, setSending] = useState(false)
  const [sent,    setSent]    = useState(false)
  const [err,     setErr]     = useState(null)

  useEffect(() => { if (reply) { setEdited(reply.drafted); setSent(false); setErr(null) } }, [reply])

  if (!reply) return null

  async function handleApprove() {
    setSending(true); setErr(null)
    try {
      const res = await fetch(`${API}/api/leads/${reply.lead.id}/approve-reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: edited }),
      })
      if (!res.ok) throw new Error(res.status)
      setSent(true); setTimeout(onClose, 1400)
    } catch (e) {
      setErr(`Backend error ${e.message} — response not sent`); setSending(false)
    }
  }

  const ts  = reply.lead.replied_at
    ? new Date(reply.lead.replied_at).toISOString().replace('T', ' ').slice(0, 19) + ' UTC'
    : 'just now'
  const btn = { padding: '7px 18px', borderRadius: '6px', fontSize: '9px', fontFamily: 'Inter, sans-serif', fontWeight: 700, letterSpacing: '1px', cursor: 'pointer' }

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 200, background: 'rgba(0,0,0,0.82)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', animation: 'modal-in 0.2s ease-out' }}>
      <div style={{ width: '560px', maxWidth: '92vw', background: 'linear-gradient(145deg, #07101f, #0d1b2a)', border: `1px solid ${C.red}55`, borderRadius: '12px', boxShadow: `0 0 70px ${C.red}18, 0 0 0 1px ${C.red}35`, overflow: 'hidden' }}>
        <div style={{ padding: '12px 18px', background: `linear-gradient(90deg, ${C.red}18, transparent)`, borderBottom: `1px solid ${C.red}25`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: C.red, color: C.red, display: 'inline-block', animation: 'pulse-dot 1.2s ease-in-out infinite' }} />
            <span style={{ fontSize: '9px', fontWeight: 800, color: C.red, letterSpacing: '3px', fontFamily: 'Inter, sans-serif', textTransform: 'uppercase' }}>Inbox Intercept</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '7px', background: `${C.red}18`, color: C.red, padding: '2px 8px', borderRadius: '10px', border: `1px solid ${C.red}35`, fontFamily: 'Inter, sans-serif', fontWeight: 700, letterSpacing: '1.5px' }}>VIP RESPONSE</span>
            <button onClick={onClose} style={{ background: 'none', border: 'none', color: C.slate, cursor: 'pointer', fontSize: '15px', lineHeight: 1 }}>✕</button>
          </div>
        </div>
        <div style={{ padding: '14px 18px 11px', borderBottom: `1px solid ${C.bgBorder}` }}>
          <div style={{ fontSize: '14px', fontWeight: 700, color: C.white, fontFamily: 'Inter, sans-serif' }}>{reply.lead.name}</div>
          <div style={{ fontSize: '9px', color: C.slate, fontFamily: 'Inter, sans-serif', marginTop: '3px' }}>{reply.lead.role} · {ts}</div>
        </div>
        <div style={{ padding: '12px 18px', borderBottom: `1px solid ${C.bgBorder}` }}>
          <div style={{ fontSize: '7.5px', color: C.slate, letterSpacing: '2px', textTransform: 'uppercase', fontFamily: 'Inter, sans-serif', marginBottom: '8px' }}>Incoming Message</div>
          <div style={{ background: 'rgba(255,255,255,0.03)', border: `1px solid ${C.bgBorder}`, borderRadius: '6px', padding: '10px 13px', fontSize: '10.5px', color: C.slateLight, fontFamily: 'Inter, sans-serif', lineHeight: '1.65', maxHeight: '80px', overflowY: 'auto' }}>{reply.message}</div>
        </div>
        <div style={{ padding: '12px 18px', borderBottom: `1px solid ${C.bgBorder}` }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '7.5px', color: C.emerald, letterSpacing: '2px', textTransform: 'uppercase', fontFamily: 'Inter, sans-serif' }}>Swarm-Drafted Response</span>
            <span style={{ fontSize: '7px', color: C.slate, fontFamily: 'Inter, sans-serif' }}>editable before send</span>
          </div>
          <textarea value={edited} onChange={e => setEdited(e.target.value)} rows={4}
            style={{ width: '100%', background: `${C.emerald}06`, border: `1px solid ${C.emerald}28`, borderRadius: '6px', padding: '10px 13px', fontSize: '10.5px', color: C.slateLight, fontFamily: "'JetBrains Mono', monospace", lineHeight: '1.6', resize: 'vertical', outline: 'none', transition: 'border-color 0.2s', boxSizing: 'border-box' }}
            onFocus={e => { e.target.style.borderColor = `${C.emerald}65` }}
            onBlur={e  => { e.target.style.borderColor = `${C.emerald}28` }}
          />
        </div>
        {err && <div style={{ padding: '7px 18px', background: `${C.red}0c`, borderBottom: `1px solid ${C.red}20` }}><span style={{ fontSize: '9px', color: C.red, fontFamily: 'Inter, sans-serif' }}>{err}</span></div>}
        <div style={{ padding: '12px 18px', display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
          <button onClick={onClose} style={{ ...btn, border: `1px solid ${C.bgBorder}`, background: 'transparent', color: C.slate }}>DISMISS</button>
          <button onClick={handleApprove} disabled={sending || sent} style={{ ...btn, border: 'none', background: sent ? C.emeraldDim : `linear-gradient(90deg, ${C.emeraldDim}, ${C.emerald})`, color: C.bg, opacity: sending ? 0.7 : 1, boxShadow: sent ? 'none' : `0 0 18px ${C.emerald}40`, transition: 'all 0.2s' }}>
            {sent ? '✓ SENT' : sending ? 'SENDING…' : '✓ APPROVE & SEND'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── UI: ANIMATED BAR ────────────────────────────────────────────────────────

function AnimatedBar({ pct, color, glow }) {
  const [width, setWidth] = useState(0)
  useEffect(() => { const t = setTimeout(() => setWidth(pct), 200); return () => clearTimeout(t) }, [pct])
  return (
    <div style={{ height: '100%', width: `${width}%`, background: color, borderRadius: 'inherit', transition: 'width 1.4s cubic-bezier(0.4, 0, 0.2, 1)', ...(glow ? { boxShadow: glow } : {}) }} />
  )
}

// ─── UI: TELEMETRY WIDGET ────────────────────────────────────────────────────

function TelemetryWidget({ label, value, unit, status, sub }) {
  const accent = status === 'ok' ? C.emerald : status === 'warn' ? C.amber : C.red
  return (
    <div style={{ background: 'linear-gradient(135deg, rgba(9,14,26,0.9), rgba(13,27,42,0.95))', border: `1px solid ${C.bgBorder}`, borderLeft: `2px solid ${accent}`, borderRadius: '6px', padding: '11px 13px', marginBottom: '9px' }}>
      <div style={{ fontSize: '8.5px', color: C.slate, textTransform: 'uppercase', letterSpacing: '1.6px', fontFamily: 'Inter, sans-serif', marginBottom: '4px' }}>{label}</div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
        <FlipNumber value={value} style={{
          fontSize: '30px', fontWeight: 700, color: C.white,
          fontFamily: "'JetBrains Mono', monospace",
          ...(status === 'ok'   ? { textShadow: `0 0 16px ${C.emerald}95` } :
              status === 'warn' ? { textShadow: `0 0 16px ${C.amber}95`   } : {}),
        }} />
        <span style={{ fontSize: '10px', color: C.slate, fontFamily: 'Inter, sans-serif' }}>{unit}</span>
      </div>
      {sub && <div style={{ fontSize: '8.5px', color: C.emeraldDim, marginTop: '3px', fontFamily: 'Inter, sans-serif' }}>{sub}</div>}
    </div>
  )
}

// ─── UI: OUTREACH ROW ────────────────────────────────────────────────────────

function OutreachRow({ name, role, progress, status, isAlert }) {
  const statusColor = isAlert ? C.red : leadStatusColor(status)
  const barColor    = isAlert
    ? `linear-gradient(90deg, #b91c1c, ${C.red})`
    : status === 'REPLIED'
      ? `linear-gradient(90deg, ${C.emeraldDim}, ${C.emeraldGlow})`
      : `linear-gradient(90deg, ${C.emeraldDim}, ${C.emerald})`

  return (
    <div style={{ marginBottom: '13px', ...(isAlert ? { background: `${C.red}08`, border: `1px solid ${C.red}28`, borderRadius: '6px', padding: '7px 9px', margin: '0 -9px 13px', animation: 'alert-row 1.8s ease-in-out infinite' } : {}) }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '5px' }}>
        <div>
          <div style={{ fontSize: '10.5px', fontWeight: 600, color: C.white, fontFamily: 'Inter, sans-serif' }}>{name}</div>
          <div style={{ fontSize: '8.5px', color: C.slate, fontFamily: 'Inter, sans-serif', marginTop: '1px' }}>{role}</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', flexShrink: 0, marginLeft: '8px' }}>
          {isAlert && <span style={{ fontSize: '7px', color: C.red, fontFamily: 'Inter, sans-serif', fontWeight: 700, letterSpacing: '1.5px' }}>REPLIED ▸</span>}
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: statusColor, display: 'inline-block', boxShadow: `0 0 6px ${statusColor}`, ...(isAlert ? { animation: 'pulse-dot 1s ease-in-out infinite' } : {}) }} />
          <span style={{ fontSize: '9.5px', fontFamily: "'JetBrains Mono', monospace", color: statusColor }}>{status}</span>
        </div>
      </div>
      <div style={{ height: '3px', background: C.bgBorder, borderRadius: '2px', overflow: 'hidden' }}>
        <AnimatedBar pct={progress} color={barColor} glow={isAlert ? `0 0 8px ${C.red}60` : `0 0 8px ${C.emerald}50`} />
      </div>
    </div>
  )
}

// ─── UI: CARD ────────────────────────────────────────────────────────────────

function Card({ title, badge, badgeAccent = C.emerald, accent = C.emerald, children, style = {} }) {
  return (
    <div style={{ background: 'linear-gradient(135deg, rgba(9,14,26,0.94), rgba(13,27,42,0.97))', border: `1px solid ${C.bgBorder}`, borderRadius: '8px', backdropFilter: 'blur(14px)', overflow: 'hidden', ...style }}>
      <div style={{ height: '2px', background: `linear-gradient(90deg, transparent, ${accent}85, ${C.cyan}65, ${accent}85, transparent)` }} />
      <div style={{ padding: '9px 13px', borderBottom: `1px solid ${C.bgBorder}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '8.5px', fontWeight: 700, color: C.slate, textTransform: 'uppercase', letterSpacing: '2px', fontFamily: 'Inter, sans-serif' }}>{title}</span>
        {badge != null && (
          <span style={{ fontSize: '7.5px', background: `${badgeAccent}18`, color: badgeAccent, padding: '2px 7px', borderRadius: '10px', border: `1px solid ${badgeAccent}35`, fontFamily: 'Inter, sans-serif', fontWeight: 700, letterSpacing: '0.8px' }}>
            {badge}
          </span>
        )}
      </div>
      <div style={{ padding: '13px', ...(style.flex ? { flex: 1, display: 'flex', flexDirection: 'column' } : {}) }}>
        {children}
      </div>
    </div>
  )
}

// ─── UI: FOOTER TICKER ───────────────────────────────────────────────────────

function FooterTicker() {
  const trackRef = useRef()
  useEffect(() => {
    if (!trackRef.current) return
    const el = trackRef.current
    const w  = el.scrollWidth / 2
    gsap.to(el, { x: -w, duration: 55, ease: 'none', repeat: -1 })
    return () => gsap.killTweensOf(el)
  }, [])
  const doubled = [...TICKER_ITEMS, ...TICKER_ITEMS]
  return (
    <div style={{ overflow: 'hidden', borderTop: `1px solid ${C.bgBorder}`, background: 'rgba(7,10,22,0.97)', padding: '7px 0', display: 'flex', alignItems: 'center', flexShrink: 0 }}>
      <div style={{ fontSize: '8px', fontFamily: 'Inter, sans-serif', fontWeight: 800, color: C.emerald, letterSpacing: '2px', padding: '0 16px', borderRight: `1px solid ${C.bgBorder}`, whiteSpace: 'nowrap', flexShrink: 0 }}>LIVE AUDIT</div>
      <div style={{ overflow: 'hidden', flex: 1 }}>
        <div ref={trackRef} style={{ display: 'flex', gap: '64px', willChange: 'transform' }}>
          {doubled.map((item, i) => (
            <span key={i} style={{ whiteSpace: 'nowrap', fontSize: '9.5px', fontFamily: "'JetBrains Mono', monospace", color: C.slate, flexShrink: 0 }}>
              <span style={{ color: C.emerald, marginRight: '8px' }}>✓</span>{item}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

// ─── DATA HOOKS ──────────────────────────────────────────────────────────────

function useProofStream() {
  const counterRef     = useRef(30)
  const wsRef          = useRef(null)
  const reconnTimerRef = useRef(null)
  const sessionStart   = useRef(Date.now())

  const [lines, setLines] = useState(() =>
    Array.from({ length: 30 }, (_, i) => ({ id: i, text: proofLine(), live: false }))
  )
  const [wsConnected,  setWsConnected]  = useState(false)
  const [proofCount,   setProofCount]   = useState(0)
  const [throughput,   setThroughput]   = useState(0)

  useEffect(() => {
    let alive = true

    function pushLine(text, live) {
      setLines(p => {
        const next = [...p]; next.shift()
        next.push({ id: counterRef.current++, text, live })
        return next
      })
      setProofCount(c => {
        const newCount = c + 1
        const elapsedMin = (Date.now() - sessionStart.current) / 60000
        setThroughput(Math.round(newCount / Math.max(elapsedMin, 0.017)))
        return newCount
      })
    }

    function connect() {
      if (!alive) return
      try {
        const ws = new WebSocket(WS)
        wsRef.current = ws
        ws.onopen    = () => { if (alive) setWsConnected(true) }
        ws.onmessage = (e) => { if (alive) pushLine(String(e.data).trim(), true) }
        ws.onclose   = () => { if (!alive) return; setWsConnected(false); reconnTimerRef.current = setTimeout(connect, 3000) }
        ws.onerror   = () => ws.close()
      } catch { reconnTimerRef.current = setTimeout(connect, 3000) }
    }

    connect()
    const simId = setInterval(() => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) pushLine(proofLine(), false)
    }, 160)

    return () => { alive = false; clearTimeout(reconnTimerRef.current); clearInterval(simId); wsRef.current?.close() }
  }, [])

  return { lines, wsConnected, proofCount, throughput }
}

function useLeads() {
  const [leads, setLeads]       = useState(FALLBACK_LEADS)
  const [alertIds, setAlertIds] = useState(new Set())
  const [vipReply, setVipReply] = useState(null)
  const prevRef = useRef({})

  useEffect(() => {
    async function poll() {
      try {
        const res = await fetch(`${API}/api/leads`)
        if (!res.ok) return
        const data = await res.json()
        const fresh = new Set()
        data.forEach(lead => {
          const prev = prevRef.current[lead.id]
          if (prev && prev.status !== 'REPLIED' && lead.status === 'REPLIED') {
            fresh.add(lead.id)
            if (VIP_NAMES.has(lead.name) && !vipReply) {
              setVipReply({ lead, message: lead.last_message ?? '(no body)', drafted: lead.drafted_response ?? '' })
            }
          }
        })
        if (fresh.size > 0) setAlertIds(prev => new Set([...prev, ...fresh]))
        prevRef.current = Object.fromEntries(data.map(l => [l.id, l]))
        setLeads(data)
      } catch { /* silent — fallback stays */ }
    }
    poll(); const id = setInterval(poll, 5000); return () => clearInterval(id)
  }, []) // eslint-disable-line

  return {
    leads, alertIds, vipReply,
    clearVipReply: () => setVipReply(null),
    clearAlert: (id) => setAlertIds(prev => { const s = new Set(prev); s.delete(id); return s }),
  }
}

function useSystemStatus() {
  const [status, setStatus]        = useState(null)
  const [backendOnline, setOnline] = useState(false)
  useEffect(() => {
    async function poll() {
      try {
        const res = await fetch(`${API}/api/status`)
        if (!res.ok) { setOnline(false); return }
        setStatus(await res.json()); setOnline(true)
      } catch { setOnline(false) }
    }
    poll(); const id = setInterval(poll, 3000); return () => clearInterval(id)
  }, [])
  return { status, backendOnline }
}

// ─── MAIN DASHBOARD ──────────────────────────────────────────────────────────

export default function SovereignDashboard() {
  const headerRef = useRef()
  const leftRef   = useRef()
  const rightRef  = useRef()
  const centerRef = useRef()

  const [now, setNow] = useState(() => new Date().toISOString().replace('T', ' ').slice(0, 19))

  // Live block counter — increments in sim mode so the terminal always feels alive
  const [simBlock, setSimBlock] = useState(441)

  const { lines, wsConnected, proofCount, throughput }    = useProofStream()
  const { leads, alertIds, vipReply, clearVipReply,
          clearAlert }                                     = useLeads()
  const { status, backendOnline }                          = useSystemStatus()

  // Clock
  useEffect(() => {
    const id = setInterval(() => setNow(new Date().toISOString().replace('T', ' ').slice(0, 19)), 1000)
    return () => clearInterval(id)
  }, [])

  // Simulated block counter — pauses when backend takes over
  useEffect(() => {
    if (backendOnline) return
    const id = setInterval(() => setSimBlock(b => b + 1), 2200)
    return () => clearInterval(id)
  }, [backendOnline])

  // Entry animations
  useEffect(() => {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out', duration: 0.85 } })
    tl.fromTo(headerRef.current, { opacity: 0, y: -18 },     { opacity: 1, y: 0 })
      .fromTo(leftRef.current,   { opacity: 0, x: -36 },     { opacity: 1, x: 0 }, '-=0.5')
      .fromTo(rightRef.current,  { opacity: 0, x: 36 },      { opacity: 1, x: 0 }, '-=0.85')
      .fromTo(centerRef.current, { opacity: 0, scale: 0.97 },{ opacity: 1, scale: 1 }, '-=0.7')
    return () => tl.kill()
  }, [])

  const v     = status?.validators    ?? {}
  const pl    = status?.proof_latency ?? {}
  const nodes = status?.nodes ?? [
    { id: 'LSK', name: 'Lusaka',     latency_ms: 12,  status: 'ok',   hsm_status: 'ONLINE' },
    { id: 'ABJ', name: 'Abidjan',    latency_ms: 38,  status: 'ok',   hsm_status: 'ONLINE' },
    { id: 'WDC', name: 'Washington', latency_ms: 142, status: 'warn', hsm_status: 'ONLINE' },
  ]

  const activeLeads   = leads.filter(l => ['SENT', 'OPENED', 'REPLIED'].includes(l.status)).length
  const currentBlock  = status?.consensus_round ?? simBlock
  const nodeLabels    = { LSK: 'Primary', ABJ: 'Relay', WDC: 'Anchor' }

  // Stream badge: shows connection state + running proof count + throughput
  const proofCountFmt = proofCount > 999 ? `${(proofCount / 1000).toFixed(1)}k` : String(proofCount)
  const streamBadge   = wsConnected
    ? `● LIVE · ${proofCountFmt} proofs`
    : `◌ SIM · ${proofCountFmt} verified`
  const streamAccent  = wsConnected ? C.emerald : C.amber

  return (
    <div style={{ width: '100vw', height: '100vh', background: C.bg, overflow: 'hidden', display: 'flex', flexDirection: 'column', fontFamily: 'Inter, sans-serif', position: 'relative' }}>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-track { background: ${C.bg}; }
        ::-webkit-scrollbar-thumb { background: ${C.bgBorder}; border-radius: 2px; }
        @keyframes pulse-dot {
          0%, 100% { box-shadow: 0 0 10px currentColor; opacity: 1; }
          50%       { box-shadow: 0 0 22px currentColor, 0 0 40px currentColor; opacity: 0.7; }
        }
        @keyframes title-shimmer {
          0%   { background-position: 0% center; }
          100% { background-position: 300% center; }
        }
        @keyframes card-glow {
          0%, 100% { box-shadow: 0 0 0 1px rgba(16,185,129,0.12); }
          50%       { box-shadow: 0 0 0 1px rgba(16,185,129,0.42), 0 0 32px rgba(16,185,129,0.10); }
        }
        @keyframes accent-pulse {
          0%, 100% { opacity: 0.5; }
          50%       { opacity: 1; }
        }
        @keyframes alert-row {
          0%, 100% { border-color: ${C.red}30; background: ${C.red}08; }
          50%       { border-color: ${C.red}65; background: ${C.red}14; }
        }
        @keyframes modal-in {
          from { opacity: 0; transform: scale(0.95) translateY(10px); }
          to   { opacity: 1; transform: scale(1) translateY(0); }
        }
        @keyframes throughput-tick {
          from { opacity: 0.5; transform: scale(0.96); }
          to   { opacity: 1;   transform: scale(1); }
        }
      `}</style>

      <VipReplyModal reply={vipReply} onClose={() => { clearVipReply(); if (vipReply) clearAlert(vipReply.lead.id) }} />

      {/* ── Header ── */}
      <div ref={headerRef} style={{ padding: '11px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(7,10,22,0.96)', backdropFilter: 'blur(12px)', zIndex: 10, flexShrink: 0, position: 'relative' }}>
        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: '1px', background: `linear-gradient(90deg, transparent, ${C.emerald}60 20%, #22d3ee80 50%, ${C.emerald}60 80%, transparent)`, animation: 'accent-pulse 3s ease-in-out infinite' }} />
        <div style={{ display: 'flex', alignItems: 'center', gap: '11px' }}>
          <div style={{ width: '7px', height: '7px', borderRadius: '50%', background: C.emerald, color: C.emerald, animation: 'pulse-dot 2.5s ease-in-out infinite' }} />
          <span style={{ fontSize: '10.5px', fontWeight: 700, letterSpacing: '3.5px', textTransform: 'uppercase', background: `linear-gradient(90deg, ${C.emerald}, #34d399, #22d3ee, #a78bfa, ${C.emerald})`, backgroundSize: '300% auto', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', animation: 'title-shimmer 6s linear infinite' }}>
            Resource Command
          </span>
          <span style={{ fontSize: '8.5px', color: C.slate, letterSpacing: '0.8px' }}>
            Sovereign Mineral Audit Terminal · v2.2 · Region: SADC
          </span>
        </div>
        <div style={{ display: 'flex', gap: '14px', alignItems: 'center' }}>
          <span style={{ fontSize: '7.5px', padding: '2px 9px', borderRadius: '10px', border: `1px solid ${backendOnline ? C.emerald : C.amber}40`, background: `${backendOnline ? C.emerald : C.amber}10`, color: backendOnline ? C.emerald : C.amber, fontFamily: 'Inter, sans-serif', fontWeight: 700, letterSpacing: '1px' }}>
            {backendOnline ? '● BACKEND ONLINE' : '◌ SIMULATION MODE'}
          </span>
          {/* Throughput pill — shows ~N/min */}
          {proofCount > 5 && (
            <span style={{ fontSize: '7.5px', padding: '2px 9px', borderRadius: '10px', border: `1px solid ${C.cyan}30`, background: `${C.cyan}08`, color: C.cyan, fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, letterSpacing: '0.5px', animation: 'throughput-tick 0.5s ease' }}>
              ~{throughput}/min
            </span>
          )}
          {nodes.map(n => (
            <span key={n.id} style={{ fontSize: '9px', color: n.status === 'ok' ? C.emerald : C.amber, fontFamily: "'JetBrains Mono', monospace", fontWeight: 600 }}>{n.id} ✓</span>
          ))}
          <span style={{ fontSize: '9px', color: C.slate, fontFamily: "'JetBrains Mono', monospace" }}>{now} UTC</span>
        </div>
      </div>

      {/* ── Body ── */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden', position: 'relative' }}>

        {/* 3D Canvas */}
        <div style={{ position: 'absolute', inset: 0, zIndex: 0 }}>
          <Canvas
            camera={{ position: [0, 0, 11], fov: 58 }}
            gl={{ antialias: false, alpha: false, powerPreference: 'high-performance' }}
            frameloop="always"
          >
            <color attach="background" args={['#090e1a']} />
            <fog   attach="fog"        args={['#090e1a', 18, 30]} />
            <KineticLattice />
            <SceneBloom />
          </Canvas>
        </div>

        {/* Ambient core glow */}
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '900px', height: '520px', background: 'radial-gradient(ellipse, rgba(16,185,129,0.09) 0%, rgba(99,102,241,0.05) 45%, transparent 72%)', pointerEvents: 'none', zIndex: 0 }} />

        {/* Scanlines */}
        <div style={{ position: 'absolute', inset: 0, zIndex: 2, pointerEvents: 'none', background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.035) 2px, rgba(0,0,0,0.035) 4px)' }} />

        {/* Vignette */}
        <div style={{ position: 'absolute', inset: 0, zIndex: 2, pointerEvents: 'none', background: 'radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.28) 100%)' }} />

        {/* ── Left Sidebar ── */}
        <div ref={leftRef} style={{ width: '238px', flexShrink: 0, padding: '14px 11px', zIndex: 3, display: 'flex', flexDirection: 'column', gap: '10px', overflowY: 'auto' }}>
          <Card title="Network Health" badge={backendOnline ? 'LIVE' : 'SIM'} badgeAccent={backendOnline ? C.emerald : C.amber} accent={C.emerald}>
            <TelemetryWidget label="Active Validators" value={v.active ?? 5}       unit={`/ ${v.total ?? 5}`}   status={v.hqr_satisfied === false ? 'warn' : 'ok'} sub={v.hqr_satisfied === false ? 'HQR DEGRADED — check quorum' : 'HQR SATISFIED — AfDB + WB confirmed'} />
            <TelemetryWidget label="Consensus Round"   value={status?.consensus_round ?? currentBlock} unit="block" status="ok" sub={`Last commit: ${v.last_commit_sec ?? '2.1'}s ago`} />
            <TelemetryWidget label="Quorum Health"     value={v.active != null ? Math.round((v.active / v.total) * 100) : 100} unit="%" status={v.active === v.total || v.active == null ? 'ok' : 'warn'} sub="Zero liveness failures" />
          </Card>

          <Card title="Proof Latency" accent={C.cyan}>
            <TelemetryWidget label="Groth16 Gen" value={pl.groth16_sec ?? '3.2'} unit="sec"     status={(pl.groth16_sec ?? 0) > 8  ? 'warn' : 'ok'} sub="BN254 — 542 constraints" />
            <TelemetryWidget label="BFT Verify"  value={pl.bft_ms     ?? '8'}   unit="ms"      status={(pl.bft_ms     ?? 0) > 50 ? 'warn' : 'ok'} sub="On-chain verification" />
            <TelemetryWidget label="Queue Depth" value={pl.queue_depth ?? '0'}  unit="pending" status={(pl.queue_depth ?? 0) > 0  ? 'warn' : 'ok'} sub={(pl.queue_depth ?? 0) > 0 ? `${pl.queue_depth} awaiting` : 'All proofs cleared'} />
          </Card>

          <Card title="Region: SADC" accent={C.violet}>
            {nodes.map(n => (
              <TelemetryWidget key={n.id} label={`${nodeLabels[n.id] ?? n.id} Node`} value={n.id} unit={n.name} status={n.status} sub={`${n.latency_ms}ms · FIPS HSM ${n.hsm_status}`} />
            ))}
          </Card>
        </div>

        {/* ── Centre ── */}
        <div ref={centerRef} style={{ flex: 1, zIndex: 3, display: 'flex', flexDirection: 'column', padding: '14px 16px', gap: '10px', minWidth: 0 }}>

          <Card title="Network Consensus" badge={`${v.active ?? 5}/${v.total ?? 5} VALIDATORS`} accent={v.hqr_satisfied === false ? C.amber : C.emerald}>
            <QuorumRing v={v} nodes={nodes} round={currentBlock} />
          </Card>

          <Card
            title="ZK-Proof Verification Engine"
            badge={streamBadge}
            badgeAccent={streamAccent}
            accent={C.cyan}
            style={{ flex: 1, display: 'flex', flexDirection: 'column', animation: 'card-glow 3.5s ease-in-out infinite' }}
          >
            <div style={{ flex: 1, minHeight: 0 }}>
              <HexStream lines={lines} />
            </div>
          </Card>
        </div>

        {/* ── Right Sidebar ── */}
        <div ref={rightRef} style={{ width: '258px', flexShrink: 0, padding: '14px 11px', zIndex: 3, display: 'flex', flexDirection: 'column', gap: '10px', overflowY: 'auto' }}>
          <Card title="Institutional Outreach" badge={`${activeLeads} ACTIVE`} accent={C.emerald}>
            {leads.map(lead => (
              <OutreachRow key={lead.id} {...lead} isAlert={alertIds.has(lead.id)} />
            ))}
          </Card>

          <Card title="Audit Pack Status" accent={C.violet}>
            {AUDIT_PACK.map(({ label, pct, done }) => (
              <div key={label} style={{ marginBottom: '9px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                  <span style={{ fontSize: '9px', color: done ? C.emerald : C.slate, fontFamily: 'Inter, sans-serif' }}>{label}</span>
                  <span style={{ fontSize: '9px', fontFamily: "'JetBrains Mono', monospace", color: done ? C.emerald : C.slate }}>{pct}%</span>
                </div>
                <div style={{ height: '2px', background: C.bgBorder, borderRadius: '1px', overflow: 'hidden' }}>
                  <AnimatedBar pct={pct} color={done ? `linear-gradient(90deg, ${C.emeraldDim}, ${C.emerald})` : C.blue} glow={done ? `0 0 6px ${C.emerald}40` : undefined} />
                </div>
              </div>
            ))}
          </Card>
        </div>

      </div>

      <FooterTicker />
    </div>
  )
}
