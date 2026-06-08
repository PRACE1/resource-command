# RESOURCE COMMAND: LEGAL & ESCROW RISK ARCHITECTURE
## Due Diligence Mandate

This document outlines the five critical legal and operational contracts required to protect the sovereign legitimacy, commercial viability, and escrow continuity of the Resource Command protocol. Failure to execute these specific clauses before capitalization or deployment exposes the project to fatal due diligence failure.

---

### 1. The Dividend Distribution Mandate
**Risk:** If the Zambian OpCo does not distribute meaningful dividends, the political shield provided by NAPSA and ZRA equity collapses entirely. The OpCo cannot simply maximize the Botswana licensing fee to extract all profit.
**Requirement:** 
- The Big 4 Transfer Pricing Study must specifically target a defensible fee structure that leaves the Zambian OpCo with a **20% to 30% net operating margin**. 
- The Shareholders' Agreement must include a **minimum dividend distribution covenant**. Without this explicit clause, Kgosi Capital and the local partner could legally vote to retain all earnings, making the sovereign equity worthless.

### 2. The HSM Escrow Activation Protocol (Re-Ceremony Timeline)
**Risk:** The source code escrow is legally complete but operationally paralyzed. Ed25519 validator private keys inside the Thales Luna HSMs are non-extractable. If the Zambian government activates the escrow, they cannot simply "resume" the network with the existing state.
**Requirement:** The Swiss Escrow Agreement must explicitly disclose the operational reality of a breach:
- Escrow activation gives the MRC the Rust source code and the administrative Shamir shards for the HSM hardware.
- It triggers a mandatory **re-ceremony (Phase 2 MPC)** to generate fresh validator keys across all nodes.
- The contract must legally disclose this **4-to-6 week reconstitution timeline** to ensure MRC lawyers cannot later claim the escrow was practically unusable in an emergency.
- The protocol must explicitly define the cross-jurisdictional physical travel and credential presentation required to access the distributed physical HSMs (Lusaka, Abidjan, DC, Geneva).

### 3. Continuous Escrow Verification
**Risk:** Standard software escrows fail because the deposited code becomes stale. The MRC activates the escrow in 2029 and receives the useless v1.0 source code from 2026.
**Requirement:** The Escrow Agreement must contain three non-standard clauses:
- **Mandatory Re-Deposit Trigger:** Any change to the R1CS circuit, consensus logic, or HSM integration mandates a re-deposit within 30 days (90 days for minor patches).
- **Version Verification:** The escrow agent (e.g., NCC Group) must independently confirm that the deposited code compiles and produces a binary matching the published production manifest hash.
- **Production Match Attestation:** Kgosi Capital must sign quarterly attestations confirming the deployed binary matches the version in the Swiss vault.

### 4. ZRA Regulatory Conflict of Interest
**Risk:** The Zambia Revenue Authority (ZRA) is the tax authority examining the arm's-length validity of the Botswana licensing fee. It is simultaneously an equity shareholder in the OpCo paying that fee, creating an inherent conflict between its regulatory mandate and its dividend interests.
**Requirement:** A formal legal opinion from a Zambian constitutional/corporate lawyer must be secured confirming that the ZRA Act and Zambian Company Law permit ZRA to hold equity in an entity it actively regulates. This must be secured **before** the cap table is filed with PACRA.

---

### Priority Execution Order
| Contract | Risk If Delayed | Must Complete Before |
|---|---|---|
| Big 4 Transfer Pricing Study | OpCo capitalisation is legally exposed without it | Before any equity is issued |
| Shareholders' Agreement (Minimum Dividend Covenant) | NAPSA/ZRA equity becomes worthless | Before any equity is issued |
| ZRA equity conflict of interest opinion | Cap table may be legally impermissible | Before filing with PACRA |
| Swiss Escrow Agreement (with HSM shards + continuous verification) | Escrow is commercially unenforceable | Before MRC signs the service agreement |
| HSM Escrow Activation Protocol | Escrow is operationally unusable | Before ceremony date |
