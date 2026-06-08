# TRUSTED SETUP & MPDC SPECIFICATION (v1.0)
## Resource Command — Multi-Party Deterministic Compilation

### 1. OVERVIEW
This document specifies the Phase 2 Specialization (Trusted Setup) ceremony for the Resource Command `compliance.circom` v1.4 protocol, and the **Multi-Party Deterministic Compilation (MPDC)** requirement that precedes it. 

The MPDC protocol is the primary defense against "Trusting Trust" compiler supply chain attacks.

### 2. THE COMPILER THREAT MODEL
A compromised `circom` binary can silently rewrite the R1CS constraints during compilation (e.g., removing the `density_d * inv_density_d === 1` non-zero check). A verification key (VK) derived from a backdoored R1CS will accept fraudulent proofs. This attack bypasses all circuit-level logic.

### 3. THE MPDC CEREMONY (Phase 0)
Because the Circom compiler is deterministic, we enforce supply-chain integrity at the consensus layer before any trusted setup begins.

**Step 1: Source Distribution**
The canonical `compliance.circom` source code (pinned via SHA-256 in the engagement pack) is distributed to all validators.

**Step 2: Independent Compilation**
Three independent nodes (ZRA, AfDB, World Bank) must compile the circuit from source on their own air-gapped infrastructure using verified rust toolchains.
*   `circom compliance.circom --r1cs --wasm --sym`

**Step 3: Quorum Hash Verification**
The parties independently calculate the SHA-256 hash of the resulting `compliance.r1cs` file and exchange them over a secure out-of-band channel.
*   **Safety Rule:** The Phase 2 Trusted Setup is HALTED unless $H_{ZRA} == H_{AfDB} == H_{WB}$.

### 4. PHASE 1: POWERS OF TAU
Resource Command utilizes the canonical Hermez Network Phase 1 Powers of Tau ceremony (`ptau`).
*   **File:** `powersOfTau28_hez_final_16.ptau`
*   **Integrity:** The SHA-256 hash of the ptau file must be verified by all participating BFT nodes prior to Phase 2.

### 5. PHASE 2: CIRCUIT SPECIALIZATION
Once the MPDC hash ceremony confirms the integrity of the R1CS, the protocol executes a multi-party computation (MPC) for the Phase 2 Specialization (Groth16 setup).

*   **Participants:** MRC, ZRA, MoF, AfDB, WB.
*   **Requirement:** At least one participant must be honest and securely destroy their toxic waste (the random entropy `τ`). The participation of both the AfDB and the World Bank guarantees this property against sovereign-level collusion.
*   **Output:** `compliance_0005.zkey` (Final ZKey) and `verification_key.json`.

### 6. VERIFICATION KEY DEPLOYMENT
The final `verification_key.json` is deployed to the BFT validator nodes. The system is now locked. An operator using a backdoored compiler locally will produce a proof that is invalid against the MPDC-derived VK.
