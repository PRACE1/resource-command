# Resource Command — Completing the G-Factor

**A memo to Ian Mwiinga, Zambia Extractive Industries Transparency Initiative**
**Pre-read for call: Tuesday 16 June 2026, 11:30 CAT**

---

## The window

Three institutional forces are converging in Zambia over the next six months:

- **The Trafigura / Konkola arbitration** (USD 92M award against ZCCM-IH, 3 June 2026) has made the cost of opacity in mineral revenue legible at a national scale. The reform window inside ZRA and the Ministry has opened with it.
- **The EU Battery Passport regulation** takes effect 18 February 2027. Every kilogram of cobalt, copper, lithium, and nickel entering the European supply chain will require cryptographic source-layer attestation. EITI chapters without a verification layer become methodologically obsolete on that date.
- **The Zambian election cycle** is a 6-month bandwidth window. After that, institutional attention shifts to political continuity, and methodological reform becomes a 2027–28 conversation.

The chapter that pairs the G-Factor framework with a cryptographic verification layer in this window becomes the reference implementation for the next EITI International Standard revision. The chapters that wait become its adopters.

This memo is about the choice in front of ZEITI in the next six months.

---

## What Resource Command provides

A zero-knowledge cryptographic protocol — compliance.circom v1.1, 839 R1CS constraints, Groth16 over BN254 — that lets a mining operator generate a mathematical proof their royalty payment is correct, without exposing the underlying production volume, grade, or commercial terms.

The protocol is built, internally audited (zero critical / high / medium / low findings), submitted to Trail of Bits in formal scoping, independently reviewed by Barry Whitehat (creator of Semaphore), and running as a live demo with a five-validator institutional panel (AfDB, World Bank IFC, ZRA, ESA Copernicus, ZCCM-IH).

This is not a prototype seeking validation. It is a production-grade primitive seeking institutional integration.

---

## How it completes the G-Factor

Resource Command is not an adjacent technology. It is the cryptographic completion of the methodology ZEITI has already built:

| G-Factor Stage | Current State | With Resource Command |
|---|---|---|
| Operator declares production figures | Self-reported; auditors must trust input | Operator generates ZK proof — figures are mathematically attested at source |
| ZEITI reconciles state and operator data | Manual reconciliation, lagged | Automated cryptographic reconciliation; gap quantified per event |
| Public report published | Annual cycle | Real-time verifiable register, annual aggregation preserved |
| Discrepancies investigated | Audit triggered after the fact | Discrepancies are mathematically impossible at the cryptographic layer |

ZEITI's independence and multi-stakeholder structure remain unchanged. The methodology becomes mathematically reproducible by any auditor — without ZEITI re-exposing operator data.

---

## The 90-day Zambia pilot

**Phase 1 (Weeks 1–4): Methodology integration.** Map the G-Factor variables onto RC's circuit inputs. ZEITI Secretariat confirms that every methodological choice already published in the framework is preserved cryptographically.

**Phase 2 (Weeks 5–8): Historical replay.** Run RC against three years of already-published ZEITI reconciliation data. Demonstrate that the cryptographic layer reproduces the same totals, with zero exposure of underlying operator data.

**Phase 3 (Weeks 9–12): Live pilot, single mine.** One operator, one mineral, one reporting period. The deliverable is a **ZEITI Secretariat methodology note, co-authored with the Chapter Lead**, stating that the cryptographic layer materially strengthens the G-Factor. This document becomes the institutional foundation for what the Zambia chapter contributes to the next EITI International Standard revision.

---

## The 24-month arc

The pilot does not end at Day 91. It opens onto a sequence:

- **Months 4–6.** Methodology note circulated to the EITI International Secretariat in Oslo. Initial conversations on framing the Zambia work as a reference implementation for the wider network.
- **Months 7–12.** Joint scoping conversations with chapters facing analogous structural pressures — DRC (cobalt revenue gap), Tanzania (gold royalty reform), Indonesia (nickel and battery supply chain). Each conversation co-led by ZEITI and Resource Command.
- **Months 13–24.** Joint methodology proposal to the EITI International Board for the next Standard revision. Zambia positioned as the chapter that defined the cryptographic verification layer for the global network.

The architecture is intentional. The Zambia chapter does not host the technology. The Zambia chapter authors the methodology.

---

## Why now, not later

Three competing chapters are in motion. Norway has the resources and the cryptography talent. Indonesia has the industrial scale and the nickel passport pressure. DRC has the cobalt revenue gap and the political will. Any of them could move first.

The Zambia chapter has something none of them have: the convergence of the Trafigura / Konkola arbitration, the EU Battery Passport deadline, and a ZRA already running probabilistic risk infrastructure (Smart Invoice, Secure Data Lab, BIDA analytics, "One ZRA" merger). That convergence is a six-month window, not a multi-year one.

There is also a parallel risk. Civil society organisations — Publish What You Pay, NRGI, Global Witness — are increasingly demanding cryptographic attestation from outside the EITI multi-stakeholder process. If ZEITI does not move first, the conversation shifts from *"methodology that ZEITI leads"* to *"demand that ZEITI accommodates."* The chapter that authors the methodology controls the conversation. The chapter that adopts it later, does not.

---

## The next conversation

The concrete next step is scoping what the Phase 2 historical replay needs from the ZEITI Secretariat — methodology specs, three reconciliation cycles, anonymisation parameters. That work begins the week after this call. Everything else — the EITI International Secretariat introduction, the co-authored methodology note, the global arc — follows naturally from the historical replay landing well.

Looking forward to Tuesday.

---

**Kennedy Thebe** · Principal, Kgosi Sovereign Holdings · Resource Command — sovereign mineral verification platform
