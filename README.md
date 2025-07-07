# Distillery Financial Model

## 1. Project Overview and Description

This project provides a comprehensive and dynamic financial model for a craft distillery business, "The Brogue Distillery." It is built using Python with the Pandas and XlsxWriter libraries to programmatically generate a detailed Excel workbook. The model projects 5 years of financial performance, incorporating monthly, quarterly, and annual granularity.

The primary goal of this tool is to offer a robust platform for strategic planning, investment analysis, and operational decision-making. It allows users to seamlessly switch between different operating scenarios (Base, Upside, and Downside cases) to understand potential financial outcomes and risks.

## 2. Features and Capabilities

- **Dynamic Scenario Analysis:** Easily switch between "Base Case," "Upside Case," and "Downside Case" from a central control panel to see the immediate impact on all financial projections.
- **5-Year Forecast Horizon:** The model provides a 60-period forecast, starting with 36 months of monthly detail, followed by 8 quarters, and 2 final years.
- **Integrated Financial Statements:** Automatically generates a fully-linked Income Statement, Cash Flow Statement, and Balance Sheet.
- **Detailed Operational Drivers:** Includes granular builds for Revenue, Cost of Goods Sold (COGS), Operating Expenses (OpEx), Capital Expenditures (CapEx), and Working Capital.
- **Distillery-Specific Logic:** Incorporates industry-specific mechanics like a 2-year product aging requirement, Angel's Share inventory loss, and tiered pricing (Wholesale vs. DTC).
- **Interactive Dashboard:** A high-level dashboard summarizes key performance indicators (KPIs), financial charts, and investment returns.
- **Returns Analysis:** Calculates key investment metrics, including Internal Rate of Return (IRR) and Multiple on Invested Capital (MOIC).
- **Built-in Checks:** An automated checks sheet ensures the model's integrity, including a check to confirm the balance sheet always balances.

## 3. Installation and Usage Instructions

To generate the financial model workbook, follow these steps:

**Prerequisites:**
- Python 3.8+
- pip (Python package installer)

**Installation:**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/timjnsin/vigilant-computing-machine.git
    cd vigilant-computing-machine
    ```

2.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

**Usage:**

1.  **Run the Python script from the terminal:**
    ```bash
    python distillery_model.py
    ```

2.  **Locate the output file:**
    A new Excel file named `distillery_financial_model_v1.xlsx` will be created in the project's root directory.

## 4. Model Structure and Components

The generated Excel workbook is organized into the following sheets:

- **Cover:** A title page with model information and a disclaimer.
- **Control Panel:** The main hub for selecting the active scenario and setting global assumptions like tax and discount rates.
- **Assumptions:** A detailed table of all model inputs, organized by category, with values for each scenario.
- **Revenue Build:** Calculates bottle sales, pricing, and net revenue, including seasonality.
- **COGS Build:** Models the cost of goods sold, including the 2-year aging process and Angel's Share.
- **OpEx Build:** Projects operating expenses, including salaries, marketing, and G&A costs.
- **Headcount:** A summary of the staffing plan by department over the years.
- **CapEx Schedule:** Manages capital expenditures and calculates PP&E and depreciation.
- **Debt Schedule:** Models the term loan, including interest and principal repayments.
- **Working Capital:** Calculates Accounts Receivable, Inventory, and Accounts Payable balances.
- **Income Statement:** Standard three-statement model component showing profitability.
- **Cash Flow Statement:** Tracks the movement of cash from operations, investing, and financing.
- **Balance Sheet:** Presents the company's assets, liabilities, and equity. Must always balance.
- **Cap Table:** A simple capitalization table showing initial equity structure.
- **Returns Analysis:** Calculates IRR and MOIC based on projected free cash flows.
- **Dashboard:** A visual summary of the most important metrics and charts.
- **Checks:** A validation sheet to ensure the model is functioning correctly.

## 5. Scenario Analysis

The model's core strength is its ability to perform scenario analysis. The **Control Panel** sheet contains a dropdown menu where you can select one of three scenarios:

- **Base Case:** The most likely or expected outcome based on current plans and market analysis.
- **Upside Case:** An optimistic scenario where key drivers (e.g., sales volume, pricing) perform better than expected.
- **Downside Case:** A pessimistic scenario that models potential challenges (e.g., lower sales, higher costs).

Changing the selection in the `SelectedScenario` cell (D4) on the Control Panel instantly updates all assumptions in the **Assumptions** sheet, which then flow through the entire model.

## 6. Key Outputs and Metrics

The model produces a wide range of outputs, with the most critical ones summarized on the **Dashboard**:

- **IRR & MOIC:** Key metrics for evaluating the overall return on investment.
- **Revenue CAGR & EBITDA Margin:** High-level indicators of growth and profitability.
- **Peak Funding Need:** The lowest point in the cash balance, indicating the maximum capital required.
- **Monthly Cash Balance Chart:** A visual representation of the company's liquidity over time.
- **Revenue Growth Waterfall:** A chart showing the progression of revenue over the forecast period.

## 7. Technical Details

- **Language:** Python 3
- **Core Libraries:**
    - **`pandas`**: Used for data structures and handling time-series data (though abstracted by the script).
    - **`xlsxwriter`**: The engine for creating the Excel file, writing data, formulas, and applying formatting.
    - **`openpyxl`**: Used alongside `xlsxwriter` for certain workbook manipulations.
- **Methodology:** The `distillery_model.py` script contains a single class, `DistilleryFinancialModel`, which encapsulates all the logic for building each sheet, defining named ranges, and writing formulas. This programmatic approach ensures consistency, reduces manual errors, and allows for easy updates.

## 8. File Structure

```
.
├── distillery_model.py
├── requirements.txt
├── README.md
└── The-Brogue-Distillery-American-Single-Malts-Moment-in-Context (6).pdf
```

- `distillery_model.py`: The main Python script that generates the Excel model.
- `requirements.txt`: A list of Python package dependencies.
- `README.md`: This documentation file.

## 9. Requirements

The project's dependencies are listed in `requirements.txt`:

```
pandas>=1.3.0
openpyxl>=3.0.9
xlsxwriter>=3.0.3
numpy>=1.20.0
python-dateutil>=2.8.2
```

## 10. Usage Example

To generate the model, navigate to the project directory in your terminal and run:

```bash
python distillery_model.py
```

This will produce the file `distillery_financial_model_v1.xlsx` in the same directory.

## 11. Notes About Model Assumptions

- **Illustrative Purposes:** This financial model is a forward-looking tool based on a specific set of assumptions. The outputs are for illustrative and strategic planning purposes only and should not be considered a guarantee of future performance.
- **Key Drivers:** The model is highly sensitive to the assumptions laid out in the **Assumptions** sheet. Users should carefully review and adjust these inputs to reflect their own analysis and expectations.
- **Simplifications:** For clarity and usability, certain complex real-world factors may be simplified. For example, depreciation is calculated on a straight-line basis, and tax calculations do not include provisions for NOLs (Net Operating Losses).

## 12. Future Enhancements

- **Advanced Sensitivity Analysis:** Implement data tables or a dedicated sensitivity analysis sheet to test the impact of simultaneous changes in key variables (e.g., price vs. volume).
- **Monte Carlo Simulation:** Add a feature to run Monte Carlo simulations to generate a probabilistic range of outcomes for key metrics like IRR and NPV.
- **Web-Based Interface:** Develop a web application (e.g., using Flask or Django) to allow users to interact with the model through a browser, removing the need for local Python execution.
- **Detailed Covenant Tracking:** Expand the debt schedule to include and track compliance with typical loan covenants (e.g., Debt Service Coverage Ratio).

