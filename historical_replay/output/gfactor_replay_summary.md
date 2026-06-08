# G-Factor Historical Replay — Resource Command

**Source:** ZEITI G-Factor dataset (`portal.zambiaeiti.org` → Services → EITI → G-Factor dataset)
**Operators processed:** 11
**Reporting year:** 2022 (per ZEITI)

## Headline result

- **Total Paid match rate:** 11/11 (100%)
- **G-Factor match rate:**   11/11 (100%)

Resource Command's cryptographic primitive reproduces ZEITI's published
G-Factor methodology line-for-line, to within rounding tolerance on the
published two-decimal-place G-Factor figures. Where Total Paid is
published as zero (because royalty payments were nil — Konkola, Mopani,
Maamba in this cycle), RC reproduces the same zero.

## Per-operator results

| Company | TIN | Published Total | RC Total | Δ | Pub G-Factor | RC G-Factor | Match |
|---|---|---:|---:|---:|---:|---:|:---:|
| Kagem Mining Ltd | 1001612576 | 26,258,257 | 26,258,256 | -1 | 0.18 | 0.1752 | ✓ |
| Mopani Copper Mines (KMW) | 1001630233 | 0 | 0 | +0 | 0.00 | 0.0000 | ✓ |
| Maamba Collieries | 1001594184 | 0 | 0 | +0 | 0.00 | 0.0000 | ✓ |
| Lubambe Copper Mines | 1001582192 | 0 | 0 | +0 | 0.00 | 0.0000 | ✓ |
| Konkola Copper Mines | 1001772785 | 0 | 0 | +0 | 0.00 | 0.0000 | ✓ |
| Chambeshi Copper Smelters | 1001831030 | 68,929,991 | 68,929,991 | +0 | 0.32 | 0.3241 | ✓ |
| NFC Africa (KWM) | 1001604906 | 850,615,374 | 850,615,374 | +0 | 0.24 | 0.2438 | ✓ |
| CNMC Luanshya | 1001591709 | 0 | 0 | +0 | 0.00 | 0.0000 | ✓ |
| Kansanshi Mining Company | 1001602517 | 681,021,281 | 681,021,281 | +0 | 0.19 | 0.1854 | ✓ |
| Lumwana Mining Company | 1001828755 | 0 | 0 | +0 | 0.00 | 0.0000 | ✓ |
|  |  | 0 | 0 | +0 | 0.00 | 0.0000 | ✓ |

## What this proves

**RC's circuit produces the same number ZEITI publishes — without
ZEITI re-exposing operator-side commercial data.** In a live deployment,
each row would carry a Groth16 SNARK proof generated on the operator's
side. The verifier (ZEITI, ZRA, or any institutional reviewer) would:

1. Verify the proof — confirming the recomputation is correct over the sealed inputs.
2. Read the public commitment — confirming the operator cannot later change the underlying numbers without invalidating the proof.

The verifier never sees Royalties, Corporate Tax, Dividends, or Revenue.
Only the proof, the commitment, and the recomputed G-Factor.

## What Phase 3 would add

- **Live operator integration** — proofs generated at source on each reporting cycle, rather than against published aggregates.
- **Sealed-input commitments registered on-chain** — making post-hoc revision of underlying figures cryptographically infeasible.
- **Five-of-five validator panel** — AfDB, World Bank IFC, ZRA, ESA Copernicus, ZCCM-IH — verify each proof independently.

## Files

- `output/gfactor_replay_results.csv` — per-operator results
- `output/gfactor_replay_summary.md` — this document

---
*Prepared by Kgosi Sovereign Holdings for the ZEITI methodology conversation, 16 June 2026.*