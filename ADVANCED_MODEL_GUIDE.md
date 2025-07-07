# Advanced Modular Financial Model – **User & Developer Guide**
*(File name: `ADVANCED_MODEL_GUIDE.md`)*  

---

## 1  Why We Re-architected

| Legacy Excel-Only | Advanced Modular Model |
|-------------------|------------------------|
| Binary file, poor Git diffs | Text-based YAML + Python ⇒ clean version control |
| Hidden formulas, hard to audit | Pure Python functions, unit-testable |
| Manual refresh, risk of broken links | Single-command regeneration; CI-friendly |
| Limited visuals | Auto-built Excel + optional PDF & Dash dashboard |
| No live data hooks | Designed for QuickBooks/Xero API feeds |

**Principle:** *Separate Data → Logic → Presentation.*  
Assumptions live in **YAML**, calculations in **Python (pandas)**, outputs in **Excel (XlsxWriter)**; other front-ends can be bolted on without touching core math.

---

## 2  Repository Layout

```
distillery_model/             # Python package
│
├─ config/
│   └─ assumptions.yaml       # Single source of truth (all scenarios + constants)
│
├─ core/
│   ├─ __init__.py
│   └─ model.py               # DistilleryModel: pure calculation engine
│
├─ outputs/
│   ├─ __init__.py
│   └─ excel.py               # ExcelReport: presentation layer
│   └─ (pdf.py, dashboard.py) # placeholders for future outputs
│
├─ __init__.py                # Package entry
│
requirements_advanced.txt     # Python deps
run_model.py                  # CLI wrapper – orchestrates everything
```

---

## 3  Installation

```bash
# 1. (Recommended) create virtual env
python -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements_advanced.txt
```

---

## 4  Running the Model

### 4.1 CLI

```bash
python run_model.py --scenario "Base Case"
```

Generates:

```
outputs/
├─ Brogue_Distillery_Model_Base_Case.xlsx
└─ (future) PDFs & dashboard assets
```

Change `--scenario` to **Upside Case** or **Downside Case** to flip the entire model.

### 4.2 Inside Python

```python
from pathlib import Path
import yaml
from distillery_model.core.model import DistilleryModel
from distillery_model.outputs.excel import create_excel_report

constants, scenarios = yaml.safe_load(Path("distillery_model/config/assumptions.yaml").read_text()).values()
scenario = next(s for s in scenarios if s["name"] == "Base Case")

results = DistilleryModel(scenario, constants).run_model()
create_excel_report(results, scenario, constants, "my_model.xlsx")
```

---

## 5  Editing Assumptions

Open `distillery_model/config/assumptions.yaml`

* **constants** – items that never change across scenarios (tax rates, depreciation life, headcount plan).
* **scenarios** – three blocks (Base, Upside, Downside).  
  Simply tweak values or add new scenario objects.

Benefits:

* **Git diff-friendly** – every assumption change shows as one-line diff.
* **No hidden Excel constants** – audit trail lives in plain text.

---

## 6  How the Engine Works

1. **Volume & Revenue**  
   `model._calculate_volume_and_revenue()` converts annual bottle targets to monthly, applies channel mix & escalators.

2. **COGS**  
   Per-bottle cost stack multiplied by volume.

3. **OpEx**  
   Payroll driven by headcount table; variable costs as % of revenue; rent & utilities escalators.

4. **CapEx / Depreciation**  
   Initial spend applied in month 2, straight-line depreciation.

5. **Cash Flow & Revolver**  
   Iterative monthly loop draws/repays a revolver to maintain positive cash or track deficit.

6. **Cap Table**  
   SAFE converts at **min(cap price, discount price)**; Series A price from pre-money valuation; ownership waterfall computed.

Unit tests can target each private step for numeric accuracy.

---

## 7  Excel Report Highlights

* Dashboard with KPI cards, Revenue vs EBITDA column chart, Cash Balance line chart.
* Financials sheet: 5-year P&L & Cash-flow summary with negative-number red fill.
* Cap Table sheet clearly separates SAFE vs Series A dilution.
* Assumptions dump for auditors – every scenario input visible.

All formatting is handled by **XlsxWriter**; no macros required, so the file opens cleanly on Mac & Windows with security prompts off.

---

## 8  Extending the Model

| Task | Where to Change | Tips |
|------|-----------------|------|
| Add scenario (e.g. *Stress Case*) | `assumptions.yaml` under `scenarios` | No code change needed |
| Add monthly detailed schedules | Add methods to `core/model.py` | Keep functions < 25 lines for readability |
| Generate PDF board pack | Implement `outputs/pdf.py` using ReportLab | Can reuse results dict |
| Live dashboard | Build `outputs/dashboard.py` with Dash | Map results into Plotly graphs |
| Actuals integration | Create `data/quickbooks_adapter.py` | Merge actuals → variance vs. model |

---

## 9  CI / Automation Ideas

* **Pre-commit hook**: `python run_model.py --scenario "Base Case"` → regenerate `.xlsx`, fail if git diff occurs.
* **GitHub Actions**: on push to `main`, run all scenarios, attach Excel & PDF artefacts to build.
* **Cron job / Airflow**: nightly pull QuickBooks API, run model, post variance dashboard.

---

## 10  Security & Governance

* Configuration and code in plain text → easy to code-review.
* No secrets in repo; connect accounting APIs via env vars or a secrets manager.
* Lock Excel sheets on distribution (`Review → Protect Sheet`), leaving dashboard & assumption cells unlocked.

---

## 11  Benefits Recap

1. **Auditability** – Transparent YAML + unit-testable Python beats opaque spreadsheets.  
2. **Version Control** – Text diffs, easy rollbacks, code reviews.  
3. **Robust Outputs** – Excel, PDF, and web can all stem from one engine.  
4. **Scalability** – Add years, channels, or new funding rounds with minimal refactor.  
5. **Professional Polish** – Auto-formatted, investor-ready files every run.

---

### Questions?  
Open an issue or ping the FP&A channel – happy modeling!
