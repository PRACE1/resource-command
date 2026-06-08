# Trail of Bits — Follow-Up SendSafely Note
**Send to:** chris.dahlheimer@trailofbits.com  
**Re:** Updated audit pack — supersedes earlier today's submission  
**Action:** Send via SendSafely + attach Resource_Command_Audit_Pack_v1.8_FINAL.zip

---

## Message to paste into SendSafely:

> Hi Chris,
>
> Follow-up to our submission earlier today. We identified a soundness gap during final pre-submission review using Circomspect — a missing upper bound constraint on `royalty_rate_bps` — and have patched it and enclosed the analysis. Please treat the v1.8 pack attached here as superseding the earlier drop.
>
> What's changed:
> - `compliance.circom` — `rateMax = LessThan(13)` added, enforcing `royalty_rate_bps ≤ 5000` (statutory maximum). The original submission had the lower bound (`> 0`) but not the upper bound. Now fully enforced.
> - `ToB_Audit_Cover_Letter.md` — updated to accurately reflect circuit v1.1 state, corrected constraint count (542), corrected royalty formula (parameterised `royalty_rate_bps × 10⁴`, not hardcoded 6%).
> - `Circomspect_Pre_Analysis.md` — enclosed for the first time. Structured using your Circomspect framework. We'd suggest running `circomspect circuits/compliance.circom` as a calibration check against our pre-analysis as an early engagement step.
>
> We found and fixed this ourselves before you looked at it — which is how it should be. Looking forward to the scoping call.
>
> — Kgosi Capital Holdings

---

## Files to attach to this SendSafely drop:
- `Resource_Command_Audit_Pack_v1.8_FINAL.zip`

---

*Note: v1.8 zip contains: compliance.circom (patched), ToB_Audit_Cover_Letter.md (updated), Circomspect_Pre_Analysis.md (new), Resource_Command_Technical_Pre-Read.md, resource_command_zkp.py*
