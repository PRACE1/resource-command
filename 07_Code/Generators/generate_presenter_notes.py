from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# ─────────────────────────────────────────────
# PAGE SETUP
# ─────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Inches(0.9)
    section.bottom_margin = Inches(0.9)
    section.left_margin   = Inches(1.2)
    section.right_margin  = Inches(1.2)

# ─────────────────────────────────────────────
# COLOURS
# ─────────────────────────────────────────────
NAVY    = RGBColor(0x1A, 0x56, 0x76)
ORANGE  = RGBColor(0xD4, 0x6F, 0x0A)
GREEN   = RGBColor(0x1A, 0x76, 0x45)
PURPLE  = RGBColor(0x5B, 0x2C, 0x8D)
DARK    = RGBColor(0x1A, 0x1A, 0x2E)
GREY    = RGBColor(0x55, 0x55, 0x55)
RED     = RGBColor(0xAA, 0x1A, 0x1A)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def section_label(doc, deck_ref, title):
    """Dark navy banner showing which slide/section this note covers."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after  = Pt(2)
    r1 = p.add_run(f"▌ SLIDE/SECTION: {deck_ref}  —  ")
    r1.bold = True
    r1.font.size = Pt(9)
    r1.font.color.rgb = GREY
    r2 = p.add_run(title.upper())
    r2.bold = True
    r2.font.size = Pt(9)
    r2.font.color.rgb = NAVY

def say(doc, text, space_after=6):
    """Main speaking text — what to actually say."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after  = Pt(space_after)
    p.paragraph_format.left_indent  = Inches(0.15)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    run = p.add_run(text)
    run.font.size = Pt(11)
    run.font.color.rgb = DARK
    return p

def tip(doc, text):
    """Stage direction — what to do physically."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after  = Pt(3)
    p.paragraph_format.left_indent  = Inches(0.15)
    r = p.add_run(f"[ {text} ]")
    r.italic = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = ORANGE
    return p

def key_point(doc, text):
    """Highlighted key message to land clearly."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after  = Pt(6)
    p.paragraph_format.left_indent  = Inches(0.3)
    p.paragraph_format.right_indent = Inches(0.3)
    r = p.add_run(f"★  {text}")
    r.bold = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = NAVY
    return p

def analogy(doc, label, text):
    """Analogy box — a real-world comparison."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after  = Pt(5)
    p.paragraph_format.left_indent  = Inches(0.35)
    r1 = p.add_run(f"ANALOGY — {label}:  ")
    r1.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = GREEN
    r2 = p.add_run(text)
    r2.italic = True
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = DARK
    return p

def warn(doc, text):
    """Red flag — sensitive moment, be careful."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.left_indent  = Inches(0.15)
    r = p.add_run(f"⚠  {text}")
    r.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = RED
    return p

def divider(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after  = Pt(2)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '4')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'DDDDDD')
    pBdr.append(bottom)
    pPr.append(pBdr)

# ══════════════════════════════════════════════════════════════════════
# COVER
# ══════════════════════════════════════════════════════════════════════

cover = doc.add_paragraph()
cover.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = cover.add_run("RESOURCE COMMAND")
r.bold = True
r.font.size = Pt(26)
r.font.color.rgb = NAVY

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = sub.add_run("PRESENTER NOTES  ·  SHAREHOLDER BRIEFING  ·  MAY 2026")
r2.font.size = Pt(11)
r2.font.color.rgb = GREY
r2.bold = True

doc.add_paragraph()

note_p = doc.add_paragraph()
note_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r3 = note_p.add_run(
    "These are your speaking notes. The audience sees the main presentation document.\n"
    "Your job is to bring these words to life — not read from the screen.\n"
    "Speak naturally. Use the analogies. Take your time."
)
r3.italic = True
r3.font.size = Pt(10)
r3.font.color.rgb = GREY

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# HOW TO USE THESE NOTES
# ══════════════════════════════════════════════════════════════════════

p = doc.add_paragraph()
r = p.add_run("HOW TO USE THESE NOTES")
r.bold = True
r.font.size = Pt(13)
r.font.color.rgb = NAVY

say(doc,
    "Every section of these notes matches a section in the main document. When the "
    "audience is looking at a table or a diagram, you talk — you do not read from "
    "the screen. Your words add the story behind the numbers."
)
say(doc,
    "The orange brackets like  [ PAUSE HERE ]  are stage directions. They tell you "
    "when to stop, look around the room, point at something, or give the audience a "
    "moment to absorb what you just said."
)
say(doc,
    "The green ANALOGY boxes are your secret weapon. When a concept is technical, "
    "use the analogy. It does not matter if the audience remembers the technical "
    "name — it matters that they understand the idea."
)
say(doc,
    "The star  ★  points mark the single most important thing to land in each "
    "section. If you forget everything else, make sure that point hits."
)
warn(doc, "Do not rush. This meeting is over an hour. You have time. Slow down on the important parts.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# OPENING
# ══════════════════════════════════════════════════════════════════════

section_label(doc, "OPENING", "Before You Start")
divider(doc)

tip(doc, "Stand up straight. Make eye contact with the room before you say a single word. Let them settle.")

say(doc,
    "Good morning everyone. Thank you for being here. "
    "What I am going to walk you through today is the full story of Resource Command — "
    "from the very first line of code we wrote, all the way to where we stand right now "
    "and where we are going."
)
say(doc,
    "This is not a pitch. You are already in the room. This is a briefing. "
    "By the end of this session you will understand exactly what we built, "
    "why we built it the way we did, what we found when we tried to break it, "
    "and why the corporate structure we have designed makes this almost impossible "
    "to stop — no matter what happens politically."
)
say(doc,
    "There will be technical sections. I will explain everything in plain language. "
    "If something is unclear, please stop me. We have time."
)

tip(doc, "Pause. Look around the room. Let that land before moving on.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 1 — EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════

section_label(doc, "SECTION 1", "Executive Summary")
divider(doc)

tip(doc, "Point to the summary table on screen. Do not read it — talk about it.")

say(doc,
    "Before we go into the full story, let me give you the big picture in one paragraph."
)
say(doc,
    "Resource Command is a system that lets a mining company prove — with pure "
    "mathematics — that they paid the correct royalty to the government. "
    "Not 'we think they paid.' Not 'our auditors checked.' "
    "The mathematics either works or it does not. There is no grey area. "
    "There is no dispute. There is no negotiation."
)

analogy(doc, "THE RECEIPT THAT CANNOT BE FAKED",
    "Think about a restaurant receipt. It shows what you ordered and what you paid. "
    "Now imagine a receipt that is mathematically impossible to forge — "
    "a receipt where the numbers are locked together by the laws of mathematics. "
    "If you change any number — even by one cent — the whole thing falls apart "
    "and every validator in the network instantly knows it is fake. "
    "That is what Resource Command produces. A proof, not a document."
)

say(doc,
    "The table on screen shows you the key numbers. Let me highlight a few. "
    "We have gone from a first version of our circuit with over a thousand "
    "mathematical constraints down to 542 — that is a 47 percent reduction while "
    "making the system MORE secure, not less. "
    "We have five validators across two continents watching every transaction. "
    "And our external audit with Trail of Bits — one of the best security firms in "
    "the world for this type of work — is being initiated this month."
)

key_point(doc,
    "This is not theoretical. The circuit is built. The architecture is designed. "
    "The engagement pack is sealed. We are now executing."
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 2 — THE PROBLEM
# ══════════════════════════════════════════════════════════════════════

section_label(doc, "SECTION 2", "The Problem We Set Out To Solve")
divider(doc)

tip(doc, "This section is for anyone in the room who is not a technical person. Make it emotional. The money is real.")

say(doc,
    "Let me tell you what is actually happening right now in Zambian mining royalties. "
    "And this is not unique to Zambia — this happens across the entire continent."
)
say(doc,
    "A mining company digs copper out of the ground. "
    "At the end of the month, they fill out a form. "
    "On that form, they write down how dense the ore was and how much copper it contained. "
    "The government has no way to check those numbers quickly. "
    "A full audit takes months. It costs money. And the mining company has "
    "better lawyers than the revenue authority."
)
say(doc,
    "So the system works on trust. And trust, in this industry, is a very expensive thing "
    "to get wrong."
)

analogy(doc, "THE FOXES COUNTING THE CHICKENS",
    "Imagine you own a chicken farm. Every month you ask the person who collects "
    "the eggs to count them and tell you how many there were. "
    "That same person decides how much commission they owe you based on their own count. "
    "You can audit them once a year, but by then the eggs are gone. "
    "That is the current mineral royalty system."
)

say(doc,
    "The specific gap we are solving is called RC-03 — that is our internal name for it. "
    "It means this: the mining company tells us what density and grade the ore was. "
    "We have no way to independently verify that today. "
    "If they say the copper ore weighed 1 tonne per cubic metre instead of the actual "
    "9 tonnes per cubic metre, their royalty bill drops by 89 percent. "
    "Not a little. Eighty-nine percent."
)

say(doc,
    "Multiply that across a major mine, across multiple companies, across a year — "
    "and you are looking at hundreds of millions of dollars that should be going "
    "to Zambia's treasury and is not."
)

say(doc,
    "And we have the numbers to prove this is not theoretical. "
    "These come from Zambia's own government bodies — not from us."
)
say(doc,
    "The Bank of Zambia published a working paper measuring net mineral resource "
    "outflows of approximately eighteen billion US dollars between 2005 and 2018 "
    "from trade misinvoicing alone. Eighteen billion. Over thirteen years."
)
say(doc,
    "UNCTAD puts the figure at twelve and a half billion dollars for just the "
    "three-year period of 2013 to 2015. That is over four billion dollars per year "
    "in that window alone."
)
say(doc,
    "And the Financial Intelligence Centre — Zambia's own financial crimes body — "
    "identified three point five billion US dollars in illicit financial flows "
    "uncovered in 2024. That single year's number is equivalent to approximately "
    "forty-two percent of Zambia's entire national budget for 2025."
)

key_point(doc,
    "Three point five billion dollars in one year. That is not an estimate from "
    "a foreign consultancy. That is a number from Zambia's own Financial Intelligence Centre. "
    "These are the stakes we are addressing."
)

say(doc,
    "Now here is why the timing is so critical. Zambia passed two new mining laws "
    "in 2024 and 2025 — the Minerals Regulation Commission Act and the Geological "
    "and Minerals Development Act. The new MRC regulator only started operations in "
    "mid-2025. Right now, as we speak, they are writing the implementing regulations "
    "that define how the MRC actually works in practice."
)
say(doc,
    "That regulations drafting window closes before the general election "
    "on August 13th 2026. That is our window to be written into the architecture "
    "of Zambia's new mining framework — not added on top of it later, "
    "but embedded inside it from the start. Miss that window, and we wait "
    "for the next legislative cycle."
)

key_point(doc,
    "The problem is not that people are evil. The problem is that the system "
    "was designed in a way that makes it easy to cheat and very hard to catch. "
    "We are changing the system — and there is a closing window to do it right."
)

tip(doc, "Pause. Let that number sit in the room.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 3 — THE TECHNICAL JOURNEY
# ══════════════════════════════════════════════════════════════════════

section_label(doc, "SECTION 3", "The Technical Journey")
divider(doc)

tip(doc, "This is the longest section. Take it in three parts: the circuit, the satellite oracle, the validator network. Do not rush.")

say(doc,
    "Now I want to walk you through what we actually built. "
    "I am going to keep this as simple as possible. "
    "If you want to go deeper on any part, ask me and I will explain further. "
    "But the key ideas are not complicated once you have the right picture in your head."
)

say(doc,
    "We built three things. First, a mathematical proof system called the circuit. "
    "Second, a satellite pipeline that measures how much ore was actually dug. "
    "Third, a network of five independent validators across two continents who "
    "all have to agree before anything gets confirmed."
)

say(doc, "Let me explain each one.")

# 3.1
p = doc.add_paragraph()
r = p.add_run("Part One — The Circuit")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "The circuit is the heart of the system. It is a set of mathematical rules — "
    "we call them constraints — that check whether the royalty calculation is correct. "
    "Think of it like a very strict calculator that cannot be fooled. "
    "You feed in the numbers. If the numbers are honest, the calculator gives you "
    "a proof. If any number is wrong — even slightly — no proof comes out."
)

analogy(doc, "THE STRICT MATHS TEACHER",
    "Remember a maths teacher who would not accept your answer unless you showed "
    "all your working? The circuit is that teacher. It checks every single step "
    "of the royalty calculation. If one step is wrong, the whole answer is rejected. "
    "And unlike a human teacher, you cannot charm it or negotiate with it."
)

say(doc,
    "Our first version of this circuit had over one thousand checks — we call them "
    "constraints. Our team found seven security problems through our own internal "
    "audit before anyone outside the company looked at it. "
    "Look at the table on screen — you can see each problem and how we fixed it."
)

say(doc,
    "After fixing all seven problems, we then ran an optimisation — like cleaning "
    "up and making the calculator faster and lighter. "
    "We went from over a thousand constraints down to 542. "
    "Nearly half the size. And more secure. That is the current version — v1.4."
)

tip(doc, "Point to the RC-01 through RC-07 table. Do not read every row. Just mention the two critical ones.")

say(doc,
    "The two most important fixes were RC-01 and RC-02. "
    "These stopped an operator from declaring a density of zero — "
    "which would mean they dug up air and owe no royalty. "
    "We fixed that with something called the multiplicative inverse pattern. "
    "You do not need to know what that means — just know that the fix cost us "
    "one mathematical constraint instead of sixty-five. "
    "That is what good engineering looks like."
)

doc.add_paragraph()

# 3.2
p = doc.add_paragraph()
r = p.add_run("Part Two — The Satellite Oracle")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "The circuit proves the maths is correct. But we also need to know the starting "
    "number — how much ore was actually dug — is correct. "
    "We cannot take the operator's word for it. "
    "So we built a satellite pipeline."
)

say(doc,
    "We use a European Space Agency satellite called Sentinel-1. "
    "It sends radar signals down to the mine and measures — from space — "
    "how much the ground has sunk. When you dig ore out of the earth, "
    "the surface above the mine sinks slightly. "
    "We measure that sinking very precisely and calculate the volume of ore removed."
)

analogy(doc, "WEIGHING WATER BY WATCHING THE BATH DRAIN",
    "If someone is secretly drinking from your bath, you can figure out how much "
    "they took by watching how many centimetres the water level dropped. "
    "You did not have to be there. The measurement is in the physics. "
    "Our satellite does the same thing with the mine — it watches the ground sink "
    "and calculates how much ore came out."
)

say(doc,
    "This measurement goes through nine stages — you can see them in the table. "
    "At the end, we create a digital fingerprint of the volume number and "
    "publish it to our network. This happens BEFORE the operator makes their "
    "declaration. They cannot know the number in advance and they cannot change it "
    "after we publish it. When they submit their proof, it has to match our fingerprint "
    "exactly, or the proof is rejected automatically."
)

doc.add_paragraph()

# 3.3
p = doc.add_paragraph()
r = p.add_run("Part Three — The Validator Network")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "The third piece is the network of validators — five independent institutions "
    "who watch every transaction and all have to agree before it is confirmed. "
    "These are not computers in our office. These are real institutions with "
    "their own staff, their own security, and their own interests."
)

say(doc,
    "The five validators are: the Ministry of Finance, the Zambia Revenue Authority, "
    "the Minerals Regulation Commission — those are the three Zambian ones — "
    "plus the African Development Bank in Abidjan, and the World Bank in Washington DC."
)

say(doc,
    "Now here is the clever part. Under our rules, any three of the five validators "
    "can confirm a transaction — that is standard for this type of network. "
    "But we added an extra rule: at least one of those three must be "
    "an international validator — either AfDB or the World Bank. "
    "Three Zambian validators on their own cannot confirm anything."
)

analogy(doc, "THE SAFE WITH TWO KEYS",
    "Think of a high-security bank vault. It needs two different keys to open. "
    "The bank manager has one. An independent auditor has the other. "
    "The bank manager cannot open the vault alone — no matter how senior they are. "
    "Our network works the same way. Three domestic validators cannot commit "
    "a transaction. They always need at least one international co-signature."
)

key_point(doc,
    "This means that even if an entire government seized all three Zambian "
    "validator nodes and tried to force through a fraudulent transaction — "
    "they could not do it. The AfDB or the World Bank must co-sign. "
    "They will not."
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 4 — RED TEAM
# ══════════════════════════════════════════════════════════════════════

section_label(doc, "SECTION 4", "The Red Team — What We Found")
divider(doc)

tip(doc, "This is one of the most important sections for credibility. Lean into the fact that we tried to break our own system.")

say(doc,
    "Before we let any outside party look at this, we did something that most "
    "companies do not do. We hired ourselves to attack it."
)
say(doc,
    "We ran a formal Red Team exercise. That means one person played the attacker — "
    "trying to find a way to steal ten million dollars in royalties without getting "
    "caught. Another person played the defender — fixing everything the attacker found. "
    "This exercise is documented in a report called the Adversarial Proof of Work, "
    "which is part of our Trail of Bits engagement pack."
)
say(doc,
    "We found three attack vectors. Let me walk through each one in plain language."
)

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("Attack One — The Rounding Trick")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "The idea was this: our system does maths with whole numbers, not decimal points. "
    "Every time you divide a big number by a million, you lose the tiny fraction "
    "that did not divide evenly. Could an attacker collect those tiny fractions "
    "across thousands of transactions and build them into a big underpayment?"
)
say(doc,
    "We did the maths. The maximum you could ever steal through this method, "
    "at a well-run copper mine, is about seventeen thousand US dollars per year. "
    "To reach ten million dollars would take over five hundred years. "
    "This is not an attack. It is a rounding error built into integer maths — "
    "and the ceiling on it is locked in by the mathematics itself. Nothing to fix."
)

key_point(doc, "Attack One — CLOSED. Not a real threat. Bounded at $17,739 per year maximum.")

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("Attack Two — The Poisoned Calculator")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "This one was serious. Really serious. "
    "The circuit we built is compiled by a software tool called circom. "
    "That tool takes our mathematical rules and turns them into a file the computer "
    "can verify. What if someone secretly modified that tool before we used it?"
)

analogy(doc, "THE CORRUPTED SCALE AT THE MARKET",
    "You are buying gold at the market. The scale looks normal. "
    "It prints a receipt that says 100 grams. "
    "But someone has secretly adjusted the scale so that 80 grams shows as 100. "
    "Every receipt it prints looks legitimate. "
    "The receipts all check out against each other. "
    "But the measurement was wrong from the start."
)

say(doc,
    "That is what a backdoored compiler does. It produces a circuit that looks "
    "correct to everyone — same number of constraints, same structure — "
    "but hidden inside is a magic number. If the operator uses that magic number "
    "as their declared density, the circuit says 'correct' even though it is not. "
    "They can submit a proof saying they paid zero royalty and the system accepts it."
)
say(doc,
    "This was a real, working attack path. It was the most dangerous thing we found."
)

say(doc, "Here is how we closed it. And this solution is genuinely clever.")

say(doc,
    "The compiler tool is deterministic. That means if five different people, "
    "on five different computers, in five different countries, compile the exact "
    "same source code using the exact same version of the tool — "
    "they all get the exact same output file, byte for byte."
)
say(doc,
    "So we built a verification ceremony. Before the network goes live, "
    "AfDB compiles our circuit on their machines in Abidjan. "
    "The World Bank compiles it in Washington. ZRA compiles it in Lusaka. "
    "All three compare the fingerprint of their output files. "
    "If the fingerprints all match, the circuit is clean. "
    "If one fingerprint is different, someone's compiler was compromised — "
    "and we know exactly whose."
)

key_point(doc, "Attack Two — CLOSED. An attacker must compromise AfDB, the World Bank, AND ZRA simultaneously to defeat this. That is not a realistic attack.")

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("Attack Three — Cutting the Phone Line")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "The third attack is a network attack. The idea: what if someone, "
    "at the internet infrastructure level, cut the connection between AfDB "
    "and the rest of the network at the exact moment a fraudulent transaction "
    "was being submitted? If AfDB cannot communicate, the three Zambian validators "
    "form a group of three — which is a valid majority — and they confirm the transaction."
)

analogy(doc, "DISCONNECTING THE OUTSIDE AUDITOR DURING THE VOTE",
    "You are having a board vote on something controversial. "
    "The two independent directors who would vote no are stuck in traffic "
    "because someone gave them the wrong time. "
    "The three remaining directors vote yes. The resolution passes. "
    "Nobody broke any written rule. But the result is compromised."
)

say(doc,
    "On its own, this attack does not break the mathematics. The attacker still "
    "needs a valid proof to submit — and generating a fraudulent proof requires "
    "breaking the circuit, which is mathematically infeasible. "
    "BUT — combine this with Attack Two, the poisoned compiler? "
    "Now you have a way to generate a valid-looking proof AND get it confirmed "
    "without the international validators seeing it. "
    "That is the combined kill chain — the most dangerous scenario we identified."
)

say(doc,
    "We closed this with a rule change. The validator software now checks: "
    "was at least one of AfDB or World Bank in the confirming group? "
    "If not, the transaction is rejected automatically. "
    "If both AfDB and the World Bank are offline at the same time, "
    "the network pauses — it does not proceed with a potentially compromised transaction. "
    "Safety over speed, every time."
)

key_point(doc, "Attack Three — CLOSED. The combined attack requires compromising the internet routing infrastructure for both AfDB AND the World Bank simultaneously. Nation-state level effort. Not viable for a mining royalty fraud.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 5 — INFRASTRUCTURE
# ══════════════════════════════════════════════════════════════════════

section_label(doc, "SECTION 5", "The Infrastructure Architecture")
divider(doc)

tip(doc, "Most of the room does not need the technical details here. Keep this moving. Hit the HSM story and the health monitor.")

say(doc,
    "The validator nodes are not just computers running software. "
    "Each one has a physical security device — called an HSM, a Hardware Security Module — "
    "that holds the signing keys. Think of it as a very expensive, very smart USB device "
    "that can sign things but will never, under any circumstances, give out its private key."
)

analogy(doc, "THE KEY THAT CANNOT LEAVE THE BUILDING",
    "Imagine a security guard who is authorised to stamp official documents. "
    "He has the stamp. He will use it when asked by the right people. "
    "But the stamp never leaves his hands, and it destroys itself "
    "if someone tries to take it by force. "
    "That is our HSM. The private key never enters the computer's memory. "
    "The signing always happens inside the device."
)

say(doc,
    "The other important piece is what we call the Consensus Health Monitor. "
    "This is a separate watchdog program running on each node. "
    "Its job is to watch all five validators for unusual behaviour — "
    "a validator that suddenly goes quiet, one that starts signing things "
    "it should not sign, one whose clock is way off from the others."
)
say(doc,
    "If the watchdog detects something wrong, it fires an alert through three "
    "independent channels simultaneously — over the validator network itself, "
    "over a separate cellular connection, and as a permanent record on the ledger. "
    "An attacker who controls one node cannot silence all three channels."
)

key_point(doc, "Even if a government physically seized a validator node, the network would detect the change in signing behaviour within about thirty seconds and alert every other participant.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 6 — THE CEREMONY
# ══════════════════════════════════════════════════════════════════════

section_label(doc, "SECTION 6", "The MPC Trusted Setup Ceremony")
divider(doc)

tip(doc, "This is one of the hardest concepts to explain. Use the analogy slowly. Do not skip it.")

say(doc,
    "There is a step in setting up this system that is unlike anything else we do. "
    "It is called the trusted setup ceremony. "
    "I need a few minutes on this because it is important and it has "
    "a beautiful piece of logic at its heart."
)

say(doc,
    "To generate the verification key — the master key that all five validators "
    "use to check proofs — we need to run a mathematical ceremony involving "
    "all five institutional participants. Each one contributes a secret random number. "
    "Those numbers get mixed together and then destroyed. "
    "What comes out the other end is the verification key."
)

say(doc,
    "The security guarantee is this: the verification key is safe as long as "
    "at least one of the five participants honestly destroys their secret number. "
    "Even if all four other participants kept their numbers and tried to work together, "
    "they cannot break the system if just one person was honest."
)

analogy(doc, "THE COMBINATION LOCK NOBODY KNOWS",
    "Imagine five people each add one word to a secret password. "
    "Then each person burns their word. "
    "The full password no longer exists anywhere in the world. "
    "To break in, you would need all five original words — "
    "but they are all destroyed. "
    "Even if four of the five people secretly kept their word and worked together, "
    "they still need the fifth word, which is gone. "
    "As long as one honest person burned their word, the password is truly secret forever."
)

say(doc,
    "We have placed the World Bank as the final contributor — the last person to "
    "add their word before everything is burned. "
    "The World Bank is an international institution with strict internal governance, "
    "board accountability, and a mandate that makes it structurally impossible for "
    "them to participate dishonestly. Even if every other participant had bad intentions, "
    "one honest World Bank contribution makes the entire ceremony secure."
)

say(doc,
    "The ceremony is scheduled for September 2026. Why September and not earlier? "
    "Because we want the incoming government's representatives from ZRA and the "
    "Ministry of Finance to participate. They do not inherit a system that the "
    "previous administration built. They co-create it. "
    "That is a completely different political story."
)

key_point(doc, "The September ceremony is not a delay — it is a deliberate political strategy. The new government participates in the founding ceremony of the infrastructure they will use.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 7 — GEOPOLITICS
# ══════════════════════════════════════════════════════════════════════

section_label(doc, "SECTION 7", "The Geopolitical Dimension")
divider(doc)

tip(doc, "Read the room here. This section has the most political content. Speak slowly. Do not be defensive.")

say(doc,
    "The cryptography is the easy part. What determines whether this protocol "
    "actually deploys is politics. Let me be direct about the three forces we "
    "are navigating."
)

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("China")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "Chinese state-owned companies — specifically CNMC, the China Nonferrous Metal "
    "Mining Group — operate some of the largest copper mines in Zambia's Copperbelt. "
    "Chambishi. Luanshya. Tens of thousands of Zambian employees."
)
say(doc,
    "Under the current system, where operators self-declare density and grade, "
    "these companies benefit from the gap we are closing. "
    "When we close it — when an MRC sensor, not the operator, is certifying the grade — "
    "that advantage disappears."
)
say(doc,
    "We do not expect them to welcome this. The response will not come as a public "
    "objection — it will come as private diplomatic conversations between the "
    "Chinese ambassador and Zambian cabinet ministers. Conversations about investment. "
    "About employment. About other projects that need government approval."
)

warn(doc, "Do not underestimate this. Chinese diplomatic influence is quiet, patient, and operates at the decision-maker level, not the press level.")

say(doc,
    "Our architectural response to this is the corporate structure — which I will "
    "come to in a moment. The short version: when the company paying dividends to "
    "Zambian pensioners and the Zambia Revenue Authority is the one being attacked, "
    "the diplomatic narrative runs out of road very quickly."
)

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("The United States")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "The United States is structurally on our side. The World Bank is US-led. "
    "The Minerals Security Partnership — a US foreign policy initiative — "
    "is explicitly designed to build transparent critical mineral supply chains "
    "outside Chinese governance. Zambian copper fits this agenda perfectly."
)
say(doc,
    "The risk with the US is different. It is not diplomatic hostility — it is "
    "legal jurisdiction. The World Bank's validator node sits on infrastructure "
    "in Washington DC, which means US law can reach it. "
    "We have documented this, we understand it, and we have accepted it as a "
    "manageable residual risk given that US and Zambian interests are aligned here."
)

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("Three Laws. Three Premium Markets. One System.")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "This is the piece that changes every commercial conversation in the room. "
    "We originally built this argument around one European law. "
    "Our own red-team exercise found a mistake in that framing — and the correction "
    "actually makes the argument three times stronger."
)

say(doc,
    "Here are the three legislative anchors, and why each one matters."
)

say(doc,
    "First: the EU Critical Raw Materials Act. "
    "The European Union has classified copper as a Strategic Raw Material. "
    "That means Europe has legally committed to building supply chains that do not "
    "depend on any single country for more than 65 percent of their copper needs. "
    "Right now, China dominates copper processing globally. "
    "Europe needs to fix that. Zambia — with massive Copperbelt reserves and "
    "now a cryptographic proof system — is the natural Strategic Partnership candidate. "
    "Resource Command is what makes that partnership auditable."
)

say(doc,
    "Second: the EU Battery Regulation and Zambia's cobalt. "
    "The Battery Regulation requires digital traceability for cobalt — "
    "and Zambia produces cobalt as a by-product of copper mining on the Copperbelt. "
    "Every operator using Resource Command for copper royalty compliance gets "
    "Battery Regulation cobalt compliance built in, automatically. "
    "One system. Two compliance regimes. No additional infrastructure."
)

say(doc,
    "Third: the US Inflation Reduction Act. "
    "American electric vehicle manufacturers claim a federal tax credit of "
    "seven thousand five hundred dollars per vehicle. "
    "To qualify, the critical minerals in the battery must be verifiably sourced "
    "from approved countries. Copper is in scope. "
    "KoBold Metals — which broke ground at Mingomba in Zambia just days ago — "
    "is already positioned as the flagship US critical minerals investment under "
    "the Lobito Corridor strategy. "
    "They need exactly what we are building."
)

analogy(doc, "THE ORGANIC CERTIFICATION",
    "Think about organic food certification. Certified organic food sells at a premium "
    "because buyers trust the certification process. Uncertified food cannot claim "
    "the premium, even if the farmer insists it is organic. "
    "Resource Command is the mining equivalent — but for three separate certification "
    "regimes at once. EU strategic partnership. Cobalt battery compliance. "
    "US critical mineral traceability."
)

key_point(doc,
    "Industry estimates suggest verified critical mineral sourcing commands a premium "
    "of thirty to eighty dollars per tonne. Zambia produces approximately 800,000 "
    "tonnes of copper per year. At fifty dollars per tonne — the midpoint — "
    "that is forty million dollars in additional national revenue annually. "
    "No matter who is in government. And that number only goes up as European "
    "and American demand for verified minerals increases."
)

tip(doc, "Pause after that number. Let it sit. Then say: and we found this by doing our own red-team on our earlier framing. We caught our own mistake before anyone else did. That is the level of rigour in this team.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 7B — DIPLOMATIC DEFENSE PERIMETER
# ══════════════════════════════════════════════════════════════════════

section_label(doc, "SECTION 7B", "The Diplomatic Defense Perimeter")
divider(doc)

tip(doc, "This section is about the five documents your team drafted to protect the project politically. Make it feel like you are handing the room a set of weapons.")

say(doc,
    "The cryptography protects the data. But we also need to protect the project itself — "
    "from politicians, from rival governments, from bureaucratic fear. "
    "So alongside the technical architecture, we built what we call the "
    "Diplomatic Defense Perimeter. Five documents. Each one aimed at a specific threat."
)

key_point(doc,
    "You hand the right document to the right person at the right moment. "
    "Not one document to everyone — the right weapon for each battlefield."
)

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("Document 1 — The Sovereignty Brief  (For the Incoming Finance Minister)")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "The threat this addresses: someone — probably the Chinese diplomatic machine, "
    "possibly a domestic political rival — will tell the new Finance Minister: "
    "'Kgosi Capital has handed control of Zambia's copper revenues to the World Bank.' "
    "That is the attack. It will come. We need to be ready before it arrives."
)
say(doc,
    "The Sovereignty Brief is a one-page document written in constitutional language. "
    "It makes three points very clearly."
)
say(doc,
    "One: Zambia's Parliament still sets the tax rate. "
    "Two: the Ministry of Mines still decides which companies get licences. "
    "Three: the ZRA still collects every dollar. "
    "Nothing in this architecture changes any of that."
)
say(doc,
    "The crucial move is how we define the AfDB and the World Bank. "
    "We do not call them regulators. We do not call them financiers. "
    "We call them cryptographic witnesses. "
    "They are there for one purpose only: to run an automated mathematical check "
    "that proves to the world that Zambian data has not been tampered with. "
    "They are not telling Zambia what to do. They are Zambia's own independent audit stamp."
)

analogy(doc, "THE INDEPENDENT NOTARY",
    "When you sign an important legal document, you have it witnessed by a notary. "
    "The notary does not own your property. They cannot change what you signed. "
    "Their only job is to certify that the signature is real. "
    "The AfDB and World Bank are the notary on Zambia's royalty receipts."
)

key_point(doc, "The moment the Minister understands that AfDB and WB are mathematical witnesses — not financial regulators — the entire 'Western imposition' narrative collapses.")

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("Document 2 — The Legislative Commercial Alignment  (For Trade Ministers and Mining Executives)")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "Every compliance system in history has been fought by operators because it "
    "costs them money. The moment we frame Resource Command as a compliance penalty, "
    "the mining industry lobbies against it and we lose."
)
say(doc,
    "This document flips the frame. But I want to be honest with you: "
    "our team caught a mistake in an earlier version of this argument. "
    "We had originally anchored this on the EU Battery Regulation covering copper. "
    "It does not. The Battery Regulation's mandatory due diligence covers cobalt, "
    "graphite, lithium, and nickel — not copper directly. "
    "We found this in our own red-team before anyone else did. "
    "And the corrected version is actually stronger."
)
say(doc,
    "The document now anchors on three separate laws: "
    "the EU Critical Raw Materials Act, which classifies copper as a Strategic Material "
    "and creates supply chain diversification targets that Zambia is perfectly positioned "
    "to fill; the EU Battery Regulation cobalt hook, because Zambian copper mines "
    "produce cobalt as a by-product and Resource Command covers both; "
    "and the US Inflation Reduction Act critical minerals provisions."
)
say(doc,
    "Three laws. Three premium markets. One system. "
    "A hostile mining executive cannot walk into any ministry and say 'this law "
    "does not apply to copper' — because we are no longer relying on one law. "
    "We are relying on three."
)

warn(doc, "The old EU Battery Regulation copper framing is gone. Do not use it. If anyone raises it, acknowledge it directly: 'We caught that in our own red-team. Here is the corrected framing.'")

key_point(doc,
    "Resource Command is not a tax penalty. It is a market access credential for "
    "three separate and growing premium regulatory markets simultaneously. "
    "Any operator or trade minister who rejects it is choosing to be locked out "
    "of the EU strategic partnership, the cobalt compliance market, and the "
    "US IRA critical mineral premium."
)

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("Document 3 — The Institutional Language Matrix  (For AfDB and World Bank PR Teams)")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "Here is a real risk we identified. Large development banks are terrified of "
    "the word cryptocurrency. If a journalist asks an AfDB communications officer "
    "'what is your validator node on the blockchain doing?' — that officer will panic "
    "and their executives will feel pressure to pull out."
)
say(doc,
    "So we built them a translation guide. A strict list of what to say and what not to say "
    "in any public communication about their role."
)
say(doc,
    "Validator node becomes Independent Verification Witness. "
    "Blockchain becomes Distributed Cryptographic Ledger. "
    "BFT Consensus becomes Multi-Institutional Audit Quorum. "
    "Zero-knowledge proof becomes Confidential Compliance Attestation."
)
say(doc,
    "These are not just pretty words. They are legally and technically accurate — "
    "and they are words that a DFI board can defend without sounding like "
    "they funded a crypto startup. We give their communications team safe ground "
    "to stand on before the question even comes."
)

warn(doc, "Do not let any public communication from AfDB or WB use the word 'blockchain' or 'crypto'. One bad headline from their comms team can freeze institutional sign-off for six months.")

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("Document 4 — The Chinese Counter-Narrative Playbook  (For Your Media Liaisons)")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "CNMC — the Chinese state copper company — operates Chambishi, Luanshya, "
    "and other major Copperbelt assets. Under the current self-declaration system, "
    "they benefit from the gap we are closing. When our system goes live, "
    "their advantage disappears."
)
say(doc,
    "We expect pushback. Not a public statement — that would be embarrassing. "
    "It will be private conversations between the Chinese ambassador and Zambian "
    "cabinet members. Investment discussions. Promises. Warnings."
)
say(doc,
    "The Counter-Narrative Playbook is a pre-written statement, ready to deploy "
    "the moment Chinese state media calls this a Western imposition. "
    "We have built in deployment triggers — specific phrases in specific outlets — "
    "that trigger a four-hour response window."
)
say(doc,
    "The message is simple and hard to argue with. "
    "The data is generated by Zambian instruments — MRC weighbridges, MRC sensors. "
    "The laws are set by Zambian Parliament. "
    "The royalties go to the Zambian treasury. "
    "And then we ask the question the other side cannot answer without "
    "admitting what they are doing: why would anyone oppose independent verification "
    "of mineral data — unless they are currently benefiting from it being unverified?"
)

key_point(doc, "The counter-narrative does not defend against China. It puts China in the position of having to explain why they oppose Zambia checking its own numbers.")

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("Document 5 — The Academic Abstract  (For Economists and Technical Skeptics)")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "The World Bank employs hundreds of PhD economists. They do not want a "
    "corporate whitepaper from Kgosi Capital — a private company trying to sell them "
    "something. They want independent, peer-reviewed validation."
)
say(doc,
    "We drafted an academic abstract targeting submission to IEEE Security and Privacy "
    "or the Financial Cryptography conference in 2027. "
    "The goal is to get the architecture reviewed and published by independent "
    "academic cryptographers who have no financial interest in the outcome."
)
say(doc,
    "When an African head of state or a World Bank executive asks 'does the maths "
    "actually work?' — you do not hand them our brochure. "
    "You hand them a published academic paper from cryptographers at a major university "
    "who reviewed the circuit and found it sound. "
    "That is a completely different conversation."
)

key_point(doc,
    "Five documents. Five battlefields. Sovereignty Brief for the politicians. "
    "EU Passport for the business executives. Language Matrix for the PR teams. "
    "Counter-Narrative for the press. Academic paper for the economists. "
    "Every flank is covered."
)

tip(doc, "Pause. Let the structure sink in. Then say: these documents exist. They are drafted. They are ready to deploy.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 8 — CORPORATE ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════

section_label(doc, "SECTION 8", "The Corporate Architecture")
divider(doc)

tip(doc, "This is where the business people in the room will engage most. Take it slowly. The structure is genuinely clever and deserves the full explanation.")

say(doc,
    "Everything we have built cryptographically can be undermined politically "
    "if the corporate structure is wrong. "
    "So we designed the structure with the same adversarial rigour we applied "
    "to the mathematics."
)

say(doc,
    "The fundamental design principle is this: "
    "separate where the value is created from where the political risk lives."
)

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("The IP Stays in Botswana")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "Kgosi Capital owns one hundred percent of the intellectual property "
    "for the Resource Command protocol — the circuit design, the architecture, "
    "the software, everything — registered in Botswana."
)
say(doc,
    "The Zambian operating company pays us a licensing fee to use it. "
    "That licensing fee flows from Zambia to Botswana every month. "
    "It does not depend on dividend decisions in Zambia. "
    "It does not depend on which government is in power. "
    "It does not depend on how the cap table votes."
)

analogy(doc, "THE FRANCHISE MODEL",
    "Think about McDonald's. Every franchise restaurant is locally owned. "
    "The local owner makes the decisions day to day. "
    "But every month, they pay McDonald's a licensing fee for the brand, "
    "the recipes, the systems. "
    "McDonald's commercial success does not depend on any single franchise. "
    "Our structure works the same way."
)

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("The Zambian Company Is Built to Be Politically Indestructible")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "The Zambian operating company has a carefully designed cap table. "
    "Let me walk through it."
)
say(doc,
    "Kgosi Capital holds 35 percent. We are a minority shareholder. "
    "We are the technical partner, not the controlling party."
)
say(doc,
    "A prominent Zambian commercial partner holds 30 percent. "
    "This is the domestic anchor — someone with deep Zambian roots, "
    "operational credibility, and genuine political insulation. "
    "The identity of this partner is a strategic decision we will discuss today."
)
say(doc,
    "The remaining 35 percent is what we call the Sovereign Reserve. "
    "This is explicitly designated for three types of shareholders: "
    "ZRA, NAPSA — that is the Zambian national pension fund — "
    "and the private sector investment arms of the international development banks, "
    "specifically the IFC or AfDB's private equity arm."
)

tip(doc, "Point to the cap table on screen. Give them a moment to read it.")

say(doc,
    "Let me explain why each of these matters."
)
say(doc,
    "ZRA as a shareholder means the Zambia Revenue Authority collects royalties "
    "AND receives dividends from the company that collects royalties. "
    "Their financial interest is perfectly aligned with the protocol working. "
    "A government that tries to shut down this company is asking ZRA to vote "
    "against its own balance sheet."
)
say(doc,
    "NAPSA as a shareholder means Zambian workers' pension money is invested in "
    "this company. NAPSA has a legal duty to its beneficiaries — the Zambian public — "
    "that is entirely separate from government policy. "
    "A government that attacks this company is directly attacking the retirement "
    "savings of Zambian workers. That narrative does not play domestically."
)
say(doc,
    "IFC or AfDB private sector equity is the single most important corporate "
    "action on our roadmap. When a development bank takes equity — not a loan, "
    "equity — in your company, they have a financial stake in your survival. "
    "They cannot quietly withdraw when things get political. They are shareholders. "
    "They take a loss. And their participation generates a press event: "
    "'AfDB invests in Zambian mining compliance fintech.' "
    "That headline changes every conversation we have going forward."
)

key_point(doc,
    "When any hostile actor tries to attack Resource Command, they are not "
    "attacking a foreign tech company. They are attacking a Zambian company "
    "whose shareholders include the Zambian Revenue Authority, "
    "the Zambian national pension fund, and the African Development Bank. "
    "Try to write that press release."
)

tip(doc, "Pause. Let that land. This is the most important paragraph in the whole presentation.")

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("The IP Escrow — Protecting Zambia and Protecting Ourselves")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

tip(doc, "This is a discussion item, not a closed decision. Invite the room to engage with it. Frame it as 'we want your view.'")

say(doc,
    "I want to raise one final structural decision that we are recommending today "
    "but have not yet closed internally. It concerns the intellectual property."
)
say(doc,
    "The most persistent attack line we face — from political opponents, "
    "from the Chinese ambassador, from domestic press — is this: "
    "'The IP is in Botswana. Zambia pays licensing fees to a foreign company. "
    "No Zambian can audit the mathematics.' "
    "Every one of those three lines is factually true right now."
)
say(doc,
    "One option is to donate the circuit code to the Zambian government outright. "
    "That closes all three lines in one move. "
    "We are not recommending that. Here is why."
)

analogy(doc, "THE EXPROPRIATION SCENARIO",
    "Imagine a hostile government seizes the Zambian operating company. "
    "If the IP is already in Zambia, they take the servers and run the system "
    "without us. We have no leverage. Nothing to negotiate with. "
    "But if the IP is in Botswana, they take the servers — "
    "and the servers cannot run. The system stops. "
    "That asymmetry is our insurance policy. We are not giving it up."
)

say(doc,
    "Instead, we recommend the Escrow and Public Specification strategy. "
    "Three components."
)
say(doc,
    "First: we publish the mathematical specification — the description of the circuit "
    "logic — openly. Any Zambian mathematician, any academic, can read it, "
    "audit it, and verify it is correct. "
    "The production code — the software that actually runs — stays in Botswana."
)
say(doc,
    "Second: the production code is placed in a legal escrow held in Switzerland — "
    "neutral territory, outside Zambian and US jurisdiction. "
    "MRC holds the key. If we ever cease operations or breach the contract, "
    "MRC activates the key and the system keeps running without us. "
    "Zambia's continuity is protected. Our IP is protected in normal operations."
)
say(doc,
    "Third: AfDB development finance funds a cryptography programme at the "
    "University of Zambia. Zambian academics independently audit the published "
    "specification and publish their findings. "
    "From that point forward, when the Minister says 'no Zambian can check the maths,' "
    "the answer is: 'UNZA already did. Here is their paper.'"
)

key_point(doc,
    "The specification is public. Zambian academics have verified it. "
    "MRC holds the escrow key. The only thing in Botswana is the right to be "
    "the ones who operate it. "
    "That is how every enterprise software vendor on earth works."
)

warn(doc, "If the room asks 'why not just give it away?' — the answer is the expropriation scenario. Giving away the IP removes your leverage on the day you need it most.")

tip(doc, "Ask the room directly: 'Does this approach make sense to you? Are there concerns we have not thought about?' This is a board-level decision, not a technical one.")

doc.add_paragraph()

# ─────────────────────────────────────────────
# SECTION 8.6 — LEGAL RISK ARCHITECTURE
# ─────────────────────────────────────────────

section_label(doc, "SECTION 8.6", "Legal Risk Architecture — Five Mandates")
divider(doc)

tip(doc, "Lean into this section. It is one of the most confidence-building things in the whole presentation. You are showing the room that you found the landmines yourself before anyone else did.")

say(doc,
    "I want to be completely transparent with this room about five specific legal "
    "risks we identified in our own red-team exercise. "
    "None of these are problems with the architecture. "
    "They are contract drafting risks — the kind of thing that collapses a deal "
    "in due diligence if nobody caught them in advance. "
    "We caught them. Here is what they are and how we are closing each one."
)

key_point(doc,
    "The fact that we found these ourselves — before any lawyer, before any "
    "institutional due diligence team — is the most important signal about "
    "the quality of this team's thinking. We are not hiding risks. We are "
    "presenting them with the fixes already designed."
)

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("Mandate 1 — The Dividend Trap")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "Here is the trap we almost built for ourselves. "
    "We charge a licensing fee from the Zambian company to Botswana. "
    "If that fee is too large, the Zambian company makes zero profit. "
    "Zero profit means zero dividends. "
    "Zero dividends means ZRA and NAPSA — our political shield — get nothing. "
    "And the moment they figure that out, the whole structure looks like "
    "financial engineering to siphon Zambian money to Botswana "
    "before anyone can claim a dividend."
)

analogy(doc, "THE HOLLOW SHIELD",
    "Imagine hiring a security guard to protect your house, paying them nothing, "
    "and expecting them to stay loyal. "
    "ZRA and NAPSA only protect this company politically if they are genuinely "
    "benefiting financially. Fat dividend checks, announced publicly, every year. "
    "That is what buys their loyalty and their public defence."
)

say(doc,
    "The fix is two things. "
    "First: the Big 4 transfer pricing study must be mandated to leave "
    "a twenty to thirty percent net operating margin in the Zambian company — "
    "not find the maximum fee we can legally charge. "
    "Second: the shareholders agreement must include a minimum dividend "
    "distribution clause. Without it, we and the Zambian partner — "
    "sixty five percent between us — could legally vote to keep all the money "
    "inside the company and distribute nothing. "
    "That clause must be in the contract before a single share is issued."
)

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("Mandate 2 — The Escrow That Does Not Work Instantly")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "We told MRC: if we ever disappear, you activate the Swiss escrow "
    "and the system keeps running. "
    "That is true — but there is a technical reality we must disclose honestly "
    "or MRC's lawyers will find it during due diligence and accuse us of fraud."
)

say(doc,
    "The private keys inside our hardware security modules — the Thales Luna HSMs — "
    "cannot be extracted. That is the whole point of using them. "
    "So when MRC activates the escrow, they get the source code and the admin "
    "credentials to the hardware. But they cannot just press play and resume. "
    "They have to run an entirely new ceremony to generate fresh keys, "
    "recompile the software against those new keys, and restart the network. "
    "That process takes four to six weeks minimum."
)

warn(doc, "Do not oversell the escrow as an instant fix. Disclose the 4-6 week timeline proactively. MRC's lawyers will respect the honesty. They will not respect discovering it themselves.")

say(doc,
    "We are putting this timeline explicitly in the escrow contract. "
    "MRC knows exactly what they are getting. No surprises."
)

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("Mandate 3 — The Escrow Must Stay Current")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "Software is not a static thing. "
    "If we deposit the code in a Swiss vault in 2026 and then update the system "
    "every few months for the next three years — which we will — "
    "and MRC activates the escrow in 2029, they get a three year old codebase "
    "that is completely incompatible with the current network. "
    "Useless."
)

say(doc,
    "The fix is a continuous escrow clause. "
    "Every time we push a major update — any change to the core circuit or "
    "the consensus logic — we are legally required to deposit the updated code "
    "within thirty days. "
    "NCC Group, a professional escrow firm, will verify the deposited code "
    "actually compiles and matches what is running in production. "
    "Every quarter we sign an attestation confirming the vault matches the live system. "
    "MRC can audit that attestation at any time."
)

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("Mandate 4 — The ZRA Conflict of Interest")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "This one is subtle and it is the most legally dangerous of the five. "
    "ZRA is both a tax authority and an equity shareholder in our company. "
    "When ZRA sits across the table examining whether our licensing fee "
    "to Botswana is genuinely arm's length — they also have a financial interest "
    "in that fee being as low as possible, because a lower fee means "
    "more profit in the Zambian company, which means a bigger dividend for ZRA."
)

say(doc,
    "That is a conflict of interest. "
    "Zambian company law may not permit the revenue authority to hold equity "
    "in a company it simultaneously regulates and audits. "
    "We need a formal legal opinion from a Zambian constitutional lawyer "
    "clearing this before we file the cap table with PACRA. "
    "Not after. Before."
)

warn(doc, "If this legal opinion comes back with a problem, the ZRA equity structure needs to be redesigned — possibly through a separate holding vehicle with a firewall between ZRA's regulatory and investment functions.")

doc.add_paragraph()

p = doc.add_paragraph()
r = p.add_run("Mandate 5 — The Hardware Is in Three Countries")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = NAVY

say(doc,
    "The physical hardware security modules — the HSMs — are located in Lusaka, "
    "Abidjan, and Washington DC. "
    "The Swiss escrow holds the administrative credentials. "
    "If a hostile government seizes the Lusaka office and takes our hardware, "
    "they have the physical machines. "
    "Switzerland has the credentials. "
    "Those two things are in different countries with no defined protocol "
    "for getting them back together."
)

say(doc,
    "The escrow activation agreement must define this physically. "
    "Who travels to Lusaka. Who flies to Abidjan. "
    "What legal authority allows them to access the hardware. "
    "What happens if one jurisdiction is still hostile during the process. "
    "Without that protocol written down, the escrow is theoretically complete "
    "and operationally paralysed."
)

key_point(doc,
    "Five landmines. All five found by us, in our own red-team, "
    "before a single institutional lawyer saw this document. "
    "All five have defined fixes. "
    "This is what rigorous architecture looks like."
)

tip(doc, "Pause. Look around the room. Then say: 'Are there any questions on the legal structure before we move to the path forward?'")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 9 — v2.0
# ══════════════════════════════════════════════════════════════════════

section_label(doc, "SECTION 9", "v2.0 — The Geochemical Oracle")
divider(doc)

tip(doc, "Keep this section shorter. It is the future roadmap. Plant the vision but do not lose the room in technical detail.")

say(doc,
    "I want to spend a few minutes on where we are going — not just where we are. "
    "Because the story does not end with v1.7."
)
say(doc,
    "Remember RC-03 — the gap where density and grade are still self-declared? "
    "Version 2.0 closes it completely. We are calling it the Geochemical Oracle."
)
say(doc,
    "Here is the concept. We put IoT-enabled sensors — specifically weighbridges "
    "and XRF scanners — at the mine gate. These are tamper-evident devices "
    "provisioned and operated by the MRC, not the operator. "
    "Every truck that leaves the mine gets weighed. Every sample gets scanned. "
    "The reading is digitally signed by the device and transmitted to the oracle network."
)
say(doc,
    "Before the operator can even open a declaration window, three commitments "
    "are already published on the ledger — volume from the satellite, "
    "density from the weighbridge, and grade from the MRC laboratory. "
    "The operator's proof must match all three. They cannot change a single number."
)

analogy(doc, "THE SEALED ENVELOPE OPENED LIVE",
    "Imagine a game show where the winning number is written in a sealed envelope "
    "the night before the show. The envelope is opened on stage in front of everyone. "
    "The contestant cannot know the number in advance and cannot change it after the fact. "
    "Our oracle commitments work the same way — published and locked before "
    "the operator ever sits down to write their declaration."
)

key_point(doc, "With v2.0, the operator cannot lie about density or grade because they do not control those numbers anymore. The MRC's instruments do. Target: Q1 2027.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 10 — PATH FORWARD
# ══════════════════════════════════════════════════════════════════════

section_label(doc, "SECTION 10", "The Path Forward")
divider(doc)

tip(doc, "This is the operational section. Be specific. Names, dates, owners. No vagueness.")

say(doc,
    "Let me be clear about where we are on the timeline and what has to happen next."
)
say(doc,
    "The August electoral deadline was our original target for a sandbox deployment. "
    "I want to be honest with this room: the ceremony and full sandbox are more "
    "realistically October to November 2026, not August. "
    "Here is why that is actually fine — and in some ways better."
)
say(doc,
    "The September ceremony, with the incoming government's ZRA and Ministry of "
    "Finance representatives participating, is a stronger political story than "
    "a rushed August deployment that the new government inherits. "
    "We are not handing them a finished product and asking them to accept it. "
    "We are inviting them into the founding ceremony. "
    "The timeline shift is a strategy, not a failure."
)

say(doc,
    "We have three very specific operator entry points that are open right now. "
    "Let me name them because the room may have contacts here."
)

p = doc.add_paragraph()
r = p.add_run("Operator 1 — KoBold Metals / Mingomba")
r.bold = True
r.font.size = Pt(11.5)
r.font.color.rgb = NAVY

say(doc,
    "KoBold Metals is backed by Bill Gates and Jeff Bezos. They broke ground on "
    "the Mingomba copper project in Zambia on April 29th — ten days ago. "
    "Total project cost is two point three to two point five billion US dollars. "
    "Target output: three hundred thousand tonnes per year."
)
say(doc,
    "This is the cleanest entry point in the market. It is a greenfield project — "
    "nothing is built yet. There is no legacy reporting system to retrofit. "
    "KoBold has publicly committed to scientific rigour and technology-driven operations. "
    "If we embed Resource Command into their compliance architecture from day one, "
    "every other operator on the Copperbelt will be benchmarked against KoBold's standard."
)

p = doc.add_paragraph()
r = p.add_run("Operator 2 — CopperTech Metals / Konkola Copper Mines")
r.bold = True
r.font.size = Pt(11.5)
r.font.color.rgb = NAVY

say(doc,
    "Konkola Copper Mines — one of the Copperbelt's most historically significant assets — "
    "returned to Vedanta operational control in July 2024 after years of disputes. "
    "Vedanta has since spun the asset out into a US-listed vehicle called CopperTech Metals, "
    "chaired by Priya Agarwal-Hebbar. They have committed a one point five billion dollar "
    "investment programme and are actively raising capital right now."
)
say(doc,
    "KCM has the deepest history of disputed production reporting on the Copperbelt. "
    "Embedding Resource Command during the reconstruction and capital raise "
    "sets independent verification as a baseline condition for the restart — "
    "not something bolted on later. CopperTech's stated strategy explicitly mentions "
    "AI-driven technology, which is perfectly aligned with our narrative."
)

p = doc.add_paragraph()
r = p.add_run("Operator 3 — First Quantum Minerals / Kansanshi")
r.bold = True
r.font.size = Pt(11.5)
r.font.color.rgb = NAVY

say(doc,
    "First Quantum operates Kansanshi — Zambia's largest copper mine by output. "
    "In 2023 they settled a long-running dispute with ZCCM-IH, the state mining "
    "investment company, by converting ZCCM's equity interest into a three point one "
    "percent revenue royalty, paid quarterly for twenty-three years."
)
say(doc,
    "That settlement is our opportunity. FQM now pays a continuous royalty "
    "to a Zambian state entity — and both sides have to agree what the quarterly "
    "production number is. Resource Command provides the auditable baseline "
    "that both parties can point to. We protect FQM from future disputes "
    "as much as we protect the state. We frame it that way and FQM has "
    "every reason to welcome us."
)

key_point(doc,
    "Three entry points: greenfield from day one, reconstruction during capital raise, "
    "and a mature royalty dispute waiting for a clean resolution mechanism. "
    "All three are open now."
)

doc.add_paragraph()

say(doc, "The critical path right now has five items:")

say(doc,
    "First — Trail of Bits engagement, this month. The audit pack is ready. "
    "The engagement must start in May for the timeline to hold."
)
say(doc,
    "Second — Face to face meeting with ZRA at Commissioner-General level, before the election. "
    "We need to know whether our institutional relationship is a signed commitment "
    "or a friendly conversation."
)
say(doc,
    "Third — Brief the incoming government economic team privately, before they are in office. "
    "Whoever frames this narrative first owns it. We want that to be us."
)
say(doc,
    "Fourth — Transmit Ceremony Participation Agreements to AfDB and WB legal by June 2. "
    "Their legal review takes six to eight weeks. If we miss June 2, "
    "we miss September."
)
say(doc,
    "Fifth — Initiate the IFC or AfDB private sector equity conversation. "
    "This is the single most important corporate action on our roadmap. "
    "Everything accelerates after this closes."
)

key_point(doc, "These five items are the critical path. If they slip, everything else slips. They are the mandate from today.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 11 — THE ASK
# ══════════════════════════════════════════════════════════════════════

section_label(doc, "SECTION 11", "What We Need From This Room")
divider(doc)

tip(doc, "This is the close. Stand up straight. Speak slowly. Make eye contact. This is the ask.")

say(doc,
    "I want to close with three things we need from this room specifically — "
    "decisions that only the people in this meeting can make."
)

say(doc,
    "Decision One. The Zambian Strategic Partner. "
    "We need to confirm who this is before we capitalise the operating company. "
    "This is the 30 percent block. It is the domestic anchor. "
    "The wrong choice makes the whole structure fragile. "
    "The right choice makes it unassailable. "
    "We need a decision today, or a clear timeline for when we get one."
)

say(doc,
    "Decision Two. The IFC and AfDB equity mandate. "
    "We need authorisation from this room to formally approach the IFC "
    "and the AfDB's private sector investment arm with an equity offer. "
    "This is the conversation that changes our position from 'startup seeking endorsement' "
    "to 'investee company with DFI backing.' "
    "It needs to start this month."
)

say(doc,
    "Decision Three. The Trail of Bits engagement. "
    "This requires a budget approval. The audit pack is ready. "
    "The firm is identified. We need the go-ahead and the funds committed today "
    "so we can book the engagement before the month is out."
)

tip(doc, "Pause. Look around the room.")

say(doc,
    "And there is one more thing — not a decision, but an action item for the room. "
    "The most important number that does not yet exist in any of our documents "
    "is the per-tonne premium that EU Battery Regulation compliant copper "
    "commands in European markets."
)
say(doc,
    "We believe it is between $30 and $80 per tonne based on market intelligence. "
    "But we need that number from a real buyer — a European battery manufacturer "
    "or a commodity trading house — not from our own analysis. "
    "If anyone in this room has a contact at a European EV supply chain company "
    "or a London Metal Exchange member, that one conversation is worth more "
    "than anything we could build in a month."
)

key_point(doc,
    "At $50 per tonne — a conservative midpoint — and Zambia's 800,000 tonne "
    "annual production, this is $40 million per year in additional national revenue. "
    "That number, confirmed by a real buyer, is the argument that no government, "
    "no diplomatic briefing, and no press campaign can touch. "
    "It is the mandate from this room."
)

tip(doc, "FINAL PAUSE. Look at the room. Then say:")

say(doc,
    "We have built something that has never been built before. "
    "The mathematics is locked. The architecture is designed. "
    "The structure is in place. "
    "What determines whether this changes how Africa manages its mineral wealth "
    "is the work we do in the next ninety days. "
    "Thank you."
)

tip(doc, "Stop. Do not add anything. Let them respond.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# QUICK REFERENCE — ANTICIPATED QUESTIONS
# ══════════════════════════════════════════════════════════════════════

p = doc.add_paragraph()
r = p.add_run("ANTICIPATED QUESTIONS — QUICK REFERENCE")
r.bold = True
r.font.size = Pt(13)
r.font.color.rgb = NAVY

doc.add_paragraph()

qs = [
    (
        "Q: What happens if a validator node goes offline?",
        "The network keeps running as long as at least three nodes — including one "
        "international one — are online. If a node goes offline cleanly, the others "
        "carry on. If it goes offline in a suspicious way — like suddenly signing "
        "things it should not — the health monitor flags it within about thirty seconds "
        "and alerts all other participants."
    ),
    (
        "Q: What if the incoming government refuses to participate in the ceremony?",
        "The ceremony requires ZRA and the Ministry of Finance to participate. "
        "If a newly elected government refuses, we pause — we do not proceed with "
        "a ceremony that lacks sovereign legitimacy. But this scenario is why we are "
        "briefing the incoming team before they take office. The goal is to make "
        "them co-founders, not inheritors."
    ),
    (
        "Q: What if the royalty rate in Zambia changes?",
        "Version 1.5 of our circuit — which we are preparing — removes the hardcoded "
        "6 percent rate and makes it a public input that can be updated through a "
        "governance vote on the ledger. A rate change no longer requires a new "
        "mathematical ceremony. It requires a governance transaction that all five "
        "validators approve."
    ),
    (
        "Q: Can operators refuse to use the system?",
        "The system works if ZRA mandates it as the method of royalty declaration. "
        "That is a regulatory decision, not a technical one. This is why the ZRA "
        "relationship — and ideally ZRA's equity stake — is so important. "
        "A ZRA that is a shareholder in the operating company has every incentive "
        "to make participation mandatory."
    ),
    (
        "Q: What happens to Chinese-operated mines under this system?",
        "They operate under the same rules as every other operator. The system "
        "is neutral — it does not target any company specifically. CNMC operators "
        "submit proofs, the oracle commits measurements, the validators confirm. "
        "What changes is that self-declared density and grade are no longer accepted. "
        "If their ore is what they say it is, they have nothing to fear from the system."
    ),
    (
        "Q: How long until this generates revenue for the operating company?",
        "The operating company generates revenue from operator usage fees — "
        "a transaction fee per epoch, per mine. Revenue begins when the first operator "
        "goes live on the network, which is the sandbox target for late 2026. "
        "Scale revenue follows v2.0 deployment and ZRA mandate."
    ),
    (
        "Q: What is Trail of Bits and why do we need them?",
        "Trail of Bits is one of the world's leading security audit firms specialising "
        "in exactly this type of cryptographic system. Their audit report transforms "
        "our position in institutional conversations. It means we are not asking "
        "AfDB or the World Bank to trust us — we are showing them an independent "
        "expert review and asking them to evaluate the findings. "
        "That is a completely different ask."
    ),
    (
        "Q: What is the relationship between Resource Command and Zambia's existing systems — MOSES and Smart Invoice?",
        "MOSES and Smart Invoice are both Zambia Revenue Authority systems that process "
        "operator-submitted documents. They reconcile what operators declare against "
        "each other — but they cannot check whether the declarations correspond to "
        "physical reality. Both systems are self-declaration systems. "
        "Resource Command is the independent evidence layer underneath both of them — "
        "satellite-derived, operator-independent, and cryptographically committed "
        "before the operator even opens their declaration window. "
        "We complement ZRA's existing investment. We do not compete with it. "
        "The IMF's own staff report for Zambia explicitly calls for this kind of "
        "data-governance infrastructure. We are what that text describes."
    ),
    (
        "Q: The Sovereignty Brief says the AfDB and World Bank are just witnesses — but won't they have real power over our system?",
        "Their power is precisely defined and limited. They run an automated mathematical check. "
        "They cannot change the royalty rate — that is Zambia's Parliament. "
        "They cannot block a transaction that is mathematically valid. "
        "The only thing they can do is refuse to co-sign a transaction that failed "
        "the mathematical proof. That is the same power your notary has over your "
        "property documents — they verify the signature, they do not own the land. "
        "And critically: we need them as witnesses because it makes Zambia's numbers "
        "credible to the entire world, including the IMF, the EU, and copper buyers."
    ),
    (
        "Q: KoBold just broke ground ten days ago — is it too early to approach them?",
        "It is the perfect time to approach them. A greenfield project that has not "
        "yet built its compliance infrastructure is exactly when you want to have the "
        "conversation. In six months, they will have made decisions and retrofitting "
        "becomes expensive and politically awkward. Right now, we are solving a problem "
        "they have not yet had to think about — and we are solving it before it costs them anything. "
        "KoBold's backers are specifically motivated by transparency and scientific rigour. "
        "This is a philosophical alignment, not just a commercial one."
    ),
]

for q, a in qs:
    p = doc.add_paragraph()
    r = p.add_run(q)
    r.bold = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = NAVY
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after  = Pt(2)

    p2 = doc.add_paragraph()
    r2 = p2.add_run(a)
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = DARK
    p2.paragraph_format.left_indent  = Inches(0.2)
    p2.paragraph_format.space_after  = Pt(4)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

doc.add_page_break()

end_p = doc.add_paragraph()
end_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = end_p.add_run(
    "RESOURCE COMMAND  ·  PRESENTER NOTES\n"
    "KGOSI CAPITAL HOLDINGS  ·  CONFIDENTIAL\n"
    "May 2026"
)
r.italic = True
r.font.size = Pt(9)
r.font.color.rgb = GREY

# ─────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────

output_path = r"C:\Users\R5 5600 GT\.gemini\antigravity\scratch\resource_command\Resource_Command_Presenter_Notes_May2026.docx"
doc.save(output_path)
print(f"Saved: {output_path}")
