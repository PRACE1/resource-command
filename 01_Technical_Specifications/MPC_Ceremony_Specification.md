# SOVEREIGN MPC CEREMONY SPECIFICATION
## Document ID: RC-CEREMONY-001
**Date:** 6 May 2026
**Classification:** Confidential — Internal Implementation Spec

---

### 1. OVERVIEW
This document defines the choreography and security architecture for the Resource Command Phase 2 Multi-Party Computation (MPC) Trusted Setup Ceremony. The objective is to generate the `compliance_0005.zkey` and `verification_key.json` for the `compliance.circom` v1.5 circuit with absolute cryptographic integrity.

### 2. THE PARTICIPANT SEQUENCE
The sequential contribution of entropy ($\tau$) is intentionally structured to maximize the security guarantee. The sequence is:
1.  **MoF (Zambia)**
2.  **ZRA (Zambia)**
3.  **MRC (Zambia)**
4.  **AfDB (Côte d'Ivoire)**
5.  **World Bank (United States)**

**Architectural Rationale:**
The international participants contribute last. The WB's contribution ($\tau_5$) is the final term in the accumulator. Because the Groth16 setup is secure as long as *at least one* participant is honest, placing the World Bank last ensures that even if all sovereign Zambian nodes colluded to retain their toxic waste, the WB's independent destruction of its entropy guarantees the integrity of the entire circuit.

### 3. THE COORDINATOR NODE
The central `snarkjs` coordinator node manages the exchange of contribution files.
*   **Hosting:** Exoscale (Switzerland). 
*   **Why Exoscale?** It is a European-sovereign cloud provider, explicitly insulated from US CLOUD Act subpoenas. This satisfies the legal requirements of the international DFIs while remaining neutral to the Zambian state.
*   **Access Control:** Administrative access to the coordinator node is secured via a **2-of-3 Shamir Secret Sharing** scheme distributed among **AfDB IT Security, WB ITS, and Zambia ZICTA**. Kgosi Capital explicitly holds no administrative access, maintaining total sovereign and institutional neutrality. No single party can unilaterally modify the coordinator state.

### 4. THE TECHNICAL REHEARSAL (July 1, 2026)
A full-dress rehearsal is mandatory.
*   **Execution:** The 5 parties will execute the protocol using a dummy `.r1cs` circuit and a test `ptau` file.
*   **Objective:** To surface and resolve strict institutional firewall policies, USB transfer restrictions within air-gapped environments, and timezone coordination failures before the live ceremony.

### 5. DIPLOMATIC CRITICAL PATH
The cryptography is secondary to the diplomacy in terms of timeline risk.
*   **Milestone 1:** Ceremony Participation Agreements (CPAs) transmitted to WB and AfDB legal counsel by **June 2, 2026**.
*   **Milestone 2:** CPA Sign-off deadline on **June 23, 2026**.
*   **Milestone 3:** Live Ceremony Window opens **September 15, 2026**.

*Strategic Reframing: By intentionally targeting September, we decouple the ceremony from the high-risk HSM hardware procurement timeline (10-16 weeks) and reframe the event as a post-election, sovereign inauguration of the new government's compliance architecture.*
