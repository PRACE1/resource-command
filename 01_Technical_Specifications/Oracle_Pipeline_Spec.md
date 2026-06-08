# ORACLE PIPELINE SECURITY SPECIFICATION (v1.0)
## Resource Command — Sovereign Attestation Framework

### 1. OVERVIEW
This document formally specifies the attestation chain from the physical world (Sentinel-1 SAR data) to the ZK-circuit field element (`volume_v`). The goal is to ensure the **Computational Integrity** of the oracle pipeline and minimize the surface area for data manipulation before the Truth Anchor commitment is posted to the ledger.

### 2. THE ATTESTATION CHAIN (STAGES 1-9)

| Stage | Process | Input | Output | Trust Assumption |
| :--- | :--- | :--- | :--- | :--- |
| **S1** | **Satellite Observation** | Radar Signal | Raw Sentinel-1 SLC data | Honest ESA ground station |
| **S2** | **Data Ingestion** | Raw SLC | Hash-verified SLC file | Pinned SHA-256 manifest |
| **S3** | **Coregistration** | N SLC Frames | Coregistered Stack | Deterministic SNAP processing |
| **S4** | **InSAR Modeling** | Stack | Surface Displacement Map | MintPy v1.5 algorithmic integrity |
| **S5** | **Volume Estimation** | Displacement Map | Float32 Volume Estimate | Geotechnical model validity |
| **S6** | **Fixed-Point Conversion** | Float32 | uint64 volume_v (10^6 scaling) | Formal rounding rule (F1) |
| **S7** | **Commitment Hashing** | volume_v + nonce | volume_commitment_hash | Poseidon(2) collision resistance |
| **S8** | **International Attestation**| volume_commitment_hash | AfDB + WB Signatures | Independent re-computation quorum |
| **S9** | **Ledger Finalization** | Signed Hash | BFT-committed Transaction | 3-of-5 Consensus safety |

### 3. SOFTWARE BILL OF MATERIALS (SBOM)
The following binary hashes are pinned for the production environment:

| Component | Version | SHA-256 |
| :--- | :--- | :--- |
| **SNAP (ESA Toolbox)**| v9.0.0 | `[recorded_at_deployment]` |
| **MintPy** | v1.5.1 | `[recorded_at_deployment]` |
| **Python** | v3.11.x | `[recorded_at_deployment]` |
| **Circom** | v2.2.3 | `[recorded_at_deployment]` |

### 4. KEY MANAGEMENT & SIGNATURES
*   **Signatories:** AfDB (v4) and WB (v5).
*   **Key Storage:** FIPS 140-2 Level 3 HSM (Hardware Security Module).
*   **Verification Rule:** The ledger will reject any `volume_commitment_hash` that lacks co-signatures from both international nodes.

---

# THREAT MODEL: RESOURCE COMMAND PROTOCOL (v1.0)

### 1. ADVERSARY CLASSES

| Class | Capability | Motivation |
| :--- | :--- | :--- |
| **A1: Malicious Operator** | Controls mine inputs | Under-declare production to avoid royalties |
| **A2: Nation-State (Sovereign)** | Controls local validators (v1, v2, v3) | Manipulate revenue or censor specific operators |
| **A3: Corrupted Oracle** | Access to processing pipeline | Inject false volume data into the ledger |
| **A4: Passive Observer** | Ledger read access | Extract sensitive corporate production data |

### 2. SECURITY GOALS
*   **Soundness (SG1):** No invalid proof (underpayment) can be accepted by the BFT network.
*   **Completeness (SG2):** An honest operator can always generate a valid proof for their declaration.
*   **Confidentiality (SG3):** Density and Grade are never revealed to the ledger or validators.
*   **Liveness (SG4):** The system remains operational as long as 4 honest nodes are reachable.

### 3. TRUST BOUNDARIES
*   **The ZK Boundary:** Private inputs (Witnesses) never cross the boundary to the Ledger.
*   **The Oracle Boundary:** Data is untrusted until it reaches Stage 8 (International Co-signature).
*   **The Consensus Boundary:** No single node (including the ZRA) can alter the state of a verified transaction.
