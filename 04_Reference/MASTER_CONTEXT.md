# RESOURCE COMMAND — FULL CONTEXT SUMMARY

**The Company**
Kgosi Sovereign Holdings (Botswana) — under registration. IP holding company. Will hold 35% stake in a Zambian operating entity that contracts directly with the Zambia Revenue Authority. Legal structure being handled by a former judge turned lawyer.

**The Product**
Resource Command — a ZK-based mineral royalty compliance system. Mining operators prove they calculated royalties correctly without exposing production volumes to the government. Built on Groth16/BN254, Circom 2.2.3, approximately 632 constraints. Oracle layer uses Poseidon hash commitments. BFT consensus layer n=5, f=1 PBFT with AfDB and World Bank as two of five validator nodes.

**Product 2**
Proof of Presence — proving a specific authorised operator was physically present at a mine site during a specific reporting window. Uses cryptokinetic decay model from IACR 2026/323, ErPR biometric signal captured via AR glasses, Halo2 + Nova/SuperNova folding on BN254. Extension of the royalty circuit, not a rebuild.

**Product 3**
Battery Passport source layer — every mineral extraction event verified through Resource Command becomes a cryptographically attested data point for EU Battery Passport compliance from February 2027.

**Technical Status**
compliance.circom v1.1 — Groth16 circuit, patched, Circomspect clean. Self-audited using Trail of Bits open source tooling before formal submission. Audit pack v1.9 dispatched to Trail of Bits. Awaiting scoping call response.

**Key Engagements**
- **Trail of Bits** — Lindsay Rakowski responded. Formal audit pack submitted. Scoping call pending.
- **Barry Whitehat** — creator of Semaphore. 11 emails deep. Has stress tested oracle model, puppet attack vector, biometric placement, temporal dimension. Asked for timelines and network introductions. Awaiting reply to last email.
- **Mikerah Quintyne-Collins** — HashCloak founder. Reached out on Twitter after seeing public conversation. Contact requested.

**Research Completed**
- **Session 1:** Cryptokinetics IACR 2026/323 verified. Exponential decay model for presence. Gap confirmed: no ZK circuit exists for this yet.
- **Session 2:** ErPR biometric verified. 97% accuracy, involuntary signal, injection-attack resistant. 44 trials needed, 3-4 minutes — acceptable for quarterly sovereign audit context.
- **Session 3:** Discretisation problem researched. IACR 2025/2326 Gauss-Legendre quadrature is the implementation path for committing e^(-kt) into a ZK circuit. IACR 2024/859 minimax polynomial alternative confirmed. Timing attack at discretisation boundary identified as open research problem — potential research contribution.
- **BioZero arXiv 2409.17509v2** verified — Pedersen commitments + Groth16 for biometric authentication on-chain. Relevant prior art.
- **CN121619107A** verified — RISC-V Keystone TEE + ZKP patent. Closest prior art to on-device ZK proof generation.

**Government**
Zambia Revenue Authority (ZRA) is the target client. Government contact in place. Meeting being arranged before Zambia elections. May and June are the critical window.

**Commercial Structure**
Kgosi Sovereign Holdings (Botswana) licenses IP to Zambia operating entity via intercompany licensing agreement. 35% equity stake in Zambia entity. Lawyer success fee agreement — percentage of first ZRA contract payment, no equity. CIPA registration for copyright protection. ARIPO for regional expansion.

**Expansion Path**
Zambia → DRC → Zimbabwe → Tanzania → Botswana government. EU Battery Passport creates direct commercial product for mining companies needing EU market access — KoBold, Mingomba, Glencore, Anglo American.

**Blockers**
Anthropic invoice overdue — Claude Code cron dead. Replicate balance zero — video render blocked. Both small amounts, need resolving before next build sprint.

**Key Technical Decisions**
Gauss-Legendre quadrature for exponential decay in circuit. ErPR epoch amplitudes committed via Poseidon, not raw frames. Nova/SuperNova folding accumulates presence score across session. Single proof output: trust stayed above threshold throughout compliance window. Raw biometric never leaves device.

**Competitive Position**
Worldcoin proves personhood not presence, banned in 5 countries, no temporal model. No competitor exists in temporal presence verification. No African company operates at this technical level in ZK security.
