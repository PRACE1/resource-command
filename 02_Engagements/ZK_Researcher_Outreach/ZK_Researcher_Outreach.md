# ZK Researcher Outreach — Targeted Messages
**Resource Command · Kgosi Capital Holdings**  
**Date:** 2026-05-09  
**Status:** Draft — ready to send

---

## 1. JORDI BAYLINA — Circom Creator · iden3 / Polygon Hermez

**Why he's the right person:** He wrote the compiler our circuit runs on. Circom 2.2.3 shipped in October 2025 with `--sanity_check` and safe witness generation mode — features directly relevant to our security posture. He will understand the circuit in 60 seconds.

**Platform:** Twitter/X (@jbaylina) or email via iden3.io

**Message:**
> Hi Jordi — we built a compliance circuit in Circom 2.2.3 for a sovereign mineral royalty protocol in Zambia (verified by AfDB and World Bank validator nodes). We're running `--sanity_check 3` as part of our pre-audit workflow before a formal ToB engagement.
>
> We wanted to ask: are there known edge cases in the 2.2.3 `safe witness generation` mode that affect how `<--` hint assignments interact with `Num2Bits` components? We have a specific pattern we'd like to sanity-check with you.
>
> Full circuit and technical spec available if you're curious. Happy to share.

**Why this works:** Opens with the circuit use-case (novel), shows technical literacy (2.2.3 specifically, not just "Circom"), asks a precise question rather than a favour. Gives him something interesting to think about, not just a cold ask.

---

## 2. KOBI GURKAN — ZK Researcher · phase2-bn254 author

**Why he's the right person:** He wrote `phase2-bn254` — the trusted setup ceremony tool for BN254 circuits. We are about to run a Phase 2 ceremony. He is literally the person who built the tool we're using and who has run these ceremonies before.

**Platform:** Twitter/X (@kobigurk) or GitHub

**Message:**
> Hi Kobi — we're preparing a Phase 2 trusted setup ceremony for a Groth16/BN254 compliance circuit (sovereign mineral royalty attestation, Zambia). We're planning to use phase2-bn254, and naturally you came up immediately.
>
> We're structuring a multi-jurisdictional ceremony with contributions from AfDB, World Bank, ZRA, and MRC Zambia — probably 4-6 parties. Would you be open to either (a) advising on ceremony design, or (b) participating as an independent entropy contributor? Your contribution would be publicly verifiable and attributed.
>
> Our Phase 1 ptau is the Hermez transcript. Happy to share the full spec.

**Why this works:** He built the tool, so the ask is a natural extension of his existing work. "Your contribution would be publicly verifiable and attributed" is the right language — ZK researchers care about provable participation in ceremonies. The Hermez ptau reference shows we know the ecosystem.

---

## 3. YING TONG LAI — ZK Researcher · PSE / Ethereum Foundation

**Why she's the right person:** PSE is actively building `mpz` (multi-party computation libraries in Rust) and `sonobe` (folding schemes). Our MPC ceremony design sits directly in that space. She's also one of the most technically rigorous Circom-adjacent researchers in the ecosystem.

**Platform:** Twitter/X (@therealyingtong) or PSE contact

**Message:**
> Hi Ying Tong — I've been following PSE's mpz and sonobe work and wanted to reach out about something adjacent.
>
> We've built a ZK compliance circuit for sovereign mineral royalty verification in Zambia — Circom 2.2.3, Groth16, BN254, 542 constraints. It's going through a Trail of Bits audit before a Phase 2 MPC ceremony. The ceremony involves multi-jurisdictional participants (AfDB, World Bank, government agencies).
>
> Given PSE's work on MPC primitives: do you see anything in the ceremony design space that the `phase2-bn254` toolchain doesn't handle well for multi-institutional settings? We're specifically thinking about entropy mixing across participants who may be adversarially motivated against each other.
>
> Would love your perspective — even a 15-minute call would be invaluable.

**Why this works:** References her actual current work (mpz, PSE) rather than past reputation. Asks a technically substantive question she can actually engage with (entropy mixing across adversarial parties). Frames the use case as genuinely interesting: governments, sovereignty, adversarial incentives.

---

## 4. BARRY WHITEHAT — ZK Pioneer · Semaphore / roll_up

**Why he's the right person:** He built the first ZK rollup and Semaphore — the commit-then-prove pattern we implemented in our Truth Anchor binding is directly descended from his architectural thinking. He's earned the right to say whether we did it properly.

**Platform:** Twitter/X (@barrywhitehat) or Ethereum Research forum

**Message:**
> Hi Barry — Resource Command is a ZK-based mineral royalty compliance system for Zambia. The core design uses a commit-then-prove Truth Anchor binding: the mine operator commits to production volume via Poseidon(v, nonce) before the oracle window opens, then proves compliance against the commitment at declaration time.
>
> The sequencing pattern is directly informed by Semaphore's design philosophy — commit first, prove later, never reveal the witness. We think we've implemented it correctly, but you built the original. If you have 20 minutes to look at 120 lines of Circom, we'd be honoured to have your feedback before we go to audit.
>
> Circuit and spec attached if you're willing.

**Why this works:** Honest attribution ("you built the original") without being sycophantic. Makes the ask concrete: 20 minutes, 120 lines. The Semaphore connection is genuine and gives him a real reason to be interested.

---

## 5. KEEGAN RYAN — Cryptographer · Trail of Bits

**Why he's the right person:** ZK-focused security researcher at ToB. We just submitted the audit pack to ToB — if he's part of the team, getting a named connection increases the chance of engagement.

**Platform:** Direct outreach via ToB contact form or LinkedIn

**Message:**
> Hi Keegan — we submitted a formal audit engagement request to Trail of Bits today for a ZK-SNARK compliance circuit (Groth16/BN254, Circom 2.2.3, 542 constraints) — the Resource Command sovereign mineral royalty protocol for Zambia.
>
> We've done five rounds of internal adversarial review and ran a Circomspect pre-analysis that's included in the submission. One specific area we'd want your team to focus on: timing side-channel exposure during Groth16 proof generation. The prover runs in a controlled sovereign node environment, but we want to understand whether proof generation duration or memory access patterns could leak anything about the private witness.
>
> Looking forward to the scoping call.

**Why this works:** We've already submitted — this isn't a cold ask. It's a warm contact that shows we know what we want from the engagement specifically. The side-channel framing is a legitimate concern and shows we're thinking beyond just constraint soundness.

---

## 6. AKSHITH GUNASEKARAN — Security Researcher · Trail of Bits

**Why he's the right person:** ZK-focused at ToB. Has likely seen the submission already given his area of specialization.

**Platform:** LinkedIn or via ToB internal routing

**Message:**
> Hi Akshith — we submitted the Resource Command ZK audit pack to Trail of Bits today via the contact form and SendSafely (addressed to Chris Dahlheimer). Circom 2.2.3, Groth16, BN254.
>
> We included a Circomspect pre-analysis that documents our self-identified findings — one open item (royalty_rate_bps upper bound, now patched) and two previously identified items confirmed addressed. We wanted to flag it to you specifically given your background in ZK systems — the pre-analysis is intended to save your team time and direct focus toward the non-obvious surface.
>
> Happy to get on a call before the formal scoping if useful.

**Why this works:** Shows awareness of who he is and what he does. The Circomspect reference is specifically relevant to a ToB researcher. "Save your team time" is the right frame — it's collaborative, not boastful.

---

## SUMMARY TABLE

| Researcher | Ask | Platform | Priority |
|---|---|---|---|
| Jordi Baylina | Technical question re: 2.2.3 sanity_check | Twitter/X | High |
| Kobi Gurkan | Phase 2 ceremony advisor / participant | Twitter/X | **Critical** |
| Ying Tong Lai | MPC ceremony design perspective | Twitter/X | High |
| Barry Whitehat | 20min circuit review | Twitter/X | Medium |
| Keegan Ryan | Named ToB contact, side-channel focus | LinkedIn | High |
| Akshith Gunasekaran | ToB warm intro, Circomspect flag | LinkedIn | High |

---

*All messages drafted by Kgosi Capital Holdings · 2026-05-09*
