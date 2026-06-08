# Budget Template — Resource Command 18-Month Programme

*Reusable across grant applications. All figures in USD. Adjustable by line item.*

---

## Headline

**Total programme budget:** USD 1,510,000 over 18 months
**Modular structure:** every workstream below can be funded independently
**Minimum viable ask:** USD 350,000 (Tier-A workstreams only)

---

## Full programme budget — line-item breakdown

### A. Independent Security Audit (USD 275,000)

| Line item | USD | Notes |
|---|---:|---|
| Trail of Bits — formal circuit + oracle audit | 125,000 | Estimate based on initial scoping; final per SOW. ~4–6 engineer-weeks. |
| Second auditor — independent verification | 100,000 | Redundancy for sovereign-grade credibility (Veridise, Zellic, ABDK, or HashCloak — pricing comparable to ToB) |
| Remediation engineering | 35,000 | Engineering time to address audit findings |
| Post-audit verification re-test | 15,000 | Validate remediation closed all identified issues |

### B. Senior Engineering (USD 580,000)

| Line item | USD | Notes |
|---|---:|---|
| ZK Circuit Lead (18 months, fully loaded) | 300,000 | Senior cryptographic engineer — Circom, Halo2, Nova / SuperNova folding |
| Rust Integration Lead (18 months, fully loaded) | 240,000 | Senior systems engineer — oracle pipeline, validator node, deployment |
| Contracting / specialist engagements | 40,000 | Short-duration specialists (e.g., trusted setup ceremony coordinator, formal-methods consultant) |

### C. Sovereign Integration Pilot — ZRA + ZEITI (USD 225,000)

| Line item | USD | Notes |
|---|---:|---|
| ZRA technical integration | 100,000 | Smart Invoice integration, BIDA hand-off interface, Secure Data Lab co-design |
| ZEITI methodology mapping | 50,000 | G-Factor variable mapping, historical replay engineering, methodology note authorship |
| Oracle architecture remediation (RC-03) | 60,000 | Extended-oracle design and implementation — closes the standing-disclosure item |
| Pilot deployment infrastructure | 15,000 | Cloud, proving infrastructure, monitoring |

### D. Battery Passport Compliance Layer (USD 150,000)

| Line item | USD | Notes |
|---|---:|---|
| EU regulatory interpretation | 25,000 | Legal review against the EU Battery Regulation (2023/1542) and CRMA — likely outsourced to a Brussels law firm with extractives/digital expertise |
| Compliance layer engineering | 90,000 | Operator-facing API, attestation document generation, downstream OEM verification interface |
| Pilot operator engagement | 35,000 | Workshop time, integration support, change management with one anchor operator |

### E. Institutional Travel & Engagement (USD 80,000)

| Line item | USD | Notes |
|---|---:|---|
| Lusaka — ZRA, ZEITI, Ministry, mining operators | 25,000 | Estimated 6–8 multi-day visits over 18 months |
| Oslo — EITI International Secretariat | 15,000 | 2–3 visits over the engagement window |
| Brussels — EU Commission (DG GROW, DG RTD) | 15,000 | Battery Passport regulatory coordination, EU Horizon application support |
| Conferences & invited presentations | 15,000 | Academic and industry visibility — RWC, ZK Summit, EITI Global Conference, AfDB Annual Meeting |
| Travel contingency | 10,000 | |

### F. Monitoring, Evaluation & Open Publication (USD 100,000)

| Line item | USD | Notes |
|---|---:|---|
| Monitoring & evaluation framework | 25,000 | M&E specialist engagement, baseline measurement, methodology |
| Independent impact assessment (Year 1) | 30,000 | External evaluator (UNU-WIDER or ICTD analogue) — quantifies pilot impact on the verification gap |
| Academic publication preparation | 20,000 | Peer-reviewed publication of the cryptographic contribution and pilot results |
| Open-source code release | 10,000 | License review, documentation, public repository hardening |
| Public reporting & dissemination | 15,000 | Methodology notes, case studies, multilateral submissions |

### G. Programme Coordination (USD 100,000)

| Line item | USD | Notes |
|---|---:|---|
| Programme management | 60,000 | Part-time programme lead — institutional coordination, grant reporting, multi-stakeholder management |
| Legal and IP | 25,000 | CIPA, ARIPO, intercompany licensing agreement maintenance, contract review |
| Accounting and audit | 15,000 | Statutory accounts, grant audit compliance, financial controls |

---

## Modular sub-budgets — adapt per grant

### Sub-budget 1: PSE / Ethereum Foundation (USD 150,000)
Cryptographic engineering and audit-specific workstreams only. Most aligned with PSE's research-grant remit.
| Workstream | USD |
|---|---:|
| ZK Circuit Lead — 6-month milestone (B partial) | 100,000 |
| ToB audit contribution (A partial) | 50,000 |

### Sub-budget 2: NORAD (USD 950,000)
Full programme minus EU-specific workstreams. Aligned with Norway's Tax for Development mandate.
| Workstream | USD |
|---|---:|
| Independent security audit (A) | 275,000 |
| Senior engineering (B) | 480,000 |
| Sovereign integration pilot (C) | 225,000 |
| Travel & engagement (E partial — Lusaka + Oslo) | 40,000 |
| M&E and reporting (F partial) | 70,000 |
| Programme coordination (G) | 100,000 |

Note: subtract overlap with other funders if co-funded. NORAD typically accepts 12–18 month programmes.

### Sub-budget 3: AfDB (USD 500,000)
Sovereign integration + audit. Aligned with digital governance / digital public infrastructure remit.
| Workstream | USD |
|---|---:|
| Audit (A partial) | 150,000 |
| Sovereign integration (C) | 225,000 |
| Travel & engagement (E partial) | 35,000 |
| M&E and reporting (F partial) | 50,000 |
| Programme coordination (G partial) | 40,000 |

### Sub-budget 4: EU Horizon Europe (EUR 1,500,000)
Consortium proposal — RC as the cryptographic/sovereign-side WP lead. EU partner leads on regulatory and OEM-side WPs. Numbers below are RC's slice of a larger consortium budget.
| Workstream | EUR |
|---|---:|
| Battery Passport compliance layer (D scaled) | 400,000 |
| Senior engineering (B partial) | 500,000 |
| EU regulatory and consortium coordination | 200,000 |
| Travel & engagement (E partial — Brussels heavy) | 100,000 |
| M&E and dissemination (F partial) | 100,000 |
| Programme coordination (G partial) | 100,000 |
| Consortium overhead | 100,000 |

### Sub-budget 5: Open Society Foundations (USD 350,000)
Governance, transparency, civil-society-alignment workstreams. Two years.
| Workstream | USD |
|---|---:|
| ZEITI methodology mapping (C partial) | 100,000 |
| Open-source release and public goods contribution (F partial) | 50,000 |
| Civil-society engagement (PWYP, NRGI, GW alignment) | 50,000 |
| Programme coordination (G partial) | 50,000 |
| Independent impact assessment (F partial) | 50,000 |
| Audit contribution (A partial) | 50,000 |

---

## Cost-recovery and overhead

Standard indirect cost recovery (overhead) is typically 10–15% on top of direct programme costs for most institutional funders (NORAD, AfDB, OSF). EU Horizon caps at 25%. The figures above are *direct* programme costs — add the appropriate overhead per funder's policy when submitting.

For the **operating entity in Zambia**, overhead also funds: office, statutory accounting, board governance, and institutional liaison. This is not waste — it is the infrastructure that makes the grant compliance possible.

---

## Co-funding scenarios

The total programme (USD 1.51M) can be assembled from any of the combinations below:

| Combination | Total raised | Notes |
|---|---|---|
| NORAD only | 950K | Covers most of the programme; gaps in EU layer and second-auditor redundancy |
| AfDB + PSE + OSF | 1.0M | Covers core engineering, audit, sovereign integration |
| NORAD + PSE + AfDB | 1.6M | Full programme with margin |
| NORAD + EU Horizon + PSE | 3.2M | Full programme plus second-country expansion runway |
| All Tier 1 + Tier 2 | 3.5–4.5M | Maximum scenario — funds Phase 2 expansion as well |

The modular budget structure means co-funding does not produce duplication. Each funder sees a defined workstream attached to their thematic mandate.

---

## Notes for grant officers

1. **Engineering costs are fully loaded** — salary, benefits, employer taxes, equipment, software licensing, and apportioned office cost. Not just headline salary.
2. **Audit costs are at market.** Trail of Bits estimate is derived from initial scoping; final SOW will be the binding document.
3. **No founder salary or principal compensation** is drawn from the grant in the first 18 months. Kennedy Thebe's compensation is performance-linked to ZRA contract realisation, not grant-funded.
4. **All foreign exchange exposure** (USD-funded programme delivered in ZMW, EUR, NOK) is monitored quarterly; budget includes a 5% FX contingency embedded in line-item allocations.
5. **Audit-readiness:** programme accounts will be maintained to OECD-DAC reporting standards, supporting any donor's audit and verification requirements.
