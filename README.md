# The Brogue Distillery – Financial Model Suite  
*(README v1.0 – July 2025)*  

Welcome to the full-stack financial model for The Brogue Distillery, the smoke-forward American Single Malt challenger brand built on the Rogue inventory acquisition.  
This workbook is engineered for FP&A-grade accuracy **and** board-room clarity: every blue cell is an input, every grey cell is a scenario feed, everything else is locked math.

---

## 1. Package Contents

| File | Purpose |
|------|---------|
| `Brogue_Distillery_Model_v1.0.xlsm` | Core model (all 13 sheets, macros enabled). |
| `Brogue_Distillery_Key_Formulas.xlsx` | Read-only crib sheet of core formulas & named ranges. |
| `Brogue_Distillery_Implementation_Guide.md` | Step-by-step build & maintenance playbook. |
| `Investor_Case_v1.0.xlsx` | Frozen copy signed off at SAFE close. |
| `Sample_Actuals_QB.csv` | Template for QuickBooks/Xero monthly export. |

*(PDF diligence pack and Monte-Carlo sheet generate automatically from inside the model.)*

---

## 2. Sheet Map (inside `Brogue_Distillery_Model`)

| # | Sheet | What It Does | Edit? |
|---|-------|--------------|-------|
| 01 | **Assumptions** | Single input grid, grouped Volume • Pricing • COGS • OpEx • CapEx • Tax • Financing • Channel Mix. | Blue cells only |
| 02 | **Revenue Engine** | Bottles → Channels → Price ladders → Returns/Allowances. | Locked |
| 03 | **COGS Calc** | Raw spirit, barrel amort, packaging, excise, freight. | Locked |
| 04 | **SG&A / OpEx** | Headcount driver table + variable OpEx. | Hire dates & salaries via inputs |
| 05 | **CapEx + Deprec.** | Timing toggle, straight-line schedules. | CapEx months via inputs |
| 06 | **Cashflow & Runway** | Monthly waterfall, revolver draw logic, 6-mo burn runway. | Locked |
| 07 | **Cap Table + SAFE** | Pre/post money, discount vs. cap conversion, dilution waterfall. | Locked |
| 08 | **Scenario Switcher** | Base / Upside / Downside parameter grid driven by `CHOOSE()`. | Grey cells (scenario values) |
| 09 | **Dashboards** | Breakeven chart • Runway gauge • EBITDA waterfall • Investor IRR. | View only |
| 10 | **Sensitivity** | One- & two-variable tables + hidden Monte-Carlo. | Run data tables only |
| 11 | **Diligence Pack** | 3-page narrative auto-PDF generator. | View only |
| 12 | **Ops Tracker** | Pulls actuals, variance traffic lights. | Post-close use |
| 13 | **Changelog** | Version log. | Add notes |

---

## 3. Quick-Start

1. **Enable Macros** when you open the workbook.  
2. Go to **01 Assumptions** and update blue cells (Volume, Pricing, etc.).  
3. Flip scenarios on **08 Scenario Switcher** via the dial (1 = Base, 2 = Upside, 3 = Downside).  
4. Review impact instantly on **09 Dashboards**.  
5. Run sensitivities:  
   • Data ► What-If ► Data Table on the pre-built grids in **10 Sensitivity**.  
6. To export the investor PDF: Developer ► Macros ► `ExportDiligencePDF`.

---

## 4. Key Features

### Scenario Dial  
Single integer feeds every assumption through `CHOOSE()`—model recalcs in <1 s.

### Revolver Auto-Draw  
Draws exactly the cash shortfall, repays on surplus, accrues interest monthly.

### Runway Gauge  
6-month trailing burn, color-coded (Green < 5 % drift, Yellow 5-15 %, Red > 15 %).

### SAFE vs. Cap Logic  
Converts at lower of valuation cap or discount; shows post-SAFE dilution and Series A waterfall.

### Sensitivity Harness  
• One-var: Channel mix, Series A timing.  
• Two-var: CapEx overrun % × Bottle velocity → runway months heat-map.  
• Hidden Monte-Carlo (toggle visibility) for nerd mode.

### Protection  
Only inputs are unlocked; workbook structure protected (`brogue!2025`).  Named ranges prevent hard-code creep.

---

## 5. Connecting Actuals (Post-Close)

1. Refresh Power Query linked to QuickBooks/Xero export (`Sample_Actuals_QB.csv` structure).  
2. Press **Refresh Variance** button on **12 Ops Tracker**—traffic lights update.  
3. Items flagged Red (>15 % variance) auto-list for board review.

---

## 6. Versioning & Governance

| Action | Version bump |
|--------|--------------|
| Data-only change | +0.0.1 |
| Formula logic | +0.1 |
| Sheet structure / macros | +1.0 |

Always archive prior version in `/Archive` before sharing externally.

---

## 7. FAQ

**Q:** Model shows `#REF!` after adding rows?  
**A:** Use structured tables (`Ctrl + T`). Extending raw ranges will break named references.

**Q:** Can I add a new sales channel?  
**A:** Yes—duplicate a column set in **02 Revenue Engine**, add input rows on **01 Assumptions**, and include in channel mix totals (must still sum 100 %).

**Q:** How do I change the revolver limit?  
**A:** Update `inp_Revolver_Limit` on **01 Assumptions**.

---

## 8. Support

Ping Jake or the FP&A lead on Slack `#brogue-fin-model`  
Bugs → GitHub issues in `BrogueDistillery/finance-model`.  

Happy modeling—may your proof-gallons be ever cheap and your runway long.
