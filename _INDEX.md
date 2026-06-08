# Resource Command — Project Index

**Owner:** Kennedy Thebe, Principal, Kgosi Sovereign Holdings
**Last reorganised:** 7 June 2026
**Project root:** `C:\Users\R5 5600 GT\.gemini\antigravity\scratch\resource_command\`

A clean, navigable file index. Find any document in 5 seconds. Keep the structure clean by adding new files to the matching folder, not the root.

---

## 🟢 Quick-access (root-level)

| File | Purpose |
|---|---|
| `_INDEX.md` | This file — table of contents |
| `CLAUDE.md` | Claude Code project memory — keep at root, read on every session start |
| `rc_intelligence_monitor.js` | The 15-layer intel monitor — run with `node rc_intelligence_monitor.js` |
| `package.json` / `package-lock.json` | Node dependencies for the intel monitor |
| `.env` / `.env.example` / `.mcp.json` | Environment + MCP server configs |

---

## 📁 01 — Technical Specifications

`01_Technical_Specifications/`

The protocol specifications. What the cryptography does and how.

| File | Purpose |
|---|---|
| `Adversarial_Proof_of_Work.md` | Attack-resistance analysis for the RC primitive |
| `Circomspect_Pre_Analysis.md` | Pre-audit clean-state confirmation from Circomspect |
| `Geochemical_Oracle_Specification.md` | Physical-data feed specification for ore characterisation |
| `MPC_Ceremony_Specification.md` | Phase 2 trusted-setup ceremony protocol |
| `Node_Infrastructure_Specification.md` | Validator-node hardware and network requirements |
| `Oracle_Pipeline_Security_Spec.md` | Full security architecture for the oracle layer |
| `Oracle_Pipeline_Spec.md` | Operational specification of the oracle pipeline |
| `RC_Verification_and_Hardening_Statement.md` | Internal certificate of readiness — five-pass audit summary |
| `Threat_Model.md` | Full attack-surface analysis |
| `Trusted_Setup_Specification.md` | Powers of Tau + Phase 2 ceremony documentation |

---

## 📁 02 — Engagements

`02_Engagements/`

One folder per relationship. All correspondence, drafts, prep, and outputs in one place.

### `Trail_of_Bits/`
Primary ZK auditor. Scoping call booked Tue 9 June 2026.

- `ToB_Audit_Cover_Letter.docx` / `.md` — cover letter
- `ToB_Followup_Note.md` — interim followup
- `DRAFT_ToB_Scheduling_Email.md` — scheduling correspondence (sent)
- `audit_engagement_memo.md` — engagement memo

### `ZEITI_Ian_Mwiinga/`
Zambia EITI Chapter Lead. Call booked Tue 16 June 2026, 11:30 CAT.

- `16Jun2026_Methodology_Call/` (the full meeting prep folder)
  - `ZEITI_Pre_Read_Brief.md` / `.pdf` — the strategic two-pager (sent)
  - `Call_Talking_Points.md` — internal strategic prep
  - `Call_Prep_Plain_Language.md` — plain-language call script
  - `ZEITI_Call_Invite.ics` — calendar invite
  - `build_brief_pdf.py` — PDF generator script

### `Barry_Whitehat/`
Semaphore creator, independent ZK reviewer. 11-email correspondence active.

- `DRAFT_Barry_Whitehat_Email.md` — latest outbound draft

### `Ministry_David_Wamulume/`
Ministry of Energy contact. Promised ministry intro — awaiting.

- `2026-06-04_v1_Followup.md` through `v5_WhatsApp.md` — five-variant followup drafts

### `KoBold_Metals/`
Mining-operator engagement target.

- `KoBold_One_Page_Intro.md` — concise intro brief

### `ZK_Researcher_Outreach/`
Wider ZK research community outreach.

- `ZK_Researcher_Outreach.md` — general outreach playbook

### `ZRA_Strategy/`
Zambia Revenue Authority — sovereign anchor client.

- `ZRA_Meeting_Strategy_June2026.md` — pre-election engagement strategy

---

## 📁 03 — Commercial

`03_Commercial/`

Pitch material, briefs, pre-reads. Everything client-facing.

### `Pitch_Material/`
- `Resource_Command_Presenter_Notes_v2_May2026.docx` — speaking notes (use the v2)
- `Resource_Command_Shareholder_Briefing_v2_May2026.docx` — shareholder version (use the v2)
- `Resource_Command_Presenter_Notes_May2026.docx` — earlier version (reference)
- `Resource_Command_Shareholder_Briefing_May2026.docx` — earlier version (reference)
- `RC_Progress_Presentation.html` — interactive progress presentation
- `SovereignDashboard.jsx` — dashboard React component (preview asset)

### `Pre_Reads/`
- `Resource_Command_Technical_Pre-Read.md` / `.docx` — institutional pre-read

### `Briefs/`
- `Resource_Command_Government_Concept_Paper.md` — government-facing concept
- `Resource_Command_Institutional_Proposal.md` — institutional proposal
- `Resource_Command_Sovereignty_Brief.md` — sovereignty positioning
- `Resource_Command_Legal_Risk_Architecture.md` — legal/IP risk architecture
- `Resource_Command_Geopolitical_Positioning.docx` — geopolitical brief
- `EU_Battery_Passport_Alignment.md` — EU regulatory alignment
- `Tripartite_Sovereign_MOU.md` / `.docx` — three-party governance MOU template

---

## 📁 04 — Reference

`04_Reference/`

Master context + reusable language. The "always-on" reference shelf.

| File | Purpose |
|---|---|
| `MASTER_CONTEXT.md` | Project-wide single source of truth |
| `Resource_Command_End_to_End.md` | End-to-end narrative |
| `Institutional_Language_Matrix.md` | Language register per audience |
| `Counter_Narrative_Response.md` | Pre-built responses to objections |
| `Academic_Paper_Abstract.md` | Academic publication abstract |

---

## 📁 05 — Drafts

`05_Drafts/`

Work-in-progress public-facing material.

- `DRAFT_LinkedIn_Profile.md` — LinkedIn profile rewrite

---

## 📁 06 — Session Logs

`06_Session_Logs/`

Periodic project status snapshots. Read-only history.

- `SESSION_SUMMARY_June4_2026.md`
- `RC_Phase2_Internal_Update.md`
- `research_log.md`

---

## 📁 07 — Code

`07_Code/`

All Python/JS scripts grouped by function. Working code — run scripts from inside their folder so relative paths work.

### `Circuit/`
- `circom.exe` — Circom compiler
- `compliance.r1cs` — compiled circuit
- `resource_command_zkp.py` — Python reference implementation
- `package_audit_pack.py` — audit pack assembler
- `boundless_prover.py` — Boundless/RISC Zero integration

### `Oracle_Pipeline/`
- `hardware_signal_pipeline.py` — telemetry signal handling
- `hardware_witness.json` — generated witness data
- `cdse_test.py` — Copernicus satellite test
- `cdse_mopani_scenes.json` — CDSE scene specs
- `trigger_oracle_render.py` — oracle rendering trigger

### `Demo_App/`
- `index.html` / `app.js` / `style.css` — web demo UI
- `data.js` — demo data
- `demo_server.py` — local demo server
- `demo_state.db` — demo SQLite
- `speaking_coach.html` — speaking-prep tool
- `test_demo_api.py` — demo API test

### `Generators/`
- `generate_docx.js` — DOCX generator
- `generate_presentation.py` — pitch deck generator
- `generate_presenter_notes.py` — presenter-notes generator
- `bulk_convert_docx.js` — DOCX converter utility

### `Runtime_Data/`
- `sovereign_memory.json` — runtime memory
- `session_memory.py` — session-memory utility

---

## 📁 Working Subfolders (not reorganised — stable as-is)

| Folder | Purpose |
|---|---|
| `circuits/` | Circom circuit source files |
| `dashboard/` | React dashboard project |
| `funding/` | Grant strategy + application pack (already organised, contains `Grant_Tracker_v1.md`, `Grant_Application_Pack/`, `RC_Grant_Pack.zip`) |
| `historical_replay/` | G-Factor historical replay — data, scripts, output (already organised) |
| `mcp-specter/` | Specter-Vision MCP server source |
| `memory/` | Claude memory files — read every session start |
| `scratch/` | Temporary working files |
| `specter-vision/` | Replicate API MCP integration |

---

## 📁 Audit Pack

`_Audit_Pack_Current/` — the current Trail of Bits transmission

- `Resource_Command_Audit_Pack_v1.8_FINAL.zip` — current dispatched version
- `Working_Folder/` — extracted working copy

Older versions in `_Archive/Audit_Packs_Old_Versions/`.

---

## 📁 Archive

`_Archive/`

- `Audit_Packs_Old_Versions/` — v1.1 through v1.7 (do not delete — provenance)
- `Misc/` — unrelated test assets (e.g. AI-generated images from earlier experiments)

---

## Status snapshot (7 June 2026)

| Track | Status | Next |
|---|---|---|
| Trail of Bits scoping call | 🟢 Booked Tue 9 Jun 2026 | Walk through audit pack v1.8 |
| ZEITI / Ian Mwiinga methodology call | 🟢 Booked Tue 16 Jun 2026, 11:30 CAT | Brief sent, calendar accepted |
| Barry Whitehat parallel review | 🟡 11 emails deep, awaiting reply | Followup if no response by mid-June |
| Ministry contact (Wamulume) | 🟡 Promised intro to mining ministry | Soft followup |
| Grant track | 🟡 PSE/AfDB/OSF priority | Apply post-ToB SOW (~late June) |
| Historical replay vs ZEITI | ✅ Complete | 11/11 match, deliverable PDF ready |

---

## Navigation rules going forward

1. **Drafts go in `05_Drafts/`** until sent or used. After that, they move to the relevant engagement folder.
2. **Spec changes go in `01_Technical_Specifications/`** with a version suffix.
3. **New engagements get a folder under `02_Engagements/`** named for the counterparty.
4. **Pitch/brief revisions** go in `03_Commercial/`. Keep one current + archive prior.
5. **Code lives in `07_Code/`**. Don't drop Python/JS into the root.
6. **Old artifacts go to `_Archive/`**, not deletion. Provenance matters in audit conversations.
