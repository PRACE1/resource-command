# Problem Statement and Theory of Change

*Reusable across grant applications. Adapt to each grant's required vocabulary.*

---

## Problem Statement

### The verification gap in African mineral revenue

African mineral economies — Zambia, the Democratic Republic of Congo, Tanzania, Botswana, Zimbabwe — collectively export over USD 60 billion in copper, cobalt, lithium, and nickel annually. Yet revenue mobilization from these exports remains structurally below potential. In Zambia alone, the empirical mineral royalty under-collection gap is **USD 550M–940M per year** (ZRA / UNU-WIDER / ICTD, 2023), equivalent to 0.5–1.0% of GDP and 5–8% of the national budget.

The gap is not a measurement failure. The Zambia Revenue Authority operates Smart Invoice (41,111 taxpayers, 161.4M invoices issued by end 2025), the BIDA analytics platform for risk-weighted audit selection, a UNU-WIDER-built Secure Data Lab, and achieved 22.1% tax-to-GDP in 2025. The technical sophistication exists.

The gap is a **verification failure**. Even the most rigorous audit must eventually trust the operator's self-declared production figures — tonnage extracted, grade assayed, price realized. The cryptographic primitive that would let a tax authority *prove* a royalty calculation is correct without seeing the underlying commercial data has, until recently, not existed at production grade.

### Why existing solutions fall short

| Approach | Limitation |
|---|---|
| **Traditional audit firms** (Big Four) | Auditors must see all underlying data. Operators resist disclosure of commercial volumes. Audit cycles run 6–24 months. Disputes are common. |
| **ERP and tax-reporting platforms** | Improved data quality at the input layer, but the input is still self-declared. No cryptographic guarantee against tampering. |
| **Blockchain provenance tools** (Minespider, Circulor) | Solve traceability but require operators to publish production data on-chain — destroying commercial confidentiality and creating an entirely new attack surface. |
| **Direct sensor-based monitoring** | Capital-intensive, jurisdiction-dependent, politically fraught, and produces data the operator can dispute. |

Each existing approach forces the operator and the state into the same impossible trade-off: full operator disclosure, or trust-based verification. Neither produces sovereign-grade mineral revenue assurance.

### The opportunity

Zero-knowledge cryptography — specifically the Groth16 SNARK construction over the BN254 elliptic curve — enables a fundamentally new approach. A mining operator can generate a mathematical proof that a royalty calculation is correctly computed from its actual production inputs, while keeping those inputs cryptographically sealed. The state verifies the proof. Nobody opens the envelope. The math makes forgery infeasible.

Resource Command operationalizes this primitive in a production-grade circuit, with an oracle commitment layer for input attestation and an institutional consensus layer for validator independence.

The EU Battery Passport regulation (in force 18 February 2027) makes this approach not merely useful but regulatory: every kilogram of cobalt, copper, lithium, and nickel entering the European supply chain will require cryptographic source-layer attestation. African mineral economies that adopt the verification infrastructure in the next 18 months become EU-compliant exporters by default. Those that do not face progressive market exclusion.

---

## Theory of Change

### Inputs (grant-funded)

- **Cryptographic engineering capacity** — two senior engineers (ZK circuit lead, Rust integration lead) over 18 months
- **Independent security audit** — Trail of Bits formal engagement (audit kickoff July 2026), plus a second auditor for redundancy
- **Sovereign integration capacity** — methodology mapping, oracle architecture remediation, ZRA technical integration
- **Institutional engagement capacity** — ZEITI methodology pilot, AfDB and EITI International coordination, EU Battery Passport regulatory liaison
- **Monitoring, evaluation, and open publication** — pilot performance data, methodology notes, peer-reviewed publication of the cryptographic contribution

### Activities (18 months)

1. **Complete the security audit and remediation cycle** with Trail of Bits and a second independent auditor.
2. **Pilot integration** with the Zambia Revenue Authority on a single mineral category and reporting period.
3. **Methodology mapping** with ZEITI Secretariat, leading to a co-authored methodology note.
4. **Battery Passport compliance layer** deployed for one mining operator, demonstrating dual-use compliance (sovereign + EU regulatory).
5. **Open publication** of the methodology and the cryptographic contribution, including any open research findings (timing-attack mitigation, Gauss-Legendre quadrature in ZK circuits).
6. **Knowledge transfer** to ZEITI International (Oslo), with the goal of contributing the verification layer to the next EITI International Standard revision.

### Outputs

- **One audited, production-grade ZK royalty-compliance protocol** with formal third-party audit report
- **One sovereign integration pilot** with ZRA in operation
- **One ZEITI Secretariat methodology note** co-authored with the Zambia chapter
- **One operator-level Battery Passport compliance deployment**
- **Open-source code release** for the cryptographic primitive (under permissive license; commercial pilot retains licensable surface)
- **One peer-reviewed academic publication** on the cryptographic contribution

### Outcomes (24–36 months)

- **Measurable closure of the verification gap** in the Zambia pilot — independently quantifiable narrowing of the 550M–940M gap on the operator/mineral pair piloted
- **Adoption by a second EITI chapter** (DRC, Tanzania, or Indonesia) via methodology transfer
- **EU Battery Passport regulatory recognition** of the cryptographic primitive as a compliance pathway for African suppliers
- **Replication interest** from at least two non-Zambian sovereign tax authorities

### Impact (36–60 months)

- **Continental mineral revenue mobilization** — measurable additional sovereign revenue across African mineral economies attributable to verification-layer adoption
- **EU regulatory access preserved** for African mineral exporters who would otherwise face progressive market exclusion under the Battery Passport regime
- **Institutional precedent** — Zambia recognized as the architect of cryptographic verification within the global EITI framework
- **Public goods contribution** — open-source ZK primitive available for replication beyond extractives (carbon accounting, foreign-aid disbursement, sovereign data verification)

### Assumptions and risks

| Assumption | Risk | Mitigation |
|---|---|---|
| ZRA willingness to pilot the integration | Political turnover before pilot starts | ZEITI methodological cover; multi-stakeholder governance reduces political dependency |
| Trail of Bits audit identifies no fundamental architectural break | Audit identifies a critical flaw | Internal 5-pass audit + Barry Whitehat independent review reduce this risk; second auditor adds redundancy |
| One mining operator agrees to pilot integration | No operator agrees | EU Battery Passport regulatory pressure creates commercial pull; first-mover competitive advantage |
| EITI International receptivity to methodology integration | Oslo rejects or stalls | ZEITI Secretariat methodology note provides national-level legitimacy independent of Oslo |
| Continued institutional bandwidth in Zambia despite election cycle | Election bandwidth eats attention | Pilot designed to be institutionally light; methodology-led, not infrastructure-led |

### Why this theory of change is credible

Resource Command is not speculative research. The cryptographic primitive is built and internally audited. The validator panel is in place (AfDB, World Bank IFC, ZRA, ESA Copernicus, ZCCM-IH). The Trail of Bits scoping engagement is booked. The ZEITI methodology call is booked. The EU Battery Passport deadline is law. The Zambian sovereign anchor is in active conversation.

What grant funding accelerates is not the demonstration of feasibility — that has been done — but the institutional integration and the open replication. The grant compresses what would otherwise be a 36-month bootstrap path into an 18-month coordinated programme.
