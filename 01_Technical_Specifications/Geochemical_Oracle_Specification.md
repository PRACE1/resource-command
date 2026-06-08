# SOVEREIGN GEOCHEMICAL ORACLE SPECIFICATION (v2.0)
## Document ID: RC-GEO-001
**Date:** 6 May 2026
**Classification:** Confidential — Post-Election Roadmap (Q1 2027)

---

### 1. OVERVIEW
This document defines the architecture for Resource Command v2.0, specifically designed to close the **RC-03 Residual Risk** (the physical reality gap). By cryptographically binding physical ore sampling and bulk density measurements to the ZK circuit, the protocol shifts the trust model from operator declaration to sovereign instrument verification.

### 2. CIRCOM v2.0 ARCHITECTURE
The v2.0 R1CS circuit ingests two new public truth anchors: `density_commitment_hash` and `grade_commitment_hash`.

*   **Constraint Impact:** The constraint count increases from 542 to **1,026**.
*   **Design Rationale:** This increase is driven by the addition of two independent `Poseidon(2)` hashes (243 constraints each). While a single `Poseidon(3)` hash (783 constraints) would be marginally cheaper, it would operationally couple the grade pipeline (48-hour laboratory turnaround) to the density pipeline (real-time weighbridge data), creating systemic fragility. Decoupling them is worth the 243-constraint premium.

### 3. CRYPTOGRAPHIC CORRELATION DEFENSE
Density and Grade must use **separate, independent nonces**.
*   **The Threat:** If a single shared nonce was used, an adversary who learns the nonce and one committed value (e.g., density from public weighbridge records) could reverse-engineer the other private value (grade) via a cross-commitment correlation attack.
*   **Open Item 1 (For ToB Review):** The secure delivery channel of these independent nonces from the Oracle Coordinator to the operator's proving environment represents a new attack surface.

### 4. ASYMMETRIC HARDWARE TRUST BOUNDARY
The physical data extraction requires asymmetric signature policies based on the specific manipulation surface area of the metric.

#### 4.1 Bulk Density (Weighbridge Pipeline)
*   **Signature Policy:** 1-of-1 MRC Officer Signature.
*   **Rationale:** Density is derived from hundreds of bulk truck passes over an epoch. Falsifying this requires a massive, logistically conspicuous conspiracy across multiple weighmasters. A single HSM signature from the active MRC officer is sufficient.

#### 4.2 Ore Grade (Geochemical Laboratory Pipeline)
*   **Signature Policy:** 2-of-2 MRC Officer Co-Signature.
*   **Rationale:** Grade is determined from a small number of geochemical samples in a laboratory. A single corrupt laboratory director can falsify a result with zero visible operational footprint. Therefore, grade commitments require two independent MRC laboratory officers to co-sign the result via their respective HSMs.

### 5. THE POLITICAL PROPOSITION (Q1 2027)
This architecture is the ultimate political deliverable for the incoming government.
With v2.0, the government does not need to trust the operator, nor do they need to trust Kgosi Capital. The system proves that the royalty arithmetic is correct *and* that the inputs to that arithmetic were cryptographically signed by the government's own Sovereign Regulator (MRC instruments). When combined with the AfDB and WB BFT-finalization, the system achieves total, trustless sovereign verification.
