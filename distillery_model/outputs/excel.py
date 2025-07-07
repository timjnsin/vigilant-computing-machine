# distillery_model/outputs/excel.py

import pandas as pd
import numpy as np  # Needed for np.ceil in financial aggregations
import xlsxwriter

class ExcelReport:
    """
    Creates a professional, board-ready Excel report from the calculated financial model data.
    This class uses the xlsxwriter engine for advanced formatting and charting capabilities.
    """

    def __init__(self, workbook, results: dict, scenario_data: dict, constants: dict):
        """
        Initializes the report generator.

        Args:
            workbook: An xlsxwriter workbook object.
            results (dict): The dictionary of results from DistilleryModel.run_model().
            scenario_data (dict): The specific scenario assumptions used.
            constants (dict): The constant assumptions used.
        """
        self.workbook = workbook
        self.results = results
        self.scenario_data = scenario_data
        self.constants = constants
        self.scenario_name = self.results.get('scenario_name', 'Default')
        self._define_formats()

    def _define_formats(self):
        """Defines all cell formats for the workbook for consistency and style."""
        # --- Base Formats ---
        self.formats = {
            'bold': self.workbook.add_format({'bold': True}),
            'percent': self.workbook.add_format({'num_format': '0.0%'}),
            'currency_0dp': self.workbook.add_format({'num_format': '$#,##0'}),
            'currency_2dp': self.workbook.add_format({'num_format': '$#,##0.00'}),
            'integer': self.workbook.add_format({'num_format': '#,##0'}),
            'date': self.workbook.add_format({'num_format': 'mmm yyyy'}),
        }

        # --- Header and Title Formats ---
        self.formats['title'] = self.workbook.add_format({
            'bold': True, 'font_size': 18, 'font_color': '#FFFFFF',
            'bg_color': '#1F497D', 'align': 'center', 'valign': 'vcenter'
        })
        self.formats['subtitle'] = self.workbook.add_format({
            'bold': True, 'font_size': 12, 'bg_color': '#4F81BD',
            'font_color': '#FFFFFF', 'bottom': 1
        })
        self.formats['kpi_title'] = self.workbook.add_format({
            'bold': True, 'font_size': 10, 'align': 'center', 'bg_color': '#F2F2F2'
        })
        self.formats['kpi_value'] = self.workbook.add_format({
            'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter',
            'num_format': '$#,##0,' # Format as thousands
        })

        # --- Data and Table Formats ---
        self.formats['row_header'] = self.workbook.add_format({'bold': True, 'bg_color': '#F2F2F2'})
        self.formats['total_row'] = self.workbook.add_format({
            'bold': True, 'bg_color': '#DCE6F1', 'top': 1, 'num_format': '$#,##0'
        })
        self.formats['negative_red'] = self.workbook.add_format({
            'font_color': '#9C0006', 'bg_color': '#FFC7CE', 'num_format': '$#,##0'
        })

    def generate_report(self):
        """Orchestrates the creation of all worksheets in the report."""
        self._create_dashboard_sheet()
        self._create_financials_sheet()
        self. _create_cap_table_sheet()
        self._create_assumptions_sheet()

    def _create_dashboard_sheet(self):
        """Creates the main dashboard with KPIs and charts."""
        ws = self.workbook.add_worksheet('Dashboard')
        ws.hide_gridlines(2)
        ws.set_column('A:A', 2)
        ws.set_column('B:D', 20)
        ws.set_column('E:E', 2)
        ws.set_column('F:H', 20)

        # --- Title ---
        ws.merge_range('B2:H3', f'The Brogue Distillery Financial Summary: {self.scenario_name}', self.formats['title'])

        # --- KPIs ---
        pnl_summary = self.results['pnl'].sum()
        cash_flow_summary = self.results['cash_flow']
        cap_table = self.results['cap_table']

        kpis = {
            'B5': ('5-Year Revenue', pnl_summary['Revenue'], self.formats['kpi_value']),
            'C5': ('5-Year EBITDA', pnl_summary['EBITDA'], self.formats['kpi_value']),
            'D5': ('Peak Funding Need', -cash_flow_summary['Ending Cash'].min() if cash_flow_summary['Ending Cash'].min() < 0 else 0, self.formats['kpi_value']),
            'F5': ('Founder Ownership', cap_table['Founder & Early Investors']['Ownership Pct'], self.workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter', 'num_format': '0.0%'})),
            'G5': ('SAFE Ownership', cap_table['SAFE Investors']['Ownership Pct'], self.workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter', 'num_format': '0.0%'})),
            'H5': ('Series A Ownership', cap_table['Series A Investors']['Ownership Pct'], self.workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter', 'num_format': '0.0%'})),
        }

        for cell, (title, value, fmt) in kpis.items():
            ws.merge_range(f'{cell}:{cell[0]}{int(cell[1])+1}', '', self.formats['kpi_title'])
            ws.write(f'{cell[0]}{int(cell[1])}', title, self.formats['kpi_title'])
            ws.write(f'{cell[0]}{int(cell[1])+1}', value, fmt)

        # --- Charts ---
        # Revenue & EBITDA Chart
        chart1 = self.workbook.add_chart({'type': 'column'})
        chart1.set_title({'name': 'Annual Revenue & EBITDA'})
        annual_pnl = self.results['pnl'].groupby(self.results['pnl'].index // 12).sum()
        num_years = len(annual_pnl)

        chart1.add_series({
            'name': 'Revenue',
            'categories': ['Financials', 1, 1, 1, num_years],
            'values': ['Financials', 2, 1, 2, num_years],
            'fill': {'color': '#4F81BD'},
        })
        chart1.add_series({
            'name': 'EBITDA',
            'categories': ['Financials', 1, 1, 1, num_years],
            'values': ['Financials', 6, 1, 6, num_years],
            'fill': {'color': '#C0504D'},
        })
        chart1.set_size({'width': 480, 'height': 288})
        ws.insert_chart('B9', chart1)

        # Cash Balance Chart
        chart2 = self.workbook.add_chart({'type': 'line'})
        chart2.set_title({'name': 'Cash Balance Over Time'})
        chart2.get_legend().set_position('none')
        chart2.add_series({
            'name': 'Ending Cash',
            'categories': ['Financials', 1, 1, 1, num_years], # Using annual for simplicity
            'values': ['Financials', 21, 1, 21, num_years],
            'line': {'color': '#1F497D', 'width': 2.25},
        })
        chart2.set_size({'width': 480, 'height': 288})
        ws.insert_chart('F9', chart2)

    def _create_financials_sheet(self):
        """Creates the detailed annual P&L and Cash Flow sheet."""
        ws = self.workbook.add_worksheet('Financials')
        
        # Aggregate monthly data to annual for summary view
        annual_pnl = self.results['pnl'].groupby(np.ceil(self.results['pnl'].index / 12)).sum()
        annual_cf = self.results['cash_flow'].groupby(np.ceil(self.results['cash_flow'].index / 12)).sum()
        annual_cf['Ending Cash'] = self.results['cash_flow']['Ending Cash'].groupby(np.ceil(self.results['cash_flow'].index / 12)).last() # Take last cash balance of year

        # Write headers
        headers = ['Metric'] + [f'Year {i}' for i in range(1, len(annual_pnl) + 1)]
        ws.write_row('A1', headers, self.formats['subtitle'])

        # Write P&L Data
        pnl_data = {
            'Revenue': annual_pnl['Revenue'], 'COGS': annual_pnl['COGS'], 'Gross Profit': annual_pnl['Gross Profit'],
            'Operating Expenses': annual_pnl['OpEx'], 'EBITDA': annual_pnl['EBITDA'], 'Depreciation': annual_pnl['Depreciation'],
            'EBIT': annual_pnl['EBIT'], 'Interest Expense': annual_pnl['Interest'], 'EBT': annual_pnl['EBT'],
            'Taxes': annual_pnl['Taxes'], 'Net Income': annual_pnl['Net Income']
        }
        row = 1
        for label, data_series in pnl_data.items():
            ws.write(row, 0, label, self.formats['row_header'])
            ws.write_row(row, 1, data_series, self.formats['currency_0dp'])
            row += 1
        
        # Write Cash Flow Data
        ws.write(row, 0, 'CASH FLOW', self.formats['subtitle'])
        row += 1
        cf_data = {
            'Net Income': annual_pnl['Net Income'], 'D&A': -annual_pnl['Depreciation'], 'CFO': annual_cf['CFO'],
            'Capital Expenditures': annual_cf['CapEx'], 'FCF': annual_cf['FCF'],
            'Revolver Activity': annual_cf['Revolver Draw/(Repay)'], 'Ending Cash Balance': annual_cf['Ending Cash']
        }
        for label, data_series in cf_data.items():
            ws.write(row, 0, label, self.formats['row_header'])
            ws.write_row(row, 1, data_series, self.formats['currency_0dp'])
            row += 1

        # Apply conditional formatting for negative numbers
        ws.conditional_format(f'B2:F{row}', {'type': 'cell', 'criteria': '<', 'value': 0, 'format': self.formats['negative_red']})
        ws.set_column('A:A', 25)
        ws.set_column('B:F', 15)

    def _create_cap_table_sheet(self):
        """Creates a clean presentation of the cap table calculations."""
        ws = self.workbook.add_worksheet('Cap Table')
        ws.set_column('A:A', 35)
        ws.set_column('B:C', 20)
        
        cap_table = self.results['cap_table']
        row = 0

        # Calculation Section
        ws.write(row, 0, 'SAFE Conversion & Series A Pricing', self.formats['subtitle'])
        row += 1
        calc_data = [
            ('Series A Pre-Money Valuation', cap_table['Series A Pre-Money Valuation'], self.formats['currency_0dp']),
            ('Effective SAFE Conversion Price', cap_table['Effective SAFE Conversion Price'], self.formats['currency_2dp']),
            ('Series A Price per Share', cap_table['Series A Price per Share'], self.formats['currency_2dp']),
        ]
        for label, value, fmt in calc_data:
            ws.write(row, 0, label)
            ws.write(row, 1, value, fmt)
            row += 1
        
        row += 1
        # Ownership Section
        ws.write(row, 0, 'Post-Series A Ownership', self.formats['subtitle'])
        ws.write(row, 1, 'Shares', self.formats['bold'])
        ws.write(row, 2, 'Ownership %', self.formats['bold'])
        row += 1

        ownership_data = [
            ('Founder & Early Investors', cap_table['Founder & Early Investors']),
            ('SAFE Investors', cap_table['SAFE Investors']),
            ('Series A Investors', cap_table['Series A Investors']),
        ]
        for label, data in ownership_data:
            ws.write(row, 0, label)
            ws.write(row, 1, data['Shares'], self.formats['integer'])
            ws.write(row, 2, data['Ownership Pct'], self.formats['percent'])
            row += 1
        
        # Total Row
        ws.write(row, 0, 'Total Post-Money', self.formats['total_row'])
        ws.write(row, 1, cap_table['Total Post-Money']['Shares'], self.formats['total_row'])
        ws.write(row, 2, cap_table['Total Post-Money']['Ownership Pct'], self.workbook.add_format({'bold': True, 'top': 1, 'num_format': '0.0%'}))


    def _create_assumptions_sheet(self):
        """Creates a sheet that dumps the input assumptions for auditability."""
        ws = self.workbook.add_worksheet('Assumptions')
        ws.set_column('A:A', 35)
        ws.set_column('B:B', 25)
        row = 0

        ws.write(row, 0, f"Scenario: {self.scenario_name}", self.formats['subtitle'])
        row += 2

        for key, value in self.scenario_data.items():
            if isinstance(value, dict):
                ws.write(row, 0, key.replace('_', ' ').title(), self.formats['bold'])
                row += 1
                for sub_key, sub_value in value.items():
                    ws.write(row, 0, sub_key.replace('_', ' ').title())
                    ws.write(row, 1, sub_value)
                    row += 1
                row += 1

def create_excel_report(results: dict, scenario_data: dict, constants: dict, filename: str):
    """
    Public function to generate and save the complete Excel report.

    Args:
        results (dict): The results from the core model calculation.
        scenario_data (dict): The specific scenario assumptions used.
        constants (dict): The constant assumptions used.
        filename (str): The path and name for the output Excel file.
    """
    with xlsxwriter.Workbook(filename) as workbook:
        report = ExcelReport(workbook, results, scenario_data, constants)
        report.generate_report()
    print(f"Successfully created Excel report: {filename}")
