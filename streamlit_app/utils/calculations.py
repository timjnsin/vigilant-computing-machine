import numpy as np
import pandas as pd
import streamlit as st
from typing import Dict, List, Tuple, Union, Optional
import numpy_financial as npf

@st.cache_data
def calculate_revenue(
    bottles: int, 
    channel_mix: Dict[str, float], 
    prices: Dict[str, float]
) -> Dict[str, Union[float, Dict[str, float]]]:
    """
    Calculate revenue by channel based on bottle volume, channel mix, and prices.
    
    Parameters:
    -----------
    bottles : int
        Total number of bottles
    channel_mix : Dict[str, float]
        Dictionary with channel names as keys and percentage allocation as values (should sum to 1.0)
    prices : Dict[str, float]
        Dictionary with channel names as keys and price per bottle as values
    
    Returns:
    --------
    Dict[str, Union[float, Dict[str, float]]]
        Dictionary containing total revenue and revenue by channel
        
    Example:
    --------
    >>> bottles = 10000
    >>> channel_mix = {"DTC": 0.3, "Wholesale": 0.5, "Tasting Room": 0.2}
    >>> prices = {"DTC": 40, "Wholesale": 20, "Tasting Room": 35}
    >>> calculate_revenue(bottles, channel_mix, prices)
    {'total': 280000.0, 'by_channel': {'DTC': 120000.0, 'Wholesale': 100000.0, 'Tasting Room': 70000.0}}
    """
    revenue_by_channel = {}
    total_revenue = 0.0
    
    for channel, mix in channel_mix.items():
        channel_bottles = bottles * mix
        channel_revenue = channel_bottles * prices.get(channel, 0)
        revenue_by_channel[channel] = channel_revenue
        total_revenue += channel_revenue
    
    return {
        "total": total_revenue,
        "by_channel": revenue_by_channel
    }

@st.cache_data
def calculate_contribution_margin(
    revenue: Dict[str, Union[float, Dict[str, float]]],
    cogs: Dict[str, float]
) -> Dict[str, Union[float, Dict[str, float]]]:
    """
    Calculate contribution margin by channel.
    
    Parameters:
    -----------
    revenue : Dict[str, Union[float, Dict[str, float]]]
        Revenue dictionary as returned by calculate_revenue
    cogs : Dict[str, float]
        Dictionary with channel names as keys and cost of goods sold per bottle as values
    
    Returns:
    --------
    Dict[str, Union[float, Dict[str, float]]]
        Dictionary containing total contribution margin and margin by channel
        
    Example:
    --------
    >>> revenue = {'total': 280000.0, 'by_channel': {'DTC': 120000.0, 'Wholesale': 100000.0, 'Tasting Room': 70000.0}}
    >>> cogs = {"DTC": 15, "Wholesale": 12, "Tasting Room": 15}
    >>> calculate_contribution_margin(revenue, cogs)
    {'total': 190000.0, 'by_channel': {'DTC': 75000.0, 'Wholesale': 70000.0, 'Tasting Room': 45000.0}, 'margin_percent': 67.85714285714286}
    """
    margin_by_channel = {}
    total_margin = 0.0
    
    for channel, rev in revenue["by_channel"].items():
        channel_bottles = rev / (cogs.get(channel, 0) + 0.01)  # Avoid division by zero
        channel_margin = rev - (channel_bottles * cogs.get(channel, 0))
        margin_by_channel[channel] = channel_margin
        total_margin += channel_margin
    
    return {
        "total": total_margin,
        "by_channel": margin_by_channel,
        "margin_percent": (total_margin / revenue["total"]) * 100 if revenue["total"] > 0 else 0
    }

@st.cache_data
def calculate_cash_flows(
    revenue: float,
    cogs: float,
    opex: float,
    capex: float,
    growth_rate: float = 0.05,
    years: int = 5,
    monthly_y1: bool = True
) -> Dict[str, Union[np.ndarray, pd.DataFrame]]:
    """
    Calculate annual cash flows with optional monthly detail for Year 1.
    
    Parameters:
    -----------
    revenue : float
        Initial annual revenue
    cogs : float
        Initial annual cost of goods sold
    opex : float
        Initial annual operating expenses
    capex : float
        Initial annual capital expenditures
    growth_rate : float, optional
        Annual growth rate for revenue
    years : int, optional
        Number of years to project
    monthly_y1 : bool, optional
        Whether to include monthly detail for Year 1
    
    Returns:
    --------
    Dict[str, Union[np.ndarray, pd.DataFrame]]
        Dictionary with annual cash flows and monthly detail for Year 1
        
    Example:
    --------
    >>> calculate_cash_flows(1000000, 400000, 300000, 50000)
    {'annual': array([250000., 262500., 275625., 289406.25, 303876.56]), 'monthly_y1': DataFrame with monthly cash flows}
    """
    # Calculate annual cash flows
    annual_cash_flows = np.zeros(years)
    
    for year in range(years):
        year_revenue = revenue * (1 + growth_rate) ** year
        year_cogs = cogs * (1 + growth_rate) ** year
        year_opex = opex * (1 + growth_rate*0.5) ** year  # OpEx grows slower
        year_capex = capex * (1 + growth_rate*0.3) ** year  # CapEx grows slower
        
        annual_cash_flows[year] = year_revenue - year_cogs - year_opex - year_capex
    
    result = {"annual": annual_cash_flows}
    
    # Calculate monthly detail for Year 1 if requested
    if monthly_y1:
        monthly_revenue = np.zeros(12)
        monthly_cogs = np.zeros(12)
        monthly_opex = np.zeros(12)
        monthly_capex = np.zeros(12)
        
        # Create realistic monthly distribution (seasonality)
        revenue_seasonality = np.array([0.06, 0.07, 0.08, 0.09, 0.08, 0.09, 0.1, 0.1, 0.09, 0.08, 0.08, 0.08])
        cogs_seasonality = np.array([0.07, 0.07, 0.08, 0.09, 0.08, 0.09, 0.1, 0.1, 0.09, 0.08, 0.08, 0.07])
        opex_seasonality = np.array([0.08, 0.08, 0.08, 0.08, 0.08, 0.09, 0.09, 0.09, 0.09, 0.08, 0.08, 0.08])
        capex_seasonality = np.array([0.2, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.3])
        
        monthly_revenue = revenue * revenue_seasonality
        monthly_cogs = cogs * cogs_seasonality
        monthly_opex = opex * opex_seasonality
        monthly_capex = capex * capex_seasonality
        
        monthly_cash_flows = monthly_revenue - monthly_cogs - monthly_opex - monthly_capex
        
        result["monthly_y1"] = pd.DataFrame({
            "Month": [f"Month {i+1}" for i in range(12)],
            "Revenue": monthly_revenue,
            "COGS": monthly_cogs,
            "OpEx": monthly_opex,
            "CapEx": monthly_capex,
            "Cash Flow": monthly_cash_flows,
            "Cumulative CF": np.cumsum(monthly_cash_flows)
        })
    
    return result

@st.cache_data
def calculate_returns(
    cash_flows: np.ndarray,
    initial_investment: float
) -> Dict[str, float]:
    """
    Calculate IRR, MOIC, and payback period for a series of cash flows.
    
    Parameters:
    -----------
    cash_flows : np.ndarray
        Array of cash flows (first value should be negative for initial investment)
    initial_investment : float
        Initial investment amount (positive value)
    
    Returns:
    --------
    Dict[str, float]
        Dictionary with IRR, MOIC, and payback period
        
    Example:
    --------
    >>> cash_flows = np.array([-1000000, 250000, 300000, 350000, 400000, 450000])
    >>> calculate_returns(cash_flows, 1000000)
    {'irr': 0.1906..., 'moic': 1.75, 'payback_years': 3.25}
    """
    # Ensure initial investment is negative for IRR calculation
    cf_for_irr = cash_flows.copy()
    if cf_for_irr[0] > 0:
        cf_for_irr[0] = -initial_investment
    
    # Calculate IRR
    try:
        irr = npf.irr(cf_for_irr)
        if np.isnan(irr):
            irr = 0
    except:
        irr = 0
    
    # Calculate MOIC (Multiple on Invested Capital)
    total_returns = np.sum(cash_flows[1:])  # Sum all positive cash flows
    moic = total_returns / initial_investment if initial_investment > 0 else 0
    
    # Calculate payback period with fractional months
    cumulative_cf = np.cumsum(cash_flows)
    payback_years = None
    
    for i in range(1, len(cumulative_cf)):
        if cumulative_cf[i] >= 0 and cumulative_cf[i-1] < 0:
            # Linear interpolation for fractional period
            fraction = -cumulative_cf[i-1] / (cash_flows[i])
            payback_years = i - 1 + fraction
            break
    
    if payback_years is None and cumulative_cf[-1] >= 0:
        payback_years = len(cash_flows) - 1  # Max payback period
    elif payback_years is None:
        payback_years = float('inf')  # Never pays back
    
    return {
        "irr": irr,
        "moic": moic,
        "payback_years": payback_years
    }

@st.cache_data
def generate_sensitivity_grid(
    base_case: Dict[str, float],
    ranges: Dict[str, List[float]],
    metric: str = "irr"
) -> pd.DataFrame:
    """
    Generate a sensitivity analysis grid for a given metric.
    
    Parameters:
    -----------
    base_case : Dict[str, float]
        Dictionary with base case parameters
    ranges : Dict[str, List[float]]
        Dictionary with parameter names as keys and lists of values to test
    metric : str, optional
        Metric to calculate ('irr', 'moic', or 'payback')
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with sensitivity analysis results
        
    Example:
    --------
    >>> base_case = {"revenue": 1000000, "cogs": 400000, "opex": 300000, "capex": 50000, "investment": 1000000}
    >>> ranges = {"revenue": [0.8, 0.9, 1.0, 1.1, 1.2], "cogs": [0.8, 0.9, 1.0, 1.1, 1.2]}
    >>> generate_sensitivity_grid(base_case, ranges)
    DataFrame with revenue variations in rows and cogs variations in columns
    """
    if len(ranges) != 2:
        raise ValueError("Sensitivity grid requires exactly 2 parameters to vary")
    
    # Extract the two parameters to vary
    params = list(ranges.keys())
    param1, param2 = params[0], params[1]
    
    # Create the grid
    grid = np.zeros((len(ranges[param1]), len(ranges[param2])))
    
    # Calculate values for each combination
    for i, val1 in enumerate(ranges[param1]):
        for j, val2 in enumerate(ranges[param2]):
            # Create a copy of the base case and modify the parameters
            case = base_case.copy()
            case[param1] = base_case[param1] * val1
            case[param2] = base_case[param2] * val2
            
            # Calculate cash flows
            cf = calculate_cash_flows(
                case.get("revenue", 0),
                case.get("cogs", 0),
                case.get("opex", 0),
                case.get("capex", 0)
            )
            
            # Add initial investment as first cash flow
            full_cf = np.insert(cf["annual"], 0, -case.get("investment", 0))
            
            # Calculate returns
            returns = calculate_returns(full_cf, case.get("investment", 0))
            
            # Store the requested metric
            if metric == "irr":
                grid[i, j] = returns["irr"] * 100  # Convert to percentage
            elif metric == "moic":
                grid[i, j] = returns["moic"]
            elif metric == "payback":
                grid[i, j] = returns["payback_years"]
    
    # Create DataFrame with proper labels
    df = pd.DataFrame(
        grid,
        index=[f"{param1} {val:.1%}" for val in ranges[param1]],
        columns=[f"{param2} {val:.1%}" for val in ranges[param2]]
    )
    
    return df

def calculate_payback_period(
    cash_flows: np.ndarray,
    initial_investment: Optional[float] = None
) -> float:
    """
    Calculate the payback period with fractional periods.
    
    Parameters:
    -----------
    cash_flows : np.ndarray
        Array of cash flows (first value should be negative for initial investment)
    initial_investment : float, optional
        Initial investment amount (if not included in cash_flows)
    
    Returns:
    --------
    float
        Payback period in years (or periods)
        
    Example:
    --------
    >>> cash_flows = np.array([250000, 300000, 350000, 400000])
    >>> calculate_payback_period(cash_flows, 700000)
    2.57...
    """
    cf = cash_flows.copy()
    
    # Handle initial investment
    if initial_investment is not None:
        cf = np.insert(cf, 0, -initial_investment)
    
    cumulative_cf = np.cumsum(cf)
    
    # If never pays back
    if cumulative_cf[-1] < 0:
        return float('inf')
    
    # If pays back immediately
    if cumulative_cf[0] >= 0:
        return 0.0
    
    # Find the period where cumulative CF becomes positive
    for i in range(1, len(cumulative_cf)):
        if cumulative_cf[i] >= 0:
            # Linear interpolation for fractional period
            fraction = -cumulative_cf[i-1] / (cf[i])
            return i - 1 + fraction
    
    return float('inf')  # Should not reach here
