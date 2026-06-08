# Resource Command: Technical Architecture & Cryptographic Specification v1.8
### Confidential Engineering Brief — 4 May 2026

**Author:** Kgosi Sovereign Holdings Proprietary Limited — Technical Team  
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
// PRODUCTION R1CS GATE SPECIFICATION
// Public Inputs: royalty_rate_num, royalty_rate_den, tax_paid_usd, volume_commitment_hash
// Private Inputs: volume_v, density_d, grade_g, volume_nonce, rem_1, rem_2, rem_3

// 0. Volume-Commitment Binding
Constraint 0: Poseidon(volume_v, volume_nonce) === volume_commitment_hash

// 1. Tonnage Scaling Gate (Normalisation by 10^6)
Constraint 1: (volume_v * density_d) === (tonnage_t * 10^6) + rem_1

// 2. Mineral Content Scaling Gate
Constraint 2: (tonnage_t * grade_g) === (mineral_content_m * 10^6) + rem_2

// 3. Fiscal Royalty Gate (Statutory 6.0%)
Constraint 3: (mineral_content_m * royalty_rate_num) === (tax_paid_usd * royalty_rate_den) + rem_3

// Range Proofs: All remainder witnesses (rem_n) are constrained to [0, divisor-1]
// to ensure soundness and prevent field-overflow attacks.
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
*   **Fiscal Configuration:** Pre-configured for Zambian Copper/Open-Cast (6.0%).
