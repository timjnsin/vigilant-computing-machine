# Brogue Distillery Financial Model  
**User Guide / Playbook (EXCEL_MODEL_GUIDE.md)**  

---

## 1. Overview

This model was purpose-built for The Brogue Distillery’s fundraising, board reporting, and post-close ops tracking.  
Everything is generated automatically from Python so you always start with a **clean, formula-perfect workbook**.

Repository artefacts:

| File | Purpose |
|------|---------|
| `requirements.txt` | single dependency (`openpyxl`) |
| `create_excel_model.py` | generates the Excel workbook |
| `Brogue_Distillery_Financial_Model.xlsx` | auto-built model (output) |

---

## 2. Quick Start

```bash
# 1. set up venv (recommended)
python -m venv .venv && source .venv/bin/activate
# 2. install deps
pip install -r requirements.txt
# 3. generate model
python create_excel_model.py
# 4. open in Excel
open Brogue_Distillery_Financial_Model.xlsx
```

> On Windows just double-click the `.xlsx` once Python finishes.

---

## 3. Sheet Map

| Tab | Name                     | Role (edit?) |
|-----|--------------------------|--------------|
| 01  | **Assumptions**          | Blue inputs only |
| 02  | **ScenarioSwitcher**     | Stores Base / Upside / Downside values |
| 03  | **Financials**           | 5-year P&L & Cash flow (locked) |
| 04  | **Cap_Table**            | SAFE conversion & dilution math |
| 05  | **Dashboard**            | KPI cards + EBITDA chart |

*(Hidden named ranges drive charts; keep them intact.)*

---

## 4. Editing Inputs

### 4.1 Blue-Cell Paradigm  
All editable drivers are blue-filled in **01_Assumptions**.  
Each input is also a **named range** (e.g., `inp_Y1_Volume`).

### 4.2 Scenario Control  
Cell **B19** (`inp_Scenario_Index`) holds 1, 2 or 3.

| Code | Scenario |
|------|----------|
| 1 | Base |
| 2 | Upside |
| 3 | Downside |

Changing this flips every input via `CHOOSE()` formulas pointing to **02_ScenarioSwitcher**.

---

## 5. Using Advanced Features

### 5.1 Sensitivities (09_Sensitivity)  
* One-variable table (Marketing %):  
  1. Select range **A3:C8**.  
  2. Ribbon → Data → *What-If Analysis* → *Data Table*.  
  3. “Column input cell” → `inp_Marketing_Pct`.

* Two-variable grid (CapEx overrun × Bottle velocity):  
  1. Select **A12:F17**.  
  2. Data Table → Row input: `inp_Y1_Volume`; Column input: `inp_Capex_Overrun`.  
  3. Apply conditional-format heatmap if desired.

### 5.2 Dashboard  
KPI cards pull live from **03_Financials** and **Cash flow** outputs:

- Year-1 & Year-5 EBITDA
- Current runway (months) → auto-updates with scenarios

Bar chart: EBITDA trajectory across five years.

### 5.3 SAFE / Cap-Table Logic  
Found in **04_Cap_Table**:

```
Effective SAFE Price = MIN(Valuation Cap / Pre-Money Shares,
                            Series-A Price × (1 – Discount))
Shares to SAFEs       = SAFE Cash / Effective Price
```

Update founder or option-pool share counts in cells B2/B3 if cap-table changes.

---

## 6. Customisation Playbook

| Task | Where | How |
|------|-------|-----|
| Extend forecast to 10 yrs | 03_Financials | Copy right two blocks of 5 yrs; adjust formulas |
| Add new sales channel | 01_Assumptions & 03_Financials | Add mix %, price, COGS; ensure mix totals 100 % |
| Change depreciation life | 01_Assumptions | Edit `inp_Depr_Years`; formulas auto flow |
| Lock workbook | Review tab → Protect Sheets; keep blue inputs unlocked |
| Versioning | Save as `Model_vX.Y.xlsx`; log in repo `CHANGELOG.md` |

---

## 7. Troubleshooting

| Issue | Fix |
|-------|-----|
| “External links” warning | Comes from chart series; click *Update*. |
| `#NAME?` after editing inputs | Check you didn’t overwrite a named range. |
| Circular reference popup | None exist by default; if you add iterative calc logic turn on *Enable iterative calculation* (Options → Formulas). |
| Mac opens read-only | Remove file from quarantine (`xattr -d com.apple.quarantine file.xlsx`). |

---

## 8. Hardening & Security

1. Workbook structure protected (`Review → Protect Workbook`), password optional.  
2. Named ranges prevent hard-coded cell refs.  
3. Store signed copies; prefer Git LFS for binary versioning.

---

## 9. Roadmap Ideas

- **Monthly granularity** (revenue, COGS, OpEx) – extend scripts to 60 columns and autopop.
- **Power Query** actuals feed – map QuickBooks exports to append actual vs. budget.
- **VBA buttons** for scenario toggle & PDF export (stubbed in Python comments).

Pull requests welcome – keep functions < 20 lines, commit messages `feat:` / `fix:` etc.

---

**Enjoy the model – and may your proof-gallons stay cheap!**  
