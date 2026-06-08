# Resource Command: Technical Architecture & Cryptographic Specification v1.8
### Confidential Engineering Brief — 4 May 2026

**Author:** Kgosi Capital Technical Team  
**Counterparty:** KoBold Metals Engineering / Mingomba Project  
**Subject:** Sovereign Mineral Verification & Data Sovereignty Architecture

---

## 1. Architectural Philosophy: Cryptographic Minimisation
Resource Command is designed as a "Non-Custodial Audit Layer." The platform is incapable of accessing an operator's sensitive commercial data.

---

## 2. Remote Sensing Pipeline: Multi-Sensor Verification

### 2.1 Multi-Sensor Oracle Fusion
To mitigate the "Single Oracle" trust problem, the platform utilizes a **Fused Commitment** approach:
1.  **Primary Source:** PS-InSAR telemetry (Sentinel-1) surface displacement monitoring.
2.  **Cross-Verification:** Periodic **UAV LiDAR** or **Optical photogrammetry** reconciliation.
3.  **Independent Commitment:** The volume commitment is posted only upon AfDB and World Bank node consensus on the fused data.

---

## 3. Cryptographic Specification: R1CS / BN254

### 3.1 R1CS Gate Representation (Fixed-Point Scaling)
The circuit is implemented over the **BN254 scalar field**. Real-valued inputs are represented as 64-bit fixed-point integers scaled by $10^6$.

```rust
// PRODUCTION R1CS GATE SPECIFICATION — compliance.circom v1.1
// Public Inputs: volume_commitment_hash, tax_paid_usd, royalty_rate_bps
// Private Inputs: volume_v, density_d, grade_g, volume_nonce,
//                 inv_density_d, inv_grade_g, rem_tonnage, rem_mineral, rem_royalty

// 0. Volume-Commitment Binding (Truth Anchor)
Constraint 0: Poseidon(volume_v, volume_nonce) === volume_commitment_hash

// 1. Tonnage Scaling Gate (Normalisation by 10^6)
Constraint 1: (volume_v * density_d) === (tonnage_t * 1_000_000) + rem_tonnage

// 2. Mineral Content Scaling Gate
Constraint 2: (tonnage_t * grade_g) === (mineral_content_m * 1_000_000) + rem_mineral

// 3. Fiscal Royalty Gate (parameterised — royalty_rate_bps is a public input)
// royalty_rate_bps is denominated in basis points (1 bps = 0.01%).
// Statutory Zambia copper rate: 600 bps (6.0%).
Constraint 3: (mineral_content_m * royalty_rate_bps) === (tax_paid_usd * 10_000) + rem_royalty

// Range Proofs:
//   rem_tonnage  ∈ [0, 1_000_000)  — LessThan(20)
//   rem_mineral  ∈ [0, 1_000_000)  — LessThan(20)
//   rem_royalty  ∈ [0, 10_000)     — LessThan(14)
// Rate Bounds:
//   royalty_rate_bps ∈ [1, 5000]   — GreaterThan(13) + LessThan(13)
// Non-zero inputs:
//   density_d, grade_g enforced non-zero via multiplicative inverse lock (RC-01/02)
```

---

## 4. Consensus & Validator Infrastructure

### 4.1 BFT Safety & Integrity Watchdogs
The validator network implements BFT consensus with **n = 5, f = 1**. Any attempt at sovereign-level collusion is **cryptographically attributable**, ensuring that a 3-node sovereign coalition cannot forge a valid consensus decision without the signature of at least one independent international node (AfDB/World Bank).

---

## 5. Implementation & Verification Strategy

### 5.1 Formal Audit & Verification
The platform follows a multi-stage verification pipeline:
*   **Property-Based Testing:** Automated verification of circuit soundness using the reference witness generator.
*   **Third-Party Audit:** Formal engagement of **Trail of Bits** for a full-scope audit of the Circom circuit and BFT protocol.
*   **Adversarial Modeling:** Continuous Red-Teaming of the Oracle-Fusion pipeline to ensure commitment integrity.
*   **Fiscal Configuration:** `royalty_rate_bps` is a public input (not a circuit constant), allowing the ZRA to update the statutory rate via governance without recompiling the circuit. Default: 600 bps (6.0% Zambian copper open-cast rate). Circuit enforces bounds [1, 5000 bps].
