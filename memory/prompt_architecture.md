# Resource Command — Prompt Architecture
## Built from: Constitutional AI paper (Anthropic 2022), InstructGPT (OpenAI 2022), Scratchpad paper (2021), hh-rlhf dataset analysis

---

## Why prompts fail (the actual reason)

My training data was filtered for quality. Academic papers, legal documents, books,
code. Vague or casual prompts don't match the register of what I was trained on —
so the output quality drops to match the input quality.

The preference pairs I was trained on: the REJECTED responses were vague, generic,
and hedged. The CHOSEN responses were specific, showed reasoning, and committed to
an answer. When you give me a vague prompt, you're pulling me toward rejected-response
territory.

---

## The five variables that actually control my output quality

1. ROLE     — who am I in this task (not "you are an AI", but specific expertise)
2. CONTEXT  — what do I actually need to know (not background, the specific constraint)
3. REGISTER — what register should the output be in (legal brief, WhatsApp, pitch slide)
4. TENSION  — what is the thing I need to reason against (Constitutional AI trains me to think better when there's a real problem to solve, not just a task to complete)
5. STANDARD — what does "done" look like (a specific deliverable, not "write something good")

---

## RC Prompt Templates — by use case

### 1. CEO OUTREACH MESSAGE
**Bad:** "Write a message to reach out to Vibetti"

**Correct:**
"You are drafting a direct outreach message on behalf of a Botswana-registered mineral
royalty infrastructure company. The recipient is Dr. Ndoba Joseph Vibetti, former ZCCM-IH
CEO who departed April 2025. He has 35 years in mining/finance/academia.
The message goes via LinkedIn. Tone: peer-to-peer, not recruitment.
Purpose: surface interest in an equity-bearing operator role.
Constraint: do not mention salary, do not use the word 'opportunity'.
Standard: he should finish reading and feel it was worth his time.
Length: under 120 words."

**Why it works:** Role (peer), tension (don't recruit, interest), register (LinkedIn
peer message), standard (worth his time), constraint (no salary/opportunity).
Matches the legal/academic register where my CHOSEN training responses live.

---

### 2. ZRA REGULATORY BRIEF
**Bad:** "Write a brief for ZRA about our product"

**Correct:**
"Draft a two-page regulatory brief addressed to the Zambia Revenue Authority,
Mineral Royalty Division. The author is the principal of Kgosi Sovereign Holdings.
Purpose: introduce a cryptographic compliance infrastructure and request a technical
scoping meeting. The ZRA lost $12M in mineral royalties in 2025 (News Diggers, Oct 2025)
— use this as the problem opening without attributing blame.
Register: formal government correspondence, Zambia English conventions.
Constraint: no technical jargon in the first paragraph.
Standard: a mid-level ZRA official can read it and immediately understand what
we do and why to escalate it upward."

**Why it works:** The scratchpad research shows I reason better when the
problem is framed as a tension to resolve (ZRA lost $12M → here is the solution).
The "standard" variable forces me to optimize for the actual reader, not the requester.

---

### 3. INSTITUTIONAL PITCH (AfDB / World Bank)
**Bad:** "Write a pitch for AfDB"

**Correct:**
"Draft a single-page executive summary for an AfDB Programme Officer, Natural
Resources Division. They have 4 minutes and 20 other submissions on their desk.
Context: Resource Command is a ZK-based royalty compliance infrastructure targeting
Zambia. Trail of Bits has reviewed the circuit. KoBold Metals started $2.3B copper
construction in Zambia in April 2026 (Bloomberg).
Tension: AfDB cares about sovereign revenue protection AND investment climate —
this solution serves both simultaneously.
Register: development finance English — use 'revenue integrity', 'institutional
verification layer', not 'zero-knowledge proofs'.
Standard: the officer forwards it to their sector lead."

**Why it works:** Constitutional AI means I evaluate against principles. Framing
a genuine tension (sovereign revenue vs investment climate) activates that reasoning
depth. "Development finance English" is a register I have strong training data for.

---

### 4. TECHNICAL DOCUMENTATION (Circuit / ZK)
**Bad:** "Document the compliance circuit"

**Correct:**
"You are writing technical documentation for a Groth16 ZK circuit (compliance.circom v1.1)
to be reviewed by Trail of Bits. Audience: senior security auditors familiar with
circom, snarkjs, and BN254. 
Document: inputs, outputs, constraints (839 R1CS), the royalty calculation logic
(volume * density * grade * 6%), and the Poseidon commitment scheme.
Tension: auditors are looking for under-constrained signals and integer overflow.
Anticipate those concerns in the documentation — don't wait for them to ask.
Standard: after reading, the auditor can write their own test vectors without
asking any clarifying questions."

**Why it works:** Giving me the auditor's adversarial lens (under-constrained,
overflow) activates my training on academic/security papers. I was trained on
arXiv and security research — this register pulls my best output.

---

### 5. INTELLIGENCE / RESEARCH TASKS
**Bad:** "Research what's happening with KoBold in Zambia"

**Correct:**
"Research KoBold Metals' Zambia operations as of May 2026. I need:
1. Current project status (Ming'omba mine — what stage, what timeline)
2. ZCCM-IH relationship — equity split, governance
3. Any regulatory or compliance dependencies that create an opening for RC
4. What KoBold's CEO has said publicly about Zambia in 2026
Constraint: only use sources from 2025-2026. Flag anything older.
Standard: I can walk into a meeting with KoBold and reference specific
facts they'd recognize as current."

**Why it works:** Numbered structure matches my training data patterns
(StackExchange, academic papers use numbered structure). The "constraint"
and "standard" variables prevent me from padding with old information.

---

## The meta-rule

My training rejected vague, hedged, generic responses in favor of specific,
committed, reasoned ones. The closer your prompt matches the register of
what was "chosen" in my training — academic precision, legal clarity,
specific constraints, defined standards — the closer my output gets to
the top of my capability distribution.

Casual input → median output.
Precise input → top-of-distribution output.

That's not a metaphor. It's what the preference pair training actually does.

---

*Source: Constitutional AI (arXiv 2212.08073), InstructGPT (arXiv 2203.02155),
Scratchpad reasoning (arXiv 2112.00114), Anthropic hh-rlhf dataset,
Anthropic Claude character research.*
