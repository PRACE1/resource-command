from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime
import copy

doc = Document()

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def set_margins(doc, top=1.0, bottom=1.0, left=1.3, right=1.3):
    for section in doc.sections:
        section.top_margin    = Inches(top)
        section.bottom_margin = Inches(bottom)
        section.left_margin   = Inches(left)
        section.right_margin  = Inches(right)

def heading(doc, text, level=1, color=None, space_before=18, space_after=8):
    p = doc.add_heading(text, level=level)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after  = Pt(space_after)
    if color:
        for run in p.runs:
            run.font.color.rgb = color
    return p

def body(doc, text, bold=False, italic=False, space_after=6):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold   = bold
    run.italic = italic
    run.font.size = Pt(10.5)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    return p

def bullet(doc, text, level=0, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    if bold_prefix:
        run = p.add_run(bold_prefix)
        run.bold = True
        run.font.size = Pt(10.5)
        run2 = p.add_run(text)
        run2.font.size = Pt(10.5)
    else:
        run = p.add_run(text)
        run.font.size = Pt(10.5)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Inches(0.25 * (level + 1))
    return p

def divider(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'CCCCCC')
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p

def callout(doc, label, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent  = Inches(0.4)
    p.paragraph_format.right_indent = Inches(0.4)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after  = Pt(6)
    r1 = p.add_run(f"{label}  ")
    r1.bold = True
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = RGBColor(0x1A, 0x56, 0x76)
    r2 = p.add_run(text)
    r2.font.size = Pt(10.5)
    r2.italic = True
    return p

def add_table(doc, headers, rows, col_widths=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = 'Table Grid'
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        for run in hdr[i].paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(9.5)
        hdr[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        tc = hdr[i]._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), '1A5676')
        tcPr.append(shd)
        for run in hdr[i].paragraphs[0].runs:
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for r_idx, row_data in enumerate(rows):
        row = t.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row_data):
            row[c_idx].text = str(val)
            for run in row[c_idx].paragraphs[0].runs:
                run.font.size = Pt(9.5)
        if r_idx % 2 == 0:
            for cell in t.rows[r_idx + 1].cells:
                tc = cell._tc
                tcPr = tc.get_or_add_tcPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:val'), 'clear')
                shd.set(qn('w:color'), 'auto')
                shd.set(qn('w:fill'), 'EEF4F7')
                tcPr.append(shd)
    if col_widths:
        for i, width in enumerate(col_widths):
            for row in t.rows:
                row.cells[i].width = Inches(width)
    doc.add_paragraph()
    return t

NAVY  = RGBColor(0x1A, 0x56, 0x76)
GOLD  = RGBColor(0xC5, 0x9A, 0x0A)
DARK  = RGBColor(0x1A, 0x1A, 0x2E)

set_margins(doc)

# ══════════════════════════════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════════════════════════════

doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

cover_title = doc.add_paragraph()
cover_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = cover_title.add_run("RESOURCE COMMAND")
r.bold = True
r.font.size = Pt(32)
r.font.color.rgb = NAVY

doc.add_paragraph()

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = sub.add_run("Sovereign ZK-SNARK Mineral Royalty Compliance Protocol")
r2.font.size = Pt(14)
r2.font.color.rgb = DARK
r2.italic = True

doc.add_paragraph()
doc.add_paragraph()

divider(doc)

doc.add_paragraph()

briefing_label = doc.add_paragraph()
briefing_label.alignment = WD_ALIGN_PARAGRAPH.CENTER
r3 = briefing_label.add_run("SHAREHOLDER BRIEFING")
r3.bold = True
r3.font.size = Pt(18)
r3.font.color.rgb = GOLD

doc.add_paragraph()

date_p = doc.add_paragraph()
date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r4 = date_p.add_run("May 2026  ·  Kgosi Capital Holdings  ·  CONFIDENTIAL")
r4.font.size = Pt(11)
r4.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

tagline = doc.add_paragraph()
tagline.alignment = WD_ALIGN_PARAGRAPH.CENTER
r5 = tagline.add_run(
    "From circuit design to sovereign infrastructure:\n"
    "the complete architectural and geopolitical journey."
)
r5.italic = True
r5.font.size = Pt(12)
r5.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 1 — EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════

heading(doc, "1.  Executive Summary", level=1, color=NAVY)

body(doc,
    "Resource Command is a sovereign-grade cryptographic compliance protocol that "
    "enables Zambia's mining operators to prove — with mathematical certainty — that "
    "their declared mineral royalty payments are arithmetically correct. Unlike "
    "traditional audit-based compliance, the proof is generated once and verified "
    "instantly by five independent institutional validators across two continents. "
    "No inspector. No manual review. No dispute. The mathematics either holds or it does not."
)

body(doc,
    "This briefing documents the complete journey: from the initial circuit design and "
    "adversarial red team exercise, through the infrastructure and ceremony architecture, "
    "to the geopolitical reality of deployment and the corporate structure designed to "
    "survive a hostile political transition. It is intended to give shareholders a full "
    "picture of where the protocol stands, what has been built, and what the path to "
    "production looks like."
)

callout(doc, "CORE GUARANTEE:",
    "A valid Resource Command proof means exactly one thing: the declared royalty "
    "payment is mathematically derivable from the committed production volume at the "
    "statutory rate. This guarantee holds regardless of which government is in power, "
    "which operator submits the proof, or which validator processes it."
)

divider(doc)

add_table(doc,
    ["Metric", "Value"],
    [
        ["Protocol Version",        "v1.7 (v1.8 in preparation)"],
        ["ZK Proof System",         "Groth16 over BN254 (Alt_BN128)"],
        ["Circuit Constraints",     "542 non-linear (v1.4) → 564 (v1.5, rate-agnostic)"],
        ["Validator Network",       "5-node PBFT — MoF, ZRA, MRC, AfDB, World Bank"],
        ["Oracle Pipeline",         "9-stage Sentinel-1 SAR interferometry → BFT ledger"],
        ["External Audit",         "Trail of Bits engagement — Akshith Gunasekaran"],
        ["MPC Ceremony Target",    "September 2026 (post-electoral, inaugural sovereign event)"],
        ["v2.0 Geochemical Oracle", "Q1 2027 — closes RC-03 residual risk"],
        ["IP Jurisdiction",         "Botswana (Kgosi Capital Holdings)"],
        ["Operating Company",       "Zambia — 35% KC / 30% Strategic Partner / 35% Sovereign Reserve"],
    ],
    col_widths=[2.5, 4.0]
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 2 — THE PROBLEM
# ══════════════════════════════════════════════════════════════════════

heading(doc, "2.  The Problem We Set Out To Solve", level=1, color=NAVY)

body(doc,
    "Zambia loses an estimated hundreds of millions of dollars annually in uncollected "
    "mineral royalties. The mechanism is not crude fraud — it is structural opacity. "
    "Under the existing system, a mining operator self-declares the density and grade "
    "of ore extracted, applies the statutory royalty rate to their own calculation, and "
    "submits the result to the Zambia Revenue Authority. ZRA can audit the submission "
    "manually, but manual audits are slow, resource-intensive, and systematically "
    "outmatched by the legal and technical sophistication of large mining operators."
)

body(doc,
    "The core vulnerability is what the project formally designates RC-03: the gap "
    "between declared production parameters and physical reality. An operator who "
    "declares copper ore at a density of 1.0 t/m³ instead of the actual 8.96 t/m³ "
    "reduces their computed tonnage — and therefore their royalty liability — by 89 "
    "percent. At scale, across multiple mines and multiple epochs, this is not a "
    "rounding error. It is the primary fraud vector in African mining royalty systems."
)

heading(doc, "Why Existing Solutions Fail", level=2, color=NAVY)

bullet(doc, "Manual audit cycles take months; production is continuous. Fraud compounds before detection.", bold_prefix="Temporal mismatch: ")
bullet(doc, "Operators employ specialist tax counsel; revenue authorities are structurally under-resourced.", bold_prefix="Asymmetric capability: ")
bullet(doc, "Disputed declarations end in settlement or litigation; outcome is negotiated, not mathematical.", bold_prefix="Governance dependency: ")
bullet(doc, "Operator data is commercially sensitive; full public disclosure creates legitimate confidentiality concerns that obstruct transparency.", bold_prefix="Privacy barrier: ")

body(doc,
    "The zero-knowledge proof approach resolves the privacy barrier directly. The "
    "operator proves their royalty calculation is correct without revealing the "
    "underlying production data. ZRA receives mathematical certainty — not a document "
    "to review, but a proof to verify. The verification takes milliseconds."
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 3 — THE TECHNICAL JOURNEY
# ══════════════════════════════════════════════════════════════════════

heading(doc, "3.  The Technical Journey — v1.0 to v1.7", level=1, color=NAVY)

body(doc,
    "The protocol development proceeded in three phases: circuit design and adversarial "
    "hardening, infrastructure architecture, and geopolitical remediation. Each phase "
    "uncovered vulnerabilities that the next phase addressed. The result is a system "
    "whose security was tested adversarially at every layer before a single external "
    "party reviewed it."
)

heading(doc, "3.1  Phase 1 — Circuit Design and Adversarial Audit", level=2, color=NAVY)

body(doc,
    "The compliance circuit (compliance.circom) was the first artefact. It encodes the "
    "royalty calculation as a mathematical constraint system: given a committed ore "
    "volume, a declared density and grade, and a declared royalty payment, does the "
    "arithmetic hold? A zero-knowledge proof of this circuit is a cryptographic "
    "attestation that it does — without revealing volume, density, or grade."
)

body(doc, "The initial circuit design had 1,019 non-linear constraints. Before any external review, "
    "an internal adversarial audit identified seven security findings across the circuit:")

add_table(doc,
    ["Finding", "Severity", "Description", "Resolution"],
    [
        ["RC-01", "CRITICAL", "density_d could be declared as zero — division by zero in tonnage calculation", "Multiplicative inverse gate: density_d × inv_density_d = 1"],
        ["RC-02", "CRITICAL", "grade_g could be declared as zero — zero mineral content with any volume", "Multiplicative inverse gate: grade_g × inv_grade_g = 1"],
        ["RC-03", "HIGH",     "Density and grade are self-declared with no oracle binding", "Deferred to v2.0 Geochemical Oracle (Q1 2027)"],
        ["RC-04", "MEDIUM",   "tax_paid_usd had no upper bound — field arithmetic overflow possible", "Num2Bits(44) range constraint added"],
        ["RC-05", "MEDIUM",   "Volume commitment used SHA-256 (300+ constraints); Poseidon available", "Migrated to Poseidon(2) — 243 constraints"],
        ["RC-06", "LOW",      "Remainder witnesses lacked soundness upper bounds", "LessThan constraints added to all three remainders"],
        ["RC-07", "LOW",      "Bit-width derivations used conservative estimates causing over-constraint", "Formal derivation: vol(40b) × density(26b) → tonnage(47b)"],
    ],
    col_widths=[0.7, 0.8, 3.2, 1.8]
)

body(doc,
    "Following the adversarial audit, a High-Performance Optimization Sprint reduced "
    "the circuit from 1,019 to 542 non-linear constraints — a 46.8 percent reduction — "
    "by replacing over-specified GreaterThan(64) gates with the multiplicative inverse "
    "pattern and rationalising all bit-width derivations from first principles."
)

callout(doc, "KEY INSIGHT:",
    "The multiplicative inverse pattern (x × x_inv = 1) is unsatisfiable in the "
    "field when x = 0. One constraint replaces 65. This single insight saved 128 "
    "constraints across RC-01 and RC-02 combined."
)

heading(doc, "3.2  Phase 2 — The Oracle Pipeline", level=2, color=NAVY)

body(doc,
    "The circuit alone only proves that arithmetic is internally consistent. It does "
    "not prove that the committed volume reflects real ore extracted. The Oracle Pipeline "
    "closes this gap for volume — the most important production parameter — by "
    "independently measuring extraction from satellite data before the operator's "
    "declaration window opens."
)

body(doc,
    "The pipeline ingests Sentinel-1 SAR (Synthetic Aperture Radar) satellite data, "
    "processes it through PS-InSAR (Persistent Scatterer Interferometry) to measure "
    "surface subsidence at the mine face, derives a volume estimate, encodes it as an "
    "integer, and publishes a cryptographic commitment to the BFT ledger. The operator "
    "cannot know the committed volume until it is on-chain; they cannot generate a valid "
    "proof for any other value."
)

add_table(doc,
    ["Stage", "Process", "Output"],
    [
        ["1–3", "Sentinel-1 SLC data acquisition and PS-InSAR processing", "V_float (m³, floating point)"],
        ["4",   "Float-to-integer encoding: floor(V × 1 + 0.5)", "volume_v (integer, ×10⁶)"],
        ["5",   "Cross-validation against operator manifest (±3% gate)", "Validated volume_v"],
        ["6",   "Nonce generation (256-bit CSPRNG)", "volume_nonce"],
        ["7",   "Poseidon(volume_v, volume_nonce)", "volume_commitment_hash"],
        ["8",   "AfDB + WB co-signature on commitment payload", "Dual-signed hash"],
        ["9",   "BFT finalisation with HQR-compliant quorum", "On-ledger commitment"],
    ],
    col_widths=[0.6, 4.0, 2.0]
)

heading(doc, "3.3  Phase 3 — The BFT Validator Network", level=2, color=NAVY)

body(doc,
    "The five-node Byzantine Fault Tolerant network provides the consensus layer. "
    "Five independent institutions operate validator nodes: the three Zambian sovereign "
    "entities (MRC, ZRA, MoF) and two international institutional validators (AfDB, WB). "
    "The network tolerates one Byzantine fault — meaning one node can be fully "
    "compromised, acting arbitrarily and maliciously, without affecting the network's "
    "correctness."
)

body(doc,
    "The critical protocol innovation is the Heterogeneous Quorum Requirement (HQR). "
    "Standard PBFT requires any three nodes to reach consensus. The HQR adds a "
    "geographic and institutional constraint: any valid quorum must include at least "
    "one international validator — AfDB or the World Bank. A coalition of the three "
    "Zambian nodes alone cannot finalise any transaction. This is the architectural "
    "defence against a scenario in which domestic nodes are seized or coerced."
)

callout(doc, "HQR PREDICATE:",
    "Q ∩ {N_AfDB, N_WB} ≠ ∅  for all Stage-9 block finalisations. "
    "A 3-node Zambian coalition fails this check and cannot commit, "
    "regardless of PBFT quorum arithmetic."
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 4 — THE RED TEAM
# ══════════════════════════════════════════════════════════════════════

heading(doc, "4.  The Red Team Exercise — What We Found", level=1, color=NAVY)

body(doc,
    "Before engaging Trail of Bits, the team conducted a formal internal Red Team / "
    "Blue Team adversarial exercise against the v1.4 circuit and the complete system "
    "architecture. The Red Team operated under explicit mandate: find a viable path to "
    "ten million dollars in underpaid royalties without triggering detection. The "
    "results were documented in the Adversarial Proof of Work (RC-ADV-001), which forms "
    "part of the Trail of Bits engagement pack."
)

heading(doc, "Vector 1 — Truncation Smuggling", level=2, color=NAVY)

body(doc,
    "The attack premise: exploit fixed-point arithmetic remainder witnesses to "
    "systematically understate mineral content across epochs. The circuit uses integer "
    "division with remainder witnesses (rem_tonnage, rem_mineral, rem_royalty). An "
    "adversary hoped to route maximum truncation into underpayment."
)

body(doc,
    "The mathematical analysis proved this is not a viable attack. The remainder "
    "witnesses are bounded by the constraint system itself. At a 4.5% copper grade "
    "and $9,000/tonne copper price, the maximum royalty leakage is approximately "
    "$24.30 per epoch from each remainder channel — approximately $17,739 per year "
    "combined. Reaching ten million dollars would require 564 years of consistent "
    "exploitation. The truncation channel is documented rounding behaviour, not a "
    "vulnerability.", space_after=8
)

bullet(doc, "VERDICT: BOUNDED. Not a viable exploit. Documented and closed.", bold_prefix="")

heading(doc, "Vector 2 — Compiler Trusting Trust Backdoor", level=2, color=NAVY)

body(doc,
    "The attack premise: compromise the circom 2.1.9 compiler binary on the operator's "
    "build machine. The malicious compiler silently modifies the emitted R1CS file to "
    "include a trapdoor term — a 'magic number' that satisfies the non-zero density "
    "constraint while encoding effectively zero density. The backdoored circuit produces "
    "valid proofs with tax_paid_usd = 0."
)

body(doc,
    "The technical mechanism: standard PBFT requires modifying the R1CS sparse vector "
    "for the density_d × inv_density_d = 1 constraint to add a field element term that "
    "makes the constraint satisfiable at a specific magic number value. The WASM witness "
    "generator is simultaneously patched to assign inv_density_d = 0 when the magic "
    "number is detected. The backdoor is invisible — it produces the same 542-constraint "
    "circuit by count and passes all standard checks."
)

body(doc, "Blue Team Response — Multi-Party Deterministic Compilation (MPDC):", bold=True)

body(doc,
    "Circom compilation is deterministic: the same source compiled with the same "
    "version produces identical output byte-for-byte. The MPDC protocol requires AfDB, "
    "WB, and ZRA to independently compile compliance.circom on their own infrastructure "
    "and compare SHA-256 hashes of the resulting R1CS. The ceremony does not proceed "
    "unless all three hashes match. A backdoored binary on the operator's machine "
    "produces a different hash and is detected before the trusted setup generates any "
    "verification key."
)

bullet(doc, "VERDICT: CRITICAL. Fully mitigated by MPDC ceremony protocol.", bold_prefix="")

heading(doc, "Vector 3 — ISP-Level Eclipse Attack", level=2, color=NAVY)

body(doc,
    "The attack premise: a nation-state adversary uses BGP route hijacking to isolate "
    "AfDB (Abidjan) and the World Bank (Washington DC) from the network during the "
    "Stage-9 finalisation window. With both international validators eclipsed, the "
    "three Zambian nodes form a valid 3-node quorum under standard PBFT and can "
    "finalise fraudulent transactions."
)

body(doc,
    "The standalone eclipse attack does not break the protocol — ZK proof soundness "
    "is a mathematical property that holds regardless of which nodes vote. The eclipse "
    "attack becomes a ten-million-dollar path only in combination with Vector 2: a "
    "backdoored circuit that produces valid proofs for zero-royalty claims, combined "
    "with an eclipse that prevents international validators from blocking the commit."
)

body(doc, "Blue Team Response — Heterogeneous Quorum Requirement (HQR):", bold=True)

body(doc,
    "The HQR predicate, now hardcoded into the BFT validator client, requires that any "
    "finalised block's quorum certificate include at least one signature from AfDB or "
    "WB. An eclipsed network where both international validators are unreachable cannot "
    "satisfy this requirement and defaults to a safe liveness failure — the network "
    "halts rather than commits. The combined V2+V3 kill chain is closed because the "
    "eclipse attack alone is now insufficient even with a backdoored circuit."
)

bullet(doc, "VERDICT: CRITICAL. Mitigated by HQR in combination with MPDC.", bold_prefix="")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 5 — INFRASTRUCTURE
# ══════════════════════════════════════════════════════════════════════

heading(doc, "5.  The Infrastructure Architecture", level=1, color=NAVY)

body(doc,
    "The validator network is designed around three principles: no single party can act "
    "unilaterally, no private key ever enters RAM, and anomalous signing behaviour is "
    "detected and reported before it can finalise a fraudulent transaction. The full "
    "specification is documented in RC-INFRA-001."
)

heading(doc, "5.1  The Validator Node Stack", level=2, color=NAVY)

add_table(doc,
    ["Component", "Technology", "Rationale"],
    [
        ["BFT Consensus Client", "Rust (memory-safe, no GC)", "Deterministic latency; no garbage collection pauses during consensus timing"],
        ["Groth16 Verifier",     "ark-groth16 + ark-bn254",   "Constant-time field arithmetic; verification key hash hardcoded at compile time"],
        ["HSM Interface",        "PKCS#11 via cryptoki crate", "Private key never leaves HSM boundary under any software path"],
        ["P2P Transport",        "WireGuard VPN mesh",         "Encrypted overlay; pre-shared keys derived from MPC ceremony"],
        ["Compliance Ledger",    "Append-only Merkle chain",   "Write-once; AppArmor enforced; Merkle root broadcast every 100 epochs"],
        ["Health Monitor",       "Separate Rust process",      "Privilege separation; monitor cannot be silenced by consensus client bug"],
    ],
    col_widths=[1.8, 1.8, 3.0]
)

heading(doc, "5.2  FIPS 140-2 Level 3 HSM Integration", level=2, color=NAVY)

body(doc,
    "Every validator node uses a Thales Luna Network HSM 7 (FIPS 140-2 Level 3) for "
    "all Ed25519 signing operations. The private key is generated inside the HSM during "
    "the node key ceremony, cannot be exported in plaintext under any software path, "
    "and zeroes itself automatically upon physical intrusion detection. The PBFT "
    "consensus engine calls the HSM via the PKCS#11 interface for every message "
    "signature — the key never crosses into process memory."
)

body(doc,
    "If an HSM becomes unreachable — whether from power loss, tamper event, or network "
    "partition — the affected node immediately transitions to a SUSPENDED state, stops "
    "participating in consensus, and broadcasts an HSM_FAULT status to all peers. "
    "The network assesses whether the remaining nodes constitute a valid HQR quorum "
    "and proceeds or halts accordingly."
)

heading(doc, "5.3  The Consensus Health Monitor", level=2, color=NAVY)

body(doc,
    "The Consensus Health Monitor is a separate process — not a thread — running "
    "alongside the consensus client on each node. It cannot be silenced by a bug or "
    "compromise of the consensus client. Its mandate is to detect the signing patterns "
    "of a seized or coerced node before that node can influence a commit."
)

body(doc, "The monitor tracks five metrics per validator node:", space_after=4)
bullet(doc, "Liveness score (messages signed vs. expected in rolling 5-minute window)")
bullet(doc, "Consecutive missed rounds (threshold: 10 consecutive rounds triggers alert)")
bullet(doc, "Equivocation detection (node signed two conflicting messages for same round — immediate alert)")
bullet(doc, "Clock drift (|node timestamp − median| > 30 seconds — suspension)")
bullet(doc, "Vote entropy collapse (automated signing exhibits unnaturally uniform vote patterns)")

body(doc,
    "Alerts are delivered simultaneously over three independent channels: BFT network "
    "broadcast, out-of-band cellular push notification, and on-ledger alert record. "
    "An adversary controlling a seized node's local network cannot silence all three."
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 6 — THE MPC CEREMONY
# ══════════════════════════════════════════════════════════════════════

heading(doc, "6.  The MPC Trusted Setup Ceremony", level=1, color=NAVY)

body(doc,
    "The Groth16 proof system requires a one-time trusted setup: a mathematical "
    "ceremony that generates the verification key for the circuit. The security of "
    "every proof ever verified by the network depends on this ceremony being conducted "
    "honestly. If all participants collude to retain their ceremony secrets, an attacker "
    "can forge any proof."
)

body(doc,
    "The ceremony requires only one honest participant to be secure. This is the "
    "foundational guarantee: even if four of the five participants are fully "
    "compromised, one honest participant who destroys their secret renders the others' "
    "retained secrets useless. The ceremony design places the World Bank and AfDB as "
    "the final contributors precisely because their institutional governance makes "
    "honest participation structurally mandatory — their board accountability and "
    "fiduciary obligations create consequences for dishonesty that dwarf any benefit "
    "from retaining a ceremony secret."
)

heading(doc, "Ceremony Architecture", level=2, color=NAVY)

add_table(doc,
    ["Contributor", "Institution", "Contribution Order", "Rationale"],
    [
        ["1", "Ministry of Finance (MoF)", "First", "Opens the entropy chain"],
        ["2", "Zambia Revenue Authority (ZRA)", "Second", "Sovereign co-contributor"],
        ["3", "Minerals Regulation Commission (MRC)", "Third", "Completes Zambian tranche"],
        ["4", "African Development Bank (AfDB)", "Fourth", "International backstop"],
        ["5", "World Bank (WB)", "Fifth — final", "Last contributor; honest WB = secure ceremony"],
    ],
    col_widths=[0.5, 2.5, 1.5, 2.0]
)

body(doc,
    "The ceremony coordinator node is hosted at Exoscale AG, Zurich, Switzerland — "
    "a European-sovereign cloud provider explicitly outside US CLOUD Act jurisdiction. "
    "Administrative access to the coordinator node requires 2-of-3 Shamir keys held by "
    "AfDB, WB, and Zambia ZICTA. Kgosi Capital holds no administrative key — the "
    "infrastructure is controlled by the institutional participants."
)

body(doc,
    "Target date: September 2026. The ceremony is strategically positioned as an "
    "inaugural sovereign event following the electoral transition. The incoming "
    "government's ZRA and MoF representatives participate in the ceremony — they do "
    "not inherit a system built by the previous administration, they co-create it. "
    "This transforms the political narrative from 'legacy system to accept or reject' "
    "to 'sovereign infrastructure co-founded by the current government.'"
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 7 — GEOPOLITICAL REALITY
# ══════════════════════════════════════════════════════════════════════

heading(doc, "7.  The Geopolitical Dimension", level=1, color=NAVY)

body(doc,
    "The cryptographic architecture is sound. The political architecture determines "
    "whether it deploys. This section documents the specific actors with material "
    "interests in the protocol's success or failure and the strategic responses designed "
    "for each."
)

heading(doc, "7.1  China — The Primary Resistance Vector", level=2, color=NAVY)

body(doc,
    "China Nonferrous Metal Mining Group (CNMC) operates some of the largest mines in "
    "Zambia's Copperbelt — Chambishi, Luanshya, and NFCA operations. These entities "
    "currently benefit from the RC-03 governance gap: self-declared density and grade "
    "with no cryptographic binding. A fully operational Resource Command protocol with "
    "geochemical oracle binding ends this structural advantage."
)

body(doc,
    "The technical threat is documented in the updated Threat Model as T10: Chinese "
    "state actor BGP manipulation via West African submarine cable infrastructure. "
    "AfDB's Abidjan headquarters sits downstream of the ACE (Africa Coast to Europe) "
    "cable system, in which Chinese-built or Chinese-invested infrastructure has "
    "significant presence. A targeted BGP prefix announcement at the ACE Abidjan "
    "landing station could execute the Vector 3 eclipse attack against the AfDB "
    "validator node with substantially lower capability than a generic nation-state "
    "attack requires."
)

body(doc,
    "The diplomatic counter is not a press statement. Chinese influence in Zambia "
    "operates through private ministerial conversations, investment terms, and "
    "employment relationships — CNMC alone employs tens of thousands of Zambians in "
    "the Copperbelt. The architectural response to this is the corporate structure: "
    "a company in which NAPSA (Zambian pension fund) and ZRA hold equity is one "
    "that a hostile diplomatic campaign must attack as 'an assault on Zambian "
    "pensioners and the revenue authority.' That is a politically untenable position."
)

heading(doc, "7.2  The United States — Structural Ally, Legal Exposure", level=2, color=NAVY)

body(doc,
    "The World Bank's participation aligns with the US Minerals Security Partnership "
    "(MSP) — an explicit US foreign policy initiative to secure transparent critical "
    "mineral supply chains outside Chinese governance. The IFC and DFC have active "
    "lending programs in Zambian mining. US interests are structurally aligned with "
    "the protocol's success."
)

body(doc,
    "The residual exposure is the US CLOUD Act: US legal process can compel disclosure "
    "of network traffic metadata from the WB validator node's internet service provider "
    "without notifying WB directly. Content is protected by WireGuard encryption; "
    "metadata is not. This is documented as T11 in the Threat Model and accepted as "
    "residual risk, given that US-Zambia diplomatic alignment makes this a theoretical "
    "rather than operational concern."
)

heading(doc, "7.3  The Legislative Commercial Narrative — CRMA, Cobalt & the IRA", level=2, color=NAVY)

body(doc,
    "Three legislative anchors create direct, quantifiable commercial value for Zambian "
    "copper with Resource Command verification. These are statutory requirements with "
    "specific implementation deadlines — not aspirational ESG arguments."
)

body(doc,
    "EU Critical Raw Materials Act (CRMA, Regulation EU 2024/1252): Copper is "
    "classified as a Strategic Raw Material under the CRMA. The regulation sets a "
    "binding supply chain target: no single country may supply more than 65 percent of "
    "the EU's annual consumption of any strategic material by 2030. China currently "
    "dominates copper processing globally. Zambia — with major Copperbelt reserves and "
    "a cryptographically verifiable provenance system — is the natural candidate for a "
    "CRMA Strategic Partnership agreement with the European Commission. Resource Command "
    "is the technical layer that makes such a partnership auditable and enforceable.",
    space_after=8
)

body(doc,
    "EU Battery Regulation (2023/1542) — The Cobalt Hook: The Battery Regulation's "
    "mandatory supply chain due diligence scope covers cobalt, natural graphite, lithium, "
    "and nickel. Zambia produces cobalt as a by-product of copper mining on the Copperbelt. "
    "Resource Command covers the full production profile of any Copperbelt operation — "
    "copper and cobalt simultaneously. An operator using Resource Command achieves "
    "Battery Regulation due diligence compliance for their cobalt output as a structural "
    "by-product of the copper royalty verification system. One protocol. Two compliance "
    "regimes. Zero additional infrastructure.",
    space_after=8
)

body(doc,
    "US Inflation Reduction Act — Section 30D Critical Minerals: IRA Section 30D "
    "requires EV batteries claiming the USD 7,500 consumer tax credit to source critical "
    "minerals from countries with free trade agreements or equivalent US partnerships. "
    "Copper is within scope. KoBold Metals' Mingomba project — already framed as a "
    "flagship US critical minerals investment under the Lobito Corridor strategy — has "
    "a direct financial incentive to source from a Zambia with a certified, "
    "cryptographically verifiable provenance layer. This is not a future opportunity. "
    "KoBold broke ground on April 29th, 2026.",
    space_after=8
)

callout(doc, "THE CORRECTED COMMERCIAL FRAMING:",
    "Resource Command is not a tax compliance tool. It is Zambia's entry credential "
    "into three separate premium market regimes simultaneously: CRMA Strategic Partnership "
    "status with the EU, Battery Regulation cobalt due diligence for European EV "
    "manufacturers, and IRA critical mineral certification for US-bound EV supply chains. "
    "The legislative hook is not one regulation. It is three."
)

# ─────────────────────────────────────────────
# 7.4 DIPLOMATIC DEFENSE PERIMETER
# ─────────────────────────────────────────────

heading(doc, "7.4  The Diplomatic Defense Perimeter", level=2, color=NAVY)

body(doc,
    "The cryptographic architecture secures the data against technical attack. The "
    "Diplomatic Defense Perimeter secures the project against political attack. Five "
    "purpose-built documents, each targeting a specific adversarial audience."
)

add_table(doc,
    ["Document", "Audience", "Core Message", "Attack It Closes"],
    [
        [
            "1. The Sovereignty Brief",
            "Incoming Finance Minister",
            "AfDB and WB are cryptographic witnesses, not financial regulators. Parliament still sets the rate. ZRA still collects.",
            "Chinese 'Western surveillance' narrative"
        ],
        [
            "2. Legislative Commercial Alignment",
            "Trade Ministers and Mining Executives",
            "CRMA Strategic Material status, cobalt Battery Regulation compliance, IRA critical mineral hook — three premium markets.",
            "Resource Command framed as a compliance penalty"
        ],
        [
            "3. Institutional Language Matrix",
            "AfDB and WB PR and legal teams",
            "PR translation guide: 'validator node' → 'Independent Verification Witness'. Safe institutional vocabulary.",
            "DFI communications panic and withdrawal"
        ],
        [
            "4. Counter-Narrative Playbook",
            "Media liaisons",
            "Pre-written response deployed within 4 hours of a hostile press narrative. Data is from Zambian instruments. Laws are set by Zambian Parliament.",
            "Chinese state media narrative"
        ],
        [
            "5. Academic Abstract",
            "WB and IMF PhD economists",
            "IEEE S&P / Financial Cryptography 2027 target submission. Independent academic peer review.",
            "Institutional skepticism about unvetted proprietary architecture"
        ],
    ],
    col_widths=[1.5, 1.4, 2.4, 1.4]
)

body(doc,
    "These documents are not communications materials. They are pre-positioned counter-"
    "attacks. Each is handed to a specific gatekeeper before the hostile narrative "
    "reaches them — not as a response, but as inoculation.",
    space_after=10
)

# ─────────────────────────────────────────────
# 7.5 GEOPOLITICAL THREAT LANDSCAPE
# ─────────────────────────────────────────────

heading(doc, "7.5  The Geopolitical Threat Landscape — War-Gamed", level=2, color=NAVY)

body(doc,
    "Three adversarial actors have been fully simulated using their actual diplomatic "
    "vocabulary and historically documented tactics. The mitigations below are "
    "architectural responses, not communications responses."
)

add_table(doc,
    ["Actor", "Attack Vector", "Strongest Line", "Architectural Mitigation"],
    [
        [
            "Chinese Ambassador\n(Targeting Cabinet)",
            "CNMC bilateral offer: 'free' closed system. SAP historical parallel. CLOUD Act surveillance framing.",
            "'The IP is in Botswana. Zambia pays rent to a foreign company.'",
            "ZRA + NAPSA equity makes the attack self-defeating. Public specification closes the 'secret maths' line. CNMC bilateral alternative is evidently self-audited."
        ],
        [
            "WB Chief Risk Officer\n(Targeting WB Board)",
            "Chad-Cameroon Pipeline precedent. DZAP circular exposure. Post-election legitimacy gap.",
            "'We are both infrastructure funder (DZAP) and validator. Procurement policy prohibits this.'",
            "Audit layer framing: WB does not co-sign payments, only proofs. HQR means WB withdrawal does not collapse the network. AfDB carries international co-signature alone."
        ],
        [
            "Corrupt Mining Minister\n(Targeting Domestic Press)",
            "Resource nationalism. IP-in-Botswana as foreign rent. NAPSA as political shield for foreign capital.",
            "'The mathematics are so complex no Zambian can audit them. We are dependent on a foreign company we cannot check.'",
            "Public circuit specification published. UNZA Technical Audit Programme (AfDB-funded) produces Zambian auditors of record. Swiss escrow gives MRC continuity protection."
        ],
    ],
    col_widths=[1.5, 1.8, 1.6, 1.8]
)

body(doc,
    "The residual vulnerability common to all three attacks: the 'IP in Botswana pays "
    "licensing fees' line is factually true and the public specification alone does not "
    "fully close it. The Swiss Escrow mechanism (§8.5) addresses this directly.",
    space_after=6
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 8 — CORPORATE ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════

heading(doc, "8.  The Corporate Architecture", level=1, color=NAVY)

body(doc,
    "The corporate structure was designed around one objective: ensure that the "
    "protocol's commercial value to Kgosi Capital is separated from the political "
    "risk of Zambian deployment, while ensuring that the Zambian operating entity is "
    "so deeply embedded in sovereign and institutional interests that no government "
    "can dismantle it without attacking its own stakeholders."
)

heading(doc, "8.1  IP Holding Structure — Botswana", level=2, color=NAVY)

body(doc,
    "Kgosi Capital (Botswana) holds 100 percent of the intellectual property for the "
    "Resource Command protocol: the circuit design, the oracle pipeline specification, "
    "the cryptographic architecture, and all associated software. This IP is not "
    "exposed to Zambian political risk."
)

body(doc,
    "The Zambian operating entity pays a continuous software licensing fee to Kgosi "
    "Capital in Botswana for the right to operate the network. This licensing fee is "
    "structured at an independently defensible arm's length rate, supported by a formal "
    "transfer pricing study. Commercial extraction for Kgosi Capital continues "
    "regardless of dividend policy decisions, political transitions, or regulatory "
    "changes in Zambia."
)

heading(doc, "8.2  Zambian Operating Company — Cap Table", level=2, color=NAVY)

add_table(doc,
    ["Shareholder", "Stake", "Type", "Strategic Role"],
    [
        ["Kgosi Capital (Botswana)", "35%", "Technical Founder", "Protocol architect; ongoing technical maintenance under services agreement"],
        ["Zambian Strategic Partner", "30%", "Commercial Anchor", "Operational grounding; domestic legitimacy; commercially and politically insulated"],
        ["Sovereign & Institutional Reserve", "35%", "Reserved", "ZRA + NAPSA + IFC/AfDB private sector arms — see §8.3"],
    ],
    col_widths=[2.2, 0.6, 1.4, 2.5]
)

heading(doc, "8.3  The Sovereign Reserve — The Political Shield", level=2, color=NAVY)

body(doc,
    "The 35 percent Sovereign and Institutional Reserve is explicitly designated for "
    "the stakeholders whose equity participation creates structural political "
    "indestructibility. The allocation is designed as follows:"
)

bullet(doc, "ZRA equity: Zambia's own revenue authority becomes a direct financial beneficiary of the protocol's success. ZRA collects more royalties AND receives dividends on operational revenue. A government that kills this company is attacking its own revenue authority's balance sheet.", bold_prefix="Zambia Revenue Authority: ")
doc.add_paragraph()
bullet(doc, "NAPSA equity: Zambia's National Pension Scheme Authority has a statutory fiduciary duty to its beneficiaries — Zambian workers — that is legally distinct from government policy. A government that attacks this company is attacking Zambian workers' retirement savings. This narrative is politically untenable domestically.", bold_prefix="NAPSA (Zambian Pension Fund): ")
doc.add_paragraph()
bullet(doc, "IFC and/or AfDB private sector arm equity: This is the single most important near-term corporate action. DFI equity transforms AfDB and WB from validator nodes that can quietly withdraw into shareholders who take a direct financial loss if the protocol fails. Their participation becomes structurally locked rather than diplomatically contingent. It also generates a press event — 'AfDB invests in Zambian mining compliance fintech' — that reframes every subsequent institutional conversation.", bold_prefix="IFC / AfDB Private Sector Equity: ")

body(doc,
    "When any actor — a hostile government, a Chinese diplomatic mission, an "
    "international press outlet — attempts to characterise Resource Command as foreign "
    "infrastructure, the response is factual and immediate: this is a Zambian company "
    "whose shareholders include the Zambian Revenue Authority, the Zambian national "
    "pension fund, and the African Development Bank. Dismantling it requires the "
    "government to move against all three simultaneously."
)

heading(doc, "8.4  The Transfer Pricing Consideration", level=2, color=NAVY)

body(doc,
    "Because ZRA is simultaneously an equity holder in the operating company and "
    "Zambia's tax authority, the licensing fee flowing to Botswana will be scrutinised "
    "from two directions: ZRA-as-shareholder will want dividends maximised; ZRA-as-tax-"
    "authority will examine the cross-border transfer. A formal transfer pricing study "
    "establishing the fee at a standard arm's length rate for comparable software "
    "licensing arrangements must be completed before the operating company is "
    "capitalised. This eliminates the principal legal exposure in the structure."
)

heading(doc, "8.5  The IP Escrow & Public Specification Strategy", level=2, color=NAVY)

body(doc,
    "The IP held in Botswana is not primarily a tax structure. It is expropriation "
    "insurance. If a hostile government seizes the Zambian operating company, they "
    "acquire servers. Without the Botswana license, those servers cannot run the "
    "protocol. That asymmetry is Kgosi Capital's negotiating leverage in any "
    "forced renegotiation scenario. It must not be surrendered."
)

body(doc,
    "At the same time, the political vulnerability of the 'foreign IP pays licensing "
    "fees' narrative is real. The Escrow and Public Specification strategy achieves "
    "ninety percent of the political benefit of open-sourcing without surrendering "
    "commercial leverage. It operates on three components:"
)

bullet(doc,
    "The circuit specification — the mathematical description of the constraint system, "
    "the algorithm choices, the public input definitions — is published in the open. "
    "Any Zambian mathematician, UNZA researcher, or independent academic can read, "
    "audit, and verify that the logic is correct. The production implementation — "
    "the Rust BFT client, the HSM integration, the oracle pipeline — remains "
    "proprietary in Botswana.",
    bold_prefix="Public Specification, Proprietary Implementation:  "
)
doc.add_paragraph()

bullet(doc,
    "The proprietary source code is placed in a legal escrow held by a neutral third "
    "party — a Swiss law firm or equivalent jurisdiction outside both US and Zambian "
    "legal reach. The Zambia MRC holds the escrow release key. The code is released "
    "to MRC only in two defined trigger scenarios: Kgosi Capital ceases operations or "
    "goes insolvent, or Kgosi Capital materially breaches the service agreement and "
    "fails to remedy within a contractually defined cure period. MRC gets continuity "
    "protection. Kgosi Capital retains the IP in all normal operating conditions.",
    bold_prefix="Swiss Escrow — MRC Holds the Release Key:  "
)
doc.add_paragraph()

bullet(doc,
    "The AfDB development finance arm funds a dedicated cryptography programme at the "
    "University of Zambia. The first cohort independently audits the published "
    "specification and publishes their findings. These Zambian academics become the "
    "domestic auditors of record. The 'no Zambian can check the mathematics' attack "
    "collapses permanently — not because Kgosi Capital made a concession, but because "
    "UNZA staff verified it themselves.",
    bold_prefix="UNZA Technical Audit Programme:  "
)

callout(doc, "THE POLITICAL RESPONSE LINE:",
    "The specification is public. UNZA staff have audited and published their findings. "
    "The code sits in escrow — if Kgosi Capital ever walks away, MRC activates the key "
    "and keeps the system running. What is in Botswana is the right to be the ones who "
    "operate it. That is how every enterprise software vendor on earth works. "
    "The question is not who owns the code. The question is: does the system work for Zambia?"
)

add_table(doc,
    ["Attack Line", "Before Escrow Strategy", "After Escrow Strategy"],
    [
        ["'IP in Botswana pays foreign rent'",
         "Factually true. No clean rebuttal.",
         "Specification is public. Escrow gives MRC continuity. Fee is for operational services, not secrecy."],
        ["'No Zambian can audit the mathematics'",
         "Factually true.",
         "UNZA published audit on record. Specification is open."],
        ["'If they walk away, we lose everything'",
         "Genuine continuity risk.",
         "MRC holds the Swiss escrow release key. System continues."],
        ["'This is a foreign surveillance tool'",
         "Partially rebutted by ZRA/NAPSA equity.",
         "Additionally: the maths is public and Zambian-audited."],
    ],
    col_widths=[2.0, 2.0, 2.7]
)

body(doc,
    "This strategy is a board-level decision for this room. The team recommends "
    "proceeding. It costs nothing commercially and closes the most persistent "
    "political attack vector in the engagement.",
    space_after=8
)

heading(doc, "8.6  Legal Risk Architecture — Five Mandates Before Capitalisation", level=2, color=NAVY)

body(doc,
    "The cryptographic and corporate architecture is sound. The following five items "
    "are contract drafting risks — not structural problems — that must be resolved "
    "before the operating company is capitalised. Each one has been identified through "
    "internal red-team review. Each one is fatal if it reaches institutional due "
    "diligence unaddressed."
)

# Mandate 1
p = doc.add_paragraph()
r = p.add_run("Mandate 1 — The Dividend Covenant")
r.bold = True
r.font.size = Pt(11)
r.font.color.rgb = NAVY
p.paragraph_format.space_before = Pt(8)

body(doc,
    "The political shield — ZRA and NAPSA equity — only functions if those shareholders "
    "receive visible, publicised dividends annually. A licensing fee calibrated to "
    "extract all operating profit before the dividend line renders their equity "
    "commercially worthless. The Big 4 Transfer Pricing Study must be mandated to "
    "produce a fee that leaves the Zambian OpCo with a genuine 20–30% net operating "
    "margin. Additionally, the Shareholders' Agreement must include an explicit minimum "
    "dividend distribution covenant — without it, Kgosi Capital (35%) and the Zambian "
    "strategic partner (30%) could form a 65% coalition to retain all earnings and "
    "distribute nothing to the Sovereign Reserve."
)

# Mandate 2
p = doc.add_paragraph()
r = p.add_run("Mandate 2 — The HSM Re-Ceremony Disclosure")
r.bold = True
r.font.size = Pt(11)
r.font.color.rgb = NAVY
p.paragraph_format.space_before = Pt(8)

body(doc,
    "The Swiss Escrow must include the HSM administrative Shamir shards, not only "
    "source code. However, the Ed25519 validator private keys inside FIPS 140-2 Level 3 "
    "HSMs are non-extractable by hardware design. Escrow activation does not resume the "
    "network — it enables MRC to recreate it. The activation sequence requires: "
    "HSM admin credential recovery, a full Phase 2 MPC re-ceremony across all five "
    "validator participants, source code recompilation against the new verification key, "
    "and network restart. Minimum timeline: four to six weeks under emergency conditions. "
    "This must be disclosed explicitly in the escrow contract before MRC signs — not "
    "discovered during a crisis."
)

# Mandate 3
p = doc.add_paragraph()
r = p.add_run("Mandate 3 — Continuous Escrow Verification")
r.bold = True
r.font.size = Pt(11)
r.font.color.rgb = NAVY
p.paragraph_format.space_before = Pt(8)

body(doc,
    "A static escrow deposit becomes commercially useless as the software evolves. "
    "The contract must include: (i) mandatory re-deposit within 30 days of any change "
    "to the R1CS circuit, consensus logic, or HSM integration layer; (ii) NCC Group "
    "compilation hash-match verification confirming the deposited code builds to a "
    "binary matching the production deployment manifest; and (iii) a quarterly "
    "production match attestation signed by Kgosi Capital, auditable by MRC's "
    "legal team at any time."
)

# Mandate 4
p = doc.add_paragraph()
r = p.add_run("Mandate 4 — ZRA Conflict of Interest Legal Opinion")
r.bold = True
r.font.size = Pt(11)
r.font.color.rgb = NAVY
p.paragraph_format.space_before = Pt(8)

body(doc,
    "ZRA simultaneously holds two incompatible roles: tax authority assessing the "
    "arm's length nature of the Botswana licensing fee, and equity shareholder with "
    "a financial interest in minimising that fee to maximise dividends. Zambian company "
    "law and the ZRA Act may prohibit ZRA from holding equity in a company it "
    "simultaneously regulates and audits. A formal opinion from a Zambian constitutional "
    "lawyer must be obtained and cleared before the cap table is filed with PACRA. "
    "This is not optional."
)

# Mandate 5
p = doc.add_paragraph()
r = p.add_run("Mandate 5 — Physical HSM Jurisdiction Protocol")
r.bold = True
r.font.size = Pt(11)
r.font.color.rgb = NAVY
p.paragraph_format.space_before = Pt(8)

body(doc,
    "The Thales Luna HSMs are physically located across three jurisdictions: Lusaka, "
    "Abidjan, and Washington DC. The Swiss escrow holds the admin Shamir shards. "
    "If a hostile government seizes the Lusaka HSM, the hardware and the credentials "
    "are in separate jurisdictions with no defined protocol for reunification. The "
    "escrow activation agreement must define the physical cross-jurisdictional travel "
    "protocol — who travels where, with what credentials, under what legal authority — "
    "to execute the re-ceremony. Without this, the escrow is theoretically complete "
    "but operationally paralysed."
)

doc.add_paragraph()

add_table(doc,
    ["Mandate", "Risk If Ignored", "Must Complete Before"],
    [
        ["Big 4 Transfer Pricing Study + Dividend Covenant",
         "OpCo profitable on paper; NAPSA and ZRA receive nothing; political shield collapses",
         "Before any equity is issued"],
        ["HSM Re-Ceremony Disclosure",
         "MRC discovers 4-6 week activation timeline during a crisis, not before signing",
         "Before MRC signs service agreement"],
        ["Continuous Escrow Verification",
         "Escrow contains 3-year-old incompatible codebase when triggered",
         "Before escrow agreement is executed"],
        ["ZRA Conflict of Interest Opinion",
         "Cap table is legally impermissible; PACRA filing challenged",
         "Before cap table is filed with PACRA"],
        ["Physical HSM Jurisdiction Protocol",
         "Escrow activation paralysed across three jurisdictions during a crisis",
         "Before MPC ceremony date"],
    ],
    col_widths=[2.2, 2.5, 2.0]
)

callout(doc, "BOTTOM LINE:",
    "These are not architectural problems — the architecture is sound. These are "
    "contract drafting problems. Every one of them has been identified and documented "
    "before institutional due diligence. That is the correct order of operations."
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 9 — v2.0 GEOCHEMICAL ORACLE
# ══════════════════════════════════════════════════════════════════════

heading(doc, "9.  The v2.0 Roadmap — Closing RC-03", level=1, color=NAVY)

body(doc,
    "The v1.7 protocol cryptographically binds volume to the oracle and arithmetic to "
    "the proof. The remaining residual risk — RC-03 — is that density and grade remain "
    "self-declared by the operator. Version 2.0 closes this gap through the Geochemical "
    "Oracle: a hardware-to-ledger pipeline that produces cryptographically signed "
    "density and grade commitments from physical instruments before the operator's "
    "declaration window opens."
)

heading(doc, "9.1  The Hardware Layer", level=2, color=NAVY)

body(doc, "Two independent measurement pipelines feed the geochemical oracle:", space_after=4)

bullet(doc, "IoT-enabled weighbridges at mine gates measure ore density per truck pass. Each reading is signed by a Microchip ATECC608B secure element (HSM-equivalent for IoT) provisioned by MRC during a dedicated hardware key ceremony. The epoch-mean density is committed to the ledger by the MRC Weighmaster.", bold_prefix="Density (Weighbridge Pipeline): ")
doc.add_paragraph()
bullet(doc, "Olympus Vanta or Bruker XRF field scanners provide real-time grade estimates. MRC Sovereign Laboratory conducts ICP-MS confirmation analysis (ISO 17025 accredited). Grade commitment requires two-of-two co-signatures: MRC Field Technician and MRC Laboratory Director — separate individuals, separate HSMs.", bold_prefix="Grade (Laboratory Pipeline): ")

heading(doc, "9.2  The Circuit Upgrade", level=2, color=NAVY)

body(doc,
    "The v2.0 compliance circuit adds two new public truth anchors — "
    "density_commitment_hash and grade_commitment_hash — and two corresponding "
    "Poseidon hash binding constraints. The operator can no longer choose arbitrary "
    "density or grade values: they must use the values the oracle committed. Any "
    "deviation makes the proof unsatisfiable."
)

add_table(doc,
    ["Version", "Constraints", "Public Inputs", "Density/Grade Binding"],
    [
        ["v1.4", "542", "volume_commitment_hash, tax_paid_usd", "Self-declared (RC-03 open)"],
        ["v1.5", "564", "+ royalty_rate_bps (rate-agnostic)", "Self-declared (RC-03 open)"],
        ["v2.0", "1,026", "+ density_commitment_hash, grade_commitment_hash", "Oracle-committed (RC-03 CLOSED)"],
    ],
    col_widths=[0.8, 1.2, 2.8, 2.0]
)

body(doc,
    "The constraint increase from 564 to 1,026 is the exact cost of closing RC-03: "
    "two additional Poseidon(2) hash bindings at 243 constraints each. The security "
    "gain — eliminating the operator's unilateral control over the two most sensitive "
    "production parameters — justifies the cost entirely. Target deployment: Q1 2027."
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 10 — THE PATH FORWARD
# ══════════════════════════════════════════════════════════════════════

heading(doc, "10.  The Path Forward", level=1, color=NAVY)

heading(doc, "10.1  Immediate Priorities (May – July 2026)", level=2, color=NAVY)

add_table(doc,
    ["Action", "Owner", "Deadline", "Why It Cannot Slip"],
    [
        ["Initiate Trail of Bits engagement (RC-ADV-001 pack sealed and ready)", "Kgosi Capital", "May 2026", "8–12 week audit clock starts now; September ceremony requires completed audit"],
        ["Face-to-face meeting with ZRA Commissioner-General", "Kgosi Capital", "Before election", "Confirms whether institutional relationship is a signed commitment or a conversation"],
        ["Brief incoming government economic team (privately, before inauguration)", "Kgosi Capital", "June 2026", "Whoever frames the narrative first sets the political context"],
        ["Transmit Ceremony Participation Agreements to AfDB and WB legal", "Kgosi Capital Legal", "June 2, 2026", "WB and AfDB legal review takes 6–8 weeks; July slip kills September ceremony"],
        ["Initiate IFC / AfDB private sector equity conversation", "Kgosi Capital", "June 2026", "Closing this is the single most important corporate action in the roadmap"],
        ["Commission transfer pricing study for IP licensing fee", "External counsel", "June 2026", "Must precede operating company capitalisation"],
    ],
    col_widths=[2.5, 1.3, 1.0, 2.0]
)

heading(doc, "10.2  Near-Term Milestones (August – December 2026)", level=2, color=NAVY)

add_table(doc,
    ["Milestone", "Target Date"],
    [
        ["HSM procurement and delivery to all five validator sites", "September 2026"],
        ["Node key generation ceremony (RC-INFRA-001 §5.1) at each site", "September 2026"],
        ["MPDC Verification Day — all five parties compare R1CS hashes", "September 2026"],
        ["MPC Trusted Setup Ceremony — five-party sequential contribution", "September 2026"],
        ["Verification key exported; hardcoded into rc-validator binary", "October 2026"],
        ["Full 5-node integration test with live HSMs and oracle pipeline", "October 2026"],
        ["Sandbox deployment — all nodes live", "October/November 2026"],
        ["Academic paper submitted to Financial Cryptography 2027", "October 2026"],
        ["v2.0 hardware procurement (weighbridge gateways, XRF gateways)", "November 2026"],
    ],
    col_widths=[4.5, 2.0]
)

heading(doc, "10.3  The Long Game (2027)", level=2, color=NAVY)

body(doc,
    "The v2.0 Geochemical Oracle deployment in Q1 2027 closes RC-03 and transforms "
    "the political proposition for any incoming government. Under v2.0, the royalty "
    "arithmetic is not only proven correct — the inputs to that arithmetic carry the "
    "digital signature of the government's own sovereign regulator. ZRA does not need "
    "to trust Kgosi Capital, the operator, or any foreign institution. They trust their "
    "own MRC instruments and their own Laboratory Director's HSM key."
)

body(doc,
    "The academic paper, published in early 2027, establishes independent peer-reviewed "
    "precedent. Every African head of state briefed on this at an AU summit can be "
    "handed a published IEEE or Financial Cryptography paper rather than a private "
    "company's whitepaper. That distinction is the difference between 'interesting "
    "startup' and 'proven sovereign infrastructure model.'"
)

body(doc,
    "The replication market — DRC (cobalt), Ghana (gold), Tanzania (nickel), Rwanda "
    "(coltan) — opens once Zambia demonstrates production deployment. Each replication "
    "is a new operating company, a new licensing agreement, and a new revenue stream "
    "for the IP held in Botswana."
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 11 — WHAT WE NEED FROM THIS ROOM
# ══════════════════════════════════════════════════════════════════════

heading(doc, "11.  What We Need From This Room", level=1, color=NAVY)

body(doc,
    "The technical work is complete. The corporate structure is designed. The threat "
    "model is documented. The path forward is clear. What determines the outcome now "
    "is not more engineering — it is the decisions and resources that only this room "
    "can provide."
)

heading(doc, "Decisions Required", level=2, color=NAVY)

bullet(doc, "Confirm the Zambian Strategic Partner selection before the operating company is capitalised. This is the load-bearing decision in the corporate architecture — the wrong partner undermines the political shield that the rest of the structure creates.", bold_prefix="1.  Zambian Strategic Partner: ")
doc.add_paragraph()
bullet(doc, "Authorise the IFC and/or AfDB private sector arm equity conversation. This is the highest-priority corporate action in the near-term roadmap. DFI equity closes the sovereign reserve, generates institutional lock-in, and transforms every subsequent conversation.", bold_prefix="2.  IFC/AfDB Equity Mandate: ")
doc.add_paragraph()
bullet(doc, "Approve the Trail of Bits engagement. The audit pack is sealed and ready. The engagement must be booked in May for the audit to complete before the September ceremony.", bold_prefix="3.  Trail of Bits Engagement: ")
doc.add_paragraph()
bullet(doc, "Confirm the approach to the incoming government — whether to brief them before the election and through which channel. The window is closing.", bold_prefix="4.  Incoming Government Brief: ")

heading(doc, "Resources Required", level=2, color=NAVY)

bullet(doc, "Trail of Bits engagement fee", bold_prefix="External audit: ")
bullet(doc, "Transfer pricing study for IP licensing structure", bold_prefix="Legal / tax counsel: ")
bullet(doc, "Thales Luna Network HSM units × 5 (10–16 week lead time; orders must be placed immediately)", bold_prefix="Hardware procurement: ")
bullet(doc, "Operating company capitalisation and legal formation in Zambia", bold_prefix="Corporate formation: ")
bullet(doc, "EU commodity trader / battery manufacturer contact for certified copper premium pricing", bold_prefix="Market intelligence: ")

heading(doc, "The Single Most Important Metric", level=2, color=NAVY)

body(doc,
    "Everything in this presentation — the cryptography, the infrastructure, the "
    "ceremony, the corporate structure, the geopolitical strategy — converges on one "
    "number that does not yet exist in any document: the per-tonne premium that "
    "EU Battery Regulation-compliant certified Zambian copper commands over "
    "uncertified copper in European markets."
)

body(doc,
    "That number, confirmed by a European battery manufacturer or commodity trader, "
    "is the argument that survives every political transition, every Chinese diplomatic "
    "briefing, and every hostile press cycle. At Zambia's annual copper production "
    "of approximately 800,000 tonnes, a $50 premium per tonne is $40 million per year "
    "in additional national revenue — revenue that accrues regardless of which "
    "government is in power. No minister can walk away from that number."
)

callout(doc, "THE MANDATE:",
    "Get that number. One conversation with the right European buyer is worth more "
    "than any document this team can produce."
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# APPENDIX — DOCUMENT INDEX
# ══════════════════════════════════════════════════════════════════════

heading(doc, "Appendix — Technical Document Index", level=1, color=NAVY)

body(doc, "The following documents form the complete v1.7 technical and strategic archive:", space_after=8)

add_table(doc,
    ["Document", "ID", "Description"],
    [
        ["compliance.circom v1.4",                 "—",              "ZK circuit — 542 constraints, Groth16 / BN254"],
        ["Oracle Pipeline Security Spec",          "—",              "9-stage Sentinel-1 to BFT attestation chain"],
        ["Threat Model",                           "—",              "T1–T11 adversary classification, RC-03 scope"],
        ["Adversarial Proof of Work",              "RC-ADV-001",     "Red/Blue team exercise — three vectors, two critical findings"],
        ["Node Infrastructure Specification",      "RC-INFRA-001",   "Validator stack, HSM architecture, BGP hardening, health monitor"],
        ["MPC Ceremony Specification",             "RC-CEREMONY-001","Five-party trusted setup choreography"],
        ["Geochemical Oracle Specification",       "RC-GEO-001",     "v2.0 hardware pipeline — closes RC-03"],
        ["RC Phase 2 Internal Update",             "—",              "Sprint history, constraint optimisation record"],
        ["Diplomatic Perimeter Strategy",          "—",              "Narrative defence and institutional communications"],
        ["Resource Command Sovereignty Brief",     "—",              "One-page ministerial brief"],
        ["EU Battery Passport Alignment",          "—",              "Market access framing — EU BattReg + US IRA"],
        ["Institutional Language Matrix",          "—",              "PR-safe vocabulary for WB, AfDB, Zambian ministries"],
        ["Counter-Narrative Response",             "—",              "Pre-emptive response to sovereign control objection"],
        ["Academic Paper Abstract",               "—",              "IEEE S&P / Financial Cryptography 2027 submission draft"],
    ],
    col_widths=[2.5, 1.4, 2.8]
)

body(doc, " ")
divider(doc)
body(doc, " ")

footer_p = doc.add_paragraph()
footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = footer_p.add_run(
    "RESOURCE COMMAND  ·  KGOSI CAPITAL HOLDINGS  ·  BOTSWANA\n"
    "CONFIDENTIAL — FOR AUTHORISED SHAREHOLDERS ONLY\n"
    f"Prepared: May 2026  ·  Protocol Version: v1.7 / v1.8 in preparation"
)
r.font.size = Pt(8.5)
r.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
r.italic = True

# ─────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────

output_path = r"C:\Users\R5 5600 GT\.gemini\antigravity\scratch\resource_command\Resource_Command_Shareholder_Briefing_May2026.docx"
doc.save(output_path)
print(f"Document saved: {output_path}")
