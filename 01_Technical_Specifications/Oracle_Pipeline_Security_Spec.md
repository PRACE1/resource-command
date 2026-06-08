# Oracle Pipeline Security Specification
## Resource Command — Attestation Chain & Supply Chain Integrity

**Document:** `Oracle_Pipeline_Security_Spec.md`  
**Version:** 1.0  
**Classification:** Confidential — Trail of Bits Engagement Pack  
**Prepared by:** Kgosi Capital Holdings (Botswana) Ltd  
**Date:** 6 May 2026

---

## 1. PURPOSE AND SCOPE

This document specifies the complete attestation chain from physical satellite observation to the finalised `volume_commitment_hash` posted to the Resource Command ledger. It is intended to satisfy the supply chain integrity review requested in the Trail of Bits engagement scope (Item 3: Fixed-Point Arithmetic Correctness) and specifically to address the oracle pipeline threat surface identified as RC-03 in the internal adversarial audit.

**In scope:**
- Every computational transformation from raw SAR data to committed field element
- Software stack integrity controls (version pinning, hash verification)
- Float-to-integer conversion specification and its interaction with the circuit's fixed-point encoding
- Key management for the AfDB and World Bank co-signatories
- Trust assumptions and their failure modes at each pipeline stage

**Out of scope:**
- The ZK circuit itself (`compliance.circom`) — covered in the primary audit target
- BFT consensus protocol — covered separately in the Technical Pre-Read
- Operator witness generation (density, grade declarations) — this is the RC-03 architectural boundary

---

## 2. ATTESTATION CHAIN OVERVIEW

The attestation chain consists of nine stages. Each stage has defined inputs, outputs, trust assumptions, and integrity controls. A compromise at any stage that is not mitigated by a downstream control constitutes an exploitable vulnerability.

```
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 1: ESA Copernicus — Sentinel-1 SLC Data Acquisition         │
│  Trust: ESA data integrity; Copernicus Open Access Hub download     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ SLC files (SHA-256 verified)
┌──────────────────────────────▼──────────────────────────────────────┐
│  STAGE 2: SAR Preprocessing (ESA SNAP v10.x)                       │
│  Trust: Pinned binary hash; air-gapped processing environment       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Coregistered SLC stack
┌──────────────────────────────▼──────────────────────────────────────┐
│  STAGE 3: PS-InSAR / DEM Differencing (MintPy v1.5.x)             │
│  Trust: Pinned binary hash; deterministic algorithm execution       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Displacement map / ΔV_float (m³)
┌──────────────────────────────▼──────────────────────────────────────┐
│  STAGE 4: UAV LiDAR Cross-Validation                                │
│  Trust: Independent sensor; requires |ΔV_lidar - ΔV_insar| ≤ τ    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Validated V_float (m³)
┌──────────────────────────────▼──────────────────────────────────────┐
│  STAGE 5: Float-to-Integer Conversion                               │
│  Trust: Deterministic; formally specified (§4)                      │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ volume_v ∈ ℤ, volume_v ∈ [1, 2^40)
┌──────────────────────────────▼──────────────────────────────────────┐
│  STAGE 6: Nonce Generation                                          │
│  Trust: CSPRNG; recorded and published post-commitment              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ (volume_v, nonce)
┌──────────────────────────────▼──────────────────────────────────────┐
│  STAGE 7: Poseidon Hash Computation                                 │
│  Trust: Pinned reference implementation (circomlibjs); HSM-hosted   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ h = Poseidon(volume_v, nonce)
┌──────────────────────────────▼──────────────────────────────────────┐
│  STAGE 8: AfDB + WB Independent Verification and Co-Signature       │
│  Trust: Independent institutional parties; HSM signing keys         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ (h, σ_AfDB, σ_WB)
┌──────────────────────────────▼──────────────────────────────────────┐
│  STAGE 9: Ledger Finalisation (BFT Commit)                         │
│  Trust: 3-of-5 BFT consensus on commitment record                  │
└─────────────────────────────────────────────────────────────────────┘
                               │
                     volume_commitment_hash
                     (public ledger — operator
                      declaration window opens)
```

---

## 3. STAGE-BY-STAGE SPECIFICATION

### Stage 1 — Sentinel-1 SLC Data Acquisition

**Input:** None (pull from ESA Copernicus Open Access Hub)  
**Output:** Raw Sentinel-1 Single Look Complex (SLC) files for ≥ 20 acquisition dates spanning the mining epoch

**Protocol:**
1. Download SLC products via authenticated HTTPS from `https://dataspace.copernicus.eu`
2. Verify each downloaded file against the SHA-256 manifest published by ESA at time of acquisition
3. Record product IDs, acquisition timestamps, and verified SHA-256 hashes in the pipeline audit log

**Integrity control:** ESA's Copernicus programme publishes file hashes alongside products. Any hash mismatch must halt the pipeline and raise a `DATA_INTEGRITY_FAILURE` event.

**Trust assumption:** ESA is an honest data publisher. ESA cannot be coerced by any single party to alter historical SAR acquisitions without the manipulation being detectable via independent Sentinel-1 data access by other parties (including the AfDB and WB nodes, which independently verify — see Stage 8).

**Attack surface:**
- Man-in-the-middle substitution of SLC files during download → mitigated by HTTPS + SHA-256 hash verification
- ESA portal compromise → partially mitigated by multi-party independent download at Stage 8

---

### Stage 2 — SAR Preprocessing

**Software:** ESA Sentinel Application Platform (SNAP), version `10.0.0`  
**Operation:** SLC co-registration, interferogram formation, topographic phase removal (using SRTM DEM)

**Integrity controls:**
- SNAP binary hash: `sha256:SNAP_10.0.0_linux_sha256` (see §5 Software Bill of Materials)
- Execution environment: air-gapped Linux VM, no external network access during processing
- Processing graph (`.xml`) is version-controlled and hash-pinned; any modification requires a new authorisation record
- All intermediate outputs written to a write-once audit log with session-level signature

**Determinism guarantee:** SNAP interferogram processing is deterministic for identical inputs. Re-running Stage 2 on the same SLC data must produce bit-identical output. The AfDB and WB verification in Stage 8 independently re-runs Stage 2 to verify reproducibility.

---

### Stage 3 — PS-InSAR Processing and Volume Estimation

**Software:** MintPy v1.5.3 (Miami InSAR Time-series software in Python)  
**Operation:** Time-series analysis of interferometric phase to extract line-of-sight surface displacement; conversion to vertical displacement using known satellite incidence angle; DEM differencing over mine extent to derive volume change estimate

**Volume estimation algorithm:**

Let `D(x, y, t)` denote the vertical displacement field at surface coordinates `(x, y)` and time `t`. The volume change over epoch `[t₀, t₁]` is:

```
ΔV_float = ∬_A [D(x, y, t₁) - D(x, y, t₀)] dx dy
```

where `A` is the mine extent polygon, defined in a GeoJSON file that is version-controlled and hash-pinned per mining claim.

**Integrity controls:**
- MintPy version pinned: `git commit sha256:mintpy_1.5.3_commit_hash`
- Mine extent polygon: version-controlled GeoJSON, SHA-256 recorded in audit log
- Processing script: hash-pinned `estimate_volume.py`, executed with `--seed 42` for reproducibility
- Output: `V_float` in units of cubic metres, with associated 1-σ uncertainty `σ_V`

**Uncertainty requirement:** The pipeline must produce and record a 1-σ uncertainty estimate. If `σ_V / V_float > 0.05` (5% relative uncertainty), the pipeline halts pending manual review.

---

### Stage 4 — UAV LiDAR Cross-Validation

**Purpose:** Independent sensor cross-validation to detect oracle manipulation or systematic PS-InSAR error

**Protocol:**
1. UAV LiDAR survey conducted within 72 hours of the PS-InSAR acquisition date used for Stage 3
2. Point cloud processed using LAStools or equivalent (version-pinned binary)
3. Volume estimate `V_lidar` computed from point cloud DEM differencing
4. Cross-validation gate: `|V_float_insar - V_lidar| ≤ τ`

**Tolerance parameter:** `τ = max(0.03 × V_float_insar, 500)` m³ — i.e., 3% relative tolerance or 500 m³ absolute, whichever is larger

**Gate condition:** If the cross-validation gate fails, the pipeline halts and the epoch commitment cannot proceed. Both the MRC and ZRA are notified. Manual adjudication is required before restart.

**What this controls:** A compromised Stage 3 that produces a fraudulently low volume estimate will diverge from the independent LiDAR survey, triggering the gate. The adversary would need to compromise both the PS-InSAR processing environment AND the UAV LiDAR survey simultaneously.

---

### Stage 5 — Float-to-Integer Conversion

**This stage is formally specified. Its definition is a protocol constant and must match exactly the witness generation in `resource_command_zkp.py` v2.4.**

**Input:** `V_float` ∈ ℝ (cubic metres, from Stage 4 validated estimate)  
**Output:** `volume_v` ∈ ℤ

**Conversion rule:**

```python
volume_v = int(round(V_float))   # IEEE 754 "round half away from zero"
```

**Validity gate:** The output must satisfy the circuit's range constraint:

```
1 ≤ volume_v < 2^40
```

If `volume_v < 1`: pipeline halts — the mine is reporting zero or negative volume change; manual review required.  
If `volume_v ≥ 2^40`: pipeline halts — volume exceeds circuit design limit (10¹² m³); this is physically impossible for any mine.

**Rounding error impact:** The maximum rounding error is ±0.5 m³. At typical Zambian copper parameters (density 2.7 t/m³, grade 4.5%), a ±0.5 m³ error produces a royalty rounding error of:

```
Δroyalty = 0.5 m³ × 2.7 t/m³ × 0.045 × 0.06 × P_Cu
         = 0.5 × 2.7 × 0.045 × 0.06 × P_Cu
         ≈ 0.003645 × P_Cu
```

At P_Cu = $9,000/tonne: Δroyalty ≈ $0.033. The rounding error is economically negligible.

**Protocol equivalence:** The Python witness generator executes the identical `int(round(...))` computation. The circuit's floor-division gate computes `tonnage_t = ⌊(volume_v × density_d) / 10⁶⌋` — an integer operation that does not introduce additional rounding. The float-to-integer conversion is the **only** precision loss in the computation chain, and it occurs at Stage 5 before any cryptographic commitment is made.

---

### Stage 6 — Nonce Generation

**Purpose:** The nonce provides commitment hiding — it prevents an adversary from reversing the Poseidon hash to learn `volume_v` via brute-force over the (physically bounded) domain of plausible volumes.

**Generation protocol:**

```python
nonce = secrets.randbelow(2**64)  # Python 3.x cryptographically secure PRNG
                                   # backed by OS /dev/urandom
```

**Properties:**
- Nonce is 64-bit (fits within the BN254 scalar field without reduction)
- Generated fresh per epoch per mine claim
- Recorded in the pipeline audit log immediately upon generation
- Published on-ledger alongside the commitment hash (post-commitment, pre-declaration-window)

**Why the nonce is published:** The nonce is not secret — it is a randomness commitment, not a privacy input. Publishing it allows any party to independently verify the commitment: `Poseidon(volume_v, nonce) = volume_commitment_hash`. However, the nonce is **not published until after the commitment hash is finalised on-ledger**, ensuring that the commitment is binding before the preimage is revealed.

---

### Stage 7 — Poseidon Hash Computation

**Implementation:** `circomlibjs` v0.1.7 (JavaScript, Node.js)  
**Reference:** `https://github.com/iden3/circomlibjs`, commit `[pinned — see §5]`

**Computation:**

```javascript
const { buildPoseidon } = require("circomlibjs");
const poseidon = await buildPoseidon();
const hash = poseidon([volume_v, nonce]);
const hash_hex = poseidon.F.toString(hash, 16);
```

**Field encoding:** `volume_v` and `nonce` are passed as BigInt values. The Poseidon implementation operates natively over the BN254 scalar field `GF(p)` where `p = 21888242871839275222246405745257275088548364400416034343698204186575808495617`.

**Integrity controls:**
- `circomlibjs` package hash-pinned in `package-lock.json` (SHA-512 integrity field)
- The same `poseidon([volume_v, nonce])` call is reproduced independently by the AfDB and WB verification scripts at Stage 8 using the same pinned library
- Hash output recorded as a 32-byte hex string in the audit log alongside the input values

**Why not an HSM for the hash computation:** The Poseidon hash is deterministic and its output is posted publicly. Confidentiality of the computation is not required. Integrity is ensured by independent reproduction at Stage 8. An HSM would add latency without meaningful security benefit at this stage.

---

### Stage 8 — AfDB and World Bank Independent Verification and Co-Signature

**This is the security-critical stage. Both AfDB and WB must independently verify the computation before signing. Neither party signs a hash presented to them without verification.**

**AfDB and WB each independently execute:**

1. **Re-download Sentinel-1 SLC data** for the same acquisition dates from Copernicus, verify SHA-256 hashes
2. **Re-run Stages 2 and 3** using the same pinned software versions and processing parameters
3. **Cross-check `volume_v`:** Verify that `|V_independent - volume_v| ≤ τ_intl` where `τ_intl = max(0.05 × volume_v, 1000)` m³ (5% tolerance for independent re-run expected variation)
4. **Re-compute Poseidon hash:** Using the published `nonce` and verified `volume_v`, compute `h' = Poseidon(volume_v, nonce)` and verify `h' = h`
5. **Sign:** If all checks pass, sign the tuple `(epoch_id, mine_claim_id, volume_v, nonce, h)` with their validator signing key

**Signing scheme:** Ed25519 (RFC 8032)

**Co-signature requirement:** **Both** AfDB and WB signatures are required. A single international signature is insufficient. This is enforced at the BFT ledger level — the commitment record is not finalised without both signatures present.

**Key management for AfDB and WB signing keys:** See §6.

**What this controls:** The independent re-computation by two separate institutions with independent data access means that a compromised oracle operator (Stage 3) would need to also compromise the independent verification pipelines of both AfDB and WB simultaneously. These are three separate institutions with separate infrastructure, separate teams, and no shared computational environment.

---

### Stage 9 — Ledger Finalisation

**Protocol:** The commitment record `{epoch_id, mine_claim_id, volume_commitment_hash, σ_AfDB, σ_WB, timestamp}` is submitted to the BFT ledger as a transaction.

**Acceptance criteria:**
- Both `σ_AfDB` and `σ_WB` are present and valid Ed25519 signatures over the commitment record
- The transaction is confirmed by 3-of-5 BFT consensus (the same PBFT protocol used for proof verification)
- Timestamp is within the authorised commitment window for the declared epoch

**After finalisation:** The operator's declaration window opens. The operator can now generate a ZK proof using `volume_v` as their private witness. The pre-committed hash is immutable — the operator cannot cause the hash to reflect a different volume.

---

## 4. FLOAT-TO-INTEGER CONVERSION — FORMAL SPECIFICATION

This section provides the precise formal specification for external verification.

**Definition F1 (Volume Integer Encoding).**  
Let `V` ∈ ℝ≥0 denote the physical volume estimate in cubic metres produced by Stage 4. The circuit input `volume_v` is defined as:

```
volume_v := round(V)
```

where `round : ℝ → ℤ` is the function `round(x) = ⌊x + 0.5⌋` (round half away from zero, consistent with Python's `round()` built-in for positive values and IEEE 754 `roundTiesToAway`).

**Definition F2 (Valid Domain).**  
The conversion is valid if and only if `volume_v ∈ [1, 2^40 − 1]`. The pipeline must gate on this condition before proceeding to Stage 6.

**Lemma F3 (Rounding Error Bound).**  
For all `V ∈ ℝ≥0`: `|V − volume_v| ≤ 0.5`.

**Lemma F4 (Protocol Equivalence).**  
The witness generator `resource_command_zkp.py` v2.4 computes `volume_v = int(round(V_float))` using Python's standard `round()` function, which implements the same rounding rule for positive values. The oracle pipeline and the witness generator are therefore computing the same integer for any shared float input.

**Note on Python 3 rounding for half-integers:** Python's built-in `round()` uses "round half to even" (banker's rounding), not "round half away from zero," for values of the form `n + 0.5`. This edge case arises with probability zero in practice (requires `V_float` to be exactly a half-integer) and the maximum discrepancy is 1 cubic metre. The formal specification uses "round half away from zero" consistently. The implementation should use `int(math.floor(V_float + 0.5))` to avoid the edge case.

---

## 5. SOFTWARE BILL OF MATERIALS

All software components in the attestation pipeline are pinned by version and binary hash. Any deviation from the pinned version invalidates the attestation and must trigger a re-certification.

| Component | Role | Version | SHA-256 / Commit |
|---|---|---|---|
| ESA SNAP | SAR preprocessing | 10.0.0 | `[record at deployment]` |
| MintPy | PS-InSAR time-series | 1.5.3 | `[record at deployment]` |
| GDAL | Raster operations | 3.8.x | `[record at deployment]` |
| LAStools | LiDAR point cloud | 240301 | `[record at deployment]` |
| Python | Pipeline runtime | 3.11.x | `[record at deployment]` |
| NumPy | Numerical computation | 1.26.x | `[record at deployment]` |
| SciPy | Integration routines | 1.12.x | `[record at deployment]` |
| circomlibjs | Poseidon hash | 0.1.7 | `[see package-lock.json]` |
| Node.js | Poseidon runtime | 20.x LTS | `[record at deployment]` |

**Hash recording protocol:** The SHA-256 of each binary or installed package directory tree is recorded at initial installation and verified at the start of each pipeline run. Verification failures halt the pipeline.

**Update policy:** Any software update requires:
1. Security review of the changelog
2. Re-pinning of the hash
3. Re-certification test run against a known reference dataset
4. Dual sign-off from the oracle operator and one international node (AfDB or WB)

---

## 6. KEY MANAGEMENT — AfDB AND WORLD BANK SIGNING KEYS

### 6.1 Key Type and Parameters

- **Algorithm:** Ed25519 (RFC 8032)
- **Key size:** 256-bit (32-byte private key, 32-byte public key)
- **Rationale:** Ed25519 is deterministic (no per-signature randomness requirement), immune to ECDSA k-reuse attacks, and widely supported across HSM vendors

### 6.2 Key Generation Ceremony

Each institution (AfDB, WB) generates its own signing key independently:

1. Key generation performed on an HSM meeting FIPS 140-2 Level 3 or equivalent
2. Generation ceremony witnessed by at least two independent officers from the institution
3. Public key extracted and published to the protocol's key registry
4. Public key fingerprint transmitted out-of-band to all other validators for verification
5. Ceremony record (witnesses, timestamp, HSM attestation certificate) retained by institution

### 6.3 Key Storage and Access Controls

- **Private key:** Never leaves HSM boundary. All signing operations performed inside HSM.
- **Access control:** HSM requires n-of-m authentication (minimum 2-of-3 institutional officers) to authorise a signing operation
- **Audit log:** All signing operations logged by HSM with timestamp and operator ID

### 6.4 Key Rotation Policy

- **Scheduled rotation:** Annual
- **Emergency rotation:** Within 24 hours of suspected compromise
- **Rotation protocol:** New key generated and registered; old key retired; all validators notified via out-of-band channel; minimum 30-day overlap period during which both keys are accepted

### 6.5 Key Compromise Response

In the event of confirmed or suspected compromise of either AfDB or WB signing key:

1. Immediately notify all five validator nodes via out-of-band channel
2. Revoke compromised key from key registry via 3-of-5 BFT transaction
3. Halt oracle commitment pipeline pending key rotation
4. Conduct forensic review to determine scope of compromise
5. Any commitments signed with the compromised key after the estimated compromise date are subject to re-verification

### 6.6 Oracle Operator Signing Key

The oracle operator holds a separate signing key used only to sign the processing outputs at Stage 7. This key is **not** one of the five BFT validator keys. It is used for audit trail integrity only — the oracle operator's signature alone carries no protocol-level authority. The protocol-level commitment requires AfDB and WB co-signatures.

---

## 7. KNOWN LIMITATIONS AND RC-03 SCOPE BOUNDARY

The oracle pipeline specified in this document commits **only `volume_v`** to the ledger. The operator's private inputs `density_d` (ore density) and `grade_g` (ore grade) are **not** independently committed.

**What this means:** The ZK proof demonstrates that the declared royalty is arithmetically consistent with the declared density, grade, and the oracle-committed volume. It does not prove that the declared density and grade correspond to the actual physical deposit parameters.

**Residual attack surface:** An operator with knowledge of their actual density and grade could declare values within the circuit's valid range (`density_d ∈ [1, 2²⁶)`, `grade_g ∈ [1, 1,000,000]`) that understate mineral content, generating a valid proof for a fraudulent royalty figure.

**Planned mitigations (Phase 3 architectural roadmap):**

| Option | Description | Security gain | Complexity |
|---|---|---|---|
| A | MRC field inspector co-signs assay report on-chain before proof submission | Adds human attestation for density/grade | Low |
| B | Extend oracle to include XRF scanner data from MRC-operated equipment | Mechanically grounds density/grade in sensor data | Medium |
| C | Commit `Poseidon(volume_v, density_d, grade_g, nonce)` replacing current 2-input hash | Grounds all three inputs in the oracle commitment | High — requires re-certification |

Option C provides the strongest cryptographic guarantee and is the target state for production deployment. It requires extending the oracle pipeline to include independently verified density and grade measurements, and recompiling the circuit with a 4-input Poseidon commitment. This is documented as the Phase 3 oracle extension.

---

## 8. SECURITY PROPERTIES CLAIMED

The following properties hold under the trust assumptions stated at each stage:

| Property | Condition | Mechanism |
|---|---|---|
| **Volume integrity** | ESA is honest; oracle operator is honest or AfDB+WB independently detect manipulation | Independent re-computation at Stage 8 |
| **Commitment binding** | Poseidon is preimage-resistant (per BN254 security assumptions) | One-way commitment; operator cannot find alternative `volume_v` for posted hash |
| **Commitment hiding** | Nonce is random and unpublished before commitment | Prevents brute-force reversal over physical volume domain |
| **Cross-sensor consistency** | UAV LiDAR is independent of PS-InSAR processing | Stage 4 cross-validation gate |
| **Software supply chain integrity** | Pipeline runs pinned, hash-verified software | SBOM at §5; per-run verification |
| **Signatory independence** | AfDB and WB have independent infrastructure and data access | Separate re-computation; separate signing keys |
| **Post-quantum vulnerability** | Ed25519 and BN254 are not quantum-resistant | **Not claimed** — see §9 |

---

## 9. KNOWN OPEN ITEM — POST-QUANTUM SECURITY

Both the Ed25519 signing scheme (based on the discrete log problem) and the Groth16 proof system over BN254 (based on elliptic curve pairings) are vulnerable to a sufficiently powerful quantum computer running Shor's algorithm. Post-quantum secure alternatives exist for signatures (e.g., CRYSTALS-Dilithium, SPHINCS+) but not yet for practical ZK proof systems at equivalent constraint counts.

This is a known limitation shared by all deployed ZK proof systems as of this document's date. It is disclosed here for completeness and will be re-evaluated as the post-quantum ZK proof landscape matures.

---

*Kgosi Capital Holdings (Botswana) Ltd · Confidential · 6 May 2026*
