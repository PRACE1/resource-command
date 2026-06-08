# Technical Brief — Resource Command

*For grant applications requiring deeper technical detail. Two-layer structure: plain-English summary for institutional reviewers, technical specification for cryptographic reviewers (PSE, Ethereum Foundation, EU Horizon technical referees).*

---

## Layer 1 — Plain English

### What it does

Resource Command lets a mining operator generate a mathematical proof their royalty calculation is correct, without exposing the underlying production volume, grade, or commercial terms.

The metaphor is a **sealed envelope**. The operator puts their actual numbers inside. The envelope produces a stamp on the outside that says *"the royalty calculation based on these numbers is correct."* The state — or an institutional verifier like ZEITI — checks the stamp. The envelope stays sealed. Nobody sees the numbers inside. Forging the stamp would require breaking the underlying cryptography, which is computationally infeasible.

### Why it matters

Existing mineral revenue audit relies on the operator's self-declared production figures. The state must either trust those figures (the current default) or force disclosure of commercially sensitive data (which operators resist, often successfully). Resource Command resolves the conflict by introducing cryptographic verification — neither party gives up what matters to them.

This is the only known mechanism that simultaneously delivers:
- Sovereign-grade revenue verification
- Operator commercial confidentiality
- Real-time auditability without lag
- EU Battery Passport regulatory compliance (Feb 2027)

---

## Layer 2 — Technical specification

### Cryptographic foundation

**Proof system:** Groth16 SNARK over the BN254 elliptic curve (`bn128` variant). Selected for production maturity, library tooling (snarkjs, circomlib), and on-chain verification cost. Trusted setup uses the canonical Hermez Phase 1 Powers of Tau transcript; Phase 2 ceremony is project-specific, documented in `Trusted_Setup_Specification.md`.

**Constraint language:** Circom 2.2.3. The core compliance circuit `compliance.circom` v1.1 compiles to **839 R1CS constraints** and has been verified clean against Circomspect.

**Commitment scheme for sealed inputs:** Poseidon hash family (t=3, r_F=8, r_P=57 over BN254 scalar field). Used for nullifier construction, identity commitment, accumulator transitions, and event-ID derivation. Domain separation across these contexts is on the standing-disclosure list pending audit guidance.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│ OPERATOR SIDE (sealed)                                  │
│  • Raw production data (volume, grade, price, time)     │
│  • Witness generation (WASM)                            │
│  • Proof generation (snarkjs Groth16)                   │
└────────────────┬────────────────────────────────────────┘
                 │ proof + public inputs
                 ▼
┌─────────────────────────────────────────────────────────┐
│ ORACLE COMMITMENT LAYER                                 │
│  • Sealed-input attestation via Poseidon commitments    │
│  • Pending: extended-oracle architecture (RC-03)        │
│    or MRC co-signature for operator-input independence  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ INSTITUTIONAL VALIDATOR CONSENSUS                       │
│  • n=5, f=1 PBFT                                        │
│  • Validators: AfDB, World Bank IFC, ZRA,               │
│    ESA Copernicus (satellite ground-truth), ZCCM-IH     │
│  • Verifies the Groth16 proof + commitment              │
└────────────────┬────────────────────────────────────────┘
                 │ verified attestation
                 ▼
┌─────────────────────────────────────────────────────────┐
│ DOWNSTREAM USES                                         │
│  • Sovereign royalty assessment (ZRA)                   │
│  • Transparency reporting (ZEITI G-Factor reconciliation│
│  • EU Battery Passport attestation (Feb 2027 deadline)  │
│  • Cross-border supply-chain provenance                 │
└─────────────────────────────────────────────────────────┘
```

### Public and private signal topology

**Public inputs (verifiable on-chain or by any institutional verifier):**
- `nullifier` — prevents double-reporting of any single event
- `public_key` — operator identity commitment
- `merkle_root` — root of the registered equipment / operator set
- `declared_commitment` — Poseidon commitment to royalty inputs

**Private witnesses (sealed):**
- `secret_key` — operator credential
- `volume`, `density`, `grade`, `price` — production figures
- `event_id` — canonical derivation from (timestamp, equipment_serial, shift_id)
- `merkle_path` — inclusion proof for operator registration
- `prev_accumulator` — running session hash

### Security posture

**Internal audit status:**
- Five-pass internal audit, zero critical / high / medium / low findings after remediation
- All seven internally-identified vulnerabilities patched
- Circomspect clean
- Trail of Bits open-source tooling used in pre-audit hardening

**Standing-disclosure items (acknowledged, not blocking):**
- **RC-01 / RC-02 — Trivial-floor parameters**: minimum density and grade values are pending ZRA / Mineral Regulation Commission regulatory determination. Will be hardcoded before Sandbox Phase 2 deployment.
- **RC-03 — Oracle architectural gap**: density and grade are operator-self-declared. Active design work on either an extended-oracle architecture or an MRC co-signature scheme. Closing this is a Tier-A workstream of the grant programme.

**Independent review:**
- **Trail of Bits** — formal audit pack v1.9 transmitted; scoping engagement booked; audit kickoff July 2026
- **Barry Whitehat** (creator of Semaphore) — has the same audit pack; stress-testing the oracle model, puppet-attack vector, biometric placement (for Product 2), and temporal dimension; eleven-email technical correspondence ongoing
- **A second auditor** — to be sourced (candidates: Veridise, Zellic, ABDK, HashCloak)

### Research contributions and novelty

Resource Command is principally an applied engineering project, but the programme produces three open research contributions:

1. **Sovereign-grade circuit hardening methodology.** The five-pass internal audit, combined with Trail of Bits and independent review, will produce a reusable institutional audit template for sovereign ZK deployments. Currently no published precedent exists.

2. **Timing-attack analysis at the discretisation boundary** (Product 2, Proof of Presence). The Gauss-Legendre quadrature approach to committing exponential decay `e^(-kt)` into a ZK circuit (per IACR 2025/2326) raises an open question about timing leakage at discretisation transitions. Initial analysis suggests a previously unpublished research contribution.

3. **PBFT + Groth16 institutional consensus design.** The n=5, f=1 validator topology with multilateral institutional signatories (AfDB, WB-IFC, ZRA, ESA, ZCCM-IH) is a novel governance construct for sovereign cryptographic infrastructure. Methodology paper planned.

### Three products on a shared cryptographic foundation

**Product 1 — Resource Command (royalty compliance)** — circuit live, audit pending. Anchors ZRA pilot.

**Product 2 — Proof of Presence** — extension of the royalty circuit. Cryptokinetic decay model (IACR 2026/323), ErPR biometric signal (arXiv 2409.17509v2 verified, 97% accuracy, injection-resistant) captured via AR glasses, Halo2 with Nova / SuperNova folding on BN254. Proves a specific authorised operator was physically present at a mine site during a specific reporting window. Closes the deepest residual attack surface in royalty verification.

**Product 3 — Battery Passport source layer** — every mineral extraction event verified through Product 1 becomes a cryptographically attested data point for EU Battery Passport compliance from February 2027. Commercial channel for European market access.

The three products share the same underlying cryptographic foundation, audit pack, and validator infrastructure. Grant funding for Product 1 directly de-risks Products 2 and 3.

### Prior art and competitive landscape

- **BioZero (arXiv 2409.17509v2)** — Pedersen commitments plus Groth16 for biometric authentication on-chain. Closest prior art for Product 2 (Proof of Presence). Resource Command's contribution is the integration of biometric attestation into a sovereign royalty workflow, with institutional consensus.
- **CN121619107A** — RISC-V Keystone TEE plus ZKP patent (China). Closest prior art to on-device ZK proof generation. Resource Command operates above the TEE layer and is not patent-blocked.
- **No published ZK royalty / compliance circuit** for mineral revenue exists. Six months of monitoring via the project's GitHub ZK repo scanner (Layer 7 of the intelligence monitor) has produced zero detections. The negative-space evidence is itself meaningful: this category is empty.

### Open-source commitment

The cryptographic primitive — the `compliance.circom` circuit, the Poseidon commitment layer, and the validator consensus design — will be released under a permissive open-source license at the conclusion of the audit cycle. The commercial layer (operator integration, ZRA deployment, Battery Passport compliance UI) is licensable via Kgosi Sovereign Holdings to the Zambian operating entity and, in time, to second-country deployments. This structure ensures the public-goods cryptographic contribution is genuinely public while preserving a sustainable commercial path.

---

## Appendix — File manifest available to reviewers

- `compliance.circom` — the core circuit (v1.1, 839 R1CS constraints)
- `compliance.r1cs` — compiled constraint system
- `compliance.wasm` — witness generator
- `Trusted_Setup_Specification.md` — Phase 1 and Phase 2 ceremony documentation
- `Oracle_Pipeline_Security_Spec.md` — sealed-input commitment architecture
- `Geochemical_Oracle_Specification.md` — physical-data feed specification
- `Threat_Model.md` — full attack-surface analysis
- `Adversarial_Proof_of_Work.md` — adversarial scenarios and resistance analysis
- `Resource_Command_Audit_Pack_v1.9.zip` — Trail of Bits transmission package

All files available to grant reviewers on request, under NDA where appropriate.
