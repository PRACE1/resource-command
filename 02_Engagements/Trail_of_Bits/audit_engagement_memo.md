# MEMORANDUM OF ENGAGEMENT: TECHNICAL AUDIT & CIRCUIT VERIFICATION
**To:** Trail of Bits Engineering Team  
**From:** Kgosi Capital Zambia Ltd  
**Date:** 4 May 2026  
**Subject:** Architectural Review of Resource Command ZKP Infrastructure

---

## 1. Engagement Scope
Kgosi Capital Zambia Ltd hereby commissions a preliminary architectural design review of the **Resource Command** mineral verification platform. The audit shall focus on the following core components:

### 1.1 Cryptographic Circuit Integrity (ZKP)
*   **Verification of R1CS Constraints:** Review of the BN254 field implementation to ensure soundness and completeness.
*   **Binding Verification:** Audit of the 'Truth Anchor' (Constraint 0) to ensure immutable binding between InSAR telemetry and the generated proof.
*   **Witness Security:** Identification of potential under-constrained witness vulnerabilities.

### 1.2 Consensus & BFT Safety
*   **Protocol Audit:** Review of the partial-synchrony BFT implementation against the established $n \ge 3f + 1$ bounds.
*   **State Machine Verification:** Assessment of validator node resilience in multi-jurisdictional network conditions.

---

## 2. Deliverables
Trail of Bits is requested to provide:
1.  **A Preliminary Design Review Report:** Outlining critical vulnerabilities or logic gaps.
2.  **An Engagement Letter for Third-Party Review:** A one-page attestation of the audit-in-progress status for presentation to the Zambian Minerals Regulation Commission (MRC) and KoBold Metals.

---

## 3. Confidentiality
This engagement is subject to a strict Non-Disclosure Agreement (NDA). All circuit logic and source code remain the exclusive Intellectual Property of Kgosi Capital Holdings (Botswana) Ltd.
