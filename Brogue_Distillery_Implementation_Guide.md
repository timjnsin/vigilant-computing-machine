# Brogue Distillery Financial Model  
**Implementation Guide & Playbook**

This document walks you (or the analyst you delegate) through building, deploying and maintaining the Brogue Distillery model exactly as spec’d.  Follow every step in sequence—cutting corners later costs more than doing it right now.

---

## 1. Workbook Skeleton

| Tab # | Sheet Name                    | Purpose                                                         |
|-------|------------------------------|-----------------------------------------------------------------|
| 01    | `Assumptions`                | Single blue-input grid. All drivers named & grouped.            |
| 02    | `Revenue Engine`             | Bottles → Channels → Price ladders → Returns.                   |
| 03    | `COGS Calc`                  | Raw spirit, barrel amort, packaging, excise, freight.           |
| 04    | `SG&A _ OpEx`               | Headcount driver table + other OpEx formulas.                   |
| 05    | `CapEx + Depreciation`       | Timing toggle, SL depreciation schedule.                        |
| 06    | `Cashflow & Runway`          | Monthly waterfall incl. financing flows.                        |
| 07    | `Cap Table + SAFE`           | Pre/post money, discount vs. cap logic, dilution waterfall.     |
| 08    | `Scenario Switcher`          | Base / Upside / Downside parameters using `CHOOSE()`.           |
| 09    | `Dashboards`                 | Breakeven, Runway gauge, EBITDA waterfall, IRR plots.           |
| 10    | `Sensitivity`               | One- & two-variable tables, Monte-Carlo (hidden).               |
| 11    | `Diligence Pack`             | 3-page printable summary (auto-PDF).                            |
| 12    | `Ops Tracker`                | Post-close actuals + variance traffic lights.                   |
| 13    | `Changelog` (optional)       | Version notes.                                                  |

> Keep tab numbers in front of sheet names. It keeps investors from getting lost when you screen-share.

---

## 2. Global Formatting Standards

| Element                    | Style                                                              |
|----------------------------|--------------------------------------------------------------------|
| Input cells                | **Blue fill** `RGB(198, 224, 255)` / white font.                   |
| Calculations               | No fill / black font.                                              |
| Output highlights          | Light green `RGB(226, 239, 218)`; totals in bold.                  |
| Hard-codes in calcs        | 🔴 **Never** – pull from named ranges only.                         |
| Named ranges prefix        | `inp_` (inputs) `out_` (outputs) `drv_` (internals).               |
| Date lines                 | Always Excel serials, custom format `mmm yy`.                      |
| Scenario-specific cells    | Wrap with `CHOOSE(inp_Scenario, …)`                                |

---

## 3. Step-by-Step Build Instructions

### 3.1 Assumptions Sheet

1. Create a 2-column grid: **Label** | **Value**.  
2. Group blocks in this order: Volume • Pricing • COGS • Fixed OpEx • CapEx • Tax • Financing • Channel Mix • Scenario Flag.  
3. Convert each value to a **named range** (e.g., `inp_Y1_Volume`).  
4. Protect sheet, unlock the blue cells only (`Review → Protect Sheet`, allow *Select Unlocked*).

### 3.2 Scenario Switcher

1. Cell `B2` on this sheet stores the scenario index (1-3). Link it to a **Form-Control Spin Button** for UX.  
2. Mirror every assumption back on `Assumptions` using:

   ```
   =CHOOSE(Scenario!$B$2, Scenario!B3, Scenario!C3, Scenario!D3)
   ```

3. Color the CHOOSE formulas light grey so users know they’re auto-fed.

### 3.3 Revenue Engine

1. Reference `inp_Y1_Volume` and monthly distribution row to create monthly bottle counts.  
2. Channel mix: multiply volume by `inp_TR_mix`, `inp_Club_mix`, `inp_WHS_mix`.  
3. Build price ladder table with annual escalator.  
4. Add Returns & Allowances % rows; net them from gross.  
5. **Checks:**  
   - Row total bottles equals input volume.  
   - Channel % adjusted rows sum to 100 %.  

### 3.4 COGS Calc

Follow the sequence already provided.  Key watch‐outs:

- Barrel amortization uses *units-of-production*; tie to volume.  
- Excise per proof-gal vs per bottle: convert properly with `inp_ProofGal_perBottle`.  
- Create an “average cost per bottle” output; use in dashboards.

### 3.5 SG&A / OpEx

1. Build the **headcount table** (position, salary, hire month).  
2. Monthly payroll row uses `IF(hire<=month,salary/12,0)`.  
3. Benefits & tax rider: `inp_Payroll_TaxRate`.  
4. Marketing & G&A are % of **net revenue** – not gross.  

### 3.6 CapEx & Depreciation

1. Timing toggle: each CapEx line has “Month Acquired”. Wrap spend formulas with `IF(month=current, cost*(1+inp_CapexOverrun),0)`.  
2. Depreciation: straight-line; create separate schedules for 7-yr equipment vs 15-yr building.  
3. Link monthly depreciation to P&L.

### 3.7 Cashflow & Runway

1. Pull Net Revenue, COGS, OpEx, Depreciation → EBITDA → EBIT.  
2. Taxes: apply combined rate only when positive EBIT; allow NOL carryforward.  
3. Financing block: SAFE cash hits month 0; revolver drawdown formula:  

   ```
   =MAX(-FreeCashBeforeFinancing,0,INPUT_Revolver_Limit-Sum(PreviousDraws))
   ```

4. Runway: rolling 6-month average burn; `Runway = EndingCash / AvgBurn`.  
5. Add conditional formatting gauge cells (<=3 red, <=6 yellow, else green).

### 3.8 Cap Table + SAFE Conversion

Replicate formulas included earlier.  Critical formula:

```
SAFE_Price = MIN(ValuationCap / PreMoneyShares, PreMoneyPrice*(1-Discount))
```

Dilution waterfall uses share counts, not percentages, to avoid circularity.

### 3.9 Dashboards

1. Insert slicers or simple cell links for key levers (Series A Valuation slider etc.).  
2. Charts:  
   - Breakeven: clustered line chart, add vertical line at breakeven bottles using secondary axis.  
   - Runway gauge: Doughnut with three colored series + needle via XY-scatter.  
   - EBITDA Waterfall: Excel 2016 “Waterfall” chart.  
   - IRR table: conditionally format >30 % green, <10 % red.

---

## 4. VBA Enhancements

### 4.1 Scenario Dial Synchronizer

```vb
'Module: mScenario
Public Sub SetScenario(idx As Integer)
    With Sheets("Scenario Switcher")
        .Range("B2").Value = idx
    End With
    'Force full calc for volatile CHOOSE
    Application.CalculateFull
End Sub
```

Assign this to three shape buttons (Base/Up/Down).

### 4.2 Traffic-Light Variance Macro (Ops Tracker)

```vb
Sub RefreshVarianceLights()
    Dim rng As Range, c As Range
    Set rng = Sheets("Ops Tracker").Range("Variance_Table").Columns("Delta")
    For Each c In rng
        Select Case c.Value
            Case Is <= -0.15: c.Interior.Color = vbRed
            Case Is <= -0.05: c.Interior.Color = RGB(255, 199, 0) 'yellow
            Case Else: c.Interior.Color = RGB(146, 208, 80) 'green
        End Select
    Next c
End Sub
```

Run after importing actuals.

### 4.3 Diligence Pack Auto-PDF

```vb
Sub ExportDiligencePDF()
    Const path$ = "C:\Brogue\Investor_Packs\"
    Dim fname$
    fname = path & "Brogue_Distillery_Diligence_" & Format(Date, "yyyymmdd") & ".pdf"
    Sheets(Array("Diligence Pack")).Select
    ActiveSheet.ExportAsFixedFormat Type:=xlTypePDF, Filename:=fname, Quality:=xlQualityStandard
    MsgBox "Diligence PDF saved to: " & fname
End Sub
```

Protect the macro with digital signature before sharing.

### 4.4 Monte Carlo (optional — hidden sheet)

Skeleton:

```vb
Sub RunMonteCarlo()
    Const trials = 1000
    Dim i&, rngOut As Range
    Application.ScreenUpdating = False
    Set rngOut = Sheets("Sensitivity").Range("MC_Outputs").Resize(trials, 2)
    For i = 1 To trials
        'Randomise inputs
        Range("inp_Y1_Volume").Value = Application.NormInv(Rnd, 50000, 5000)
        Range("inp_WHS_Price").Value = Application.TriangularInv(Rnd, 22, 24, 26)
        '...
        Application.Calculate
        rngOut.Cells(i, 1).Value = Range("out_EBITDA_Y1").Value
        rngOut.Cells(i, 2).Value = Range("out_Runway_Months").Value
    Next i
    Application.ScreenUpdating = True
End Sub
```

You will need helper UDFs `TriangularInv` and `PERTInv`.

---

## 5. Sheet Protection & Named Range Lockdown

1. Review ► Protect Workbook (structure).  
2. For every sheet except *Assumptions* & *Scenario Switcher* mark **Select Locked Cells** only.  
3. Save workbook as `.xlsm` with password to modify.  Keep a plain `.xlsx` “viewer” copy for paranoid investors.

---

## 6. Connecting QuickBooks / Xero (Post-Close)

1. Use **Power Query**:  
   - Data ► Get Data ► From Online Services ► QuickBooks Online.  
   - Map P&L and Balance Sheet exports to staging tables.  
2. Build a transformation query that outputs monthly Actuals table (`tbl_Actuals`).  
3. In `Ops Tracker`, use `SUMIFS(tbl_Actuals[Amount], …)` to populate actuals columns.  
4. Call `RefreshVarianceLights` after each data refresh (`Workbook_Open` event).

---

## 7. Version Control & Handoff

| Event                         | Action                                                                |
|-------------------------------|-----------------------------------------------------------------------|
| New external share            | Save as `Brogue_Model_vX.Y.xlsx`, bump minor version.                 |
| Structural formula change     | Bump **major** version, update `Changelog` tab.                       |
| Board deck generation         | Run `ExportDiligencePDF`, archive both model & PDF in `/Archive`.     |

Always freeze the “investor case” before the SAFE round closes—tag it `Investor_Case_v1.0`.

---

## 8. Final QA Checklist

- [ ] Row/column totals balance on **every** sheet.  
- [ ] Circularity? If yes, resolve or allow one-pass iterative calc (`Options ► Formulas`).  
- [ ] Scenario switch flips ► dashboards update in <1 s on a 2022 MacBook Air.  
- [ ] Model passes Excel **Inquire → Workbook Analysis** with 0 errors.  
- [ ] Protection cannot be removed by casual dragging (test!).  

---

### When in doubt…

> “No mystery-meat cells.”  
> If you can’t explain a cell to a drunk billionaire in 15 seconds, the formula’s too opaque—rewrite it.
