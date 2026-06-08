# Threat Model
## Resource Command ZK Compliance Protocol

**Document:** `Threat_Model.md`  
**Version:** 1.0  
**Classification:** Confidential — Trail of Bits Engagement Pack  
**Prepared by:** Kgosi Capital Holdings (Botswana) Ltd  
**Date:** 6 May 2026  
**Format:** Adapted from Trail of Bits threat modelling methodology

---

## 1. SYSTEM OVERVIEW

Resource Command is a zero-knowledge proof-based mineral royalty compliance protocol deployed for the Republic of Zambia. Operators of open-cast copper mines generate a Groth16 proof demonstrating that their declared royalty payment is arithmetically consistent with their private production data and an independently oracle-committed volume estimate, without revealing the production data to the verifier.

**Core claim:** A valid proof and accepted declaration jointly assert that `tax_paid_usd ≈ (volume_v × density_d × grade_g × 0.06) / 10¹²` within fixed-point rounding tolerance, where `volume_v` is independently committed by a satellite oracle.

**The system does not claim:** That `density_d` and `grade_g` reflect actual physical conditions (RC-03 architectural gap — see §7).

---

## 2. SECURITY GOALS

The following properties are the formal security objectives of the protocol. Each is stated precisely to bound what the threat model must defend.

**G1 — Royalty Soundness.**  
No PPT adversary can cause the BFT validator network to reach state VERIFIED with `tax_paid_usd` less than `⌊(volume_v × density_d × grade_g × 6) / (10¹² × 100)⌋` for the oracle-committed `volume_v`, except with probability negligible in the security parameter κ.

*Relies on:* Groth16 knowledge soundness (A1), Poseidon preimage resistance (A2), honest trusted setup (A3).

**G2 — Volume Integrity.**  
The `volume_v` in any accepted proof reflects the physical mine volume as measured by the independent oracle pipeline, within the cross-validation tolerance τ.

*Relies on:* Oracle pipeline integrity (§3 of `Oracle_Pipeline_Security_Spec.md`), AfDB and WB independence.

**G3 — Production Data Confidentiality.**  
An observer with access to all public data — the proof π, public inputs (`volume_commitment_hash`, `tax_paid_usd`), and all on-ledger records — learns nothing about the operator's private inputs (`density_d`, `grade_g`, `volume_nonce`) beyond what is implied by the public inputs and the circuit's arithmetic.

*Relies on:* Groth16 zero-knowledge property, Poseidon commitment hiding (nonce randomness).

**G4 — BFT Safety.**  
No coalition of at most f=1 Byzantine validator nodes can cause the network to reach VERIFIED for a proof that would be rejected by all honest nodes.

*Relies on:* PBFT safety under partial synchrony; n=5, f=1 quorum structure.

**G5 — Oracle Commitment Binding.**  
An operator cannot submit a proof for a `volume_v` value different from the one committed in the oracle-posted `volume_commitment_hash` for that epoch, except with probability negligible in κ.

*Relies on:* Poseidon preimage resistance (A2); commit-then-prove sequencing invariant (I₁).

---

## 3. CRYPTOGRAPHIC ASSUMPTIONS

| ID | Assumption | Formal Statement |
|---|---|---|
| A1 | Groth16 Knowledge Soundness | ∀ PPT 𝒜: Pr[Verify(π, pub) = 1 ∧ pub ∉ L] ≤ negl(κ) |
| A2 | Poseidon Preimage Resistance | ∀ PPT 𝒜: Pr[𝒜(h) → x : Poseidon(x) = h] ≤ negl(κ) |
| A3 | Trusted Setup Integrity | At least one participant in the Powers of Tau ceremony was honest |
| A4 | Ed25519 Unforgeability | ∀ PPT 𝒜: Pr[𝒜 forges σ without sk] ≤ negl(κ) |
| A5 | BN254 Discrete Log | No PPT adversary solves the discrete log on the BN254 curve |

**Post-quantum caveat:** A1, A4, and A5 do not hold against a quantum adversary with access to Shor's algorithm. See §8.

---

## 4. TRUST BOUNDARIES

Trust boundaries define the lines across which data moves between components with different trust levels. Crossing a trust boundary is an attack surface.

```
══════════════════════════════════════════════════════════════════════
  TB-1: OPERATOR BOUNDARY
  ┌─────────────────────────────────────────────────────────┐
  │  Operator's infrastructure (UNTRUSTED by protocol)      │
  │  • density_d, grade_g declaration                       │
  │  • Witness generation (resource_command_zkp.py)         │
  │  • Proof generation (snarkjs prove)                     │
  │  • Proof submission to BFT network                      │
  └──────────────────────┬──────────────────────────────────┘
                         │ proof π, tax_paid_usd (public)
══════════════════════════╪══════════════════════════════════════════
  TB-2: ORACLE BOUNDARY
  ┌──────────────────────▼──────────────────────────────────┐
  │  Oracle pipeline (SEMI-TRUSTED — mitigated by Stage 8)  │
  │  • Sentinel-1 processing (Stages 1–3)                   │
  │  • Float-to-integer conversion (Stage 5)                │
  │  • Nonce generation (Stage 6)                           │
  │  • Poseidon computation (Stage 7)                       │
  └──────────────────────┬──────────────────────────────────┘
                         │ (volume_v, nonce, h) for co-sign
══════════════════════════╪══════════════════════════════════════════
  TB-3: INTERNATIONAL SIGNATORY BOUNDARY
  ┌──────────────────────▼──────────────────────────────────┐
  │  AfDB + WB nodes (TRUSTED for oracle co-signature)      │
  │  • Independent re-computation of Stages 2–3             │
  │  • Independent Poseidon verification                     │
  │  • HSM-backed Ed25519 signing                           │
  └──────────────────────┬──────────────────────────────────┘
                         │ (h, σ_AfDB, σ_WB)
══════════════════════════╪══════════════════════════════════════════
  TB-4: LEDGER BOUNDARY
  ┌──────────────────────▼──────────────────────────────────┐
  │  BFT Ledger (PUBLIC — tamper-evident append-only log)   │
  │  • volume_commitment_hash posted                         │
  │  • Operator declaration window opens                     │
  │  • Proof submitted and verified by validators            │
  └──────────────────────┬──────────────────────────────────┘
                         │ VERIFIED / REJECTED state
══════════════════════════╪══════════════════════════════════════════
  TB-5: VALIDATOR BOUNDARY (per node)
  ┌──────────────────────▼──────────────────────────────────┐
  │  Each validator node (TRUSTED for its own signatures)   │
  │  • MRC, ZRA, MoF, AfDB, WB — independent nodes         │
  │  • Each runs Groth16 verifier deterministically         │
  │  • BFT protocol over validator-to-validator network     │
  └─────────────────────────────────────────────────────────┘
══════════════════════════════════════════════════════════════════════
```

**TB-1 (Operator):** Entirely untrusted. The entire cryptographic architecture exists to constrain what an untrusted operator can prove. Private inputs cross TB-1 as private witnesses — they are committed to in the proof but never transmitted in the clear.

**TB-2 (Oracle):** Semi-trusted. The oracle operator is trusted to run the correct software, but this trust is verified rather than assumed — by the AfDB/WB re-computation at TB-3. A compromised oracle operator cannot succeed without also compromising both international signatories.

**TB-3 (International signatories):** Trusted for the oracle co-signature. Not trusted to resist collusion with the operator in the BFT proof verification step. Cryptographic attributability (their signatures on any fraudulent commitment are permanently on-ledger) is the deterrent mechanism.

**TB-4 (Ledger):** Trusted for data availability; not trusted for data integrity by any single party. The BFT consensus mechanism ensures that a ledger entry accepted by 3-of-5 validators reflects the honest state with high probability under the f=1 assumption.

**TB-5 (Validators):** Each validator is trusted only for its own protocol-compliant behaviour. No single validator is trusted to be uncorruptible — the BFT structure is designed to tolerate exactly one Byzantine node.

---

## 5. ADVERSARY TABLE

Each adversary class is formally defined by its goal, capabilities, and constraints. The "success condition" states what would constitute a protocol break.

---

### T1 — Malicious Operator

| Field | Description |
|---|---|
| **Goal** | Generate a valid, accepted proof for `tax_paid_usd` < correct royalty |
| **Motivation** | Financial — reduce royalty payment to the ZRA |
| **Capabilities** | Full control of own proving environment; knowledge of circuit structure and all public parameters; can supply arbitrary private witness values (`density_d`, `grade_g`, `rem_*`, `inv_*`); cannot break cryptographic primitives |
| **Constraints** | Cannot alter oracle-committed `volume_commitment_hash`; cannot find Poseidon preimage for a false `volume_v`; cannot forge BFT validator signatures |
| **Success condition** | VERIFIED state reached with `tax_paid_usd` < correct royalty |
| **Primary attack vectors** | Zero-value input (density=0 or grade=0); trivial floor (density=1, grade=1); RC-03 abuse (self-declare low density/grade) |
| **Mitigations** | Multiplicative inverse gates close zero-value attack; `Num2Bits` range gates bound inputs; Groth16 soundness prevents accepting proofs for out-of-range values |
| **Residual risk** | RC-03: Operator can self-declare low-but-nonzero density/grade within circuit bounds; no cryptographic mitigation exists without oracle extension |

---

### T2 — Corrupted Single Validator

*Applies to any single node: MRC, ZRA, MoF, AfDB, or WB.*

| Field | Description |
|---|---|
| **Goal** | Force acceptance of a fraudulent proof; OR deny acceptance of a valid proof (liveness attack) |
| **Motivation** | Regulatory capture; bribery; national interest |
| **Capabilities** | Full control of one validator node; can send arbitrary PREPARE/COMMIT messages; can refuse to participate; can attempt to manipulate public inputs visible to the node |
| **Constraints** | Cannot forge signatures of other validators; cannot produce a proof that fails Groth16 verification on honest nodes; cannot alter oracle commitment without AfDB+WB collusion |
| **Success condition (safety)** | BFT network reaches VERIFIED for a proof that Verify() = 0 on honest nodes |
| **Success condition (liveness)** | BFT network cannot reach VERIFIED or REJECTED for any proof |
| **Safety analysis** | Verify() is deterministic; honest nodes compute the same result; single Byzantine node cannot assemble a 3-of-5 COMMIT(ACCEPT) quorum for a false proof without two honest node co-signatures |
| **Liveness analysis** | A single Byzantine node refusing to participate leaves 4 honest nodes — above the 3-of-5 quorum threshold. Liveness is preserved post-GST. |
| **Mitigations** | BFT quorum structure; Groth16 deterministic verification; PBFT view-change for liveness recovery |
| **Residual risk** | Liveness can be degraded (not eliminated) by a single Byzantine node before GST under partial synchrony |

---

### T3 — Corrupted Oracle Operator

| Field | Description |
|---|---|
| **Goal** | Commit a `volume_commitment_hash` that binds a volume lower than the actual physical volume |
| **Motivation** | Collusion with operator; bribery |
| **Capabilities** | Full control of the oracle processing pipeline (Stages 1–7); can modify software, alter intermediate data, substitute processing results |
| **Constraints** | Cannot post commitment without AfDB+WB co-signatures; cannot prevent AfDB/WB from independently re-running the computation; cannot forge AfDB/WB Ed25519 signatures |
| **Success condition** | `volume_commitment_hash` for a fraudulent `volume_v` is finalised on-ledger with valid AfDB+WB co-signatures |
| **Attack vector** | Modify Stage 3 volume estimate before Stage 8; present fraudulent `(volume_v, nonce, h)` to AfDB/WB for signing |
| **Why this fails** | AfDB and WB independently re-run Stages 2–3 and verify `h' = Poseidon(volume_v, nonce)`. A fraudulent `volume_v` that diverges from independent re-computation by more than τ_intl will cause the verification to fail. |
| **Mitigations** | Stage 8 independent re-computation; Stage 4 UAV LiDAR cross-validation; SBOM hash-pinning prevents silent software substitution |
| **Residual risk** | If oracle operator and both AfDB+WB are simultaneously compromised (T5), this attack succeeds. This requires compromise of three separate, internationally independent institutions. |

---

### T4 — Corrupted Single International Signatory (AfDB or WB)

| Field | Description |
|---|---|
| **Goal** | Co-sign a fraudulent oracle commitment; OR refuse to co-sign legitimate commitments (liveness attack) |
| **Motivation** | Political pressure; bribery; nation-state coercion |
| **Capabilities** | Full control of one international signatory node; can sign any hash; can refuse to sign |
| **Constraints** | **Both** AfDB and WB signatures are required for ledger finalisation; a single corrupted signatory cannot post a fraudulent commitment alone |
| **Success condition (safety)** | Fraudulent commitment finalised on-ledger |
| **Success condition (liveness)** | Legitimate commitment cannot be posted (declaration window never opens) |
| **Safety analysis** | Requires T3 (corrupted oracle) + T4 (corrupted signatory) + the other international node. Three separate institutions. Safety holds against any single international signatory corruption. |
| **Liveness analysis** | A single corrupted signatory refusing to sign blocks the oracle commitment pipeline. The declaration window cannot open. Liveness fails for the commitment stage. |
| **Mitigations** | Dual-signature requirement; key rotation on suspected compromise |
| **Residual risk** | Liveness attack by a single international signatory has no cryptographic mitigation — it is addressed by legal/governance mechanisms (MOU dispute resolution) |

---

### T5 — Sovereign Collusion Coalition (MRC + ZRA + MoF)

| Field | Description |
|---|---|
| **Goal** | Override BFT consensus to accept fraudulent declarations; extract private operator data |
| **Motivation** | Corruption; sovereign policy capture; fiscal manipulation |
| **Capabilities** | Control of 3 of 5 validator nodes (f=3 for this coalition — exceeds the BFT tolerance of f=1); can assemble a 3-of-5 COMMIT quorum; can observe all validator-to-validator network traffic |
| **Constraints** | Cannot produce a valid Groth16 proof for a false statement (A1); cannot forge AfDB/WB signatures on oracle commitments; all coalition signatures are permanently on-ledger |
| **Success condition (BFT fraud)** | 3 sovereign nodes COMMIT(ACCEPT) for a proof with Verify() = 0 on honest nodes |
| **Why partial mitigation holds** | Groth16 soundness: no false proof exists for a false statement. Even if MRC+ZRA+MoF vote COMMIT(ACCEPT), the proof they are voting on must satisfy Verify() = 1 — which requires the operator to know a valid witness. For Verify() = 1 with false fiscal claim, the operator would need to exploit an under-constrained witness — a circuit-level bug. V1.4 has no known exploitable under-constrained witnesses. |
| **Real remaining attack surface** | RC-03: The coalition could pressure an operator to declare false density/grade (within circuit bounds), accept the resulting valid proof, and direct the verified declaration into the ZRA's accounting. The proof is cryptographically sound; the fraud is at the governance layer. |
| **Mitigations** | Cryptographic attributability: any fraudulent COMMIT bears all three sovereigns' signatures. Independent AfDB/WB nodes observe all BFT messages. Fraud is attributable to specific signatories with cryptographic certainty. |
| **Residual risk** | High at governance layer; low at cryptographic layer. The cryptographic guarantees hold under A1. Governance-layer fraud requires three sovereign institutions to collectively commit an attributable act. |

---

### T6 — Nation-State Adversary

| Field | Description |
|---|---|
| **Goal** | Break cryptographic primitives to forge proofs; compromise satellite data at source; deploy long-term persistent access in oracle infrastructure |
| **Motivation** | Strategic intelligence; economic benefit; regulatory manipulation |
| **Capabilities** | Large-scale computational resources; potential to compromise ESA Copernicus data pipeline; potential to compromise key infrastructure (HSMs, network equipment); advanced persistent threat (APT) capabilities; eventually, quantum computing |
| **Constraints** | Cannot break A1–A5 under classical computing; quantum computer capable of breaking elliptic curves does not yet exist at sufficient scale |
| **Attack vectors** | (a) Compromise ESA Copernicus data feed; (b) Long-term infiltration of oracle operator network; (c) Side-channel attack on HSM to extract signing keys; (d) Quantum attack on BN254 discrete log (future) |
| **Current mitigations** | (a) Multi-party independent download from Copernicus; AfDB+WB independent verification; (b) Air-gapped processing environment; SBOM; (c) FIPS 140-2 Level 3 HSM; (d) None — see §8 |
| **Residual risk** | The system is not designed to resist a nation-state adversary with quantum computing capability. This is a known limitation of all current ZK proof systems. |

---

### T7 — Passive Observer / Privacy Adversary

| Field | Description |
|---|---|
| **Goal** | Learn private production data (volume, density, grade) from public proof and on-ledger data |
| **Motivation** | Competitive intelligence; corporate espionage |
| **Capabilities** | Access to all public ledger data: π, `volume_commitment_hash`, `tax_paid_usd`, all BFT messages, nonce (published post-commitment) |
| **Constraints** | Cannot learn private witnesses from a Groth16 proof (zero-knowledge property); cannot reverse Poseidon commitment without knowing `volume_v` and nonce |
| **Attack vectors** | Brute-force over plausible `volume_v` domain using published nonce + commitment hash |
| **Why brute-force is hard** | After commitment is posted, the nonce is not yet public. After the declaration window, the nonce is published. At that point, `volume_v` can in principle be searched. But `volume_v ∈ [1, 2^40)` — a search space of 10^12. Poseidon computation at ~10^9 hashes/second implies ~10^3 seconds (17 minutes) of computation. The nonce provides only computational hiding, not information-theoretic hiding, for a resource-limited adversary. This is a **known limitation** of commitment hiding for bounded domains. |
| **Mitigations** | The nonce is published only after the commitment is finalised; by that point, the declaration window is also closed and the proof has been submitted. Learning `volume_v` post-hoc from the commitment gives the adversary no protocol-level advantage. |
| **Residual risk** | A well-resourced adversary can learn `volume_v` from the public nonce and commitment hash post-declaration. Volume is not the primary commercial secret; `density_d` and `grade_g` are not committed and remain private. |

---

### T8 — Network Infrastructure Adversary (Eclipse Attack)

| Field | Description |
|---|---|
| **Goal** | Isolate specific validators to force a 3-node quorum on a fraudulent proof |
| **Motivation** | Nation-state manipulation; coordinated liveness/safety failure |
| **Capabilities** | BGP route hijacking; control of Tier-1 transit or national ISP infrastructure |
| **Constraints** | Cannot forge cryptographic signatures; relies on existing circuit/compiler vulnerabilities |
| **Attack vector** | Hijack BGP routes to AfDB and WB during Stage 9 finalization, isolating them from {MRC, ZRA, MoF}. The domestic nodes form a valid 3-of-5 PBFT quorum. |
| **Mitigations** | **Heterogeneous Quorum Requirement:** The BFT consensus logic enforces that a valid quorum of 3 MUST contain at least one international node (AfDB or WB). If both are eclipsed, the network halts (safe liveness failure). |
| **Residual risk** | An eclipse attack can still cause a liveness failure (denial of service), but cannot cause a safety failure (acceptance of fraud). |

---

### T9 — Supply Chain Adversary (Compiler Backdoor)

| Field | Description |
|---|---|
| **Goal** | Embed a backdoor in the `.r1cs` circuit to bypass constraint logic |
| **Motivation** | Subvert ZK soundness without altering the audited `.circom` source code |
| **Capabilities** | "Trusting Trust" attack on the `circom` binary; compromise of the operator's build environment |
| **Attack vector** | A malicious compiler binary silently modifies the `density_d * inv_density_d === 1` constraint in the emitted R1CS, allowing a "magic number" bypass for zero-density. |
| **Mitigations** | **Multi-Party Deterministic Compilation (MPDC):** Detailed in `Trusted_Setup_Specification.md`. AfDB, WB, and ZRA independently compile the circuit from source. The Phase 2 setup only proceeds if `H_AfDB == H_WB == H_ZRA`. |
| **Residual risk** | Requires simultaneous compromise of three independent international IT supply chains to defeat. |

---

### T10 — State Actor BGP Manipulation (Chinese Routing Subversion)

| Field | Description |
|---|---|
| **Goal** | Partition AfDB from the network to enable a 3-node Zambian quorum to finalise a zero-royalty epoch |
| **Motivation** | Protect CNMC (China Nonferrous Metal Mining Group) Zambian royalty exposure |
| **Capabilities** | Access to routing decisions at ACE Abidjan landing station or West African internet exchange points |
| **Constraints** | Cannot forge AfDB signatures; relies on Zambian node collusion (T5) plus circuit exploit |
| **Attack vector** | Triggered by announcement of Resource Command deployment affecting CNMC. BGP prefix injection isolates AfDB during the 10-minute Stage 9 finalisation window. |
| **Mitigations** | **Heterogeneous Quorum Requirement (HQR):** Requires simultaneous eclipse of AfDB AND WB. RPKI route hardening coordinated directly with AfDB IT. |
| **Residual risk** | Simultaneous multi-continent BGP hijacking is difficult but within the capability of a motivated state actor. |

---

### T11 — US Jurisdiction Intelligence Access (CLOUD Act)

| Field | Description |
|---|---|
| **Goal** | Reconstruct timing, traffic patterns, and connection metadata from the World Bank node's network layer |
| **Motivation** | Geopolitical intelligence gathering; potential leverage if US-Zambia relations deteriorate |
| **Capabilities** | Compelled disclosure via US National Security Letters to WB's ISP infrastructure in Washington DC |
| **Constraints** | WB data protected by International Organizations Immunities Act; cannot compel WB directly |
| **Attack vector** | US government bypasses WB and compels ISP to disclose network traffic metadata, bypassing WB diplomatic immunity at the infrastructure layer. |
| **Mitigations** | **Content Encryption:** TLS and WireGuard overlay protect the payload content. Exposure is strictly limited to traffic metadata. |
| **Residual risk** | Accepted as passive/informational threat given general US policy alignment with protocol objectives. |

---

## 6. ATTACK SURFACE ENUMERATION

| Surface | Location | Controls | Residual |
|---|---|---|---|
| Witness substitution | TB-1 (operator) | Groth16 soundness; circuit gates | RC-03 gap |
| Zero-value inputs | TB-1 | Multiplicative inverse gates | Trivial-floor (d=1) |
| Remainder manipulation | TB-1 | Num2Bits + LessThan bounds | Closed |
| Field wrap-around | TB-1 | Num2Bits range checks on all inputs | Closed |
| Volume substitution | TB-2 (oracle) | Poseidon preimage resistance; commit-then-prove | Closed under A2 |
| Oracle software compromise | TB-2 | SBOM hash-pinning; air-gap; AfDB/WB re-run | T3 residual |
| Float-to-int manipulation | TB-2 | Formal specification (§4 of Oracle spec) | ±0.5 m³ rounding |
| Fraudulent oracle commitment | TB-2/TB-3 | Dual AfDB+WB co-signature requirement | T3+T4 residual |
| Single validator corruption | TB-5 | BFT f=1 tolerance; deterministic Verify() | Liveness degradation |
| Sovereign coalition (3 nodes) | TB-5 | Cryptographic attributability; A1 soundness | RC-03 governance |
| Side-channel on prover | TB-1 | Not yet analysed (ToB scope item 6) | Open |
| Trusted setup compromise | Protocol | Hermez ceremony integrity; at-least-one-honest | Open — ceremony not yet done |
| Verification key integrity | TB-5 | Distribution via MPDC hash ceremony (Trusted_Setup_Spec.md) | Closed |
| Compiler binary integrity | Protocol | Multi-Party Deterministic Compilation (MPDC) | T9 residual |
| BGP/Routing infrastructure | Network | Heterogeneous Quorum Requirement (intl node required) | Liveness failure |
---

## 7. RC-03 FORMAL SCOPE BOUNDARY

**Definition (RC-03).** The protocol's cryptographic guarantees are conditioned on the declared inputs (`density_d`, `grade_g`) being honestly chosen by the operator. The circuit does not, and cannot without oracle extension, verify that these values correspond to physical reality.

**Formal statement:** G1 (Royalty Soundness) guarantees that `tax_paid_usd` is arithmetically correct relative to the **declared** `density_d` and `grade_g`. It does not guarantee correctness relative to the **true** density and grade of the deposit.

**Consequence:** An operator who honestly commits a true volume (enforced by G2 and G5) but dishonestly declares a low density or low grade can generate a valid proof for an understated royalty.

**Attack bound:** The maximum underpayment achievable via RC-03 is:

```
Max underpayment = tax_correct - tax_declared
                 = volume_v × (density_true - density_declared) × grade_declared × 0.06 / 10^12
                   + volume_v × density_declared × (grade_true - grade_declared) × 0.06 / 10^12
```

This is proportional to the gap between true and declared values. An operator declaring `density_d = 1` against a true density of 2,700,000 achieves near-total royalty elimination. An operator declaring a 10% understatement of density achieves a 10% royalty reduction.

**Why G2 (Volume Integrity) provides partial mitigation:** If volume is correctly committed, the adversary's choice variable is reduced to `(density_d, grade_g)`. Without oracle commitment of these values, the system is providing assurance on approximately one-third of the fiscal inputs.

**Governance mitigations operational during Phase 3:** The MRC is the licensing authority for mining claims and requires submission of annual assay reports. Cross-referencing the declared `density_d` and `grade_g` against licensed assay data is a regulatory process that operates outside the ZK proof system but provides a governance check on the RC-03 attack surface.

---

## 8. POST-QUANTUM CONSIDERATIONS

The following protocol components are broken by a cryptographically relevant quantum computer (CRQC):

| Component | Broken by | Impact |
|---|---|---|
| BN254 elliptic curve | Shor's algorithm | Groth16 proofs forgeable; A1 fails |
| Ed25519 signing | Shor's algorithm | Validator and oracle signatures forgeable; A4 fails |
| Poseidon hash (preimage) | Grover's algorithm (quadratic speedup only) | Effective security halved: 128-bit → 64-bit classical equivalent. Not broken by near-term quantum. |

**Current posture:** No post-quantum mitigations are deployed. This is consistent with the industry standard for all deployed ZK proof systems as of this document's date.

**Migration path:** Post-quantum signature schemes (CRYSTALS-Dilithium, SPHINCS+) can replace Ed25519 for validator and oracle signatures without requiring circuit changes. Post-quantum ZK proof systems are an active research area; no production-ready alternative to Groth16/BN254 with comparable constraint efficiency is available. The system will require re-engineering when a post-quantum ZK primitive becomes standardised.

---

## 9. OUT-OF-SCOPE CLAIMS

The following are explicitly **not** security properties of the current system:

1. **Oracle density and grade verification.** The system does not claim to verify declared density or grade against physical reality (RC-03).

2. **Operator identity binding.** The proof does not bind to an operator identity. Any party with knowledge of the correct private witnesses and the oracle-committed hash can generate a valid proof.

3. **Royalty payment enforcement.** The system verifies that a declared payment is arithmetically correct given the declared inputs. It does not enforce that the declared `tax_paid_usd` has actually been remitted to the ZRA.

4. **Post-quantum security.** As documented in §8.

5. **Byzantine tolerance beyond f=1.** Safety and liveness against two or more simultaneous Byzantine validator nodes is not claimed. The T5 (sovereign collusion) scenario exceeds the formal BFT tolerance.

6. **Side-channel resistance of the prover.** Not yet assessed. This is Trail of Bits audit scope item 6.

---

*Kgosi Capital Holdings (Botswana) Ltd · Confidential · 6 May 2026*
