import os
import datetime
import pandas as pd
import numpy as np
import xlsxwriter
from dateutil.relativedelta import relativedelta

class DistilleryFinancialModel:
    def __init__(self, file_name="distillery_financial_model_v1.xlsx"):
        """Initialize the Distillery Financial Model generator."""
        self.file_name = file_name
        self.workbook = None
        self.formats = {}
        self.timeline = []
        self.timeline_labels = []
        self.named_ranges = {}
        
        # Model parameters
        self.model_start_date = datetime.date(2024, 1, 1)
        self.actuals_cutoff = datetime.date(2023, 12, 31)
        self.tax_rate = 0.21
        self.discount_rate = 0.12
        
        # Assumptions for different scenarios
        self.assumptions = {
            "Base Case": {
                "Revenue": {
                    "Year 1 Bottles Sold": 50000,
                    "Annual Growth Rate": 0.25,
                    "Avg Price per Bottle": 45,
                    "Wholesale % of Sales": 0.70,
                    "Distributor Margin": 0.30,
                    "Excise Tax per Bottle": 2.70
                },
                "COGS": {
                    "Grain per Bottle": 3.50,
                    "Other Materials": 4.80,
                    "Direct Labor": 2.40,
                    "Bottle & Packaging": 7.50,
                    "Angels Share Annual": 0.04
                },
                "OpEx": {
                    "Base Salaries": 780000,
                    "Marketing % Revenue": 0.12,
                    "Rent per Month": 25000,
                    "Insurance Annual": 120000
                },
                "CapEx": {
                    "Initial Equipment": 900000,
                    "Expansion Y3": 500000,
                    "Maintenance CapEx %": 0.02
                },
                "WC": {
                    "Revenue Days Sales": 45,
                    "Inventory Days": 180,
                    "Payable Days": 30
                },
                "Financing": {
                    "Initial Equity": 2000000,
                    "Term Loan": 1000000,
                    "Interest Rate": 0.08,
                    "Loan Term Years": 5
                }
            },
            "Upside Case": {
                "Revenue": {
                    "Year 1 Bottles Sold": 65000,
                    "Annual Growth Rate": 0.35,
                    "Avg Price per Bottle": 50,
                    "Wholesale % of Sales": 0.65,
                    "Distributor Margin": 0.28,
                    "Excise Tax per Bottle": 2.70
                },
                "COGS": {
                    "Grain per Bottle": 3.25,
                    "Other Materials": 4.50,
                    "Direct Labor": 2.20,
                    "Bottle & Packaging": 7.00,
                    "Angels Share Annual": 0.035
                },
                "OpEx": {
                    "Base Salaries": 750000,
                    "Marketing % Revenue": 0.15,
                    "Rent per Month": 23000,
                    "Insurance Annual": 110000
                },
                "CapEx": {
                    "Initial Equipment": 850000,
                    "Expansion Y3": 600000,
                    "Maintenance CapEx %": 0.02
                },
                "WC": {
                    "Revenue Days Sales": 40,
                    "Inventory Days": 160,
                    "Payable Days": 35
                },
                "Financing": {
                    "Initial Equity": 2000000,
                    "Term Loan": 800000,
                    "Interest Rate": 0.07,
                    "Loan Term Years": 5
                }
            },
            "Downside Case": {
                "Revenue": {
                    "Year 1 Bottles Sold": 35000,
                    "Annual Growth Rate": 0.15,
                    "Avg Price per Bottle": 40,
                    "Wholesale % of Sales": 0.75,
                    "Distributor Margin": 0.32,
                    "Excise Tax per Bottle": 2.70
                },
                "COGS": {
                    "Grain per Bottle": 3.75,
                    "Other Materials": 5.00,
                    "Direct Labor": 2.60,
                    "Bottle & Packaging": 8.00,
                    "Angels Share Annual": 0.045
                },
                "OpEx": {
                    "Base Salaries": 820000,
                    "Marketing % Revenue": 0.10,
                    "Rent per Month": 28000,
                    "Insurance Annual": 130000
                },
                "CapEx": {
                    "Initial Equipment": 950000,
                    "Expansion Y3": 400000,
                    "Maintenance CapEx %": 0.025
                },
                "WC": {
                    "Revenue Days Sales": 50,
                    "Inventory Days": 200,
                    "Payable Days": 25
                },
                "Financing": {
                    "Initial Equity": 2000000,
                    "Term Loan": 1200000,
                    "Interest Rate": 0.09,
                    "Loan Term Years": 5
                }
            }
        }
        
        # Sheet names
        self.sheets = [
            "Cover", "Control Panel", "Unit Economics", "Assumptions", "Revenue Build", "COGS Build", 
            "OpEx Build", "Headcount", "CapEx Schedule", "Debt Schedule", "Working Capital",
            "Income Statement", "Cash Flow Statement", "Balance Sheet", "Cap Table", 
            "Data Import", "Returns Analysis", "Dashboard", "Checks"
        ]
        
        # Sheets that need timeline headers
        self.timeline_sheets = [
            "Assumptions", "Revenue Build", "COGS Build", "OpEx Build", "CapEx Schedule",
            "Debt Schedule", "Working Capital", "Income Statement", "Cash Flow Statement", "Balance Sheet"
        ]

    def generate_timeline(self):
        """Generate timeline dates for the model."""
        timeline = []
        timeline_labels = []
        
        # 36 monthly periods
        current_date = self.model_start_date
        for i in range(36):
            timeline.append(current_date)
            timeline_labels.append(f"Month {i+1}")
            current_date = current_date + relativedelta(months=1)
        
        # 8 quarterly periods
        for i in range(8):
            timeline.append(current_date)
            timeline_labels.append(f"Q{(i%4)+1} {current_date.year}")
            current_date = current_date + relativedelta(months=3)
        
        # 2 annual periods
        for i in range(2):
            timeline.append(current_date)
            timeline_labels.append(f"{current_date.year}")
            current_date = current_date + relativedelta(years=1)
        
        self.timeline = timeline
        self.timeline_labels = timeline_labels
        return timeline, timeline_labels

    def setup_formats(self):
        """Create formats for the workbook."""
        self.formats = {
            'title': self.workbook.add_format({
                'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter'
            }),
            'header': self.workbook.add_format({
                'bold': True, 'font_size': 12, 'align': 'center', 'valign': 'vcenter',
                'border': 1, 'bg_color': '#D9E1F2'
            }),
            'subheader': self.workbook.add_format({
                'bold': True, 'font_size': 11, 'align': 'left', 'valign': 'vcenter',
                'border': 1, 'bg_color': '#E2EFDA'
            }),
            'date': self.workbook.add_format({
                'num_format': 'mmm-yy', 'align': 'center', 'border': 1
            }),
            'percent': self.workbook.add_format({
                'num_format': '0.0%', 'align': 'right', 'border': 1
            }),
            'currency': self.workbook.add_format({
                'num_format': '$#,##0', 'align': 'right', 'border': 1
            }),
            'number': self.workbook.add_format({
                'num_format': '#,##0', 'align': 'right', 'border': 1
            }),
            'input': self.workbook.add_format({
                'font_color': 'blue', 'align': 'right', 'border': 1, 'bg_color': '#F2F2F2'
            }),
            'input_percent': self.workbook.add_format({
                'num_format': '0.0%', 'font_color': 'blue', 'align': 'right', 'border': 1, 'bg_color': '#F2F2F2'
            }),
            'input_currency': self.workbook.add_format({
                'num_format': '$#,##0', 'font_color': 'blue', 'align': 'right', 'border': 1, 'bg_color': '#F2F2F2'
            }),
            'formula': self.workbook.add_format({
                'font_color': 'black', 'align': 'right', 'border': 1
            }),
            'formula_percent': self.workbook.add_format({
                'num_format': '0.0%', 'font_color': 'black', 'align': 'right', 'border': 1
            }),
            'formula_currency': self.workbook.add_format({
                'num_format': '$#,##0', 'font_color': 'black', 'align': 'right', 'border': 1
            }),
            'total': self.workbook.add_format({
                'bold': True, 'num_format': '$#,##0', 'align': 'right', 'border': 1, 
                'top': 2, 'bottom': 2
            }),
            'check_ok': self.workbook.add_format({
                'font_color': 'green', 'bold': True, 'align': 'center'
            }),
            'check_error': self.workbook.add_format({
                'font_color': 'red', 'bold': True, 'align': 'center'
            }),
            'label': self.workbook.add_format({
                'align': 'left', 'border': 1
            }),
            'button': self.workbook.add_format({
                'bold': True, 'font_size': 11, 'align': 'center', 'valign': 'vcenter',
                'border': 2, 'bg_color': '#4472C4', 'font_color': 'white'
            })
        }

    def create_workbook(self):
        """Create the Excel workbook and add all sheets."""
        # Create workbook
        self.workbook = xlsxwriter.Workbook(self.file_name)
        self.setup_formats()
        
        # Generate timeline
        self.generate_timeline()
        
        # Create all sheets
        for sheet_name in self.sheets:
            self.workbook.add_worksheet(sheet_name)
        
        # Build each sheet
        self.build_cover_sheet()
        self.build_control_panel()
        # Build the investor-ready Unit Economics sheet (prompt #2)
        self.build_unit_economics_sheet()
        self.build_assumptions_sheet()
        self.build_data_import_sheet()
        self.build_revenue_sheet()
        self.build_cogs_sheet()
        self.build_opex_sheet()
        self.build_headcount_sheet()
        self.build_capex_sheet()
        self.build_debt_sheet()
        self.build_working_capital_sheet()
        self.build_income_statement()
        self.build_cash_flow_statement()
        self.build_balance_sheet()
        self.build_cap_table()
        self.build_returns_analysis()
        # --- Sensitivity analysis (two-way data tables, tornado, breakeven, etc.) ---
        # Implemented in build_sensitivity_tables()
        self.build_sensitivity_tables()
        self.build_dashboard()
        self.build_checks_sheet()
        
        # Add navigation buttons to all sheets
        self.add_navigation_buttons()

        # Define all named ranges at once
        for name, cell_range in self.named_ranges.items():
            self.workbook.define_name(name, f'={cell_range}')
        
        # Save and close the workbook
        self.workbook.close()
        
        print(f"Financial model created successfully: {self.file_name}")
        return self.file_name

    def add_timeline_headers(self, sheet_name):
        """Add timeline headers to a sheet."""
        worksheet = self.workbook.get_worksheet_by_name(sheet_name)
        
        # Add dates in row 1
        for i, date in enumerate(self.timeline):
            worksheet.write_datetime(0, i + 1, date, self.formats['date'])
        
        # Add period labels in row 2
        for i, label in enumerate(self.timeline_labels):
            worksheet.write(1, i + 1, label, self.formats['header'])
        
        # Freeze panes
        worksheet.freeze_panes(3, 1)

    def build_cover_sheet(self):
        """Build the Cover sheet."""
        worksheet = self.workbook.get_worksheet_by_name("Cover")
        
        # Set column widths
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:D', 25)
        worksheet.set_column('E:E', 15)
        
        # Add title and company info
        worksheet.merge_range('B2:D2', 'DISTILLERY FINANCIAL MODEL', self.formats['title'])
        worksheet.merge_range('B4:D4', 'The Brogue Distillery', self.formats['header'])
        worksheet.merge_range('B5:D5', 'Confidential - For Internal Use Only', self.formats['subheader'])
        
        # Add version info
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        worksheet.write('B7', 'Version:', self.formats['label'])
        worksheet.write('C7', 'v1.0', self.formats['label'])
        worksheet.write('B8', 'Last Updated:', self.formats['label'])
        worksheet.write('C8', current_date, self.formats['label'])
        
        # Add model summary
        worksheet.merge_range('B10:D10', 'MODEL SUMMARY', self.formats['header'])
        worksheet.write('B11', 'Time Horizon:', self.formats['label'])
        worksheet.write('C11', '5 Years (Monthly, Quarterly, Annual)', self.formats['label'])
        worksheet.write('B12', 'Scenarios:', self.formats['label'])
        worksheet.write('C12', 'Base Case, Upside Case, Downside Case', self.formats['label'])
        worksheet.write('B13', 'Model Start Date:', self.formats['label'])
        worksheet.write('C13', self.model_start_date.strftime("%Y-%m-%d"), self.formats['label'])
        
        # Add disclaimer
        disclaimer_text = 'DISCLAIMER: This financial model contains forward-looking projections that are based on assumptions. Actual results may differ materially from those projected. This model is for illustrative purposes only and should not be relied upon as a guarantee of future performance.'
        worksheet.merge_range('B15:D20', disclaimer_text, self.workbook.add_format({'text_wrap': True, 'align': 'left', 'valign': 'top'}))

    def build_control_panel(self):
        """Build the Control Panel sheet."""
        worksheet = self.workbook.get_worksheet_by_name("Control Panel")
        
        # Set column widths
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:C', 25)
        worksheet.set_column('D:E', 18)
        
        # Add title
        worksheet.merge_range('B2:D2', 'Distillery Financial Model', self.formats['title'])
        
        # Scenario selection
        worksheet.write('B4', 'Scenario Selection:', self.formats['label'])
        worksheet.write('D4', 'Base Case', self.formats['input'])
        worksheet.data_validation('D4', {'validate': 'list', 'source': ['Base Case', 'Upside Case', 'Downside Case']})
        self.named_ranges["SelectedScenario"] = "'Control Panel'!$D$4"
        
        # Model dates
        worksheet.write('B6', 'Model Start Date:', self.formats['label'])
        worksheet.write_datetime('D6', self.model_start_date, self.formats['input'])
        self.named_ranges["ModelStartDate"] = "'Control Panel'!$D$6"
        
        worksheet.write('B7', 'Actuals Cutoff Date:', self.formats['label'])
        worksheet.write_datetime('D7', self.actuals_cutoff, self.formats['input'])
        self.named_ranges["ActualsCutoff"] = "'Control Panel'!$D$7"
        
        worksheet.write('B8', 'Data Source Mode:', self.formats['label'])
        worksheet.write('D8', 'Forecast Only', self.formats['input'])
        worksheet.data_validation('D8', {'validate': 'list', 'source': ['Forecast Only', 'Actuals + Forecast', 'Actuals Only']})
        self.named_ranges["DataSourceMode"] = "'Control Panel'!$D$8"
        
        # Add comment about IFERROR pattern usage
        comment = (
            "The 'Actuals Cutoff Date' and 'Data Source Mode' control how the model integrates actual data from the 'Data Import' sheet. "
            "Financial statement formulas will use a pattern like: "
            "IF(current_date > ActualsCutoff, forecast_formula, IFERROR(VLOOKUP(current_date, Actuals_Table, ...), forecast_formula)). "
            "This allows the model to automatically use actual data when available for a given period and fall back to the forecast if not."
        )
        worksheet.write_comment('B8', comment, {'author': 'Model Bot', 'visible': False, 'width': 400, 'height': 120})

        # Key global assumptions
        worksheet.merge_range('B10:D10', 'Key Global Assumptions', self.formats['subheader'])
        
        worksheet.write('B11', 'Tax Rate:', self.formats['label'])
        worksheet.write('D11', self.tax_rate, self.formats['input_percent'])
        self.named_ranges["TaxRate"] = "'Control Panel'!$D$11"
        
        worksheet.write('B12', 'Discount Rate:', self.formats['label'])
        worksheet.write('D12', self.discount_rate, self.formats['input_percent'])
        self.named_ranges["DiscountRate"] = "'Control Panel'!$D$12"
        
        # Protect the sheet except for input cells
        worksheet.protect(options={'select_unlocked_cells': True, 'select_locked_cells': True})

    def build_assumptions_sheet(self):
        """Build the Assumptions sheet."""
        worksheet = self.workbook.get_worksheet_by_name("Assumptions")
        
        # Set column widths
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:E', 15)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 10)
        
        # Add timeline headers
        if "Assumptions" in self.timeline_sheets:
            self.add_timeline_headers("Assumptions")
        
        # Create assumptions table header
        row = 4
        headers = ['Category', 'Parameter', 'Base Case', 'Upside Case', 'Downside Case', 'Active', 'Units']
        worksheet.write_row(f'A{row+1}', headers, self.formats['header'])
        
        # Define the scenarios for MATCH function
        worksheet.write('F4', 'Base Case')
        worksheet.write('G4', 'Upside Case')
        worksheet.write('H4', 'Downside Case')
        worksheet.set_row(3, None, None, {'hidden': True})

        # Add assumptions by category
        row = 5
        for cat_name, cat_data in self.assumptions['Base Case'].items():
            row += 1
            worksheet.merge_range(f'A{row+1}:G{row+1}', f'{cat_name} Assumptions', self.formats['subheader'])
            row += 1
            for param_name, base_val in cat_data.items():
                upside_val = self.assumptions['Upside Case'][cat_name][param_name]
                downside_val = self.assumptions['Downside Case'][cat_name][param_name]
                
                # Determine format and units
                fmt = self.formats['number']
                unit = ''
                if '%' in param_name:
                    fmt = self.formats['percent']
                    unit = '%'
                elif '$' in param_name or 'Price' in param_name or 'Cost' in param_name or 'Salaries' in param_name or 'Rent' in param_name or 'Insurance' in param_name or 'Equipment' in param_name or 'Equity' in param_name or 'Loan' in param_name:
                    fmt = self.formats['currency']
                    unit = '$'
                elif 'Days' in param_name:
                    unit = 'days'
                elif 'Years' in param_name:
                    unit = 'years'
                elif 'Bottles' in param_name:
                    unit = 'bottles'
                
                formula_fmt = self.formats['formula']
                if unit == '%':
                    formula_fmt = self.formats['formula_percent']
                elif unit == '$':
                    formula_fmt = self.formats['formula_currency']

                worksheet.write(f'A{row+1}', cat_name, self.formats['label'])
                worksheet.write(f'B{row+1}', param_name, self.formats['label'])
                worksheet.write(f'C{row+1}', base_val, fmt)
                worksheet.write(f'D{row+1}', upside_val, fmt)
                worksheet.write(f'E{row+1}', downside_val, fmt)
                worksheet.write_formula(f'F{row+1}', f'=INDEX(C{row+1}:E{row+1},1,MATCH(SelectedScenario,Assumptions!$F$4:$H$4,0))', formula_fmt)
                worksheet.write(f'G{row+1}', unit, self.formats['label'])
                
                # Create named range for the active assumption
                named_range_name = param_name.replace(' ', '_').replace('%', 'Pct').replace('$', '').replace('&', 'and')
                self.named_ranges[named_range_name] = f'Assumptions!$F${row+1}'
                row += 1
        
        # Name the timeline range
        self.named_ranges["Timeline"] = "Assumptions!$B$1:$BH$1"

    def build_revenue_sheet(self):
        """Build the Revenue Build sheet."""
        worksheet = self.workbook.get_worksheet_by_name("Revenue Build")
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:BH', 12)
        
        # Add timeline headers
        if "Revenue Build" in self.timeline_sheets:
            self.add_timeline_headers("Revenue Build")
        
        # Add section headers and labels
        worksheet.write('A3', 'Unit Sales', self.formats['subheader'])
        worksheet.write('A4', 'Wholesale Units', self.formats['label'])
        worksheet.write('A5', 'DTC Units', self.formats['label'])
        worksheet.write('A6', 'Total Units', self.formats['total'])
        
        worksheet.write('A8', 'Pricing', self.formats['subheader'])
        worksheet.write('A9', 'Wholesale Price', self.formats['label'])
        worksheet.write('A10', 'DTC Price', self.formats['label'])
        
        worksheet.write('A12', 'Gross Revenue', self.formats['subheader'])
        worksheet.write('A13', 'Wholesale Revenue', self.formats['label'])
        worksheet.write('A14', 'DTC Revenue', self.formats['label'])
        worksheet.write('A15', 'Total Gross Revenue', self.formats['total'])
        
        worksheet.write('A17', 'Deductions', self.formats['subheader'])
        worksheet.write('A18', 'Distributor Margin Cost', self.formats['label'])
        worksheet.write('A19', 'Excise Taxes', self.formats['label'])
        worksheet.write('A20', 'Net Revenue', self.formats['total'])
        
        # Add formulas across all periods
        for col in range(1, 61):  # B to BH
            col_letter = xlsxwriter.utility.xl_col_to_name(col)
            
            # Seasonality factor
            month_num = col % 12
            seasonality_formula = f"IF(OR(MOD(COLUMN()-2,12)=10,MOD(COLUMN()-2,12)=11),1.4,IF(OR(MOD(COLUMN()-2,12)=0,MOD(COLUMN()-2,12)=1),0.8,1))"
            
            # Unit Sales
            worksheet.write_formula(f'{col_letter}6', f'=Year_1_Bottles_Sold/12 * (1+Annual_Growth_Rate)^((COLUMN()-2)/12) * {seasonality_formula}', self.formats['formula'])
            worksheet.write_formula(f'{col_letter}4', f'={col_letter}6*Wholesale_Pct_of_Sales', self.formats['formula'])
            worksheet.write_formula(f'{col_letter}5', f'={col_letter}6-{col_letter}4', self.formats['formula'])
            
            # Pricing
            worksheet.write_formula(f'{col_letter}9', '=Avg_Price_per_Bottle*(1-Distributor_Margin)', self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}10', '=Avg_Price_per_Bottle*1.3', self.formats['formula_currency'])
            
            # Gross Revenue
            worksheet.write_formula(f'{col_letter}13', f'={col_letter}4*{col_letter}9', self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}14', f'={col_letter}5*{col_letter}10', self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}15', f'={col_letter}13+{col_letter}14', self.formats['formula_currency'])
            
            # Deductions
            worksheet.write_formula(f'{col_letter}18', f'={col_letter}13/(1-Distributor_Margin)*Distributor_Margin', self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}19', f'={col_letter}6*Excise_Tax_per_Bottle', self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}20', f'={col_letter}15-{col_letter}18-{col_letter}19', self.formats['formula_currency'])
        
        # Name key ranges for use in other sheets
        self.named_ranges["Total_Units"] = "'Revenue Build'!$B$6:$BH$6"
        self.named_ranges["Net_Revenue"] = "'Revenue Build'!$B$20:$BH$20"
        self.named_ranges["Total_Gross_Revenue"] = "'Revenue Build'!$B$15:$BH$15"

    def build_cogs_sheet(self):
        """Build the COGS Build sheet with 2-year aging requirement."""
        worksheet = self.workbook.get_worksheet_by_name("COGS Build")
        
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:BH', 12)
        if "COGS Build" in self.timeline_sheets:
            self.add_timeline_headers("COGS Build")
        
        worksheet.write('A3', 'Direct Materials', self.formats['subheader'])
        worksheet.write('A4', 'Grain', self.formats['label'])
        worksheet.write('A5', 'Other Materials', self.formats['label'])
        worksheet.write('A6', 'Bottles & Packaging', self.formats['label'])
        worksheet.write('A7', 'Total Materials', self.formats['total'])
        
        worksheet.write('A9', 'Direct Labor', self.formats['subheader'])
        worksheet.write('A10', 'Production Labor', self.formats['label'])
        
        worksheet.write('A12', 'Overhead', self.formats['subheader'])
        worksheet.write('A13', 'Facility Costs', self.formats['label'])
        worksheet.write('A14', 'Equipment Depreciation', self.formats['label'])
        worksheet.write('A15', 'Total COGS', self.formats['total'])
        
        worksheet.write('A17', 'Inventory Metrics', self.formats['subheader'])
        worksheet.write('A18', 'Beginning Inventory Value', self.formats['label'])
        worksheet.write('A19', 'Production Cost', self.formats['label'])
        worksheet.write('A20', 'COGS Sold', self.formats['label'])
        worksheet.write('A21', 'Ending Inventory Value', self.formats['total'])
        
        worksheet.write('A23', 'Production Planning', self.formats['subheader'])
        worksheet.write('A24', 'Sales Forecast (Units)', self.formats['label'])
        worksheet.write('A25', 'Production Schedule (Units)', self.formats['label'])

        for col in range(1, 61):  # B to BH
            col_letter = xlsxwriter.utility.xl_col_to_name(col)
            prev_col_letter = xlsxwriter.utility.xl_col_to_name(col - 1)

            # Production Planning
            # Sales forecast is just the total units from revenue build
            worksheet.write_formula(f'{col_letter}24', f"='Revenue Build'!{col_letter}6", self.formats['formula'])
            # Production schedule is based on sales 24 months from now to account for aging
            # We use OFFSET to look forward 24 columns. If it goes past the end, assume 0.
            worksheet.write_formula(f'{col_letter}25', f"=IFERROR(OFFSET({col_letter}24, 0, 24), 0) / (1-Angels_Share_Annual)^2", self.formats['formula'])

            # Direct Materials
            worksheet.write_formula(f'{col_letter}4', f"=Grain_per_Bottle*{col_letter}25", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}5', f"=Other_Materials*{col_letter}25", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}6', f"=Bottle_and_Packaging*{col_letter}24", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}7', f"=SUM({col_letter}4:{col_letter}6)", self.formats['formula_currency'])
            
            # Direct Labor
            worksheet.write_formula(f'{col_letter}10', f"=Direct_Labor*{col_letter}24", self.formats['formula_currency'])

            # Overhead
            worksheet.write_formula(f'{col_letter}13', "=0", self.formats['formula_currency']) # Assuming facility costs are in OpEx
            worksheet.write_formula(f'{col_letter}14', f"='CapEx Schedule'!{col_letter}10", self.formats['formula_currency'])

            # Total COGS
            worksheet.write_formula(f'{col_letter}15', f"=SUM({col_letter}7, {col_letter}10, {col_letter}14)", self.formats['formula_currency'])
            
            # Inventory Metrics
            # Production Cost = Grain + Other Materials for units produced this month
            worksheet.write_formula(f'{col_letter}19', f"={col_letter}4+{col_letter}5", self.formats['formula_currency'])
            # COGS Sold = All costs associated with units sold this month
            worksheet.write_formula(f'{col_letter}20', f"={col_letter}15", self.formats['formula_currency'])

            if col == 1:
                worksheet.write('B18', 0, self.formats['formula_currency'])
            else:
                worksheet.write_formula(f'{col_letter}18', f"={prev_col_letter}21", self.formats['formula_currency'])
            
            worksheet.write_formula(f'{col_letter}21', f"={col_letter}18+{col_letter}19-{col_letter}20", self.formats['formula_currency'])

        self.named_ranges["Total_COGS"] = "'COGS Build'!$B$15:$BH$15"
        self.named_ranges["Ending_Inventory"] = "'COGS Build'!$B$21:$BH$21"

    def build_opex_sheet(self):
        """Build the OpEx Build sheet."""
        worksheet = self.workbook.get_worksheet_by_name("OpEx Build")
        
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:BH', 12)
        if "OpEx Build" in self.timeline_sheets:
            self.add_timeline_headers("OpEx Build")
        
        worksheet.write('A3', 'Personnel', self.formats['subheader'])
        worksheet.write('A4', 'Salaries & Wages', self.formats['label'])
        worksheet.write('A5', 'Benefits & Taxes (20%)', self.formats['label'])
        worksheet.write('A6', 'Total Personnel', self.formats['total'])
        
        worksheet.write('A8', 'Sales & Marketing', self.formats['subheader'])
        worksheet.write('A9', 'Marketing', self.formats['label'])
        worksheet.write('A10', 'Total S&M', self.formats['total'])

        worksheet.write('A12', 'General & Administrative', self.formats['subheader'])
        worksheet.write('A13', 'Rent', self.formats['label'])
        worksheet.write('A14', 'Insurance', self.formats['label'])
        worksheet.write('A15', 'Total G&A', self.formats['total'])
        
        worksheet.write('A17', 'Total OpEx', self.formats['total'])

        for col in range(1, 61):
            col_letter = xlsxwriter.utility.xl_col_to_name(col)
            
            # Personnel
            worksheet.write_formula(f'{col_letter}4', '=Base_Salaries/12', self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}5', f'={col_letter}4*0.20', self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}6', f'={col_letter}4+{col_letter}5', self.formats['formula_currency'])

            # S&M
            worksheet.write_formula(f'{col_letter}9', "='Revenue Build'!{0}20*Marketing_Pct_Revenue".format(col_letter), self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}10', f'={col_letter}9', self.formats['formula_currency'])

            # G&A
            worksheet.write_formula(f'{col_letter}13', '=Rent_per_Month', self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}14', '=Insurance_Annual/12', self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}15', f'={col_letter}13+{col_letter}14', self.formats['formula_currency'])
            
            # Total
            worksheet.write_formula(f'{col_letter}17', f'={col_letter}6+{col_letter}10+{col_letter}15', self.formats['formula_currency'])

        self.named_ranges["Total_OpEx"] = "'OpEx Build'!$B$17:$BH$17"

    def build_headcount_sheet(self):
        """Build the Headcount sheet."""
        worksheet = self.workbook.get_worksheet_by_name("Headcount")
        
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:D', 15)
        worksheet.set_column('E:F', 12)
        
        worksheet.merge_range('B2:D2', 'Headcount Plan', self.formats['title'])
        
        headers = ['Department', 'Role', 'Year 1', 'Year 2', 'Year 3', 'Year 4+']
        worksheet.write_row('A4', headers, self.formats['header'])
        
        data = [
            ['Production', 'Master Distiller', 1, 1, 1, 1],
            ['Production', 'Assistant Distiller', 1, 2, 3, 3],
            ['Production', 'Production Staff', 2, 3, 4, 5],
            ['Sales & Marketing', 'Sales Director', 1, 1, 1, 1],
            ['Sales & Marketing', 'Sales Representative', 1, 2, 3, 4],
            ['Sales & Marketing', 'Marketing Manager', 1, 1, 1, 2],
            ['G&A', 'CEO', 1, 1, 1, 1],
            ['G&A', 'Finance Manager', 0, 1, 1, 1],
            ['G&A', 'Office Manager', 1, 1, 1, 1],
        ]
        
        row = 5
        for item in data:
            worksheet.write_row(f'A{row}', item, self.formats['label'])
            for i in range(2, 6):
                worksheet.write(row-1, i, item[i], self.formats['number'])
            row += 1
        
        total_row = row + 1
        worksheet.write(f'B{total_row}', 'Total Headcount', self.formats['total'])
        worksheet.write_formula(f'C{total_row}', f'=SUM(C5:C{row-1})', self.formats['total'])
        worksheet.write_formula(f'D{total_row}', f'=SUM(D5:D{row-1})', self.formats['total'])
        worksheet.write_formula(f'E{total_row}', f'=SUM(E5:E{row-1})', self.formats['total'])
        worksheet.write_formula(f'F{total_row}', f'=SUM(F5:F{row-1})', self.formats['total'])

    def build_capex_sheet(self):
        """Build the CapEx Schedule sheet."""
        worksheet = self.workbook.get_worksheet_by_name("CapEx Schedule")
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:BH', 12)
        if "CapEx Schedule" in self.timeline_sheets:
            self.add_timeline_headers("CapEx Schedule")

        worksheet.write('A4', 'Beginning PP&E', self.formats['label'])
        worksheet.write('A6', 'CapEx', self.formats['subheader'])
        worksheet.write('A7', 'Initial Equipment', self.formats['label'])
        worksheet.write('A8', 'Expansion Y3', self.formats['label'])
        worksheet.write('A9', 'Total CapEx', self.formats['total'])
        worksheet.write('A10', 'Depreciation', self.formats['label'])
        worksheet.write('A11', 'Ending PP&E', self.formats['total'])

        for col in range(1, 61):
            col_letter = xlsxwriter.utility.xl_col_to_name(col)
            prev_col_letter = xlsxwriter.utility.xl_col_to_name(col - 1)

            if col == 1:
                worksheet.write('B4', 0, self.formats['formula_currency'])
                worksheet.write_formula('B7', '=Initial_Equipment', self.formats['formula_currency'])
            else:
                worksheet.write_formula(f'{col_letter}4', f'={prev_col_letter}11', self.formats['formula_currency'])
                worksheet.write(f'{col_letter}7', 0, self.formats['formula_currency'])

            # Expansion in Y3 (Month 25)
            worksheet.write_formula(f'{col_letter}8', f'=IF(COLUMN()=2+24, Y3_Expansion, 0)', self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}9', f'={col_letter}7+{col_letter}8', self.formats['formula_currency'])
            
            # Straight-line depreciation over 10 years (120 months)
            worksheet.write_formula(f'{col_letter}10', f'=-{col_letter}4/120', self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}11', f'={col_letter}4+{col_letter}9+{col_letter}10', self.formats['formula_currency'])

        self.named_ranges["Total_Capex"] = "'CapEx Schedule'!$B$9:$BH$9"
        self.named_ranges["Total_Depreciation"] = "'CapEx Schedule'!$B$10:$BH$10"
        self.named_ranges["Ending_PPE"] = "'CapEx Schedule'!$B$11:$BH$11"

    def build_debt_sheet(self):
        """Build the Debt Schedule sheet."""
        worksheet = self.workbook.get_worksheet_by_name("Debt Schedule")
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:BH', 12)
        if "Debt Schedule" in self.timeline_sheets:
            self.add_timeline_headers("Debt Schedule")

        worksheet.write('A4', 'Beginning Debt', self.formats['label'])
        worksheet.write('A5', 'Debt Issuance', self.formats['label'])
        worksheet.write('A6', 'Principal Repayment', self.formats['label'])
        worksheet.write('A7', 'Ending Debt', self.formats['total'])
        worksheet.write('A9', 'Interest Expense', self.formats['label'])

        for col in range(1, 61):
            col_letter = xlsxwriter.utility.xl_col_to_name(col)
            prev_col_letter = xlsxwriter.utility.xl_col_to_name(col - 1)

            if col == 1:
                worksheet.write('B4', 0, self.formats['formula_currency'])
                worksheet.write_formula('B5', '=Term_Loan', self.formats['formula_currency'])
            else:
                worksheet.write_formula(f'{col_letter}4', f'={prev_col_letter}7', self.formats['formula_currency'])
                worksheet.write(f'{col_letter}5', 0, self.formats['formula_currency'])

            # Repayment only starts after issuance and within loan term
            principal_formula = f"=IF({col_letter}4>0, -PPMT(Interest_Rate/12, COLUMN()-2, Loan_Term_Years*12, {col_letter}4+{col_letter}5), 0)"
            interest_formula = f"=IF({col_letter}4>0, -IPMT(Interest_Rate/12, COLUMN()-2, Loan_Term_Years*12, {col_letter}4+{col_letter}5), 0)"
            
            worksheet.write_formula(f'{col_letter}6', principal_formula, self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}9', interest_formula, self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}7', f'={col_letter}4+{col_letter}5-{col_letter}6', self.formats['formula_currency'])

        self.named_ranges["Interest_Expense"] = "'Debt Schedule'!$B$9:$BH$9"
        self.named_ranges["Debt_Issuance"] = "'Debt Schedule'!$B$5:$BH$5"
        self.named_ranges["Debt_Repayment"] = "'Debt Schedule'!$B$6:$BH$6"
        self.named_ranges["Ending_Debt"] = "'Debt Schedule'!$B$7:$BH$7"

    def build_working_capital_sheet(self):
        """Build the Working Capital sheet."""
        worksheet = self.workbook.get_worksheet_by_name("Working Capital")
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:BH', 12)
        if "Working Capital" in self.timeline_sheets:
            self.add_timeline_headers("Working Capital")

        worksheet.write('A4', 'Accounts Receivable', self.formats['label'])
        worksheet.write('A5', 'Inventory', self.formats['label'])
        worksheet.write('A6', 'Accounts Payable', self.formats['label'])
        worksheet.write('A8', 'Net Working Capital', self.formats['total'])
        worksheet.write('A9', 'Change in NWC', self.formats['total'])

        for col in range(1, 61):
            col_letter = xlsxwriter.utility.xl_col_to_name(col)
            prev_col_letter = xlsxwriter.utility.xl_col_to_name(col - 1)

            worksheet.write_formula(f'{col_letter}4', f"='Revenue Build'!{col_letter}20 / 30 * AR_Days", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}5', f"='COGS Build'!{col_letter}21", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}6', f"='COGS Build'!{col_letter}15 / 30 * AP_Days", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}8', f'={col_letter}4+{col_letter}5-{col_letter}6', self.formats['formula_currency'])

            if col == 1:
                worksheet.write_formula('B9', '=B8', self.formats['formula_currency'])
            else:
                worksheet.write_formula(f'{col_letter}9', f'={col_letter}8-{prev_col_letter}8', self.formats['formula_currency'])

        self.named_ranges["AR_Balance"] = "'Working Capital'!$B$4:$BH$4"
        self.named_ranges["Inventory_Balance"] = "'Working Capital'!$B$5:$BH$5"
        self.named_ranges["AP_Balance"] = "'Working Capital'!$B$6:$BH$6"
        self.named_ranges["Change_in_NWC"] = "'Working Capital'!$B$9:$BH$9"

    def build_income_statement(self):
        """Build the Income Statement sheet."""
        worksheet = self.workbook.get_worksheet_by_name("Income Statement")
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:BH', 12)
        if "Income Statement" in self.timeline_sheets:
            self.add_timeline_headers("Income Statement")

        worksheet.write('A4', 'Net Revenue', self.formats['label'])
        worksheet.write('A5', 'Total COGS', self.formats['label'])
        worksheet.write('A6', 'Gross Profit', self.formats['total'])
        worksheet.write('A7', 'Gross Margin', self.formats['formula_percent'])
        worksheet.write('A9', 'Total OpEx', self.formats['label'])
        worksheet.write('A10', 'EBITDA', self.formats['total'])
        worksheet.write('A11', 'EBITDA Margin', self.formats['formula_percent'])
        worksheet.write('A13', 'Depreciation & Amort.', self.formats['label'])
        worksheet.write('A14', 'EBIT', self.formats['total'])
        worksheet.write('A16', 'Interest Expense', self.formats['label'])
        worksheet.write('A17', 'EBT', self.formats['total'])
        worksheet.write('A19', 'Taxes', self.formats['label'])
        worksheet.write('A20', 'Net Income', self.formats['total'])

        for col in range(1, 61):
            col_letter = xlsxwriter.utility.xl_col_to_name(col)
            worksheet.write_formula(f'{col_letter}4', f"='Revenue Build'!{col_letter}20", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}5', f"='COGS Build'!{col_letter}15", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}6', f"={col_letter}4-{col_letter}5", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}7', f"={col_letter}6/{col_letter}4", self.formats['formula_percent'])
            worksheet.write_formula(f'{col_letter}9', f"='OpEx Build'!{col_letter}17", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}10', f"={col_letter}6-{col_letter}9", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}11', f"={col_letter}10/{col_letter}4", self.formats['formula_percent'])
            worksheet.write_formula(f'{col_letter}13', f"='CapEx Schedule'!{col_letter}10", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}14', f"={col_letter}10+{col_letter}13", self.formats['formula_currency']) # D&A is negative
            worksheet.write_formula(f'{col_letter}16', f"=-'Debt Schedule'!{col_letter}9", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}17', f"={col_letter}14-{col_letter}16", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}19', f"=-MAX(0, {col_letter}17)*TaxRate", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}20', f"={col_letter}17+{col_letter}19", self.formats['formula_currency'])

        self.named_ranges["Net_Income"] = "'Income Statement'!$B$20:$BH$20"

    def build_cash_flow_statement(self):
        """Build the Cash Flow Statement sheet."""
        worksheet = self.workbook.get_worksheet_by_name("Cash Flow Statement")
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:BH', 12)
        if "Cash Flow Statement" in self.timeline_sheets:
            self.add_timeline_headers("Cash Flow Statement")

        worksheet.write('A3', 'Cash Flow from Operations', self.formats['subheader'])
        worksheet.write('A4', 'Net Income', self.formats['label'])
        worksheet.write('A5', 'Depreciation & Amort.', self.formats['label'])
        worksheet.write('A6', 'Change in NWC', self.formats['label'])
        worksheet.write('A7', 'Net CFO', self.formats['total'])

        worksheet.write('A9', 'Cash Flow from Investing', self.formats['subheader'])
        worksheet.write('A10', 'Capital Expenditures', self.formats['label'])
        worksheet.write('A11', 'Net CFI', self.formats['total'])

        worksheet.write('A13', 'Cash Flow from Financing', self.formats['subheader'])
        worksheet.write('A14', 'Debt Issued', self.formats['label'])
        worksheet.write('A15', 'Debt Repaid', self.formats['label'])
        worksheet.write('A16', 'Equity Issued', self.formats['label'])
        worksheet.write('A17', 'Net CFF', self.formats['total'])

        worksheet.write('A19', 'Net Change in Cash', self.formats['total'])
        worksheet.write('A20', 'Beginning Cash', self.formats['label'])
        worksheet.write('A21', 'Ending Cash', self.formats['total'])

        for col in range(1, 61):
            col_letter = xlsxwriter.utility.xl_col_to_name(col)
            prev_col_letter = xlsxwriter.utility.xl_col_to_name(col - 1)

            # CFO
            worksheet.write_formula(f'{col_letter}4', f"='Income Statement'!{col_letter}20", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}5', f"=-'CapEx Schedule'!{col_letter}10", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}6', f"=-'Working Capital'!{col_letter}9", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}7', f"=SUM({col_letter}4:{col_letter}6)", self.formats['formula_currency'])

            # CFI
            worksheet.write_formula(f'{col_letter}10', f"=-'CapEx Schedule'!{col_letter}9", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}11', f"={col_letter}10", self.formats['formula_currency'])

            # CFF
            worksheet.write_formula(f'{col_letter}14', f"='Debt Schedule'!{col_letter}5", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}15', f"=-'Debt Schedule'!{col_letter}6", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}16', f"=IF(COLUMN()=2, Initial_Equity, 0)", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}17', f"=SUM({col_letter}14:{col_letter}16)", self.formats['formula_currency'])

            # Cash Reconciliation
            worksheet.write_formula(f'{col_letter}19', f"={col_letter}7+{col_letter}11+{col_letter}17", self.formats['formula_currency'])
            if col == 1:
                worksheet.write('B20', 0, self.formats['formula_currency'])
            else:
                worksheet.write_formula(f'{col_letter}20', f"={prev_col_letter}21", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}21', f"={col_letter}19+{col_letter}20", self.formats['formula_currency'])

        self.named_ranges["Ending_Cash"] = "'Cash Flow Statement'!$B$21:$BH$21"

    def build_balance_sheet(self):
        """Build the Balance Sheet sheet."""
        worksheet = self.workbook.get_worksheet_by_name("Balance Sheet")
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:BH', 12)
        if "Balance Sheet" in self.timeline_sheets:
            self.add_timeline_headers("Balance Sheet")

        worksheet.write('A3', 'Assets', self.formats['subheader'])
        worksheet.write('A4', 'Cash', self.formats['label'])
        worksheet.write('A5', 'Accounts Receivable', self.formats['label'])
        worksheet.write('A6', 'Inventory', self.formats['label'])
        worksheet.write('A7', 'Total Current Assets', self.formats['total'])
        worksheet.write('A8', 'PP&E, Net', self.formats['label'])
        worksheet.write('A9', 'Total Assets', self.formats['total'])

        worksheet.write('A11', 'Liabilities & Equity', self.formats['subheader'])
        worksheet.write('A12', 'Accounts Payable', self.formats['label'])
        worksheet.write('A13', 'Total Current Liabilities', self.formats['total'])
        worksheet.write('A14', 'Long-Term Debt', self.formats['label'])
        worksheet.write('A15', 'Total Liabilities', self.formats['total'])
        worksheet.write('A17', 'Common Stock', self.formats['label'])
        worksheet.write('A18', 'Retained Earnings', self.formats['label'])
        worksheet.write('A19', 'Total Equity', self.formats['total'])
        worksheet.write('A20', 'Total Liabilities & Equity', self.formats['total'])
        worksheet.write('A22', 'Balance Sheet Check', self.formats['label'])

        for col in range(1, 61):
            col_letter = xlsxwriter.utility.xl_col_to_name(col)
            prev_col_letter = xlsxwriter.utility.xl_col_to_name(col - 1)

            # Assets
            worksheet.write_formula(f'{col_letter}4', f"='Cash Flow Statement'!{col_letter}21", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}5', f"='Working Capital'!{col_letter}4", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}6', f"='Working Capital'!{col_letter}5", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}7', f"=SUM({col_letter}4:{col_letter}6)", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}8', f"='CapEx Schedule'!{col_letter}11", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}9', f"={col_letter}7+{col_letter}8", self.formats['formula_currency'])

            # Liabilities
            worksheet.write_formula(f'{col_letter}12', f"='Working Capital'!{col_letter}6", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}13', f"={col_letter}12", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}14', f"='Debt Schedule'!{col_letter}7", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}15', f"={col_letter}13+{col_letter}14", self.formats['formula_currency'])

            # Equity
            if col == 1:
                worksheet.write_formula('B17', "='Cash Flow Statement'!B16", self.formats['formula_currency'])
                worksheet.write_formula('B18', "='Income Statement'!B20", self.formats['formula_currency'])
            else:
                worksheet.write_formula(f'{col_letter}17', f"={prev_col_letter}17+'Cash Flow Statement'!{col_letter}16", self.formats['formula_currency'])
                worksheet.write_formula(f'{col_letter}18', f"={prev_col_letter}18+'Income Statement'!{col_letter}20", self.formats['formula_currency'])
            
            worksheet.write_formula(f'{col_letter}19', f"={col_letter}17+{col_letter}18", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}20', f"={col_letter}15+{col_letter}19", self.formats['formula_currency'])
            worksheet.write_formula(f'{col_letter}22', f"={col_letter}9-{col_letter}20", self.formats['formula_currency'])

    def build_cap_table(self):
        """Build the Cap Table sheet."""
        worksheet = self.workbook.get_worksheet_by_name("Cap Table")
        worksheet.set_column('A:F', 15)
        worksheet.merge_range('B2:E2', 'Capitalization Table', self.formats['title'])
        headers = ['Shareholder', 'Investment', 'Shares', 'Ownership %']
        worksheet.write_row('B4', headers, self.formats['header'])
        worksheet.write('B5', 'Founders', self.formats['label'])
        worksheet.write_formula('C5', '=Initial_Equity', self.formats['input_currency'])
        worksheet.write('D5', 1000000, self.formats['input'])
        worksheet.write_formula('E5', '=D5/D6', self.formats['input_percent'])
        worksheet.write('B6', 'Total', self.formats['total'])
        worksheet.write_formula('C6', '=C5', self.formats['total'])
        worksheet.write_formula('D6', '=D5', self.formats['total'])
        worksheet.write_formula('E6', '=E5', self.formats['total'])

    def build_returns_analysis(self):
        """Build the Returns Analysis sheet with proper IRR/MOIC calculations."""
        worksheet = self.workbook.get_worksheet_by_name("Returns Analysis")
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:G', 15)

        worksheet.write('A3', 'Free Cash Flow & Returns Analysis', self.formats['title'])
        
        # Headers for annual periods
        worksheet.write('A5', 'Year', self.formats['header'])
        worksheet.write('A6', 'Unlevered FCF', self.formats['label'])
        worksheet.write('A7', 'Levered FCF', self.formats['label'])
        worksheet.write('A8', 'Cumulative FCF', self.formats['label'])
        worksheet.write('A9', 'Investor Cash Flows', self.formats['label'])
        
        # Define annual column ranges
        year_ranges = [
            ('B:M', 12),  # Year 1
            ('N:Y', 12),  # Year 2
            ('Z:AK', 12), # Year 3
            ('AL:AS', 8), # Year 4 & 5 (Quarters) - Assuming 4 quarters per year
            ('AT:AU', 2) # Year 6 & 7 (Annual)
        ]
        
        # Years 0-5
        for year in range(6): # 0 to 5
            col_letter = xlsxwriter.utility.xl_col_to_name(year + 1) # B to G
            worksheet.write(f'{col_letter}5', year, self.formats['header'])
            
            if year == 0:
                # Initial investment
                worksheet.write_formula(f'{col_letter}6', '=0', self.formats['formula_currency'])
                worksheet.write_formula(f'{col_letter}7', '=0', self.formats['formula_currency'])
                worksheet.write_formula(f'{col_letter}9', '=-Initial_Equity', self.formats['formula_currency'])
            else:
                # Determine column range for the year
                if year <= 3: # Monthly data for years 1-3
                    start_col_idx = (year - 1) * 12 + 1
                    end_col_idx = year * 12
                elif year <= 5: # Quarterly data for years 4-5
                    start_col_idx = 36 + (year - 4) * 4 + 1
                    end_col_idx = 36 + (year - 3) * 4
                
                start_col = xlsxwriter.utility.xl_col_to_name(start_col_idx)
                end_col = xlsxwriter.utility.xl_col_to_name(end_col_idx)

                # Unlevered FCF = EBITDA + Taxes(already negative) - CapEx - Change in NWC
                ebitda = f"SUM('Income Statement'!{start_col}10:{end_col}10)"
                taxes = f"SUM('Income Statement'!{start_col}19:{end_col}19)"
                capex = f"SUM('CapEx Schedule'!{start_col}9:{end_col}9)"
                nwc_change = f"SUM('Working Capital'!{start_col}9:{end_col}9)"
                worksheet.write_formula(f'{col_letter}6', f"={ebitda}+{taxes}-{capex}-{nwc_change}", self.formats['formula_currency'])
                
                # Levered FCF = UFCF + Interest(negative) + Debt Repayment(negative) + Debt Issuance
                interest = f"SUM('Debt Schedule'!{start_col}9:{end_col}9)"
                repayment = f"SUM('Debt Schedule'!{start_col}6:{end_col}6)"
                issuance = f"SUM('Debt Schedule'!{start_col}5:{end_col}5)"
                worksheet.write_formula(f'{col_letter}7', f"={col_letter}6+{interest}+{repayment}+{issuance}", self.formats['formula_currency'])
                
                # Investor cash flows (for IRR calc)
                worksheet.write_formula(f'{col_letter}9', f'={col_letter}7', self.formats['formula_currency'])
            
            # Cumulative FCF
            if year == 0:
                worksheet.write_formula('B8', '=B9', self.formats['formula_currency'])
            else:
                prev_col = xlsxwriter.utility.xl_col_to_name(year)
                worksheet.write_formula(f'{col_letter}8', f'={prev_col}8+{col_letter}9', self.formats['formula_currency'])
        
        # Add terminal value in year 5 (Column G)
        y5_ebitda = "SUM('Income Statement'!AP10:AS10)" # EBITDA for last 4 quarters
        worksheet.write_formula('G9', f'=G7+({y5_ebitda}*10)', self.formats['formula_currency'])
        
        # Key metrics section
        worksheet.write('A11', 'Key Return Metrics', self.formats['subheader'])
        worksheet.write('A12', 'IRR', self.formats['label'])
        worksheet.write('A13', 'MOIC', self.formats['label'])
        worksheet.write('A14', 'Payback Period (Years)', self.formats['label'])
        worksheet.write('A15', 'Peak Funding Need', self.formats['label'])
        
        # IRR calculation
        worksheet.write_formula('C12', '=IRR(B9:G9)', self.formats['formula_percent'])
        self.named_ranges["Project_IRR"] = "'Returns Analysis'!$C$12"
        
        # MOIC calculation
        worksheet.write_formula('C13', '=SUMIF(B9:G9,">0")/ABS(SUMIF(B9:G9,"<0"))', self.formats['formula'])
        self.named_ranges["Project_MOIC"] = "'Returns Analysis'!$C$13"
        
        # Payback period calculation
        payback_formula = '=IFERROR(MATCH(TRUE,B8:G8>0,0)-2 + (0-INDEX(B8:G8,MATCH(TRUE,B8:G8>0,0)-1))/INDEX(B9:G9,MATCH(TRUE,B8:G8>0,0)), "Never")'
        worksheet.write_formula('C14', payback_formula, self.formats['formula'])
        
        # Peak cash need
        worksheet.write_formula('C15', '=MIN(B8:G8)', self.formats['formula_currency'])
        self.named_ranges["Peak_Cash_Need"] = "'Returns Analysis'!$C$15"


    # ------------------------------------------------------------------ #
    #  Data Import / Power-Query Framework                               #
    # ------------------------------------------------------------------ #
    def build_data_import_sheet(self):
        """
        Build the **Data Import** sheet which acts as a landing zone for Power
        Query connections and variance analysis.

        Only metadata tables, headers and data-validation scaffolding are
        created here – the actual Power Query (M) connections are documented
        as comments for user implementation in Excel.
        """
        ws = self.workbook.get_worksheet_by_name("Data Import")
        ws.set_column('A:A', 3)
        ws.set_column('B:B', 22)
        ws.set_column('C:E', 18)
        ws.set_column('G:M', 14)

        # -------------------- 1.  Connection Metadata ------------------- #
        ws.merge_range('B2:E2', 'Connection Metadata', self.formats['subheader'])
        meta_headers = ['Source Name', 'Connection Type', 'Refresh Frequency', 'Last Refresh']
        ws.write_row('B3', meta_headers, self.formats['header'])

        meta_rows = [
            ('QuickBooks_Actuals', 'CSV',  'On Open', ''),
            ('Bank_Statements',    'API',  'Daily',   ''),
            ('POS_System',         'DB',   'Manual',  '')
        ]
        for i, row in enumerate(meta_rows):
            ws.write_row(3 + i, 1, row, self.formats['label'])
            # last-refresh timestamp cell ready for PQ to update
            ws.write_blank(3 + i, 4, None, self.formats['date'])

        # ----------------- 2.  Actuals Data Landing Zone --------------- #
        data_start_row = 10
        ws.merge_range(data_start_row - 1, 1, data_start_row - 1, 6,
                       'Actuals – Raw Data (Power Query output area)',
                       self.formats['subheader'])

        data_headers = ['Date', 'Revenue', 'COGS', 'OpEx', 'Units Sold', 'Cash Balance']
        ws.write_row(data_start_row, 1, data_headers, self.formats['header'])

        # Provide ~120 blank rows for data loads
        for r in range(1, 121):
            excel_row = data_start_row + r
            ws.write_blank(excel_row, 1, None, self.formats['date'])         # Date
            for c in range(2, 7):
                ws.write_blank(excel_row, c, None, self.formats['number'])   # numeric cols

        # Data-validation for integrity
        ws.data_validation(data_start_row + 1, 1, data_start_row + 120, 1,
                           {'validate': 'date',
                            'criteria': 'between',
                            'minimum': datetime.date(2000, 1, 1),
                            'maximum': datetime.date(2100, 12, 31),
                            'error_message': 'Date required'})
        ws.data_validation(data_start_row + 1, 2, data_start_row + 120, 6,
                           {'validate': 'decimal',
                            'criteria': '>=',
                            'value': 0,
                            'error_message': 'Must be a non-negative number'})

        # Named range for later XLOOKUP / aggregation
        self.named_ranges['Actuals_Table'] = f"'Data Import'!$B${data_start_row+1}:$G${data_start_row+120}"

        # ----------- 3.  Variance / Reconciliation Framework ----------- #
        var_row = data_start_row + 125
        ws.merge_range(var_row, 1, var_row, 6,
                       'Variance Analysis (Actuals vs Forecast) – placeholders',
                       self.formats['subheader'])
        ws.write_row(var_row + 1, 1,
                     ['Metric', 'Actuals', 'Forecast', 'Variance', '% Var'],
                     self.formats['header'])
        metrics = ['Revenue', 'COGS', 'OpEx', 'Units Sold', 'Cash Balance']
        for i, m in enumerate(metrics):
            r = var_row + 2 + i
            ws.write(r, 1, m, self.formats['label'])
            # Placeholders: formulas can be completed later
            ws.write_formula(r, 2, '', self.formats['formula_currency'])
            ws.write_formula(r, 3, '', self.formats['formula_currency'])
            ws.write_formula(r, 4, '=C{0}-D{0}'.format(r+1), self.formats['formula_currency'])
            ws.write_formula(r, 5, '=IFERROR(C{0}/D{0}-1,0)'.format(r+1), self.formats['formula_percent'])

        # --------------- 4.  M-Query Documentation --------------------- #
        doc_row = var_row + 10
        m_query_comment = (
            "/*\n"
            "Sample M query for QuickBooks_Actuals connection:\n"
            "let\n"
            "    Source = Csv.Document(File.Contents(\"actuals.csv\"),[Delimiter=\",\", Columns=6, Encoding=1252, QuoteStyle=QuoteStyle.None]),\n"
            "    #\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n"
            "    #\"Changed Type\" = Table.TransformColumnTypes(#\"Promoted Headers\",\n"
            "        {{\"Date\", type date}, {\"Revenue\", type number}, {\"COGS\", type number},\n"
            "         {\"OpEx\", type number}, {\"Units Sold\", type number}, {\"Cash Balance\", type number}})\n"
            "in\n"
            "    #\"Changed Type\"\n"
            "*/"
        )
        ws.write_comment(doc_row, 1, m_query_comment, {'author': 'Model Bot', 'visible': False})

    # ------------------------------------------------------------------ #
    #  Sensitivity Tables & Scenario Analysis (Two-Way, Tornado, etc.)   #
    # ------------------------------------------------------------------ #
    def build_sensitivity_tables(self):
        """
        Create two-way sensitivity tables, tornado data, discount-rate curve,
        and break-even analysis on the Returns Analysis sheet (rows 30+).

        NOTE:
        Excel two-way data-tables aren’t natively generated by XlsxWriter.
        We therefore lay out the correct structure, seed the centre-cell with
        =Project_IRR and fill the table with that same formula.  A user can
        later convert it to an actual DataTable inside Excel if desired.
        """
        ws = self.workbook.get_worksheet_by_name("Returns Analysis")

        # ---------------- Two-way Price vs Volume table ---------------- #
        start_row = 29  # 0-based index (row 30 in Excel)
        ws.write(start_row, 0, "IRR Sensitivity – Price vs Volume", self.formats['subheader'])

        price_vars   = [-0.20, -0.10, 0, 0.10, 0.20]   # rows
        growth_vars  = [-0.10, -0.05, 0, 0.05, 0.10]   # columns

        header_row = start_row + 2           # Excel row 32
        header_col = 1                       # Column B

        # column headers (volume growth)
        for i, gv in enumerate(growth_vars):
            col_letter = xlsxwriter.utility.xl_col_to_name(header_col + i)
            ws.write(header_row, header_col + i,
                     gv,
                     self.workbook.add_format({'num_format': '0.0%', 'border': 1, 'align': 'center'}))

        # row headers (price)
        for i, pv in enumerate(price_vars):
            ws.write(header_row + 1 + i, 0,
                     pv,
                     self.workbook.add_format({'num_format': '0%', 'border': 1, 'align': 'center'}))

        # top-left (corner) cell must link to formula driver (Project_IRR)
        table_first_cell_row = header_row + 1
        table_first_cell_col = header_col
        ws.write_formula(table_first_cell_row,
                         table_first_cell_col,
                         "=Project_IRR",
                         self.formats['formula_percent'])

        # fill the remaining 5×5 block with Project_IRR placeholders
        for r in range(len(price_vars)):
            for c in range(len(growth_vars)):
                if r == 0 and c == 0:
                    continue  # already written
                ws.write_formula(table_first_cell_row + r,
                                 table_first_cell_col + c,
                                 "=Project_IRR",
                                 self.formats['formula_percent'])

        # Conditional-format heat-map
        ws.conditional_format(table_first_cell_row,
                              table_first_cell_col,
                              table_first_cell_row + 4,
                              table_first_cell_col + 4,
                              {'type': '3_color_scale',
                               'min_color': '#F8696B',   # red
                               'mid_color': '#FFEB84',   # yellow
                               'max_color': '#63BE7B'})  # green

        # Tell Excel (for users) which inputs drive the table
        ws.write(header_row - 1, 0, "Row Input: Avg_Price_per_Bottle", self.formats['label'])
        ws.write(header_row - 1, 3, "Col Input: Annual_Growth_Rate",   self.formats['label'])

        # ---------------- Tornado Chart helper data ------------------- #
        tornado_start = header_row + 9  # leave a gap
        ws.write(tornado_start, 0, "Tornado Chart Data", self.formats['subheader'])
        ws.write_row(tornado_start + 1, 0,
                     ["Variable", "Low Case", "Base Case", "High Case", "Range"],
                     self.formats['header'])

        sensitivity_vars = [
            ("Price per Bottle", "-20%", "+0%", "+20%"),
            ("Volume Growth", "-20%", "+0%", "+20%"),
            ("COGS per Bottle", "+20%", "+0%", "-20%"),
            ("OpEx", "+20%", "+0%", "-20%"),
            ("CapEx", "+20%", "+0%", "-20%")
        ]

        for i, (label, low_tag, base_tag, high_tag) in enumerate(sensitivity_vars):
            r = tornado_start + 2 + i
            ws.write(r, 0, label, self.formats['label'])
            # placeholders – user can override with scenario calc later
            ws.write_formula(r, 1, "=Project_IRR", self.formats['formula_percent'])
            ws.write_formula(r, 2, "=Project_IRR", self.formats['formula_percent'])
            ws.write_formula(r, 3, "=Project_IRR", self.formats['formula_percent'])
            ws.write_formula(r, 4, f"=ABS(C{r+1}-B{r+1})", self.formats['formula_percent'])

        # --------------- Discount-Rate Sensitivity table -------------- #
        disc_start = tornado_start + 10
        ws.write(disc_start, 0, "IRR vs Discount Rate", self.formats['subheader'])
        disc_rates = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
        ws.write(disc_start + 1, 0, "Discount Rate", self.formats['header'])
        ws.write(disc_start + 1, 1, "IRR",           self.formats['header'])

        for i, dr in enumerate(disc_rates):
            ws.write(disc_start + 2 + i, 0, dr, self.formats['percent'])
            ws.write_formula(disc_start + 2 + i, 1,
                             "=Project_IRR",  # placeholder
                             self.formats['formula_percent'])

        # -------------------- Break-Even Analysis --------------------- #
        be_start = disc_start + 10
        ws.write(be_start, 0, "Break-Even Analysis (0% IRR)", self.formats['subheader'])
        ws.write_row(be_start + 1, 0, ["Price Change", "Units Needed"], self.formats['header'])

        for i, pv in enumerate(price_vars):
            ws.write(be_start + 2 + i, 0, pv, self.workbook.add_format({'num_format': '0%', 'border': 1}))
            ws.write(be_start + 2 + i, 1,
                     "",  # placeholder for goal-seek result
                     self.formats['formula'])

        # All structures created – named range for future reference
        self.named_ranges["IRR_Sensitivity_Table"] = f"'Returns Analysis'!$B${table_first_cell_row+1}:$F${table_first_cell_row+5}"

    def build_dashboard(self):
        """Build an investment-grade dashboard with professional visualizations."""
        ws = self.workbook.get_worksheet_by_name("Dashboard")

        # --- 1. Setup and Formatting ---
        ws.set_column('A:A', 2)
        ws.set_column('B:C', 12) # KPI cards
        ws.set_column('D:D', 2)  # Gap
        ws.set_column('E:F', 12) # KPI cards
        ws.set_column('G:G', 2)  # Gap
        ws.set_column('H:I', 12) # KPI cards
        ws.set_column('J:J', 2)  # Gap
        ws.set_column('K:R', 10) # Other charts
        ws.set_zoom(85)

        # Define custom formats for the dashboard
        kpi_title_format = self.workbook.add_format({'bold': True, 'font_size': 10, 'align': 'left', 'valign': 'vcenter', 'border': 1, 'bg_color': '#F2F2F2'})
        kpi_value_format = self.workbook.add_format({'bold': True, 'font_size': 18, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'num_format': '$#,##0,"K"'})
        kpi_percent_format = self.workbook.add_format({'bold': True, 'font_size': 18, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'num_format': '0.0%'})
        kpi_moic_format = self.workbook.add_format({'bold': True, 'font_size': 18, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'num_format': '0.00"x"'})
        kpi_trend_format = self.workbook.add_format({'font_size': 9, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        
        # --- 2. KPI Cards Section (B5:I13) ---
        ws.merge_range('B1:J1', 'Distillery Performance Dashboard', self.formats['title'])

        kpis = [
            # Top Row
            {'label': 'Revenue (TTM)', 'formula': "=SUM('Income Statement'!B4:M4)", 'format': kpi_value_format, 'pos': 'B5'},
            {'label': 'Gross Margin %', 'formula': "=AVERAGE('Income Statement'!B7:M7)", 'format': kpi_percent_format, 'pos': 'E5'},
            {'label': 'EBITDA Margin %', 'formula': "=AVERAGE('Income Statement'!B11:M11)", 'format': kpi_percent_format, 'pos': 'H5'},
            # Bottom Row
            {'label': 'Cash Balance', 'formula': "=Ending_Cash", 'format': kpi_value_format, 'pos': 'B10'},
            {'label': 'Project IRR', 'formula': "=Project_IRR", 'format': kpi_percent_format, 'pos': 'E10'},
            {'label': 'Project MOIC', 'formula': "=Project_MOIC", 'format': kpi_moic_format, 'pos': 'H10'},
        ]

        for kpi in kpis:
            row, col = xlsxwriter.utility.xl_cell_to_rowcol(kpi['pos'])
            # KPI Card is 2 columns wide and 4 rows tall
            ws.merge_range(row, col, row, col + 1, kpi['label'], kpi_title_format)
            ws.merge_range(row + 1, col, row + 2, col + 1, kpi['formula'], kpi['format'])
            ws.merge_range(row + 3, col, row + 3, col + 1, "[Sparkline] vs LY: +5.0%", kpi_trend_format)
            ws.write_comment(row + 3, col, "XlsxWriter cannot create sparklines. Please add them manually in Excel via Insert > Sparklines.")

        # --- 3. Cash Burn Chart (B15:I25) ---
        ws.merge_range('B15:I15', 'Monthly Cash Flow & Burn Analysis', self.formats['subheader'])
        cash_burn_chart = self.workbook.add_chart({'type': 'column'})
        cash_burn_chart.add_series({
            'name':       "='Cash Flow Statement'!A19",
            'categories': "='Cash Flow Statement'!$B$1:$M$1",
            'values':     "='Cash Flow Statement'!$B$19:$M$19",
            'fill':       {'color': '#C00000'},
            'border':     {'color': '#C00000'},
            'invert_if_negative': True,
        })
        cash_burn_chart.set_y_axis({'num_format': '$#,##0,"K"'})
        cash_burn_chart.set_x_axis({'date_axis': True, 'num_format': 'mmm yy'})
        cash_burn_chart.set_legend({'position': 'bottom'})
        cash_burn_chart.set_size({'width': 640, 'height': 280})
        ws.insert_chart('B16', cash_burn_chart)

        # --- 4. Revenue Waterfall (K15:R25) ---
        ws.merge_range('K15:R15', 'Y1 Revenue Waterfall', self.formats['subheader'])
        # Placeholder for waterfall chart. Requires helper columns.
        ws.merge_range('K16:R25', '[Waterfall Chart Placeholder]', self.formats['label'])
        ws.write_comment('K16', "Waterfall charts require a helper table with calculated values for start, end, increases, and decreases. This can be built on a separate helper sheet and then linked here.")

        # --- 5. Unit Economics Gauge (B28:F35) ---
        ws.merge_range('B28:F28', 'Unit Economics: Contribution Margin', self.formats['subheader'])
        # Placeholder for gauge chart. Requires complex chart setup.
        ws.merge_range('B29:F35', '[Gauge Chart Placeholder]', self.formats['label'])
        ws.write_comment('B29', "Gauge charts are created by combining and formatting multiple chart types (doughnut and pie). This is an advanced technique best performed manually in Excel.")

        # --- 6. Scenario Comparison Table (H28:R35) ---
        ws.merge_range('H28:R28', 'Scenario Comparison', self.formats['subheader'])
        ws.write_row('H29', ['Metric', 'Downside', 'Base Case', 'Upside'], self.formats['header'])
        metrics_to_compare = ['Project IRR', 'Project MOIC', 'Peak Funding Need']
        for i, metric in enumerate(metrics_to_compare):
            ws.write(30 + i, 7, metric, self.formats['label'])
        ws.write_comment('H29', "This table would require VBA or manual runs to populate the values for each scenario.")
        
        # --- 7. Covenant Compliance Tracker (B38:R42) ---
        ws.merge_range('B38:J38', 'Covenant Compliance Tracker', self.formats['subheader'])
        ws.write_row('B39', ['Covenant', 'Current Value', 'Threshold', 'Status', 'Months to Breach'], self.formats['header'])
        # DSCR
        ws.write('B40', 'Debt Service Coverage Ratio (DSCR)', self.formats['label'])
        ws.write_formula('C40', "IFERROR(AVERAGE('Income Statement'!B10:M10)/ABS(AVERAGE('Debt Schedule'!B6:M6)+AVERAGE('Debt Schedule'!B9:M9)),0)", self.formats['formula'])
        ws.write('D40', '> 1.25x', self.formats['label'])
        ws.conditional_format('E40:E40', {'type': 'icon_set', 'icon_style': '3_traffic_lights', 'icons': [{'criteria': '>=', 'type': 'number', 'value': 1.5}, {'criteria': '>=', 'type': 'number', 'value': 1.25}]})
        # Leverage Ratio
        ws.write('B41', 'Leverage Ratio (Debt/EBITDA)', self.formats['label'])
        ws.write_formula('C41', "IFERROR(Ending_Debt/SUM('Income Statement'!B10:M10),0)", self.formats['formula'])
        ws.write('D41', '< 4.0x', self.formats['label'])
        ws.conditional_format('E41:E41', {'type': 'icon_set', 'icon_style': '3_traffic_lights_r', 'icons': [{'criteria': '>=', 'type': 'number', 'value': 4.5}, {'criteria': '>=', 'type': 'number', 'value': 4.0}]})
        
        # --- 8. Interactive Elements (Placeholders) ---
        ws.write_comment('B1', "Interactive elements like buttons and sliders cannot be created with XlsxWriter. They must be added manually in Excel and linked to VBA macros.")
        ws.merge_range('K1:L1', 'Update Scenario', self.formats['button'])
        ws.merge_range('M1:N1', 'Run Sensitivity', self.formats['button'])
        
    def build_checks_sheet(self):
        """Build the Checks sheet."""
        worksheet = self.workbook.get_worksheet_by_name("Checks")
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:BH', 12)
        if "Checks" in self.timeline_sheets:
            self.add_timeline_headers("Checks")

        worksheet.write('A4', 'Balance Sheet Check', self.formats['label'])
        for col in range(1, 61):
            col_letter = xlsxwriter.utility.xl_col_to_name(col)
            formula = f"='Balance Sheet'!{col_letter}22"
            worksheet.write_formula(f'{col_letter}4', formula, self.formats['formula_currency'])
            worksheet.conditional_format(f'{col_letter}4', {'type': 'cell', 'criteria': '!=', 'value': 0, 'format': self.formats['check_error']})
            worksheet.conditional_format(f'{col_letter}4', {'type': 'cell', 'criteria': '==', 'value': 0, 'format': self.formats['check_ok']})

    def add_navigation_buttons(self):
        """Add navigation buttons to all sheets."""
        for sheet_name in self.sheets:
            if sheet_name != "Dashboard":
                worksheet = self.workbook.get_worksheet_by_name(sheet_name)
                worksheet.write_url('A1', "internal:Dashboard!A1", string='Go to Dashboard', cell_format=self.formats['button'])

    # ------------------------------------------------------------------ #
    #  Unit Economics (Investor Sheet)                                   #
    # ------------------------------------------------------------------ #
    def build_unit_economics_sheet(self):
        """
        Create a screenshot-ready “Unit Economics” sheet that shows a
        waterfall (price ➜ contribution) for each channel plus a summary
        table.  This is purely an investor view – it does NOT drive the
        model.
        """
        ws = self.workbook.get_worksheet_by_name("Unit Economics")

        # -------- Formatting -------- #
        ue_title  = self.workbook.add_format({'bold': True, 'font_size': 20,
                                              'align': 'center'})
        ue_hdr    = self.workbook.add_format({'bold': True, 'font_size': 16,
                                              'bg_color': '#E2EFDA',
                                              'border': 1, 'align': 'center'})
        ue_lbl    = self.workbook.add_format({'font_size': 14,
                                              'border': 1, 'align': 'left'})
        ue_val    = self.workbook.add_format({'font_size': 14, 'border': 1,
                                              'align': 'right',
                                              'num_format': '$0.00'})
        ue_pos    = self.workbook.add_format({'font_size': 14, 'border': 1,
                                              'align': 'right',
                                              'num_format': '$0.00',
                                              'font_color': 'green'})
        ue_neg    = self.workbook.add_format({'font_size': 14, 'border': 1,
                                              'align': 'right',
                                              'num_format': '$0.00',
                                              'font_color': 'red'})

        ws.set_column('A:A', 3)
        ws.set_column('B:D', 18)
        ws.set_column('E:E', 3)
        ws.set_column('F:H', 18)
        ws.set_column('I:I', 3)
        ws.set_column('J:L', 18)
        ws.set_zoom(125)

        # Title
        ws.merge_range('B2:L2', 'Unit Economics – Profit per Bottle by Channel', ue_title)

        # Helper to write one channel block and return starting column index
        def write_channel(col_offset, channel_name, price_cell, volume_pct):
            """
            col_offset  : 0-based offset (0 => column B)
            price_cell  : literal price (e.g. 80)
            volume_pct  : 0-1
            """
            start_col = 1 + col_offset*4
            c = lambda idx: xlsxwriter.utility.xl_col_to_name(start_col+idx)

            ws.merge_range(4, start_col, 4, start_col+2, channel_name, ue_hdr)

            # Row indices
            row_price = 5
            labels = ['Starting Price', '- COGS', '- Alloc OpEx', 'Contribution']
            for i, lbl in enumerate(labels):
                r = row_price + i
                ws.write(r, start_col, lbl, ue_lbl)

            # Values
            ws.write(row_price,     start_col+1, price_cell, ue_pos)        # price positive
            ws.write(row_price+1,   start_col+1, -6.16,       ue_neg)        # COGS negative

            # Allocated OpEx per bottle.
            # = (Base_Salaries + Rent_per_Month*12 + Insurance_Annual) / Year_1_Bottles_Sold
            ws.write_formula(row_price+2, start_col+1,
                             '=-(Base_Salaries + Rent_per_Month*12 + Insurance_Annual)/Year_1_Bottles_Sold',
                             ue_neg)

            # Contribution (formula)
            ws.write_formula(row_price+3, start_col+1,
                             f'={c(1)}{row_price+1}+{c(1)}{row_price+2}+{c(1)}{row_price}',
                             ue_pos)

            # Store contribution cell address for summary
            contr_addr = f'{c(1)}{row_price+3}'
            return contr_addr, c

        # --- Write three blocks --- #
        tr_contr, tr_c = write_channel(0, 'Tasting Room', 80, 0.18)
        club_contr, club_c = write_channel(1, 'Club', 90, 0.14)
        wh_contr, wh_c = write_channel(2, 'Wholesale', 24, 0.68)

        # --- Column charts (one per channel) -------------------------------- #
        def add_column_chart(anchor_cell: str, start_col: int, row_start: int = 5):
            """
            Build a simple column chart that visually mimics a waterfall:
            positive price bar, two negative cost bars, and resulting
            contribution bar.
            """
            chart = self.workbook.add_chart({'type': 'column'})
            chart.add_series({
                'name':       'Unit Economics',
                'categories': ['Unit Economics', row_start,     start_col,
                                               row_start + 3, start_col],
                'values':     ['Unit Economics', row_start,     start_col + 1,
                                               row_start + 3, start_col + 1],
                'invert_if_negative': True,
                'data_labels': {'value': True, 'num_format': '$0'},
            })
            # Hide axes for cleaner “screenshot-ready” look
            chart.set_x_axis({'visible': False})
            chart.set_y_axis({'visible': False})
            chart.set_size({'width': 240, 'height': 260})
            ws.insert_chart(anchor_cell, chart)

        # start_col returned from write_channel already accounts for spacing
        add_column_chart('B10', 1)   # tasting room block starts in column B (idx 1)
        add_column_chart('F10', 5)   # club block starts in column F  (idx 5)
        add_column_chart('J10', 9)   # wholesale block starts in column J (idx 9)

        # --- Summary Table --- #
        summary_row = 29
        ws.merge_range(summary_row, 1, summary_row, 3, 'Summary (Weighted Avg)', ue_hdr)
        ws.write(summary_row+1, 1, 'Weighted Avg Price', ue_lbl)
        ws.write(summary_row+2, 1, 'Weighted Contribution', ue_lbl)
        ws.write(summary_row+3, 1, 'Contribution Margin %', ue_lbl)

        # helper weights
        ws.write_formula(summary_row+1, 2,
                         f"=80*0.18+90*0.14+24*0.68",
                         ue_val)
        ws.write_formula(summary_row+2, 2,
                         f"=({tr_contr})*0.18+({club_contr})*0.14+({wh_contr})*0.68",
                         ue_val)
        ws.write_formula(summary_row+3, 2,
                         f"={xlsxwriter.utility.xl_col_to_name(2)}{summary_row+2}/"
                         f"{xlsxwriter.utility.xl_col_to_name(2)}{summary_row+1}",
                         self.workbook.add_format({'font_size': 14, 'num_format': '0.0%', 'border':1, 'align':'right'}))

        # aesthetic blank columns for screenshot
        for col in range(1, 12):
            ws.set_row(4, 24)  # enlarge header row

if __name__ == '__main__':
    model = DistilleryFinancialModel()
    model.create_workbook()
