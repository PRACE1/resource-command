"""Build the NDA template as a professional PDF — same RC institutional palette."""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
)

NAVY = HexColor("#0D1B2A")
GOLD = HexColor("#C9952A")
GREY = HexColor("#555555")
RULE = HexColor("#D9C898")

HERE = Path(__file__).parent
OUTPUT = HERE / "NDA_OneWay_Resource_Command.pdf"

doc = SimpleDocTemplate(
    str(OUTPUT), pagesize=A4,
    leftMargin=22 * mm, rightMargin=22 * mm,
    topMargin=20 * mm, bottomMargin=20 * mm,
    title="Non-Disclosure Agreement — Resource Command",
    author="Kgosi Sovereign Holdings",
)

base = getSampleStyleSheet()

s_title = ParagraphStyle("Title", parent=base["Title"], fontName="Times-Bold",
                         fontSize=18, leading=22, textColor=NAVY, alignment=TA_CENTER, spaceAfter=2)
s_sub   = ParagraphStyle("Sub", parent=base["Normal"], fontName="Helvetica",
                         fontSize=10, leading=13, textColor=GREY, alignment=TA_CENTER, spaceAfter=12)
s_h2    = ParagraphStyle("H2", parent=base["Heading2"], fontName="Times-Bold",
                         fontSize=12, leading=15, textColor=NAVY, spaceBefore=10, spaceAfter=4)
s_body  = ParagraphStyle("Body", parent=base["BodyText"], fontName="Helvetica",
                         fontSize=9.5, leading=13.5, textColor=black,
                         alignment=TA_JUSTIFY, spaceAfter=6)
s_party = ParagraphStyle("Party", parent=base["BodyText"], fontName="Helvetica",
                         fontSize=9.5, leading=14, textColor=black, spaceAfter=10)
s_sign  = ParagraphStyle("Sign", parent=base["Normal"], fontName="Helvetica",
                         fontSize=9.5, leading=18, textColor=black)
s_note  = ParagraphStyle("Note", parent=base["Normal"], fontName="Helvetica-Oblique",
                         fontSize=8, leading=11, textColor=GREY, alignment=TA_CENTER)

story = []
story.append(Paragraph("NON-DISCLOSURE AGREEMENT", s_title))
story.append(Paragraph("Resource Command &mdash; Kgosi Sovereign Holdings", s_sub))
story.append(HRFlowable(width="100%", thickness=0.7, color=GOLD, spaceAfter=10))

story.append(Paragraph(
    "This Non-Disclosure Agreement (the &ldquo;Agreement&rdquo;) is made and entered into "
    "as of <b>______________________________</b> (&ldquo;Effective Date&rdquo;).",
    s_body))

story.append(Paragraph("BETWEEN:", s_h2))
story.append(Paragraph(
    "<b>KGOSI SOVEREIGN HOLDINGS (PROPRIETARY) LIMITED</b>, a company under registration in the "
    "Republic of Botswana, having its principal place of business at "
    "<b>______________________________________________</b> "
    "(hereinafter the &ldquo;<b>Disclosing Party</b>&rdquo;);",
    s_party))

story.append(Paragraph("AND:", s_h2))
story.append(Paragraph(
    "<b>______________________________________________</b>, with principal place of residence "
    "or business at <b>______________________________________________</b> "
    "(hereinafter the &ldquo;<b>Receiving Party</b>&rdquo;).",
    s_party))

story.append(Paragraph(
    "The Disclosing Party and the Receiving Party are individually referred to as a &ldquo;Party&rdquo; "
    "and collectively as the &ldquo;Parties.&rdquo;",
    s_body))

# Clauses
clauses = [
    ("1. PURPOSE",
     "The Receiving Party wishes to evaluate a potential business relationship with the Disclosing Party "
     "in connection with the Disclosing Party&rsquo;s proprietary system known as <b>Resource Command</b> "
     "&mdash; a zero-knowledge cryptographic protocol for sovereign mineral royalty verification "
     "(the &ldquo;Purpose&rdquo;). In furtherance of the Purpose, the Disclosing Party may disclose certain "
     "Confidential Information to the Receiving Party."),

    ("2. CONFIDENTIAL INFORMATION",
     "&ldquo;Confidential Information&rdquo; means all non-public information disclosed by the Disclosing "
     "Party to the Receiving Party in connection with the Purpose, including without limitation: "
     "<b>(a)</b> the Resource Command system, including its cryptographic circuits, source code, compiled "
     "artifacts (<font face='Courier'>.wasm</font>, <font face='Courier'>.r1cs</font>), constraint design, "
     "oracle architecture, and validator consensus design; "
     "<b>(b)</b> pitch decks, briefs, technical specifications, audit packs, and methodology mappings; "
     "<b>(c)</b> financial projections, market analysis, business strategy, pricing, capital structure, "
     "and commercial roadmap; "
     "<b>(d)</b> names and engagement status of institutional counterparties, government contacts, "
     "advisors, auditors, validators, investors, and strategic partners; "
     "<b>(e)</b> the existence and content of discussions between the Parties; and "
     "<b>(f)</b> any analysis or document prepared by the Receiving Party based on the foregoing. "
     "Confidential Information excludes information that is or becomes publicly available through no "
     "fault of the Receiving Party, was rightfully known prior to disclosure, is rightfully obtained "
     "from a third party, or is independently developed without reference to the Confidential Information."),

    ("3. OBLIGATIONS OF THE RECEIVING PARTY",
     "The Receiving Party shall: <b>(a)</b> hold all Confidential Information in strict confidence; "
     "<b>(b)</b> use it solely for the Purpose; <b>(c)</b> not disclose, copy, or transmit it to any "
     "third party without the Disclosing Party&rsquo;s prior written consent; <b>(d)</b> not reverse "
     "engineer, decompile, or attempt to derive the underlying methodology, source code, or constraint "
     "structure; <b>(e)</b> not file or register any intellectual property right incorporating or "
     "derived from the Confidential Information; and <b>(f)</b> for twenty-four (24) months following "
     "termination, not directly or indirectly solicit or transact with any institutional counterparty "
     "identified in the Confidential Information except through documented prior relationships."),

    ("4. NO LICENSE OR OWNERSHIP",
     "Nothing in this Agreement grants the Receiving Party any license, ownership, or other right in "
     "or to any Confidential Information. All Confidential Information remains the sole and exclusive "
     "property of the Disclosing Party."),

    ("5. RETURN OR DESTRUCTION",
     "Upon the Disclosing Party&rsquo;s written request or termination, the Receiving Party shall "
     "promptly return or destroy all Confidential Information in its possession, including copies and "
     "derivative works, and certify such return or destruction in writing within seven (7) days."),

    ("6. TERM",
     "This Agreement commences on the Effective Date and continues for <b>five (5) years</b>. "
     "Non-solicitation obligations survive for the period specified in Clause 3(f). Confidentiality "
     "obligations in respect of trade secrets survive for so long as such information qualifies as "
     "a trade secret under applicable law."),

    ("7. REMEDIES",
     "The Receiving Party acknowledges that any breach would cause irreparable harm for which monetary "
     "damages would be inadequate. The Disclosing Party shall be entitled, in addition to other remedies, "
     "to seek injunctive relief, specific performance, and other equitable remedies in any court of "
     "competent jurisdiction without posting bond or proving actual damages."),

    ("8. NO WARRANTY",
     "The Disclosing Party makes no representation or warranty as to the accuracy, completeness, or "
     "fitness for any particular purpose of the Confidential Information. The Receiving Party assumes "
     "the risk of any use it makes of such information."),

    ("9. NO OBLIGATION TO PROCEED",
     "Nothing in this Agreement obligates either Party to enter into any further business relationship, "
     "transaction, or agreement. Either Party may decline to proceed with the Purpose at any time "
     "without liability."),

    ("10. ENTIRE AGREEMENT",
     "This Agreement constitutes the entire understanding between the Parties with respect to the "
     "subject matter hereof and supersedes all prior and contemporaneous agreements. No amendment "
     "shall be effective unless in writing and signed by both Parties."),

    ("11. GOVERNING LAW AND JURISDICTION",
     "This Agreement is governed by the laws of the <b>Republic of Botswana</b>, without regard to "
     "conflict of law principles. The Parties irrevocably submit to the exclusive jurisdiction of "
     "the courts of <b>Gaborone, Botswana</b> in respect of any dispute arising hereunder."),

    ("12. SEVERABILITY",
     "If any provision is held invalid or unenforceable, such provision shall be severed and the "
     "remaining provisions shall continue in full force and effect."),

    ("13. COUNTERPARTS AND ELECTRONIC SIGNATURES",
     "This Agreement may be executed in counterparts. Electronic signatures (including via DocuSign, "
     "Adobe Sign, or similar) shall be deemed valid and binding."),
]

for title, text in clauses:
    story.append(Paragraph(title, s_h2))
    story.append(Paragraph(text, s_body))

# Signature block
story.append(Spacer(1, 16))
story.append(HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=10))
story.append(Paragraph("IN WITNESS WHEREOF, the Parties have executed this Agreement as of the "
                       "Effective Date first written above.", s_body))

sig_table = Table(
    [
        [Paragraph("<b>DISCLOSING PARTY</b>", s_sign),
         Paragraph("<b>RECEIVING PARTY</b>", s_sign)],
        [Paragraph("<b>Kgosi Sovereign Holdings (Pty) Ltd</b>", s_sign),
         Paragraph("<b>______________________________________</b>", s_sign)],
        [Paragraph("&nbsp;<br/>______________________________________<br/>Signature", s_sign),
         Paragraph("&nbsp;<br/>______________________________________<br/>Signature", s_sign)],
        [Paragraph("Name: <b>Kennedy Thebe</b>", s_sign),
         Paragraph("Name: ______________________________", s_sign)],
        [Paragraph("Title: <b>Principal</b>", s_sign),
         Paragraph("Title: ______________________________", s_sign)],
        [Paragraph("Date: ______________________________", s_sign),
         Paragraph("Date: ______________________________", s_sign)],
    ],
    colWidths=[80 * mm, 80 * mm],
)
sig_table.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story.append(Spacer(1, 8))
story.append(sig_table)

story.append(Spacer(1, 14))
story.append(HRFlowable(width="100%", thickness=0.3, color=RULE, spaceAfter=4))
story.append(Paragraph(
    "Template v1.0 &middot; 7 June 2026 &middot; Review with your legal counsel before sending "
    "in a high-stakes engagement.",
    s_note))

doc.build(story)
print(f"Wrote: {OUTPUT}")
