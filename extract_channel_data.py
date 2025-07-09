#!/usr/bin/env python3
"""
extract_channel_data.py

This script extracts channel data from the Brogue Distillery financial model
to analyze and validate the Channel Strategy sheet calculations.
"""

import sys
import pandas as pd
from distillery_model import DistilleryFinancialModel

def extract_channel_data():
    """Extract and analyze channel data from the distillery model."""
    # Initialize the model
    model = DistilleryFinancialModel()
    
    # Get Base Case assumptions
    base_case = model.assumptions['Base Case']
    
    # Basic model parameters
    total_bottles = base_case['Revenue']['Year 1 Bottles Sold']
    wholesale_pct = base_case['Revenue']['Wholesale % of Sales']
    avg_price = base_case['Revenue']['Avg Price per Bottle']
    
    # Channel percentages from Unit Economics sheet
    tasting_pct = 0.18
    club_pct = 0.14
    wholesale_pct_check = 0.68
    
    # Channel pricing from Unit Economics sheet
    tasting_price = 80
    club_price = 90
    wholesale_price = 24
    
    # COGS per bottle (simplified)
    cogs_per_bottle = 6.16
    
    # Calculate allocated OpEx per bottle
    # = (Base_Salaries + Rent_per_Month*12 + Insurance_Annual) / Year_1_Bottles_Sold
    base_salaries = base_case['OpEx']['Base Salaries']
    rent_per_month = base_case['OpEx']['Rent per Month']
    insurance_annual = base_case['OpEx']['Insurance Annual']
    opex_per_bottle = (base_salaries + rent_per_month*12 + insurance_annual) / total_bottles
    
    # Calculate channel volumes
    tasting_bottles = int(total_bottles * tasting_pct)
    club_bottles = int(total_bottles * club_pct)
    wholesale_bottles = int(total_bottles * wholesale_pct_check)
    dtc_bottles = tasting_bottles + club_bottles
    
    # Calculate channel revenues
    tasting_revenue = tasting_bottles * tasting_price
    club_revenue = club_bottles * club_price
    wholesale_revenue = wholesale_bottles * wholesale_price
    total_revenue = tasting_revenue + club_revenue + wholesale_revenue
    dtc_revenue = tasting_revenue + club_revenue
    
    # Calculate channel margins
    tasting_margin = (tasting_price - cogs_per_bottle - opex_per_bottle) / tasting_price
    club_margin = (club_price - cogs_per_bottle - opex_per_bottle) / club_price
    wholesale_margin = (wholesale_price - cogs_per_bottle - opex_per_bottle) / wholesale_price
    
    # Calculate channel gross profits
    tasting_profit = tasting_bottles * (tasting_price - cogs_per_bottle)
    club_profit = club_bottles * (club_price - cogs_per_bottle)
    wholesale_profit = wholesale_bottles * (wholesale_price - cogs_per_bottle)
    total_profit = tasting_profit + club_profit + wholesale_profit
    dtc_profit = tasting_profit + club_profit
    
    # Calculate percentages for insights
    dtc_volume_pct = dtc_bottles / total_bottles
    dtc_revenue_pct = dtc_revenue / total_revenue
    dtc_profit_pct = dtc_profit / total_profit
    
    # Create a DataFrame for the data table
    data = {
        'Channel': ['Tasting Room', 'Club', 'Wholesale', 'Total'],
        'Bottles': [tasting_bottles, club_bottles, wholesale_bottles, total_bottles],
        'Price': [tasting_price, club_price, wholesale_price, avg_price],
        'Margin': [tasting_margin, club_margin, wholesale_margin, None]
    }
    df = pd.DataFrame(data)
    
    # Print results
    print("\n===== CHANNEL STRATEGY DATA ANALYSIS =====\n")
    
    print("VOLUME MIX:")
    print(f"Tasting Room: {tasting_bottles:,} bottles ({tasting_pct:.1%})")
    print(f"Club: {club_bottles:,} bottles ({club_pct:.1%})")
    print(f"Wholesale: {wholesale_bottles:,} bottles ({wholesale_pct_check:.1%})")
    print(f"Total: {total_bottles:,} bottles")
    
    print("\nREVENUE MIX:")
    print(f"Tasting Room: ${tasting_revenue:,.0f} ({tasting_revenue/total_revenue:.1%})")
    print(f"Club: ${club_revenue:,.0f} ({club_revenue/total_revenue:.1%})")
    print(f"Wholesale: ${wholesale_revenue:,.0f} ({wholesale_revenue/total_revenue:.1%})")
    print(f"Total: ${total_revenue:,.0f}")
    
    print("\nMARGIN BY CHANNEL:")
    print(f"Tasting Room: {tasting_margin:.1%}")
    print(f"Club: {club_margin:.1%}")
    print(f"Wholesale: {wholesale_margin:.1%}")
    
    print("\nGROSS PROFIT BY CHANNEL:")
    print(f"Tasting Room: ${tasting_profit:,.0f} ({tasting_profit/total_profit:.1%})")
    print(f"Club: ${club_profit:,.0f} ({club_profit/total_profit:.1%})")
    print(f"Wholesale: ${wholesale_profit:,.0f} ({wholesale_profit/total_profit:.1%})")
    print(f"Total: ${total_profit:,.0f}")
    
    print("\nDTC SUMMARY INSIGHTS:")
    print(f"DTC channels are {dtc_volume_pct:.1%} of volume but deliver {dtc_revenue_pct:.1%} of revenue and {dtc_profit_pct:.1%} of gross profit")
    
    print("\nDATA TABLE:")
    print(df)
    
    return {
        'volume_mix': {
            'tasting': tasting_pct,
            'club': club_pct,
            'wholesale': wholesale_pct_check
        },
        'revenue_mix': {
            'tasting': tasting_revenue/total_revenue,
            'club': club_revenue/total_revenue,
            'wholesale': wholesale_revenue/total_revenue
        },
        'margins': {
            'tasting': tasting_margin,
            'club': club_margin,
            'wholesale': wholesale_margin
        },
        'dtc_insights': {
            'volume': dtc_volume_pct,
            'revenue': dtc_revenue_pct,
            'profit': dtc_profit_pct
        },
        'data_table': df
    }

if __name__ == "__main__":
    extract_channel_data()
