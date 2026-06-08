# Resource Command — Executive Summary

**Sovereign mineral revenue verification through zero-knowledge cryptography**

*Prepared by Kgosi Sovereign Holdings (Botswana). For grant application use. One page.*

---

## The problem

Zambia loses an estimated **USD 550M–940M per year** in mineral royalty under-collection (ZRA / UNU-WIDER / ICTD, 2023) — roughly 0.5–1.0% of GDP. The gap is not a measurement failure. The Zambia Revenue Authority operates world-class probabilistic risk infrastructure, achieved 22.1% tax-to-GDP in 2025, and runs the BIDA analytics platform alongside Smart Invoice (41,111 taxpayers, 161.4M invoices). The gap is a **verification** failure: even the most sophisticated audit must ultimately trust the operator's self-declared production figures.

The Trafigura / Konkola arbitration (USD 92M award against ZCCM-IH, June 2026) has made the cost of this opacity legible at a national scale. The EU Battery Passport regulation (in force 18 February 2027) makes cryptographic source-layer attestation mandatory for every kilogram of cobalt, copper, lithium, and nickel entering the European supply chain. Every African mineral economy faces the same structural verification gap, with the same regulatory deadline.

## The solution

**Resource Command** is a zero-knowledge cryptographic protocol that lets a mining operator generate a mathematical proof their royalty calculation is correct — *without exposing the underlying production volume, grade, or commercial terms*. The protocol resolves the central tension in extractives transparency: governments need verification, operators need confidentiality. Cryptography makes both possible simultaneously.

## Technical foundation

- **`compliance.circom` v1.1** — Groth16 SNARK over BN254, 839 R1CS constraints, Circomspect clean
- **Poseidon-hash oracle commitment layer** for sealed input attestation
- **5-node PBFT consensus** with institutional validators (AfDB, World Bank IFC, ZRA, ESA Copernicus, ZCCM-IH)
- **Live browser demo** generating verifiable proofs in under one second
- **Trail of Bits** — formal scoping engagement, audit kickoff July 2026
- **Independent review** by Barry Whitehat (creator of Semaphore, foundational ZK identity researcher)

## Institutional engagement

- **Zambia Revenue Authority (ZRA)** — sovereign anchor client, government contact engaged, meeting in pre-election window
- **Zambia Extractive Industries Transparency Initiative (ZEITI)** — methodology integration scoping call booked 16 June 2026, pathway to co-authored Secretariat methodology note
- **EITI International (Oslo)** — global reference-implementation pathway for the next Standard revision (2027–28)

## Expansion arc

Zambia (Phase 1) → DRC, Tanzania, Indonesia (Phase 2, via EITI chapters) → EU Battery Passport commercial channel for mining majors (KoBold, Glencore, Anglo American, FQM) requiring February 2027 compliance.

## What the grant funds

A 12–18 month deployment programme covering:

1. **Independent security audit** (Trail of Bits + second auditor) — USD 200K–300K
2. **Two senior engineering hires** (ZK circuit lead, Rust integration lead) — USD 400K–600K
3. **Sovereign integration pilot** with ZRA + ZEITI — USD 150K–250K
4. **Battery Passport compliance layer** — USD 100K–200K
5. **Institutional travel & engagement** (Lusaka, Oslo, Brussels) — USD 50K–100K
6. **Monitoring, evaluation, and reporting** — USD 50K–100K

**Total programme budget:** **USD 950K–1.55M** over 18 months (full programme). Modular: individual workstreams can be funded discretely.

## Why this matters now

Three institutional forces converge in Zambia in the six-month window before the September 2026 election:
- The Trafigura / Konkola arbitration has opened the political reform window inside ZRA and the Ministry
- The EU Battery Passport deadline forces every mining-export economy to adopt verification infrastructure
- ZRA's existing technical sophistication (Smart Invoice, BIDA analytics, Secure Data Lab) provides the integration foundation

The chapter that pairs the EITI G-Factor framework with cryptographic verification in this window becomes the global reference implementation. The chapters that wait become adopters.

## Structure and governance

**Kgosi Sovereign Holdings (Botswana)** — IP holding entity, in registration. **Zambian operating entity** — licensed IP, 35% Kgosi equity, direct contracting relationship with ZRA. **Legal architecture** designed by a former Zambian High Court judge. **CIPA + ARIPO registration** for regional IP protection.

The structure ensures the technology is a Zambian deliverable, not a vendor product. Sovereign-led, institutionally accountable, methodologically open.

## Contact

**Kennedy Thebe** — Principal, Kgosi Sovereign Holdings
Resource Command — sovereign mineral verification platform
