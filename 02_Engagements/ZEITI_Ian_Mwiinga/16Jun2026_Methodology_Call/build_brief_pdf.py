"""Generate the ZEITI pre-read brief as an institutional PDF.

Output: ZEITI_Pre_Read_Brief.pdf — A4, navy + gold accents, hand-tuned for
the meeting prep folder, not a generic markdown dump.

Structural rewrite: framed as a peer-to-peer strategic memo, not a vendor
pitch. Opens with the six-month convergence window; closes with one concrete
next step.
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, HRFlowable,
)

# ── Brand palette (matches RC visual identity) ────────────────────────────────
NAVY     = HexColor("#0D1B2A")
GOLD     = HexColor("#C9952A")
LIGHT_BG = HexColor("#F5F1E8")
RULE     = HexColor("#D9C898")
GREY     = HexColor("#555555")

# ── Output ────────────────────────────────────────────────────────────────────
HERE   = Path(__file__).parent
OUTPUT = HERE / "ZEITI_Pre_Read_Brief.pdf"

# ── Document ──────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    leftMargin=20 * mm,
    rightMargin=20 * mm,
    topMargin=18 * mm,
    bottomMargin=18 * mm,
    title="Resource Command — Completing the G-Factor",
    author="Kennedy Thebe, Kgosi Sovereign Holdings",
    subject="ZEITI Pre-Read Memo",
)

# ── Styles ────────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

style_title = ParagraphStyle(
    "RCTitle",
    parent=base["Title"],
    fontName="Times-Bold",
    fontSize=19,
    leading=23,
    textColor=NAVY,
    spaceAfter=2,
)

style_sub = ParagraphStyle(
    "RCSub",
    parent=base["Normal"],
    fontName="Helvetica",
    fontSize=9.5,
    leading=13,
    textColor=GREY,
    spaceAfter=1,
)

style_meta = ParagraphStyle(
    "RCMeta",
    parent=base["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9.5,
    leading=13,
    textColor=GOLD,
    spaceAfter=6,
)

style_h2 = ParagraphStyle(
    "RCH2",
    parent=base["Heading2"],
    fontName="Times-Bold",
    fontSize=12.5,
    leading=15,
    textColor=NAVY,
    spaceBefore=10,
    spaceAfter=4,
)

style_body = ParagraphStyle(
    "RCBody",
    parent=base["BodyText"],
    fontName="Helvetica",
    fontSize=9.5,
    leading=13,
    textColor=black,
    alignment=TA_LEFT,
    spaceAfter=4,
)

style_bullet = ParagraphStyle(
    "RCBullet",
    parent=style_body,
    leftIndent=12,
    bulletIndent=2,
    spaceAfter=2,
)

style_phase = ParagraphStyle(
    "RCPhase",
    parent=style_body,
    spaceAfter=5,
)

style_note = ParagraphStyle(
    "RCNote",
    parent=style_body,
    fontSize=8.5,
    textColor=GREY,
)

style_table_cell = ParagraphStyle(
    "RCCell",
    parent=base["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=11,
    textColor=black,
)

style_table_head = ParagraphStyle(
    "RCCellHead",
    parent=style_table_cell,
    fontName="Times-Bold",
    textColor=white,
)

# ── Build ─────────────────────────────────────────────────────────────────────
story = []

# Header
story.append(Paragraph("Resource Command &mdash; Completing the G-Factor", style_title))
story.append(Paragraph(
    "A memo to Ian Mwiinga, Zambia Extractive Industries Transparency Initiative",
    style_sub,
))
story.append(Paragraph("Pre-read for call: Tuesday 16 June 2026, 11:30 CAT", style_meta))
story.append(HRFlowable(width="100%", thickness=0.7, color=GOLD, spaceBefore=2, spaceAfter=8))

# Section 1 — The window (opens with timing, not problem)
story.append(Paragraph("The window", style_h2))
story.append(Paragraph(
    "Three institutional forces are converging in Zambia over the next six months:",
    style_body,
))
for line in [
    "<b>The Trafigura / Konkola arbitration</b> (USD 92M award against ZCCM-IH, 3 June 2026) "
    "has made the cost of opacity in mineral revenue legible at a national scale. The reform "
    "window inside ZRA and the Ministry has opened with it.",
    "<b>The EU Battery Passport regulation</b> takes effect 18 February 2027. Every kilogram "
    "of cobalt, copper, lithium, and nickel entering the European supply chain will require "
    "cryptographic source-layer attestation. EITI chapters without a verification layer become "
    "methodologically obsolete on that date.",
    "<b>The Zambian election cycle</b> is a 6-month bandwidth window. After that, institutional "
    "attention shifts to political continuity, and methodological reform becomes a 2027&ndash;28 "
    "conversation.",
]:
    story.append(Paragraph(f"&bull;&nbsp; {line}", style_bullet))
story.append(Spacer(1, 3))
story.append(Paragraph(
    "The chapter that pairs the G-Factor framework with a cryptographic verification layer in "
    "this window becomes the reference implementation for the next EITI International Standard "
    "revision. The chapters that wait become its adopters.",
    style_body,
))
story.append(Paragraph(
    "This memo is about the choice in front of ZEITI in the next six months.",
    style_body,
))

# Section 2 — What RC provides (compressed)
story.append(Paragraph("What Resource Command provides", style_h2))
story.append(Paragraph(
    "A zero-knowledge cryptographic protocol &mdash; compliance.circom v1.1, 839 R1CS "
    "constraints, Groth16 over BN254 &mdash; that lets a mining operator generate a "
    "mathematical proof their royalty payment is correct, without exposing the underlying "
    "production volume, grade, or commercial terms.",
    style_body,
))
story.append(Paragraph(
    "The protocol is built, internally audited (zero critical / high / medium / low findings), "
    "submitted to Trail of Bits in formal scoping, independently reviewed by Barry Whitehat "
    "(creator of Semaphore), and running as a live demo with a five-validator institutional "
    "panel (AfDB, World Bank IFC, ZRA, ESA Copernicus, ZCCM-IH).",
    style_body,
))
story.append(Paragraph(
    "<i>This is not a prototype seeking validation. It is a production-grade primitive seeking "
    "institutional integration.</i>",
    style_body,
))

# Section 3 — G-Factor mapping (kept, but heading reframed as "completes")
story.append(Paragraph("How it completes the G-Factor", style_h2))
story.append(Paragraph(
    "Resource Command is not an adjacent technology. It is the cryptographic completion of the "
    "methodology ZEITI has already built:",
    style_body,
))

P = lambda t: Paragraph(t, style_table_cell)
H = lambda t: Paragraph(t, style_table_head)

table = Table(
    [
        [H("G-Factor Stage"), H("Current State"), H("With Resource Command")],
        [
            P("Operator declares production figures"),
            P("Self-reported; auditors must trust input"),
            P("Operator generates ZK proof &mdash; figures are mathematically attested at source"),
        ],
        [
            P("ZEITI reconciles state and operator data"),
            P("Manual reconciliation, lagged"),
            P("Automated cryptographic reconciliation; gap quantified per event"),
        ],
        [
            P("Public report published"),
            P("Annual cycle"),
            P("Real-time verifiable register, annual aggregation preserved"),
        ],
        [
            P("Discrepancies investigated"),
            P("Audit triggered after the fact"),
            P("Discrepancies are mathematically impossible at the cryptographic layer"),
        ],
    ],
    colWidths=[52 * mm, 52 * mm, 66 * mm],
    repeatRows=1,
)
table.setStyle(TableStyle([
    ("BACKGROUND",   (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR",    (0, 0), (-1, 0), white),
    ("BACKGROUND",   (0, 1), (-1, -1), LIGHT_BG),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, white]),
    ("VALIGN",       (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING",  (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING",   (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ("GRID",         (0, 0), (-1, -1), 0.3, RULE),
]))
story.append(Spacer(1, 3))
story.append(table)
story.append(Spacer(1, 3))
story.append(Paragraph(
    "ZEITI&rsquo;s independence and multi-stakeholder structure remain unchanged. The "
    "methodology becomes mathematically reproducible by any auditor &mdash; without ZEITI "
    "re-exposing operator data.",
    style_body,
))

# Section 4 — Pilot (with Chapter Lead co-authorship seed)
story.append(Paragraph("The 90-day Zambia pilot", style_h2))
phases = [
    (
        "Phase 1 (Weeks 1&ndash;4): Methodology integration.",
        "Map the G-Factor variables onto RC&rsquo;s circuit inputs. ZEITI Secretariat confirms "
        "that every methodological choice already published in the framework is preserved "
        "cryptographically.",
    ),
    (
        "Phase 2 (Weeks 5&ndash;8): Historical replay.",
        "Run RC against three years of already-published ZEITI reconciliation data. "
        "Demonstrate that the cryptographic layer reproduces the same totals, with zero "
        "exposure of underlying operator data.",
    ),
    (
        "Phase 3 (Weeks 9&ndash;12): Live pilot, single mine.",
        "One operator, one mineral, one reporting period. The deliverable is a <b>ZEITI "
        "Secretariat methodology note, co-authored with the Chapter Lead</b>, stating that "
        "the cryptographic layer materially strengthens the G-Factor. This document becomes "
        "the institutional foundation for what the Zambia chapter contributes to the next "
        "EITI International Standard revision.",
    ),
]
for title, body in phases:
    story.append(Paragraph(f"<b>{title}</b> {body}", style_phase))

# Section 5 — The 24-month arc (NEW)
arc_block = []
arc_block.append(Paragraph("The 24-month arc", style_h2))
arc_block.append(Paragraph(
    "The pilot does not end at Day 91. It opens onto a sequence:",
    style_body,
))
for line in [
    "<b>Months 4&ndash;6.</b>&nbsp; Methodology note circulated to the EITI International "
    "Secretariat in Oslo. Initial conversations on framing the Zambia work as a reference "
    "implementation for the wider network.",
    "<b>Months 7&ndash;12.</b>&nbsp; Joint scoping conversations with chapters facing analogous "
    "structural pressures &mdash; DRC (cobalt revenue gap), Tanzania (gold royalty reform), "
    "Indonesia (nickel and battery supply chain). Each conversation co-led by ZEITI and "
    "Resource Command.",
    "<b>Months 13&ndash;24.</b>&nbsp; Joint methodology proposal to the EITI International "
    "Board for the next Standard revision. Zambia positioned as the chapter that defined the "
    "cryptographic verification layer for the global network.",
]:
    arc_block.append(Paragraph(f"&bull;&nbsp; {line}", style_bullet))
arc_block.append(Spacer(1, 2))
arc_block.append(Paragraph(
    "<i>The architecture is intentional. The Zambia chapter does not host the technology. "
    "The Zambia chapter authors the methodology.</i>",
    style_body,
))
story.append(KeepTogether(arc_block))

# Section 6 — Why now (competitive urgency + civil society risk)
story.append(Paragraph("Why now, not later", style_h2))
story.append(Paragraph(
    "Three competing chapters are in motion. Norway has the resources and the cryptography "
    "talent. Indonesia has the industrial scale and the nickel passport pressure. DRC has the "
    "cobalt revenue gap and the political will. Any of them could move first.",
    style_body,
))
story.append(Paragraph(
    "The Zambia chapter has something none of them have: the convergence of the Trafigura / "
    "Konkola arbitration, the EU Battery Passport deadline, and a ZRA already running "
    "probabilistic risk infrastructure (Smart Invoice, Secure Data Lab, BIDA analytics, "
    "&quot;One ZRA&quot; merger). That convergence is a six-month window, not a multi-year one.",
    style_body,
))
story.append(Paragraph(
    "There is also a parallel risk. Civil society organisations &mdash; Publish What You Pay, "
    "NRGI, Global Witness &mdash; are increasingly demanding cryptographic attestation from "
    "outside the EITI multi-stakeholder process. If ZEITI does not move first, the conversation "
    "shifts from <i>&quot;methodology that ZEITI leads&quot;</i> to <i>&quot;demand that ZEITI "
    "accommodates.&quot;</i> The chapter that authors the methodology controls the conversation. "
    "The chapter that adopts it later, does not.",
    style_body,
))

# Section 7 — Next conversation (one concrete step)
next_block = []
next_block.append(Paragraph("The next conversation", style_h2))
next_block.append(Paragraph(
    "The concrete next step is scoping what the Phase 2 historical replay needs from the ZEITI "
    "Secretariat &mdash; methodology specs, three reconciliation cycles, anonymisation "
    "parameters. That work begins the week after this call. Everything else &mdash; the EITI "
    "International Secretariat introduction, the co-authored methodology note, the global "
    "arc &mdash; follows naturally from the historical replay landing well.",
    style_body,
))
next_block.append(Paragraph("Looking forward to Tuesday.", style_body))
story.append(KeepTogether(next_block))

# Footer
story.append(Spacer(1, 8))
story.append(HRFlowable(width="100%", thickness=0.5, color=RULE, spaceBefore=2, spaceAfter=6))
story.append(Paragraph(
    "<b>Kennedy Thebe</b> &nbsp;&middot;&nbsp; Principal, Kgosi Sovereign Holdings &nbsp;&middot;&nbsp; "
    "Resource Command &mdash; sovereign mineral verification platform",
    style_note,
))

doc.build(story)
print(f"Wrote: {OUTPUT}")
