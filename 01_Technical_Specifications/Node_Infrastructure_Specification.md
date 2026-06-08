# SOVEREIGN NODE INFRASTRUCTURE SPECIFICATION
## Document ID: RC-INFRA-001
**Date:** 6 May 2026
**Classification:** Confidential — Internal Implementation Spec

---

### 1. OVERVIEW
This document defines the deployment architecture for the 5-node PBFT validator network (MRC, ZRA, MoF, AfDB, WB) that enforces the Resource Command v1.4 zero-knowledge protocol. The infrastructure is designed to survive state-level network isolation and physical node seizure.

### 2. CONSENSUS ENGINE: RUST STACK
The PBFT consensus client is written exclusively in **Rust**.
*   **Why Rust?** Garbage collection languages (like Go) introduce non-deterministic latency spikes. In a PBFT environment with strict phase timeouts (e.g., 2000ms), a 50ms GC pause degrades tolerance budgets and risks liveness failures. Rust provides deterministic memory safety and predictable timing guarantees.

### 3. CRYPTOGRAPHIC BINDING
*   **Compile-Time VK Hardcoding:** The verification key hash (`EXPECTED_VK_HASH`) generated during the MPC Trusted Setup must be hardcoded into the Rust binary at compile time. 
*   **Threat Mitigated:** A runtime load of `verification_key.json` allows an attacker with root filesystem access to replace the VK and force the node to verify fraudulent proofs. Compile-time binding ensures the binary and the VK are mathematically inseparable.

### 4. KEY MANAGEMENT: FIPS 140-2 LEVEL 3 HSM
*   **Hardware:** Thales Luna Network HSM (or equivalent FIPS 140-2 Level 3 device).
*   **Integration:** The Rust consensus client interfaces with the HSM via PKCS#11. The Ed25519 validator private keys never reside in the host machine's RAM. The client submits the BFT phase digest to the HSM, and the HSM returns the signature.

### 5. INSTITUTIONAL DEFENSE: CONSENSUS HEALTH MONITOR
A dedicated, isolated Rust process runs parallel to the consensus engine.
*   **Function:** It continuously monitors signing behavior and quorum participation. 
*   **Governance Halt:** If sovereign nodes are seized by a hostile actor, the network can be halted. However, this halt mechanism is subject to the **Heterogeneous Quorum Requirement (HQR)**. A governance halt vote requires `Q ∩ {AfDB, WB} ≠ ∅`. No single party (including Kgosi Capital) possesses a unilateral kill-switch.
*   **HQR Liveness Deadlock Defense:** To prevent permanent liveness failures during a partial BGP eclipse where view-changes succeed but commits fail due to HQR, the monitor enforces `HQR_DEADLOCK_HALT_THRESHOLD = 5`. If 5 consecutive rounds achieve a valid PBFT quorum but fail the HQR, the monitor triggers an automated, cryptographically signed Governance Halt.

### 6. GOVERNANCE RATE UPDATE PROTOCOL
The v1.5 ZK architecture decouples the statutory tax rate from the cryptographic circuit. The BFT verifier must check the proof's `royalty_rate_bps` against the `governanceLedger.CurrentStatutoryRate()`. To update this ledger rate:
1. Zambian Parliament passes a statutory instrument amending the royalty rate.
2. ZRA submits a signed `GovernanceProposal` transaction to the BFT network: `{ proposal_type: ROYALTY_RATE_UPDATE, new_rate_bps: X, legal_reference: "SI 2027/004" }`.
3. BFT validators verify the ZRA signature and the legal reference.
4. A governance vote proceeds under HQR (requires 3-of-5 quorum with AfDB or WB).
5. On acceptance, the new rate is appended to the governance ledger, and all subsequent `ProofSubmissions` must use the new rate.

### 7. PROCUREMENT PATH & TIMELINE (CRITICAL)
*   **Hardware Lead Time:** Thales Luna HSM delivery to sub-Saharan Africa carries an estimated 8-week lead time.
*   **Action Required:** Orders must be placed prior to May 13 to clear the June 3 deployment window. If the AfDB possesses existing FIPS 140-2 L3 infrastructure in Abidjan, it must be leveraged immediately to de-risk the critical path.
