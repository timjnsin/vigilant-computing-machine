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
            "Cover", "Control Panel", "Unit Economics", "Channel Strategy", "Assumptions", "Revenue Build", "COGS Build", 
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
        # Build the Channel Strategy sheet (prompt #3)
        self.build_channel_strategy_sheet()
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

    # ------------------------------------------------------------------ #
    #  Unit Economics (Investor Sheet)                                   #
    # ------------------------------------------------------------------ #
    def build_unit_economics_sheet(self):
        """
        Create a screenshot-ready "Unit Economics" sheet that shows a
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
            # Hide axes for cleaner "screenshot-ready" look
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

    # ------------------------------------------------------------------ #
    #  Channel Strategy (Investor Sheet)                                 #
    # ------------------------------------------------------------------ #
    def build_channel_strategy_sheet(self):
        """
        Create a screenshot-ready "Channel Strategy" sheet with 4 key visuals:
        1. Volume mix pie chart (18% tasting, 14% club, 68% wholesale)
        2. Revenue mix pie chart (showing how DTC drives revenue despite lower volume)
        3. Margin by channel bar chart (showing 74% tasting, 77% club, 13% wholesale)
        4. Summary insight box with data table
        
        The sheet is formatted for 16:9 slide export with a consistent color scheme:
        - Tasting Room: Blue (#4472C4)
        - Club: Gold (#FFD966) 
        - Wholesale: Gray (#A5A5A5)
        """
        ws = self.workbook.get_worksheet_by_name("Channel Strategy")
        
        # -------- Formatting for 16:9 slide -------- #
        # Set zoom to make the whole sheet fit on a screen
        ws.set_zoom(85)
        
        # Set column widths for proper spacing
        ws.set_column('A:A', 2)   # Left margin
        ws.set_column('B:G', 12)  # Left charts area
        ws.set_column('H:H', 2)   # Middle spacing
        ws.set_column('I:N', 12)  # Right charts area
        ws.set_column('O:O', 2)   # Right margin
        
        # Set row heights for proper spacing
        ws.set_row(0, 20)  # Top margin
        ws.set_row(1, 30)  # Title row
        
        # -------- Color scheme -------- #
        tasting_color = '#4472C4'  # Blue
        club_color = '#FFD966'     # Gold
        wholesale_color = '#A5A5A5'  # Gray
        
        # -------- Formats -------- #
        title_format = self.workbook.add_format({
            'bold': True, 'font_size': 24, 'align': 'center', 'valign': 'vcenter'
        })
        
        subtitle_format = self.workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter',
            'border': 0
        })
        
        header_format = self.workbook.add_format({
            'bold': True, 'font_size': 12, 'align': 'center', 'valign': 'vcenter',
            'border': 1, 'bg_color': '#D9E1F2'
        })
        
        label_format = self.workbook.add_format({
            'font_size': 11, 'align': 'left', 'valign': 'vcenter', 'border': 1
        })
        
        number_format = self.workbook.add_format({
            'font_size': 11, 'align': 'right', 'valign': 'vcenter',
            'border': 1, 'num_format': '#,##0'
        })
        
        currency_format = self.workbook.add_format({
            'font_size': 11, 'align': 'right', 'valign': 'vcenter',
            'border': 1, 'num_format': '$#,##0'
        })
        
        percent_format = self.workbook.add_format({
            'font_size': 11, 'align': 'right', 'valign': 'vcenter',
            'border': 1, 'num_format': '0.0%'
        })
        
        # Bold version of percent format for margin column
        percent_bold_format = self.workbook.add_format({
            'bold': True, 'font_size': 11, 'align': 'right', 'valign': 'vcenter',
            'border': 1, 'num_format': '0.0%'
        })
        
        insight_box_format = self.workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter',
            'border': 1, 'text_wrap': True, 'bg_color': '#E2EFDA'
        })
        
        # -------- Title -------- #
        ws.merge_range('B2:N2', 'The Brogue Distillery - Channel Strategy', title_format)
        
        # -------- Data for charts -------- #
        # Channel volumes
        total_bottles = 50000
        tasting_pct = 0.18
        club_pct = 0.14
        wholesale_pct = 0.68
        
        tasting_bottles = int(total_bottles * tasting_pct)
        club_bottles = int(total_bottles * club_pct)
        wholesale_bottles = int(total_bottles * wholesale_pct)
        
        # Channel prices
        tasting_price = 80
        club_price = 90
        wholesale_price = 24
        
        # Channel revenues
        tasting_revenue = tasting_bottles * tasting_price
        club_revenue = club_bottles * club_price
        wholesale_revenue = wholesale_bottles * wholesale_price
        total_revenue = tasting_revenue + club_revenue + wholesale_revenue
        
        # Channel margins
        tasting_margin = 0.74
        club_margin = 0.77
        wholesale_margin = 0.13
        
        # DTC calculations
        dtc_bottles = tasting_bottles + club_bottles
        dtc_revenue = tasting_revenue + club_revenue
        dtc_volume_pct = dtc_bottles / total_bottles
        dtc_revenue_pct = dtc_revenue / total_revenue
        dtc_profit_pct = 0.84  # As specified in the requirements
        
        # -------- 1. Volume Mix Pie Chart (Top Left) -------- #
        ws.merge_range('B4:G4', 'Volume Mix', subtitle_format)
        
        # Add data table for the pie chart
        ws.write('B5', 'Channel', header_format)
        ws.write('C5', 'Bottles', header_format)
        ws.write('D5', 'Percent', header_format)
        
        ws.write('B6', 'Tasting Room', label_format)
        ws.write('C6', tasting_bottles, number_format)
        ws.write('D6', tasting_pct, percent_format)
        
        ws.write('B7', 'Club', label_format)
        ws.write('C7', club_bottles, number_format)
        ws.write('D7', club_pct, percent_format)
        
        ws.write('B8', 'Wholesale', label_format)
        ws.write('C8', wholesale_bottles, number_format)
        ws.write('D8', wholesale_pct, percent_format)
        
        # Create the pie chart
        volume_chart = self.workbook.add_chart({'type': 'pie'})
        volume_chart.add_series({
            'name': 'Volume Mix',
            'categories': ['Channel Strategy', 5, 1, 7, 1],  # B6:B8
            'values': ['Channel Strategy', 5, 3, 7, 3],      # D6:D8
            'points': [
                {'fill': {'color': tasting_color}},
                {'fill': {'color': club_color}},
                {'fill': {'color': wholesale_color}}
            ],
            'data_labels': {
                'percentage': True,
                'position': 'outside_end',
                'font': {'bold': True, 'size': 12}
            }
        })
        
        # Format the pie chart
        volume_chart.set_title({'name': 'Volume Mix', 'name_font': {'size': 14, 'bold': True}})
        volume_chart.set_style(10)
        volume_chart.set_size({'width': 300, 'height': 250})
        volume_chart.set_legend({'position': 'bottom', 'font': {'size': 11}})
        
        # Insert the chart
        ws.insert_chart('B10', volume_chart)
        
        # -------- 2. Revenue Mix Pie Chart (Top Right) -------- #
        ws.merge_range('I4:N4', 'Revenue Mix', subtitle_format)
        
        # Add data table for the pie chart
        ws.write('I5', 'Channel', header_format)
        ws.write('J5', 'Revenue', header_format)
        ws.write('K5', 'Percent', header_format)
        
        ws.write('I6', 'Tasting Room', label_format)
        ws.write('J6', tasting_revenue, currency_format)
        ws.write('K6', tasting_revenue/total_revenue, percent_format)
        
        ws.write('I7', 'Club', label_format)
        ws.write('J7', club_revenue, currency_format)
        ws.write('K7', club_revenue/total_revenue, percent_format)
        
        ws.write('I8', 'Wholesale', label_format)
        ws.write('J8', wholesale_revenue, currency_format)
        ws.write('K8', wholesale_revenue/total_revenue, percent_format)
        
        # Create the pie chart
        revenue_chart = self.workbook.add_chart({'type': 'pie'})
        revenue_chart.add_series({
            'name': 'Revenue Mix',
            'categories': ['Channel Strategy', 5, 8, 7, 8],  # I6:I8
            'values': ['Channel Strategy', 5, 10, 7, 10],    # K6:K8
            'points': [
                {'fill': {'color': tasting_color}},
                {'fill': {'color': club_color}},
                {'fill': {'color': wholesale_color}}
            ],
            'data_labels': {
                'percentage': True,
                'position': 'outside_end',
                'font': {'bold': True, 'size': 12}
            }
        })
        
        # Format the pie chart
        revenue_chart.set_title({'name': 'Revenue Mix', 'name_font': {'size': 14, 'bold': True}})
        revenue_chart.set_style(10)
        revenue_chart.set_size({'width': 300, 'height': 250})
        revenue_chart.set_legend({'position': 'bottom', 'font': {'size': 11}})
        
        # Insert the chart
        ws.insert_chart('I10', revenue_chart)
        
        # -------- 3. Margin by Channel Bar Chart (Bottom Left) -------- #
        ws.merge_range('B20:G20', 'Margin by Channel', subtitle_format)
        
        # Add data table for the bar chart
        ws.write('B21', 'Channel', header_format)
        ws.write('C21', 'Margin', header_format)
        
        ws.write('B22', 'Tasting Room', label_format)
        ws.write('C22', tasting_margin, percent_format)
        
        ws.write('B23', 'Club', label_format)
        ws.write('C23', club_margin, percent_format)
        
        ws.write('B24', 'Wholesale', label_format)
        ws.write('C24', wholesale_margin, percent_format)
        
        # Create the bar chart
        margin_chart = self.workbook.add_chart({'type': 'column'})
        margin_chart.add_series({
            'name': 'Margin',
            'categories': ['Channel Strategy', 21, 1, 23, 1],  # B22:B24
            'values': ['Channel Strategy', 21, 2, 23, 2],      # C22:C24
            'fill': {'type': 'pattern', 'pattern': 'solid', 'fg_color': '#4472C4'},
            'data_labels': {
                'value': True,
                'num_format': '0%',
                'font': {'bold': True, 'size': 12}
            },
            'points': [
                {'fill': {'color': tasting_color}},
                {'fill': {'color': club_color}},
                {'fill': {'color': wholesale_color}}
            ]
        })
        
        # Format the bar chart
        margin_chart.set_title({'name': 'Margin by Channel', 'name_font': {'size': 14, 'bold': True}})
        margin_chart.set_y_axis({
            'num_format': '0%',
            'major_gridlines': {'visible': True},
            'min': 0,
            'max': 1
        })
        margin_chart.set_size({'width': 300, 'height': 250})
        margin_chart.set_legend({'position': 'none'})
        
        # Insert the chart
        ws.insert_chart('B25', margin_chart)
        
        # -------- 4. Data Table and Insight Box (Bottom Right) -------- #
        ws.merge_range('I20:N20', 'Channel Data', subtitle_format)
        
        # Data table headers
        ws.write('I21', 'Channel', header_format)
        ws.write('J21', 'Bottles', header_format)
        ws.write('K21', 'Price', header_format)
        ws.write('L21', 'Margin', header_format)
        
        # Data table rows
        ws.write('I22', 'Tasting Room', label_format)
        ws.write('J22', tasting_bottles, number_format)
        ws.write('K22', tasting_price, currency_format)
        ws.write('L22', tasting_margin, percent_bold_format)
        
        ws.write('I23', 'Club', label_format)
        ws.write('J23', club_bottles, number_format)
        ws.write('K23', club_price, currency_format)
        ws.write('L23', club_margin, percent_bold_format)
        
        ws.write('I24', 'Wholesale', label_format)
        ws.write('J24', wholesale_bottles, number_format)
        ws.write('K24', wholesale_price, currency_format)
        ws.write('L24', wholesale_margin, percent_bold_format)
        
        ws.write('I25', 'Total', header_format)
        ws.write('J25', total_bottles, number_format)
        ws.write_formula('K25', '=J22*K22+J23*K23+J24*K24', currency_format)
        
        # Add conditional formatting to the margin column
        ws.conditional_format('L22:L24', {
            'type': '3_color_scale',
            'min_color': '#FF5050',  # Red
            'mid_color': '#FFFF99',  # Yellow
            'max_color': '#00B050',  # Green
            'min_type': 'num',
            'mid_type': 'num',
            'max_type': 'num',
            'min_value': 0,
            'mid_value': 0.35,
            'max_value': 0.7
        })
        
        # Insight box
        insight_text = f"DTC channels are {dtc_volume_pct:.0%} of volume but deliver {dtc_revenue_pct:.0%} of revenue and {dtc_profit_pct:.0%} of gross profit"
        ws.merge_range('I27:N30', insight_text, insight_box_format)
        
        # -------- Add navigation and notes -------- #
        # Add a note about the story flow
        story_note = (
            "Story Flow:\n"
            "1. Volume mix shows wholesale dominance\n"
            "2. Revenue mix shows DTC value capture\n"
            "3. Margin chart shows why DTC matters\n"
            "4. Table gives the hard numbers to back it up"
        )
        ws.write_comment('A1', story_note, {'author': 'Model Bot', 'visible': False, 'width': 300, 'height': 120})

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

    # ------------------------------------------------------------------ #
    #  PLACEHOLDER SHEETS  (minimal stubs to restore syntax integrity)   #
    # ------------------------------------------------------------------ #

    def _simple_title(self, sheet_name: str, title: str):
        """Utility to write a big centred title in a sheet."""
        ws = self.workbook.get_worksheet_by_name(sheet_name)
        if ws is None:  # sheet might be removed from self.sheets
            return
        ws.merge_range('B3:M3', title, self.formats["title"])

    def build_working_capital_sheet(self):
        """Minimal stub – replace later with real WC logic."""
        self._simple_title("Working Capital", "Working-Capital Placeholder")

    def build_income_statement(self):
        """Minimal stub – replace later with real P&L logic."""
        self._simple_title("Income Statement", "Income-Statement Placeholder")

    def build_cash_flow_statement(self):
        """Minimal stub – replace later with real CFS logic."""
        self._simple_title("Cash Flow Statement", "Cash-Flow Placeholder")

    def build_balance_sheet(self):
        """Minimal stub – replace later with real BS logic."""
        self._simple_title("Balance Sheet", "Balance-Sheet Placeholder")

    def build_cap_table(self):
        """Minimal stub – replace later with real Cap-Table logic."""
        self._simple_title("Cap Table", "Cap-Table Placeholder")

    def build_returns_analysis(self):
        """Minimal stub – replace later with IRR/MOIC logic."""
        self._simple_title("Returns Analysis", "Returns-Analysis Placeholder")
        # define dummy named ranges to avoid downstream errors
        self.named_ranges.setdefault("Project_IRR", "'Returns Analysis'!$B$5")
        self.named_ranges.setdefault("Project_MOIC", "'Returns Analysis'!$B$6")

    def build_sensitivity_tables(self):
        """Minimal stub – add blank area for future sensitivity tables."""
        # Use a different row from build_returns_analysis to avoid merge overlap.
        ws = self.workbook.get_worksheet_by_name("Returns Analysis")
        if ws:
            # Place the placeholder header lower (row 5) to prevent clash with
            # the title already written by `build_returns_analysis` at row 3.
            ws.merge_range('B5:M5',
                           "Sensitivity-Tables Placeholder",
                           self.formats["title"])

    def build_dashboard(self):
        """Minimal stub dashboard."""
        self._simple_title("Dashboard", "Dashboard Placeholder")

    def build_checks_sheet(self):
        """Minimal stub checks sheet."""
        self._simple_title("Checks", "Model-Checks Placeholder")

    def add_navigation_buttons(self):
        """Insert ‘Go to Cover’ button on each sheet (quick nav)."""
        for sheet_name in self.sheets:
            ws = self.workbook.get_worksheet_by_name(sheet_name)
            if ws and sheet_name != "Cover":
                ws.write_url(
                    "A1",
                    "internal:Cover!A1",
                    string="Cover",
                    cell_format=self.formats["button"],
                )


# ---------------------------------------------------------------------- #
#  Main entry-point (for standalone testing)                            #
# ---------------------------------------------------------------------- #

if __name__ == "__main__":
    # Generate a quick test workbook to verify no syntax / runtime errors.
    model = DistilleryFinancialModel("distillery_financial_model_test.xlsx")
    model.create_workbook()
    print("Test workbook created.")
