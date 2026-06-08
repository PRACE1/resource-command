# Historical Replay — ZEITI 2022 Cycle

**Purpose:** Demonstrate that Resource Command's cryptographic verification primitive reproduces ZEITI's published reconciliation totals — *without* exposing operator-side commercial data.

**Deliverable:** A one-page printed PDF to hand Ian Mwiinga on Tuesday 16 June 2026.

---

## Folder structure

```
historical_replay/
├── README.md           ← you are here
├── replay.py           ← the script that does the work
├── data/               ← ZEITI Excel files go here
└── output/             ← results land here after a run
    ├── replay_results.csv
    └── replay_summary.md
```

---

## Phase 1 — Get the data (you, today, 30 min)

1. Go to **https://portal.zambiaeiti.org/home**
2. Find the data downloads section (look for "Data", "Reports", "Reconciliation", or "Open Data" nav links).
3. Download the most recent Excel files — at minimum the **2022 Reconciliation Report**, ideally also the **2023–24** if it's posted.
4. Drop the files into the `data/` folder.

If the portal nav is unclear, try:
- `eiti.org/documents/zambia` (EITI International archive)
- Google: `site:zambiaeiti.org filetype:xlsx`
- Or contact ZEITI directly via the portal — but only as a fallback, since the data is supposed to be public.

---

## Phase 2 — Map the columns (you + me, 1 hour, tomorrow)

After you have one Excel file:

1. Open it in Excel.
2. Look at the column headers in the reconciliation sheet.
3. Tell me what the column names are.

The script's `DEFAULT_COLUMN_MAP` (top of `replay.py`) has educated guesses — it'll auto-detect common variants like "Company", "Operator", "Volume", "Tonnes", etc. If a column name doesn't match a guess, the script prints out the actual columns and asks me to update the mapping.

---

## Phase 3 — Run the replay (1 command)

```powershell
cd "C:\Users\R5 5600 GT\.gemini\antigravity\scratch\resource_command\historical_replay"
python replay.py
```

The script:

1. Loads every `.xlsx` / `.xls` file in `data/`.
2. For each row: applies RC's cryptographic commitment scheme + recomputes the royalty using RC's canonical formula.
3. Compares the recomputed royalty against ZEITI's published number.
4. Writes:
   - `output/replay_results.csv` — full per-row results
   - `output/replay_summary.md` — the one-pager you take to the call

---

## Phase 4 — Generate the PDF deliverable (1 hour)

Once `replay_summary.md` looks good, we convert it to PDF using the same `build_brief_pdf.py` pattern from the ZEITI brief. Two pages max, navy + gold institutional palette, ready to print or attach.

---

## Dependencies

- Python 3.10+
- `pandas`, `openpyxl` (install: `python -m pip install pandas openpyxl`)
- `reportlab` (for the PDF, already installed from the ZEITI brief work)

---

## What this gives you on the call

Instead of asking Ian for permission to do Phase 2 (historical replay) — you walk in showing him you've **already done it**. The conversation jumps a step. The asks shift:

- ❌ "Could ZEITI share three reconciliation cycles?"
- ✅ "I've done the 2022 cycle. Want to extend it to 2023–24 together?"

That's the move.
