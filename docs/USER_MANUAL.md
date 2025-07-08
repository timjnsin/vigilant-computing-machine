# Distillery Financial Model
*User Manual, Getting-Started Guide & Technical Review*

---

## 1. Overview
This repository contains a Python-generated, multi-scenario, 5-year financial model for *The Brogue Distillery*. Running the `distillery_model.py` script produces a detailed Excel workbook named `distillery_financial_model_v1.xlsx`. This workbook is a standalone, fully functional financial model that can be shared with stakeholders and manipulated directly in Excel.

This manual is written for an **Excel-centric user** who wants to:
*   Generate the workbook without needing to write Python code.
*   Understand the workbook's structure, key drivers, and financial logic.
*   Confidently change assumptions and switch between scenarios for planning or investor presentations.
*   Validate the model's outputs and troubleshoot common issues.

A second half of this document provides a **technical and financial review** of the model and its underlying Python code, offering recommendations for future improvements and maintenance.

---

## 2. Quick-Start Guide
Follow these steps to generate the Excel model. This only needs to be done once, or whenever you need to regenerate the model from scratch.

```bash
# 1.  Clone the repository and install dependencies (requires Python 3.8+)
#     You only need to do this part once.
$ git clone https://github.com/timjnsin/vigilant-computing-machine.git
$ cd vigilant-computing-machine
$ pip install -r requirements.txt

# 2.  Generate the Excel model by running the Python script.
#     Make sure the previous version of the Excel file is closed.
$ python distillery_model.py

# 3.  Open the newly-created `distillery_financial_model_v1.xlsx` file in Excel.
```
That’s it. All further steps for using the model are performed inside the Excel workbook.

---

## 3. Workbook Map: Understanding the Sheets
The workbook is organized into several sheets, each with a specific purpose. All sheets have a blue **“Go to Dashboard”** button in cell A1 for easy navigation.

| Sheet | Purpose | Typical Actions for the User |
|:---|:---|:---|
| **Cover** | A professional title page with the model name, version, and a disclaimer. | None (informational). |
| **Control Panel** | The main hub for controlling the model. Contains global selectors for the active scenario and key rates. | **This is your primary control center.** Change the active scenario (Base, Upside, Downside) from the dropdown menu. Adjust the global tax and discount rates here. |
| **Assumptions** | A detailed table of all model inputs, organized by category, with values for each scenario. | **This is where you change inputs.** Edit the yellow-shaded input cells in the `Base Case`, `Upside Case`, and `Downside Case` columns to see how changes affect the model. The `Active` column updates automatically based on your selection in the Control Panel. |
| **Revenue Build** | Calculates bottle sales, pricing, and net revenue, including seasonality and channel mix (Wholesale vs. DTC). | Review the formulas to understand revenue logic. You rarely need to edit this sheet directly. |
| **COGS Build** | Models the cost of goods sold, including the 2-year product aging requirement and "Angel's Share" inventory loss. | Review to understand how production costs are calculated. The logic is complex and driven by assumptions. |
| **OpEx Build** | Projects operating expenses, including salaries, marketing, and general & administrative (G&A) costs. | Review to verify how operating costs are calculated based on inputs from the `Assumptions` sheet. |
| **Headcount** | A simple table showing the staffing plan by department over the years. | Adjust headcount numbers for each year to reflect your hiring plan. |
| **CapEx Schedule** | Manages capital expenditures (initial and expansion) and calculates the corresponding depreciation. | Review to confirm the timing and amount of large capital purchases. |
| **Debt Schedule** | Models the term loan, including the initial draw, interest expense, and principal repayments over time. | Review to understand debt service obligations. You can change loan terms in the `Assumptions` sheet. |
| **Working Capital** | Calculates balances for Accounts Receivable, Inventory, and Accounts Payable based on "days" assumptions. | Review to understand cash tied up in operations. The "days" assumptions are key drivers. |
| **Income Statement** | Standard financial statement showing profitability (Revenue, Expenses, Net Income). | Read-only. All values are calculated from other sheets. |
| **Cash Flow** | Standard financial statement tracking cash from Operations, Investing, and Financing. | Read-only. This sheet shows how cash moves through the business. |
| **Balance Sheet** | Standard financial statement showing Assets, Liabilities, and Equity. | Read-only. The model is built to ensure this sheet always balances. |
| **Returns Analysis** | Summarizes annual Free Cash Flow and calculates key investment metrics (IRR, MOIC). Includes sensitivity tables. | **This is a key sheet for investors.** Present the IRR, MOIC, and sensitivity tables to show potential returns and risks. |
| **Dashboard** | A high-level visual summary of Key Performance Indicators (KPIs), financial charts, and investment returns. | Use this for a quick overview or for screenshots in presentations. It updates live with any changes. |
| **Checks** | An automated validation sheet to ensure the model's integrity (i.e., the balance sheet balances). | **Crucial for validation.** Before sharing the model, ensure all cells in row 4 show a green `0`. A red, non-zero number indicates a broken formula or link. |
| **Data Import** | A landing zone to connect external data sources (e.g., from QuickBooks) via Power Query for actuals vs. forecast analysis. | (Advanced) Use this to integrate historical data into the model. |

---

## 4. Driving the Model – A Step-by-Step Guide

### 4.1 How to Select a Scenario
The model is built to toggle between three pre-defined scenarios.

1.  Navigate to the **Control Panel** sheet.
2.  Find the "Scenario Selection" section. Cell **D4** contains a dropdown menu.
3.  Click the dropdown and choose **Base Case**, **Upside Case**, or **Downside Case**.
4.  When you make a selection, the entire workbook instantly recalculates to reflect that scenario's assumptions. You can see the impact immediately on the **Dashboard** and **Returns Analysis** sheets.

### 4.2 How to Modify Assumptions
You can easily change any input to see its effect on the financial projections.

1.  Navigate to the **Assumptions** sheet.
2.  Find the assumption you want to change (e.g., `Avg Price per Bottle` under the `Revenue` category).
3.  **Edit the values in the yellow-shaded cells** within the `Base Case`, `Upside Case`, or `Downside Case` columns.
    *   **Input Cells:** Cells with a grey/yellow background and blue text are designed for your input.
    *   **Formula Cells:** Cells with a white background contain formulas and should not be edited directly, as this can break the model.
4.  After changing an input, go to the **Dashboard** or **Returns Analysis** sheet to see the impact on KPIs like IRR and Net Income.

> **Pro Tip:** For a quick "what-if" analysis, you can edit an assumption in the `Base Case` column and ensure the `Control Panel` is set to "Base Case." The other scenarios (Upside, Downside) remain unchanged, allowing you to quickly flip back to them for comparison.

### 4.3 How to Check the Model's Health
Before sharing the model or relying on its outputs, always perform this quick check:

1.  Navigate to the **Checks** sheet.
2.  Look at row 4, "Balance Sheet Check."
3.  This row should display **$0** in every column for all 60 periods. The cells are conditionally formatted to be **green** if the check passes.
4.  If you see any non-zero value (which will be formatted in **red**), it means the balance sheet is not balancing for that period, and there is an error in the model's logic that needs to be fixed.

---

## 5. Editing in Excel vs. Editing the Code
This is a critical concept for maintaining the model.

| Your Goal | Recommended Method | Why? |
|:---|:---|:---|
| I want to quickly test a different price or growth rate for a meeting. | **Edit the yellow input cells on the `Assumptions` sheet in Excel.** | This is the fastest and easiest way to perform "what-if" analysis. The changes are immediate. |
| I want to make a permanent change to an assumption that will be the new default. | **Edit the Python `self.assumptions` dictionary in `distillery_model.py`, then regenerate the file.** | Your changes in Excel will be overwritten the next time you run the Python script. Editing the code makes the change permanent for all future versions of the model. |
| I want to add a completely new assumption (e.g., a new marketing expense). | **This requires editing the Python code.** You must add the new assumption to the dictionary and then update the relevant `build_*` method to use it. | The model's structure is defined in the Python script. New line items must be added there. |
| I want to add a new scenario (e.g., "Worst Case"). | **This requires editing the Python code.** You would add a new "Worst Case" dictionary to `self.assumptions` and update the data validation list in `build_control_panel`. | Adding a new scenario requires changing the core structure of the `Assumptions` sheet, which is controlled by the script. |

**In short: Use Excel for analysis. Use the Python script to manage the model's core structure and permanent assumptions.**

---

## 6. Troubleshooting Common Issues

| Symptom | Likely Cause | How to Fix |
|:---|:---|:---|
| **#NAME?** or **#REF!** errors appear in many cells. | A named range is missing or broken. This usually happens if the Python script was interrupted or failed before it could finish creating all named ranges. | Delete the corrupted `.xlsx` file and regenerate it by running `python distillery_model.py` again. |
| The **Balance Sheet Check** on the `Checks` sheet is not zero. | A formula was likely edited or deleted by mistake on one of the financial statement sheets, breaking the accounting logic. | The safest fix is to regenerate a fresh copy of the model. Avoid editing any white-colored formula cells. |
| When running the script, I get a "Permission denied" or "Workbook is currently open" error. | You have the `distillery_financial_model_v1.xlsx` file open in Excel, which prevents the script from deleting and overwriting it. | Close the Excel file completely, then re-run the `python distillery_model.py` command. |
| Dates are showing up as large numbers (e.g., 45291). | The cell's number formatting in Excel was accidentally changed from "Date" to "General" or "Number." | Right-click the cell, select "Format Cells," and change the category back to "Date." Regenerating the model will also fix this. |

---

## 7. Technical Review & Recommendations
This section provides a review of the model's code, financial logic, and user experience, with suggestions for future improvements.

### 7.1 Code Architecture
*   **Strengths:**
    *   The single-class `DistilleryFinancialModel` effectively encapsulates all logic for creating the workbook.
    *   Separating the logic for each sheet into its own `build_*` method is a clean design that makes the code easy to understand.
    *   Storing named ranges in the `self.named_ranges` dictionary before defining them is a robust way to manage cross-sheet references.
*   **Areas for Improvement:**
    *   **Monolithic File:** At ~1,400 lines, `distillery_model.py` is becoming large. Consider splitting the logic into a more modular structure (e.g., a `sheets` directory with a separate Python file for each `build_*` method, a `formats.py` module, etc.).
    *   **Lack of Automated Tests:** The model's integrity relies on manual checks. Adding a simple test script that uses a library like `openpyxl` to open the generated workbook and assert that `Checks!B4:BH4` are all zero would prevent regressions.

### 7.2 Maintainability
*   **Hardcoded Values:** The code repeats constants like the 60-period timeline length in multiple loops. This should be derived from `len(self.timeline)` to make the timeline length easily configurable in one place.
*   **Magic Strings:** Assumption keys (e.g., `"Avg Price per Bottle"`) are used as strings to create named ranges. A typo in one of these strings would break the model silently. Using a central dictionary or an Enum class for these keys would be safer.
*   **Error Handling:** The script will crash if it encounters an unexpected error (like a permissions issue), potentially leaving a corrupted file. Wrapping the main `create_workbook` logic in a `try...finally` block to ensure `self.workbook.close()` is always called would be more robust.

### 7.3 Financial Modeling Best Practices
*   **Strengths:**
    *   The inclusion of a dedicated `Checks` sheet for the balance sheet tie-out is a core best practice.
    *   The scenario manager (`INDEX/MATCH` formula driven by the `Control Panel`) is a standard and effective way to handle scenario analysis.
*   **Areas for Improvement:**
    *   **Working Capital Calculation:** The formulas for AR and AP currently divide by a fixed `30` days. This is a common simplification, but it can be inaccurate. A more precise method would be to use the actual days in each period or a `365/12` average.
    *   **Depreciation:** The model uses straight-line depreciation over a fixed 10-year life. This is acceptable, but for a more flexible model, the useful life of assets should be a configurable assumption.
    *   **Interest Calculation:** The model calculates interest on the beginning-of-period debt balance. For higher precision, it could be calculated on the average balance of the period.
    *   **Circularity:** The model currently avoids circular references. If you were to add logic where interest is calculated on the cash balance (which itself is affected by the interest), you would need to implement a circularity breaker (usually an iterative calculation toggle in the `Control Panel`).

### 7.4 User Experience (Excel)
*   **Strengths:**
    *   The navigation buttons in cell A1 are a great touch for usability.
    *   The use of color (blue text for inputs) and frozen panes makes the sheets easy to read and navigate.
*   **Areas for Improvement:**
    *   **Dashboard Control:** Add a scenario selection dropdown directly on the **Dashboard** that is linked to the `SelectedScenario` cell on the `Control Panel`. This would allow users to switch scenarios without leaving the main summary page.
    *   **Consistency:** The color scheme for input cells is mostly consistent (grey fill, blue font), but this could be strictly enforced across all user-editable cells for clarity.

### 7.5 Suggested Next Steps (Roadmap)
1.  **P0: Modularize the Codebase:** Break the single `distillery_model.py` file into smaller, more manageable modules (e.g., one file per sheet).
2.  **P1: Add Unit Tests:** Implement a basic test suite to automatically validate the `Checks` sheet after every build.
3.  **P1: Externalize Assumptions:** Move the `self.assumptions` dictionary from the Python code into a separate `config.yaml` or `config.json` file. The Python script would then read this file to populate the model. This is a major step towards allowing non-developers to manage the core assumptions.
4.  **P2: Automate PDF Generation:** Add a feature to the script (using a library like `win32com` on Windows or `excel2img`) to automatically export the **Dashboard** as a PDF, streamlining the creation of presentation materials.
5.  **P2: Enhance the `Data Import` Sheet:** Provide a more detailed guide or template for setting up the Power Query connection to a data source like QuickBooks, making the "Actuals vs. Forecast" feature more accessible.

---

## 8. FAQ
**Q: Do I need to have Excel installed to run the Python script?**  
**A:** No. The script uses the `XlsxWriter` library, which generates the `.xlsx` file from scratch without needing Excel. You only need Excel to open and view the final output file.

**Q: Can I actually connect my QuickBooks data to this model?**  
**A:** Yes. The **Data Import** sheet is designed for this. In Excel, you would use the "Get Data" (Power Query) feature to connect to a CSV export from QuickBooks. You would then set the query's output location to be the table on the `Data Import` sheet. Once your actuals are loaded, you can change the `DataSourceMode` on the **Control Panel** to `Actuals + Forecast` to have the model use your real data for past periods.

**Q: The generated Excel file is very large. How can I make it smaller?**  
**A:** The file size is primarily due to the large number of formulas and cells. When sending the file externally, you can significantly reduce its size by copy-pasting the entire model as values into a new workbook. However, this will remove all formulas and interactivity. For a smaller but still functional model, ensure there are no unnecessary blank rows or columns on any sheet.

---

*This document was generated on July 8, 2025.*
