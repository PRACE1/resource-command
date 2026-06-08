# DRAFT — Trail of Bits Scoping Call Scheduling Email

**To:** Lindsay Rakowski, Trail of Bits
**From:** Kennedy Thebe, kennedy@resourcecommand.africa
**Subject:** Re: Resource Command — Scoping Call Scheduling

---

Lindsay,

Thank you for reviewing the pack. I'd like to schedule the scoping call at your earliest availability — ideally this week or early next.

A correction from my original email: the compiled constraint count for compliance.circom v1.1 is **839 constraints** (Groth16/BN254), not 632. The 632 figure was from an earlier development snapshot. The circuit, R1CS, and WASM in the audit pack (v1.7) are the authoritative compiled outputs.

For scope context: we're looking at the full circuit plus the oracle commitment layer (Poseidon-based volume commitment from the InSAR/LiDAR pipeline). The BFT consensus layer (n=5, f=1 PBFT) is a secondary scope item we can discuss on the call.

On timing: we have a regulatory engagement window with the Zambia Revenue Authority in June. Getting the audit scoped and a timeline locked before that meeting materially strengthens our position.

If Tjaden Hess or Fredrik Dahlgren have bandwidth for the Circom review, that would be ideal given their specific experience with circuit-level analysis and Circomspect.

I'm flexible on times. Let me know what works on your end.

Kennedy Thebe
Resource Command
kennedy@resourcecommand.africa
