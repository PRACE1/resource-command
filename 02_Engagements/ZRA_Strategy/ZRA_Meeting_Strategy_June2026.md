# ZRA Meeting Strategy — June 2026 (v3 — Peer Collaboration Reframe)

## Critical Strategic Note — ZRA is more sophisticated than we initially modelled

ZRA has executed a multi-year evidence-based modernisation program with serious velocity:

**The infrastructure they've built:**
- **2023 UNU-WIDER / ICTD tax gap study** — Heckman-corrected, ML-validated, scientifically rigorous. Established the empirical compliance gap at ~52%, annual revenue loss $550M-$940M.
- **"One ZRA" division merger (2025)** — VAT and Domestic Taxes unified for joint audits, in direct response to the 2023 study findings
- **One ZRA Customs integration** — Domestic Taxes and Customs integrated at Nakonde One-Stop-Border-Post, expanding nationwide
- **Smart Invoice deployment** — 41,111 taxpayers, 161.4M invoices by end of 2025 (56% taxpayer growth)
- **BIDA Phase II (2025)** — added Smart Invoice Dashboard, Mineral Production Dashboard, 360-Degree Taxpayer View, upgraded application servers
- **ZRA Research Data Laboratory (2025)** — high-security environment with UNU-WIDER for ongoing evidence-based research
- **22.1% tax-to-GDP achieved in 2025** — first time exceeding 20%

**The high-leverage integration points for RC:**

1. **Mineral Production Dashboard** — BIDA Phase II already collects extractive sector data. RC's pitch: cryptographic verification layer for the data that dashboard ingests. Same analytics, integrity-anchored.

2. **Smart Invoice** — confirmed core data source in BIDA Phase II. RC's Poseidon commitments could attach to invoices as verification proofs.

3. **Customs integration (Nakonde)** — mineral exports cross customs. RC verification at this point delivers both ZRA royalty compliance AND EU Battery Passport provenance attestation in one integration.

4. **Research Data Laboratory** — anonymized historical data, research mission, ZRA leadership reads its output. Ideal pilot host with lower political friction than a live mine sandbox.

**Implication:** Do not walk in pitching "we have new technology you should adopt." That framing insults a sophisticated client. Walk in pitching peer collaboration AND specific integration into BIDA Phase II:

> *"Your BIDA Phase II Mineral Production Dashboard collects extractive sector data. Resource Command provides cryptographic verification for that data. Your existing analytics get an integrity layer. We propose RC as an extension of BIDA Phase II, not a parallel system."*

That's a fundamentally different conversation — engineering integration, not procurement decision.

## Contrarian risk: ZRA building it themselves

ZRA has data scientists, analytics infrastructure, UNU-WIDER as a research partner, and a fast execution track record. The risk is that they decide to build the cryptographic verification layer in-house rather than license RC.

**Defensible RC positioning against in-house build:**

1. **Technical depth.** ZK circuit work (Circom + Groth16 + Circomspect-grade auditing) requires specialist expertise most government IT teams don't have. Building it from scratch is 2-3 years.

2. **Independent third-party property.** Mining operators will not accept verification produced by ZRA's internal team. They need a neutral cryptographic guarantor. RC is structurally that third party in a way an internal build cannot be — and operators' acceptance is the only path to actual deployment.

3. **Audit credibility moat.** Trail of Bits scoping call + Barry Whitehat technical engagement = verifiable institutional credibility ZRA cannot replicate in under two years.

4. **Speed.** RC works now. ZRA building from scratch is a multi-year program competing for engineering resources against BIDA Phase III, Customs integration completion, and other priorities.

**Tactical implication:** The ToB audit and Barry engagement are not optional credentials. They are the actual moat. Treat both with maximum care.

## The Opening Story: Konkola

You don't lead with technology. You don't lead with Vedanta. You lead with the wound that's still bleeding.

> *"Last week, Trafigura was awarded $92 million against ZCCM-IH in international arbitration over Konkola Copper Mines. Vedanta's Konkola unit is on a 60-day maintenance shutdown right now. The Mopani dispute took fourteen years to resolve. Every one of these cases comes back to the same root cause — when operators control the production data, the state has no independent way to verify the numbers until the dispute is already in arbitration.*
>
> *Resource Command was built to make the next Konkola impossible. Not by replacing your inspectors. Not by exposing operator commercial data. By giving the state a mathematical proof of compliance at the point of declaration, before the dispute exists."*

This is your opening. It uses a wound that was inflicted **this week**. Every fiscal official in the room is going to spend the next month dealing with the fallout from the $92M Trafigura award. Walking in with the solution to that exact pattern of failure is the most powerful framing you can use.

Mopani is the historical reinforcement after the Konkola lead lands.

---

## The Leverage Stack

Four things in the last week reframe the entire conversation.

### 1. The Konkola arbitration award (June 3, 2026)

Trafigura was awarded $92 million against ZCCM-IH in international arbitration over Konkola Copper Mines. The Zambian state is paying this. Every shilling of that $92M is money that does not arrive in the Treasury.

**What this means for ZRA:** This is not theoretical. The exact failure mode RC prevents just cost the country $92M last week. The cost of *not* having an independent verification layer is now a verifiable number, paid out in real money, this fiscal quarter.

**The pitch angle:** "The $92M Trafigura award is the cost of the problem we solve. The question isn't whether the state needs an independent verification layer. It's whether the next $92M dispute is already brewing while we're in this meeting."

### 2. Vedanta IPO on the NYSE (June 3, 2026)

Vedanta announced an IPO on the New York Stock Exchange specifically to fund their Zambian copper operations. American investors and the SEC will now be asking hard questions about royalty compliance and operational transparency.

**What this means for ZRA:** A foreign-listed entity mining Zambian copper now has US regulatory disclosure obligations layered on top of Zambian fiscal obligations. The disclosures will produce data the public can read. Inconsistencies between what Vedanta tells American investors and what they declare to ZRA will become very visible, very fast.

**The pitch angle:** "Vedanta is about to be publicly disclosing data about their Zambian operations to American investors. ZRA needs to be in a position to independently verify that data, not consume it after the fact. RC gives you that capability."

### 3. ZCCM-IH revenue royalty — audited figures and structural preference for verification

ZCCM-IH converted their 20% profit-based dividend rights in Kansanshi Mining Plc (KMP) into a **3.1% gross revenue royalty** on 31 March 2023. Per the ZCCM-IH Integrated Annual Report:
- 2023: US$56.13 million
- 2024: US$54.51 million
- **Audited total: US$110.64 million over 24 months**

**Why ZCCM-IH made this conversion matters strategically.** Profit-based dividends erode through transfer mispricing, inflated operational costs, accelerated depreciation, and thin capitalization — exactly the failure modes the 2023 tax gap study identified. Revenue-based royalty cannot be eroded the same way; it only needs verifiable revenue.

ZCCM-IH has already architecturally chosen a verification-friendlier structure. RC is the natural completion of that choice.

**The pitch angle:** *"ZCCM-IH chose revenue-based royalty over profit-based dividends specifically because revenue is harder to manipulate than profit. Resource Command provides the cryptographic proof that the revenue figure itself is accurate. You completed the institutional layer; we complete the technical layer."*

This positions ZCCM-IH as the *easiest* sovereign customer to convert, not the hardest.

### 4. The 2026 copper concentrate export duty waiver (June 3-4, 2026)

The government just extended the duty-free export waiver because smelters are down for maintenance. The waiver is costing revenue. Ending the waiver pressures operators. The government is making these decisions with imperfect data about what is actually being produced and exported.

**What this means:** Fiscal policy on copper is in active flux right now. The government needs better data to make better decisions. RC provides exactly that — independent, verifiable production data that lets policy be set with confidence rather than estimation.

### 5. The empirical extractives tax gap is documented and exactly RC's target

The 2023 ZRA / UNU-WIDER / ICTD study established empirically that the extractives sector has **the highest CIT gap in the Zambian economy**. The specific failure modes named: transfer mispricing, profit shifting, thin capitalisation, accelerated depreciation. The annual revenue loss across all sectors is $550M-$940M (rigorously estimated, machine-learning-validated).

**What this means:** ZRA's own research already made the case that mining is the highest-priority gap. We don't have to argue this — they've published it. RC's pitch becomes: "Your own study identified the extractives sector as the highest CIT gap. ML risk scoring flags anomalies probabilistically. Cryptographic verification turns those flags into mathematical certainty about what was actually produced."

**Important: kill the $3B narrative.** The 2015 War on Want figure has been empirically rebutted (Swiss destination reporting error + production value impossibility). Citing it now damages credibility because the rebuttal is in ZRA's own commissioned research. Use the $550M-$940M figure — it's defensible, citable, and still massive.

### 6. The Vedanta KCM disclosure — $1.26B of disputed value with no mathematical ground truth

The verified facts from Vedanta's Form 20-F and ZCCM-IH's filings:
- ZCCM-IH alleges Vedanta operated KCM at a cumulative loss of **US$1.26 billion** between 2013 and 2019
- ZCCM-IH served a "Notice of Deemed Transfer of Shares" in July 2020
- State appointed a Provisional Liquidator; Vedanta deconsolidated KCM from financial statements
- Vedanta admits in SEC filings there is **"no assurance"** they will ever regain control
- Vedanta alleges Zambia breached the Shareholders' Agreement by bypassing international arbitration in Johannesburg

**The pitch angle:** *"Vedanta says they lost US$1.26 billion. ZCCM-IH says Vedanta operated against the country's interest. Neither claim can be cryptographically verified or refuted. That ambiguity is the cost of not having an independent verification layer — billions of dollars of disputed value with no mathematical resolution. Resource Command would have made those losses or those allegations provably true or provably false at the time of declaration, not fifteen years later in court."*

**Use the $1.26B figure as the new headline number for the disputed-value problem.** It is audited, recent, and specific. Both sides admit it in their official filings. Replace $3B with $1.26B in all materials.

---

## Meeting Structure

### Lead with Konkola, not the technology

Open with the story above. Let it land. Pause. Then transition with one sentence:

> *"This is what Resource Command is built to prevent. May I show you how?"*

Only then introduce the technology.

### The 3 things ZRA needs to hear about RC

1. **It doesn't expose operator data.** Mining companies will fight any system that reveals production volumes. ZK proofs verify compliance without revealing the numbers. Operators keep their commercial privacy. ZRA gets mathematical certainty. *This is the key unlock — without it, operators block the rollout.*

2. **It's already been reviewed by Trail of Bits.** ToB is the cybersecurity firm that has audited systems for the US Department of Defense and major American financial institutions. Their formal scoping call happened Monday [adjust based on actual ToB call outcome]. Separately, one of the most respected zero-knowledge engineers globally has personally been reviewing our architecture.

3. **It works now.** The demo is live. Working circuit, sub-second proof generation, five-validator network. This is not a roadmap. It is a working system that needs a regulatory sandbox to prove itself at scale.

### The ask

Not a contract. A regulatory sandbox slot. Low-risk for ZRA: they designate one mine, one quarter, one reporting cycle. RC runs in parallel with the existing process. If the proofs match the declared figures, they have their validation. If they don't, ZRA has caught a discrepancy the current process missed.

The sandbox ask is designed to be impossible to say no to. No budget allocation. No policy change. No reorganization. Just permission to run a parallel verification test on one mine for one quarter.

If it adds nothing, nothing has been lost.
If it catches one Konkola, the value is settled.

---

## Risks and mitigations

**Risk:** "Why should we trust a Botswana company with Zambian fiscal infrastructure?"
**Mitigation:** The operating entity is Zambian. Kgosi Sovereign Holdings (Botswana) is the IP holding company only. The software runs on Zambian infrastructure. The legal structure is being handled by a senior Zambian lawyer. The audits are international (Trail of Bits + others). Frame it: "the IP is protected in Botswana, the service is delivered in Zambia, the audit is international, the value stays in the country."

**Risk:** "We already have auditors and inspection systems."
**Mitigation:** "Auditors verify what operators declare. Resource Command verifies whether what they declared is mathematically consistent with the physical evidence. Existing systems answer 'is the paperwork correct?' RC answers 'is the paperwork true?' Both questions need answering. Today only the first one is — and the $92M Konkola award is the cost of that gap."

**Risk:** "This is too experimental / too early / too crypto."
**Mitigation:** "The Konkola award was paid out last week. Vedanta is listing in New York next quarter. The EU Battery Regulation enforcement begins February 2027. The environment is not waiting for us to be ready. The question is whether Zambia leads the region on verifiable mineral compliance, or whether it follows DRC's recent lithium royalty enforcement increase and the rest of the AfCFTA region. A sandbox costs nothing and answers that question."

**Risk:** "The technology is too complicated for us to evaluate."
**Mitigation:** "You don't need to evaluate the cryptography. Trail of Bits will do that for us at engineering level. What ZRA needs to evaluate is the operational fit: does the sandbox produce useful data, does it integrate with existing reporting, does it tell you something you don't already know. We propose the sandbox specifically to answer those questions before any formal commitment."

---

## People in the room

Prepare a 2-page technical pre-read that any official can hand to their superior. It must survive without you in the room.

Contents:
- **What Resource Command does** (one paragraph, no cryptographic jargon)
- **Why it matters now** (Konkola, Vedanta IPO, EU Battery Regulation — three bullets)
- **Who has reviewed it** (Trail of Bits scoping, Barry Whitehat technical review, plus the audit pack v1.8 and Circumspect-clean status)
- **What the sandbox would look like** (one mine, one quarter, parallel verification, no budget allocation, no policy change)
- **What ZRA gains** (independent verification layer, investor confidence post-Vedanta IPO, regional leadership, EU Battery Passport readiness)

The pre-read should make it possible for a mid-level official to bring this proposal to a senior decision-maker without you having to brief them again. That is how sovereign institutions actually move — through documents that travel internally.

---

## Strategic note on sequencing

The Konkola award is fresh. Use it now. Within 60-90 days the story will fade and you will be back to using Mopani as historical reference. The next 30 days are the maximum-leverage window for this specific framing.

If David Wamulume's introduction lands within that window, the conversation has its hook ready. If the introduction doesn't materialize, escalate to the direct government contact in place. Either way, do not let the Konkola moment pass without using it.

---

## Alternative pathways unlocked by ZRA's sophistication

ZRA's existing infrastructure opens approaches that don't require a direct contract pitch:

### Path A — Digital Innovate 360 pilot (PRIMARY)

Established by the ZRA Board under the ZRA Amendment Act No. 20 of 2025, **Digital Innovate 360** is an institutional vehicle specifically designed "to support innovation, harness emerging talent, and pilot technology-driven solutions." Smart Invoice was its flagship project. The Innovation and Project Management Committee provides Board-level oversight.

This is the cleanest institutional door. Approach Digital Innovate 360 with a RC pilot proposal modelled on the Smart Invoice rollout framework:
- Phased timeline (launch → mandatory adoption → grace period)
- Pilot training cohort (modelled on the 61 in-person + 2,335 online Smart Invoice cohort)
- Dedicated Project Office with Innovation Committee oversight
- Segmented interfaces by mine size / operator type

**This is not asking ZRA to invent a procurement process. It is asking them to apply their proven Digital Innovate 360 framework to a new technology.** Massive reduction in political and operational friction.

### Path B — ASM (Artisanal Small-Scale Mining) pilot — under the radar

ASM royalty collection dropped 79% year-over-year (K57.8M in 2024 → K12.0M in 2025). ZRA has specialised ASM units in place but flags informal tax agents and inadequate regulatory capacity as enterprise risks.

**Pitch framing:** *"ASM royalty collection collapsed 79% last year. Specialised units are in place, but informal intermediaries and capacity gaps remain. Resource Command provides cryptographic verification at the cooperative level — eliminating the need for trusted intermediaries while integrating with BIDA's existing analytics. Pilot scope: 2-3 cooperatives, one quarter, parallel to current collection methods."*

This is a politically easier yes than auditing a Vedanta-scale operator. ZRA already wants ASM solved. Lower stakes, faster decision, real revenue recovery if it works.

### Path C — UNU-WIDER research collaboration

UNU-WIDER co-authored the 2023 tax gap study and runs the ZRA Research Data Laboratory. They are ZRA's trusted academic partner. Approaching them as a *research collaborator* — "we have cryptographic verification technology that complements the ML risk-scoring approach you've published; can we explore an applied research engagement?" — is potentially faster than direct ZRA procurement and produces compounding academic credibility (papers, conference talks).

### Path D — ZRA Research Data Laboratory as pilot host

The Research Data Laboratory is a high-security analytical environment with anonymized administrative data and an explicit research mission. A pilot of RC inside the Lab, using anonymized historical data to test whether RC's cryptographic verification would have caught known historical discrepancies, is a much lighter ask than a live mine sandbox. The Lab's output is read by senior ZRA leadership.

### Path E — Smart Invoice extension

Smart Invoice has built the legally mandated digital transaction infrastructure (invoices not generated via Smart Invoice are legally invalid for tax deductions as of January 2025). RC could position as the cryptographic verification layer that extends Smart Invoice from "this invoice was issued" to "this invoice is mathematically consistent with the physical production it represents." Massive structural leverage — RC plugs into a legally captive data source.

### Path F — 9NDP / MTRS alignment

The 9th National Development Plan needs a Medium-Term Revenue Strategy. RC fits naturally as a structural tool for sustainable domestic revenue mobilisation, especially in the extractives sector. Aligning with the 9NDP gives RC a programmatic home that survives political turnover and election cycles.

**Sequenced priority:** Path A (Digital Innovate 360) is the primary institutional door. Path B (ASM) is the lowest-friction pilot opportunity. Paths C-F are reinforcing institutional anchors. The conventional "direct ZRA procurement" path remains valid as a fallback but is no longer the optimal first move.
