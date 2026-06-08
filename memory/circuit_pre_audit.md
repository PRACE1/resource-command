# RC Circuit — Pre-Audit Manual Analysis
## compliance.circom v1.1 + ExponentialDecay.circom
**Analyst:** Internal review (pre-Trail of Bits)
**Date:** 2026-06-01
**Status:** 4 findings. Blocker for ToB scoping call = Finding I.

---

## FINDING I — CRITICAL
### GreaterEqThan(32) Undersized — Wraparound Check Fails for Valid Inputs

**Location:** `ExponentialDecay.circom`, line 40
```circom
component geq = GreaterEqThan(nBits);  // nBits = 32 (passed from caller)
geq.in[0] <== A;   // A = 120 + 12 * x^2
geq.in[1] <== B;   // B = 60*x + x^3
```
Called from compliance.circom line 87:
```circom
component decay = ExponentialDecayPade3(32);  // nBits = 32
```

**The Problem:**
`GreaterEqThan(n)` in circomlib uses `Num2Bits(n)` internally to decompose
the difference. It is only correct for inputs ≤ 2^n.

For `x` near the Padé validity boundary (where the wraparound check is
actually needed), the actual magnitudes of A and B are:

```
x ≈ 4.7 * (scale)  →  A = 120 + 12*x² ≈ 2^55 bits
                         B = 60*x + x³   ≈ 2^78 bits
```

Both operands exceed 2^32 by 23+ bits. The comparison operates on
(A mod 2^32) vs (B mod 2^32) — not on A vs B. The check can pass even
when A < B in the integer sense.

**Attack Vector:**
An adversarial prover constructs (A, B) where A < B but
(A mod 2^32) ≥ (B mod 2^32). The `geq.out === 1` constraint passes.
The numerator `num = A - B` becomes a large prime-field element (wraps
around BN254 prime p ≈ 2^254). `out * den === num` then enforces a
specific `out` value that corresponds to a field element near p, not
to any valid approximation of e^{-x}.

**Impact:** The decay function's output is not constrained to a valid
approximation of the exponential. An adversary can satisfy the circuit
with a fabricated `current_token` value that bypasses the presence
threshold check (line 106–109 of compliance.circom).

**Fix:**
```circom
// Increase nBits to match actual operand magnitude.
// A and B are at most O(x^3) where x is 32 bits → max ~96 bits.
// Use 128 bits minimum for safety buffer from BN254 prime.
component geq = GreaterEqThan(128);
```
And update the caller:
```circom
component decay = ExponentialDecayPade3(128);
```
Also check `denBound = Num2Bits(128)` — this is already 128 bits and
correctly bounds den. Only `geq` needs the fix.

---

## FINDING II — HIGH
### ExponentialDecay Output Scaling — Integer Division Produces 0 for All x > 0

**Location:** `ExponentialDecay.circom`, line 63–64
```circom
out <-- num / den;
out * den === num;
```

**The Problem:**
`out` is constrained by `out * den === num`, where num = A - B and
den = A + B. For all x ≥ 1 in the integer domain, num < den (since
the Padé ratio is < 1), so:

```
out = floor(num / den) = 0   for all integer x ≥ 1
```

This makes the exponential decay function a step function:
- x = 0   → out = 1  (120/120 = 1 exactly)
- x ≥ 1   → out = 0  (integer division truncates)

**Downstream Effect (compliance.circom lines 91–97):**
```circom
current_token <-- (initial_token * decay.out) \ 1000000;
decay_mult <== initial_token * decay.out;
decay_mult === (current_token * 1000000) + rem_decay;
```

If `decay.out = 0`, then `decay_mult = 0`, `current_token = 0`,
`rem_decay = 0`. The presence check `current_token ≥ min_token_threshold`
then ALWAYS FAILS for any non-zero x (any elapsed time > 0).

**Clarification Needed:**
The circuit may intend `x` to be a fixed-point encoding where values
like x = 693147 represent x_real = 0.693147 (= ln(2)). In that case,
in the INTEGER polynomial A and B, the relationship holds but the
output still suffers from integer truncation unless the coefficients
are pre-scaled to produce `out` in units of [0, 1,000,000].

The standard fix for integer Padé is to scale the numerator by a
precision factor S before division:
```circom
// Scaled output: out ∈ [0, S] where S = 1,000,000
out <-- (num * 1000000) / den;
out * den === num * 1000000;
```

**Impact:** Either the circuit always rejects valid presence proofs
(if x > 0), or the scaling is implicit and undocumented — making the
circuit impossible to audit without the prover's off-circuit witness
generation code.

**Required Action Before ToB Call:**
Document the intended fixed-point encoding of `x`, `out`, and
`initial_token` with explicit scale factors. Provide test vectors
showing a working proof with non-zero decay.

---

## FINDING III — MEDIUM
### Unconstrained Upper Bound on `reduced_x` — Range Reduction Bypass

**Location:** `ExponentialDecay.circom` (RangeReduction template), line 88
```circom
component reducedBound = Num2Bits(32);
reducedBound.in <== reduced_x;
```

**The Problem:**
The range reduction is:
```
raw_kt === reduced_x + (k_shift * LN2_FIXED)
```
This enforces that `reduced_x` is the fractional part after subtracting
multiples of `LN2_FIXED = 69314718`. The INTENDED invariant is:
```
0 ≤ reduced_x < LN2_FIXED   (i.e., reduced_x < 69,314,718 ≈ 2^26)
```
But the circuit only enforces `Num2Bits(32)` — meaning
`reduced_x ≤ 2^32 - 1 = 4,294,967,295`.

A prover can set `reduced_x = 2 * LN2_FIXED` (= 138,629,436) with
`k_shift` adjusted to compensate, while still satisfying the linear
constraint. The Padé approximation receives an `x` value outside its
valid range.

**Fix:**
Add an upper bound constraint after the range check:
```circom
component reducedBound = Num2Bits(32);
reducedBound.in <== reduced_x;

// Enforce reduced_x < LN2_FIXED
component reducedMax = LessThan(27);  // 2^27 > LN2_FIXED
reducedMax.in[0] <== reduced_x;
reducedMax.in[1] <== 69314718;
reducedMax.out === 1;
```

---

## FINDING IV — LOW / INFO
### `<--` Hint Operators Without Defensive Comments

**Location:** `compliance.circom`, lines 92, 123, 141
```circom
current_token <-- (initial_token * decay.out) \ 1000000;
tonnage_t     <-- (volume_v * density_d) \ 1000000;
mineral_content_m <-- (tonnage_t * grade_g) \ 1000000;
```

**Note:** This is the standard circom pattern for integer division
(assign hint outside circuit, enforce multiplication balance inside).
The subsequent `===` constraints correctly enforce the relationship.
This is NOT a vulnerability — it is the only way to do division in R1CS.

**However:** Trail of Bits will flag every `<--` usage by policy.
Pre-empt this with inline comments:
```circom
// DIVISION PATTERN: assign quotient as hint, enforce via multiplication
// balance constraint below. Standard circom integer division idiom.
tonnage_t <-- (volume_v * density_d) \ 1000000;
```

---

## Summary Table

| # | Severity | Location | Issue |
|---|---|---|---|
| I | CRITICAL | ExponentialDecay.circom:40 | GreaterEqThan(32) undersized — operands up to 2^96 |
| II | HIGH | ExponentialDecay.circom:63 | Integer division yields out=0 for all x≥1 — scaling missing |
| III | MEDIUM | ExponentialDecay.circom:88 | reduced_x upper bound not enforced (< LN2_FIXED) |
| IV | LOW | compliance.circom:92,123,141 | <-- operators need defensive comments |

---

## Action Items Before Trail of Bits Scoping Call

1. **Fix Finding I** — Change `ExponentialDecayPade3(32)` to `ExponentialDecayPade3(128)`
2. **Resolve Finding II** — Either:
   a. Document the fixed-point encoding with test vectors showing a working proof, OR
   b. Apply scaled division `out * den === num * 1000000`
3. **Fix Finding III** — Add `LessThan(27)` constraint on `reduced_x`
4. **Address Finding IV** — Add inline comments to all `<--` operators

**Do not share the circuit with Trail of Bits until Finding II is resolved.**
Finding II may indicate the CryptoKinetics presence proof currently
does not function as intended. If ToB finds this first, it undermines
the audit engagement premise.

---

*Generated by manual static analysis. Circomspect not available on this
machine (no MSVC or MinGW toolchain). ToB will run circomspect as part
of their tooling — these findings should be pre-resolved or acknowledged
before the scoping call.*
