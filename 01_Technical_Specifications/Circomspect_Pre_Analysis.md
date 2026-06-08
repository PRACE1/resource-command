# Circomspect Pre-Audit Analysis — `compliance.circom` v1.1

**Tool:** Circomspect (Trail of Bits) — [github.com/trailofbits/circomspect](https://github.com/trailofbits/circomspect)  
**Methodology:** Manual application of Circomspect's static analysis checklist to `compliance.circom` v1.1  
**Date:** 2026-05-09  
**Analyst:** Kgosi Capital Holdings — Internal Pre-Submission Review  
**Purpose:** Disclose self-identified findings prior to formal ToB engagement; maximise audit efficiency

---

## Summary

| Severity | Count | Status |
|---|---|---|
| High | 1 | RESOLVED |
| Medium | 1 | UNRESOLVED (Submitted for verification) |
| Informational | 3 | ACKNOWLEDGED |

All findings are disclosed transparently. The High finding was a soundness gap that has been fully resolved/patched in circuit v1.1. The Medium finding is confirmed sound by internal analysis but warrants independent verification.

---

## FINDING 1 — HIGH: Missing Upper Bound on `royalty_rate_bps` [RESOLVED]

**Location:** Lines 59–63 (range check), Lines 107–118 (royalty attestation gate)

**Description:**

The circuit previously enforced a lower bound on `royalty_rate_bps` (> 0) via a `GreaterThan(13)` component, but did not enforce an upper bound. The commented specification states the valid range is `[1, 5000]` bps, but no `LessThan` constraint enforced the upper limit.

**Status:** RESOLVED. Patched in `compliance.circom` v1.1 by adding a `LessThan(13)` component to enforce `royalty_rate_bps <= 5000` (lines 59–63):

```circom
    // Upper bound: royalty_rate_bps <= 5000 (statutory maximum — RC-05)
    component rateMax = LessThan(13);
    rateMax.in[0] <== royalty_rate_bps;
    rateMax.in[1] <== 5001;
    rateMax.out === 1;
```

This closes the soundness gap where a prover could supply a rate up to 8,191 bps (representing an unauthorized 81.91% rate) and generate a valid proof.

**Submitted for:** Independent confirmation of patch correctness and soundness.

---

## FINDING 2 — MEDIUM: Hint-Assignment Signals (`<--`) Without Simultaneous Constraint

**Location:** Lines 68, 86

**Description:**

Two intermediate signals are assigned using the `<--` (hint/witness-generation) operator rather than `<==` (assign-and-constrain):

```circom
tonnage_t       <-- (volume_v * density_d) \ 1000000;    // Line 68
mineral_content_m <-- (tonnage_t * grade_g) \ 1000000;  // Line 86
```

Circomspect flags all `<--` assignments for manual review, as the prover can assign any value without immediate R1CS enforcement. Constraint is deferred to the scaling gate equalities:

```circom
vol_dens === (tonnage_t * 1000000) + rem_tonnage;         // Line 76
ton_grad === (mineral_content_m * 1000000) + rem_mineral; // Line 94
```

**Internal Assessment:**

The combination of:
1. The scaling gate equality
2. The bounded remainder witness (`0 ≤ rem < 10⁶`, enforced by `LessThan(20)`)
3. The `Num2Bits(47)` range constraint on both signals

…uniquely determines `tonnage_t` and `mineral_content_m` for any valid input assignment. A malicious prover assigning a wrong value for `tonnage_t` would require either a `rem_tonnage ≥ 10⁶` (rejected by `lt1`) or an inequality in the scaling gate (rejected by `===`).

**Status:** Assessed as sound by internal review. Submitted for independent confirmation.

---

## FINDING 3 — INFORMATIONAL: Intermediate Product Field-Size Analysis

**Description:** All intermediate products fit comfortably within the BN254 scalar field (`p ≈ 2²⁵⁴`). No overflow risk.

| Signal | Max Bit-Width | Derivation | Field-Safe? |
|---|---|---|---|
| `vol_dens` | 2⁶⁶ | 2⁴⁰ × 2²⁶ | ✓ |
| `ton_grad` | 2⁶⁷ | 2⁴⁷ × 2²⁰ | ✓ |
| `lhs` | 2⁶⁰ | 2⁴⁷ × 2¹³ | ✓ |
| `rhs` | 2⁵⁸ | 2⁴⁴ × 2¹⁴ | ✓ |

---

## FINDING 4 — INFORMATIONAL: Rationalized Bit-Widths (Positive Finding)

**Description:** The circuit uses physics-derived bit widths rather than blanket `Num2Bits(64)`:

| Signal | Width | Physical Bound |
|---|---|---|
| `volume_v` | 40 bits | Max 10¹² m³ |
| `density_d` | 26 bits | Max ~67 t/m³ |
| `grade_g` | 20 bits | Max 1,000,000 (100%) |
| `tonnage_t` | 47 bits | Derived (2⁴⁰ × 2²⁶ / 10⁶) |
| `mineral_content_m` | 47 bits | Derived (≤ tonnage) |
| `tax_paid_usd` | 44 bits | Regulatory cap |

This reduces constraint count vs. naive 64-bit implementation and constrains the attack surface of each intermediate multiplication. Submitted for confirmation that the physical bounds are correctly encoded.

---

## FINDING 5 — INFORMATIONAL: LessThan Component Bit-Width Verification

**Description:** All `LessThan(n)` components are verified to have sufficient bit-width to represent their comparison constant without overflow within the component's internal arithmetic.

| Component | Bit-Width `n` | Comparison Constant | 2ⁿ | Safe? |
|---|---|---|---|---|
| `gMax` | 20 | 1,000,001 | 1,048,576 | ✓ |
| `lt1` (rem_tonnage) | 20 | 1,000,000 | 1,048,576 | ✓ |
| `lt2` (rem_mineral) | 20 | 1,000,000 | 1,048,576 | ✓ |
| `lt3` (rem_royalty) | 14 | 10,000 | 16,384 | ✓ |

---

## Relationship to Trail of Bits Toolchain

This pre-analysis was structured using the Circomspect static analysis framework developed by Trail of Bits. Specific checks performed correspond to Circomspect's published detection categories:

- `under-constrained-signal` — Findings 1 and 2
- `signal-assignment` (`<--` pattern) — Finding 2  
- `field-element-arithmetic` — Finding 3

We additionally reference **ZKDocs** (trailofbits.github.io/zkdocs) for the Groth16/BN254 soundness properties and the Poseidon specification cited in section 3.2 of our Technical Architecture document.

We were unable to execute `circomspect circuits/compliance.circom` directly due to environment constraints. **We invite Trail of Bits to run Circomspect as the first step of the formal engagement** and compare output against this pre-analysis as a calibration exercise.

---

*Document prepared by Kgosi Capital Holdings (Botswana) Ltd · Pre-submission internal review · 2026-05-09*
