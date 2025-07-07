# distillery_model/core/model.py

import pandas as pd
import numpy as np
import numpy_financial as npf

class DistilleryModel:
    """
    The core financial calculation engine for the distillery model.
    This class takes structured assumptions and produces a full set of financial statements
    and key metrics, completely decoupled from any presentation layer.
    """
    def __init__(self, scenario_data: dict, constants: dict):
        """
        Initializes the model with a specific scenario and constant assumptions.

        Args:
            scenario_data (dict): A dictionary containing all assumptions for a single scenario.
            constants (dict): A dictionary of assumptions that are fixed across all scenarios.
        """
        self.scenario = scenario_data
        self.const = constants
        self.months = self.const['general']['forecast_months']
        
        # Initialize the main DataFrame for time-series calculations
        self.df = pd.DataFrame(index=range(1, self.months + 1))

    def run_model(self) -> dict:
        """
        Executes all calculation steps in the correct order to generate the financial model.

        Returns:
            dict: A dictionary containing the resulting DataFrames for P&L, Cash Flow,
                  Balance Sheet, and the calculated Cap Table.
        """
        # Orchestrate the build process
        self._calculate_schedule()
        self._calculate_volume_and_revenue()
        self._calculate_cogs()
        self._calculate_opex()
        self._calculate_capex_and_depreciation()
        
        # Build the integrated financial statements
        self._build_pnl_and_cash_flow()
        
        # Perform non-time-series calculations
        cap_table_results = self._calculate_cap_table()

        # Prepare final output
        results = {
            "pnl": self.df[['Revenue', 'COGS', 'Gross Profit', 'OpEx', 'EBITDA', 'Depreciation', 'EBIT', 'Interest', 'EBT', 'Taxes', 'Net Income']],
            "cash_flow": self.df[['Net Income', 'Depreciation', 'CFO', 'CapEx', 'CFI', 'FCF', 'Revolver Draw/(Repay)', 'CFF', 'Net Cash Flow', 'Beginning Cash', 'Ending Cash']],
            "metrics": self.df[['Runway (Months)']],
            "cap_table": cap_table_results,
            "scenario_name": self.scenario['name']
        }
        return results

    def _calculate_schedule(self):
        """Sets up the basic time structure (month number, year) for the model."""
        self.df['Year'] = np.ceil(self.df.index / 12).astype(int)
        self.df['Month of Year'] = self.df.index % 12
        self.df.loc[self.df['Month of Year'] == 0, 'Month of Year'] = 12

    def _calculate_volume_and_revenue(self):
        """Models bottle sales, channel mix, and pricing over time."""
        # Volume Calculation
        y1_vol = self.scenario['volume']['y1_bottle_target']
        y2_growth = self.scenario['volume']['y2_growth_pct']
        y3_plus_growth = self.scenario['volume']['y3_onwards_growth_pct']
        
        annual_volumes = [y1_vol]
        annual_volumes.append(annual_volumes[0] * (1 + y2_growth))
        for _ in range(3, 6): # Years 3, 4, 5
            annual_volumes.append(annual_volumes[-1] * (1 + y3_plus_growth))
            
        self.df['Annual Volume'] = self.df['Year'].map(lambda y: annual_volumes[y-1])
        self.df['Monthly Volume'] = self.df['Annual Volume'] / 12

        # Pricing with annual escalator
        price_increase = self.scenario['pricing']['annual_price_increase_pct']
        for channel in ['tasting_room', 'club', 'wholesale_fob']:
            base_price = self.scenario['pricing'][f'{channel}_per_bottle']
            self.df[f'{channel}_price'] = base_price * (1 + price_increase) ** (self.df['Year'] - 1)

        # Revenue Calculation
        for channel in ['tasting_room', 'club', 'wholesale']:
            mix_pct = self.scenario['channel_mix'][f'{channel}_pct']
            price_col = 'wholesale_fob_price' if channel == 'wholesale' else f'{channel}_price'
            self.df[f'{channel}_revenue'] = self.df['Monthly Volume'] * mix_pct * self.df[price_col]
            
        self.df['Revenue'] = self.df[['tasting_room_revenue', 'club_revenue', 'wholesale_revenue']].sum(axis=1)

    def _calculate_cogs(self):
        """Calculates the cost of goods sold based on volume."""
        cogs_per_bottle = sum(self.scenario['cogs_per_bottle'].values())
        self.df['COGS'] = -self.df['Monthly Volume'] * cogs_per_bottle

    def _calculate_opex(self):
        """Calculates operating expenses, including detailed payroll and variable costs."""
        # Headcount-driven payroll
        payroll_df = pd.DataFrame(self.const['headcount_plan'], columns=['Position', 'Salary', 'Start Month'])
        monthly_payroll = 0
        for _, row in payroll_df.iterrows():
            monthly_payroll += (row['Salary'] / 12) * (self.df.index >= row['Start Month'])
        
        benefits_multiplier = 1 + self.const['opex']['payroll_benefits_tax_pct']
        payroll_growth = self.const['opex']['payroll_annual_growth_pct']
        self.df['Payroll'] = -monthly_payroll * benefits_multiplier * (1 + payroll_growth) ** (self.df['Year'] - 1)

        # Other OpEx
        rent_growth = self.const['opex']['rent_annual_escalator_pct']
        self.df['Rent'] = -(self.const['opex']['rent_y1'] / 12) * (1 + rent_growth) ** (self.df['Year'] - 1)
        
        utils_growth = self.const['opex']['utilities_insurance_growth_pct']
        self.df['Utilities & Insurance'] = -(self.const['opex']['utilities_insurance_y1'] / 12) * (1 + utils_growth) ** (self.df['Year'] - 1)
        
        self.df['Marketing'] = -self.df['Revenue'] * self.scenario['opex']['marketing_pct_of_revenue']
        self.df['G&A'] = -self.df['Revenue'] * self.scenario['opex']['g_and_a_pct_of_revenue']
        
        self.df['OpEx'] = self.df[['Payroll', 'Rent', 'Utilities & Insurance', 'Marketing', 'G&A']].sum(axis=1)

    def _calculate_capex_and_depreciation(self):
        """Handles capital expenditures and the resulting depreciation schedule."""
        capex_month = self.const['capex']['initial_spend_month']
        capex_amount = self.const['capex']['initial_spend_base'] * (1 + self.scenario['capex']['initial_spend_overrun_pct'])
        
        self.df['CapEx'] = 0
        self.df.loc[capex_month, 'CapEx'] = -capex_amount
        
        depr_years = self.const['capex']['equipment_depreciation_years']
        monthly_depr = capex_amount / (depr_years * 12)
        
        self.df['Depreciation'] = 0
        self.df.loc[self.df.index >= capex_month, 'Depreciation'] = -monthly_depr
        
    def _build_pnl_and_cash_flow(self):
        """Constructs the integrated P&L and Cash Flow statements."""
        # P&L Items
        self.df['Gross Profit'] = self.df['Revenue'] + self.df['COGS']
        self.df['EBITDA'] = self.df['Gross Profit'] + self.df['OpEx']
        self.df['EBIT'] = self.df['EBITDA'] + self.df['Depreciation']

        # Cash Flow & Financing Loop
        cash = np.zeros(self.months + 1)
        revolver = np.zeros(self.months + 1)
        cash[0] = self.const['financing']['initial_cash_position'] + self.const['financing']['safe_round_investment']
        
        interest_paid = np.zeros(self.months)
        revolver_draw_repay = np.zeros(self.months)
        
        for m in range(1, self.months + 1):
            interest = -revolver[m-1] * self.const['financing']['revolver_interest_rate'] / 12
            interest_paid[m-1] = interest

            ebt = self.df.loc[m, 'EBIT'] + interest
            
            tax_rate = self.const['tax']['federal_income_tax_rate'] + self.const['tax']['oregon_state_income_tax_rate']
            taxes = -ebt * tax_rate if ebt > 0 else 0
            
            net_income = ebt + taxes
            
            # Update P&L in DataFrame
            self.df.loc[m, 'Interest'] = interest
            self.df.loc[m, 'EBT'] = ebt
            self.df.loc[m, 'Taxes'] = taxes
            self.df.loc[m, 'Net Income'] = net_income

            # Cash Flow Calculations
            cfo = net_income - self.df.loc[m, 'Depreciation'] # Add back non-cash depreciation
            cfi = self.df.loc[m, 'CapEx']
            
            cash_before_financing = cash[m-1] + cfo + cfi
            
            # Revolver Logic
            if cash_before_financing < 0:
                draw = min(-cash_before_financing, self.const['financing']['revolver_limit'] - revolver[m-1])
                revolver_draw_repay[m-1] = draw
            else:
                repayment = min(cash_before_financing, revolver[m-1])
                revolver_draw_repay[m-1] = -repayment
            
            revolver[m] = revolver[m-1] + revolver_draw_repay[m-1]
            cash[m] = cash_before_financing + revolver_draw_repay[m-1]

        # Store results back into the main DataFrame
        self.df['Beginning Cash'] = cash[:-1]
        self.df['Ending Cash'] = cash[1:]
        self.df['Revolver Balance'] = revolver[1:]
        self.df['Revolver Draw/(Repay)'] = revolver_draw_repay
        
        self.df['CFO'] = self.df['Net Income'] - self.df['Depreciation']
        self.df['CFI'] = self.df['CapEx']
        self.df['CFF'] = self.df['Revolver Draw/(Repay)']
        self.df['FCF'] = self.df['CFO'] + self.df['CFI']
        self.df['Net Cash Flow'] = self.df['FCF'] + self.df['CFF']
        
        # Runway Calculation
        monthly_burn = self.df['Net Cash Flow'].rolling(window=6, min_periods=1).mean()
        self.df['Runway (Months)'] = np.where(monthly_burn < 0, -self.df['Ending Cash'] / monthly_burn, 999)

    def _calculate_cap_table(self) -> dict:
        """Performs SAFE conversion and calculates equity dilution."""
        pre_money_shares = self.const['financing']['founder_shares'] + self.const['financing']['early_investor_shares']
        series_a_valuation = self.scenario['financing']['series_a_pre_money_valuation']
        
        series_a_price = series_a_valuation / pre_money_shares
        
        # Determine effective SAFE conversion price
        price_from_cap = self.scenario['financing']['safe_valuation_cap'] / pre_money_shares
        price_from_discount = series_a_price * (1 - self.scenario['financing']['safe_discount'])
        effective_safe_price = min(price_from_cap, price_from_discount)
        
        # Calculate shares issued
        safe_investment = self.const['financing']['safe_round_investment']
        safe_shares = safe_investment / effective_safe_price
        
        series_a_investment = self.const['financing']['series_a_investment']
        series_a_shares = series_a_investment / series_a_price
        
        # Build final cap table
        total_shares = pre_money_shares + safe_shares + series_a_shares
        
        return {
            "Series A Pre-Money Valuation": series_a_valuation,
            "Effective SAFE Conversion Price": effective_safe_price,
            "Series A Price per Share": series_a_price,
            "Founder & Early Investors": {
                "Shares": pre_money_shares,
                "Ownership Pct": pre_money_shares / total_shares
            },
            "SAFE Investors": {
                "Shares": safe_shares,
                "Ownership Pct": safe_shares / total_shares
            },
            "Series A Investors": {
                "Shares": series_a_shares,
                "Ownership Pct": series_a_shares / total_shares
            },
            "Total Post-Money": {
                "Shares": total_shares,
                "Ownership Pct": 1.0
            }
        }
