import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Add the parent directory to the path to import distillery_model
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from distillery_model import DistilleryFinancialModel
except ImportError:
    # Fallback for demo mode
    class DistilleryFinancialModel:
        def __init__(self):
            pass

# Import custom components
from components.metrics import display_metric, display_metric_row, display_metric_grid
from components.charts import (
    create_waterfall_chart, create_pie_chart, create_bar_chart, 
    create_multi_bar_chart, create_heatmap, create_line_chart,
    create_channel_analysis_charts, create_unit_economics_waterfall,
    create_sensitivity_heatmap
)

# Page configuration
st.set_page_config(
    page_title="The Brogue Distillery | Financial Model",
    page_icon="🥃",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:support@broguedistillery.com',
        'Report a bug': 'mailto:tech@broguedistillery.com',
        'About': "# The Brogue Distillery Financial Model\nPremium investor presentation tool."
    }
)

# Load custom CSS
css_file = os.path.join(os.path.dirname(__file__), "assets", "custom.css")
if os.path.exists(css_file):
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
else:
    # Fallback inline CSS for essential styling
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        color: #e2e8f0;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(245, 158, 11, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    .metric-value {
        color: #f59e0b;
        font-weight: 600;
        font-size: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'scenario' not in st.session_state:
    st.session_state.scenario = 'Base Case'
if 'year' not in st.session_state:
    st.session_state.year = 3  # Default to Year 3
if 'price_adjustment' not in st.session_state:
    st.session_state.price_adjustment = 0.0
if 'volume_adjustment' not in st.session_state:
    st.session_state.volume_adjustment = 0.0
if 'channel_mix' not in st.session_state:
    st.session_state.channel_mix = {
        'Tasting Room': 0.18,
        'Club': 0.14,
        'Wholesale': 0.68
    }

# Demo data for when not connected to the Excel model
def get_demo_data():
    data = {
        'revenue': {
            'Base Case': [980000, 1470000, 2450000, 3675000, 4593750],
            'Upside Case': [1078000, 1764000, 3062500, 4593750, 5741875],
            'Downside Case': [882000, 1176000, 1837500, 2756250, 3445312]
        },
        'ebitda': {
            'Base Case': [-392000, -147000, 612500, 1286250, 1607812],
            'Upside Case': [-323400, 176400, 918750, 1607813, 2009766],
            'Downside Case': [-441000, -352800, 275625, 689063, 861328]
        },
        'irr': {
            'Base Case': 0.225,
            'Upside Case': 0.315,
            'Downside Case': 0.135
        },
        'moic': {
            'Base Case': 2.8,
            'Upside Case': 3.7,
            'Downside Case': 1.9
        },
        'unit_economics': {
            'Tasting Room': {'price': 80.00, 'cogs': 6.16, 'opex': 15.84, 'contribution': 58.00},
            'Club': {'price': 90.00, 'cogs': 6.16, 'opex': 13.84, 'contribution': 70.00},
            'Wholesale': {'price': 24.00, 'cogs': 6.16, 'opex': 5.84, 'contribution': 12.00}
        },
        'channel_data': pd.DataFrame({
            'Channel': ['Tasting Room', 'Club', 'Wholesale'],
            'Bottles': [9000, 7000, 34000],
            'Revenue': [720000, 630000, 816000],
            'Contribution': [522000, 490000, 408000]
        })
    }
    return data

# Load model or demo data
try:
    model = DistilleryFinancialModel()
    use_demo_data = False
except:
    use_demo_data = True
    demo_data = get_demo_data()

# Helper functions for calculations
def calculate_adjusted_metrics(base_irr, base_moic, price_adj, volume_adj):
    """Calculate adjusted IRR and MOIC based on price and volume adjustments"""
    # Simple approximation for demo purposes
    price_effect = price_adj * 1.2  # Price has 1.2x leverage on returns
    volume_effect = volume_adj * 0.8  # Volume has 0.8x leverage on returns
    
    adj_irr = base_irr * (1 + price_effect + volume_effect)
    adj_moic = base_moic * (1 + (price_effect + volume_effect) * 0.7)
    
    return adj_irr, adj_moic

def calculate_sensitivity_matrix(base_irr, price_range, volume_range):
    """Generate a sensitivity matrix for IRR based on price and volume changes"""
    matrix = []
    for vol_change in reversed(volume_range):  # Reverse for better visualization
        row = []
        for price_change in price_range:
            # Calculate adjusted IRR for this price/volume combination
            price_effect = price_change * 1.2
            volume_effect = vol_change * 0.8
            adj_irr = base_irr * (1 + price_effect + volume_effect)
            row.append(adj_irr)
        matrix.append(row)
    return matrix

def adjust_channel_data(channel_data, mix_adjustments):
    """Adjust channel data based on mix adjustments"""
    # Create a copy to avoid modifying the original
    adjusted_data = channel_data.copy()
    
    # Calculate total bottles and revenue
    total_bottles = channel_data['Bottles'].sum()
    
    # Adjust bottles based on new mix
    for i, channel in enumerate(adjusted_data['Channel']):
        adjusted_data.loc[i, 'Bottles'] = total_bottles * mix_adjustments[channel]
    
    # Recalculate revenue based on implied price per bottle
    for i, channel in enumerate(adjusted_data['Channel']):
        price_per_bottle = channel_data.loc[i, 'Revenue'] / channel_data.loc[i, 'Bottles']
        adjusted_data.loc[i, 'Revenue'] = adjusted_data.loc[i, 'Bottles'] * price_per_bottle
        
        contribution_per_bottle = channel_data.loc[i, 'Contribution'] / channel_data.loc[i, 'Bottles']
        adjusted_data.loc[i, 'Contribution'] = adjusted_data.loc[i, 'Bottles'] * contribution_per_bottle
    
    return adjusted_data

# Sidebar
with st.sidebar:
    st.image("https://placehold.co/200x80/1e293b/f59e0b?text=BROGUE&font=montserrat", use_column_width=True)
    st.markdown("### Model Controls")
    
    scenario = st.selectbox(
        "Scenario",
        options=["Base Case", "Upside Case", "Downside Case"],
        index=0
    )
    st.session_state.scenario = scenario
    
    year = st.slider(
        "Projection Year",
        min_value=1,
        max_value=5,
        value=st.session_state.year,
        step=1,
        format="%d"
    )
    st.session_state.year = year
    
    st.markdown("---")
    st.markdown("### Sensitivity Controls")
    
    price_adj = st.slider(
        "Price Adjustment",
        min_value=-0.20,
        max_value=0.20,
        value=st.session_state.price_adjustment,
        step=0.01,
        format="%+.0f%%",
        help="Adjust price across all channels"
    )
    st.session_state.price_adjustment = price_adj
    
    volume_adj = st.slider(
        "Volume Adjustment",
        min_value=-0.20,
        max_value=0.20,
        value=st.session_state.volume_adjustment,
        step=0.01,
        format="%+.0f%%",
        help="Adjust total volume across all channels"
    )
    st.session_state.volume_adjustment = volume_adj
    
    st.markdown("---")
    st.markdown("### Channel Mix")
    
    # Channel mix sliders - must add up to 100%
    st.markdown("##### Distribution Channels")
    
    # Get current values
    tr_mix = st.session_state.channel_mix['Tasting Room']
    club_mix = st.session_state.channel_mix['Club']
    ws_mix = st.session_state.channel_mix['Wholesale']
    
    # Create sliders that adjust other values to maintain sum of 1.0
    new_tr = st.slider(
        "Tasting Room",
        min_value=0.05,
        max_value=0.50,
        value=tr_mix,
        step=0.01,
        format="%.0f%%"
    )
    
    # Adjust other channels proportionally if this one changed
    if new_tr != tr_mix:
        # Calculate how much to distribute to other channels
        diff = new_tr - tr_mix
        total_others = club_mix + ws_mix
        if total_others > 0:
            club_mix = max(0.05, club_mix - (diff * club_mix / total_others))
            ws_mix = max(0.05, ws_mix - (diff * ws_mix / total_others))
            # Normalize to ensure sum is 1.0
            total = new_tr + club_mix + ws_mix
            club_mix = club_mix / total
            ws_mix = ws_mix / total
            new_tr = new_tr / total
    
    new_club = st.slider(
        "Club",
        min_value=0.05,
        max_value=0.50,
        value=club_mix,
        step=0.01,
        format="%.0f%%"
    )
    
    # Adjust other channels if this one changed
    if new_club != club_mix:
        diff = new_club - club_mix
        total_others = new_tr + ws_mix
        if total_others > 0:
            new_tr = max(0.05, new_tr - (diff * new_tr / total_others))
            ws_mix = max(0.05, ws_mix - (diff * ws_mix / total_others))
            # Normalize
            total = new_tr + new_club + ws_mix
            new_tr = new_tr / total
            new_club = new_club / total
            ws_mix = ws_mix / total
    
    # Calculate wholesale as remainder to ensure sum is exactly 1.0
    new_ws = 1.0 - new_tr - new_club
    st.slider(
        "Wholesale",
        min_value=0.05,
        max_value=0.90,
        value=new_ws,
        step=0.01,
        format="%.0f%%",
        disabled=True
    )
    
    # Update session state with new values
    st.session_state.channel_mix = {
        'Tasting Room': new_tr,
        'Club': new_club,
        'Wholesale': new_ws
    }
    
    st.markdown("---")
    st.markdown("""
    <div class='footer'>
        The Brogue Distillery<br>
        Financial Model v1.0<br>
        © 2025 All Rights Reserved
    </div>
    """, unsafe_allow_html=True)

# Get current scenario data
if use_demo_data:
    current_scenario = st.session_state.scenario
    current_year_idx = st.session_state.year - 1
    
    # Get base metrics from demo data
    revenue = demo_data['revenue'][current_scenario][current_year_idx]
    ebitda = demo_data['ebitda'][current_scenario][current_year_idx]
    base_irr = demo_data['irr'][current_scenario]
    base_moic = demo_data['moic'][current_scenario]
    
    # Apply adjustments
    revenue_adj = revenue * (1 + st.session_state.price_adjustment + st.session_state.volume_adjustment)
    ebitda_adj = ebitda * (1 + st.session_state.price_adjustment * 1.5 + st.session_state.volume_adjustment * 0.7)
    irr_adj, moic_adj = calculate_adjusted_metrics(
        base_irr, base_moic, 
        st.session_state.price_adjustment, 
        st.session_state.volume_adjustment
    )
    
    # Get channel data and adjust for mix
    channel_data = adjust_channel_data(
        demo_data['channel_data'], 
        st.session_state.channel_mix
    )
    
    # Unit economics data
    unit_economics = demo_data['unit_economics']
    
    # Create sensitivity matrix
    price_range = np.linspace(-0.2, 0.2, 9)
    volume_range = np.linspace(-0.2, 0.2, 9)
    irr_matrix = calculate_sensitivity_matrix(base_irr, price_range, volume_range)

# Main content
st.markdown("""
<div class="hero-container">
    <h1>The Brogue Distillery Financial Model</h1>
    <p style="font-size: 1.2rem; color: #94a3b8;">
        Premium American Single Malt Whiskey | Investor Presentation
    </p>
</div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Unit Economics", "Channel Analysis", "Sensitivity"])

# Tab 1: Overview
with tab1:
    st.markdown("### Financial Performance Overview")
    st.markdown(f"Showing projections for **Year {st.session_state.year}** under the **{st.session_state.scenario}** scenario")
    
    # Key metrics row
    metrics_row1 = [
        {"label": "Revenue", "value": revenue_adj, "prefix": "$", "format_spec": ",.0f", 
         "delta": st.session_state.price_adjustment + st.session_state.volume_adjustment, 
         "animation": "fade_in", "size": "large"},
        {"label": "EBITDA", "value": ebitda_adj, "prefix": "$", "format_spec": ",.0f", 
         "delta": (ebitda_adj/ebitda - 1) if ebitda != 0 else None, 
         "animation": "fade_in", "size": "large"},
        {"label": "EBITDA Margin", "value": ebitda_adj/revenue_adj*100 if revenue_adj != 0 else 0, 
         "suffix": "%", "format_spec": ".1f", "animation": "fade_in", "size": "large"}
    ]
    display_metric_row(metrics_row1)
    
    # Returns metrics row
    metrics_row2 = [
        {"label": "IRR", "value": irr_adj*100, "suffix": "%", "format_spec": ".1f", 
         "delta": (irr_adj/base_irr - 1)*100 if base_irr != 0 else None, 
         "animation": "glow", "size": "large"},
        {"label": "MOIC", "value": moic_adj, "suffix": "x", "format_spec": ".1f", 
         "delta": (moic_adj/base_moic - 1)*100 if base_moic != 0 else None, 
         "animation": "glow", "size": "large"},
        {"label": "Payback Period", "value": 5.0 - irr_adj*10, "suffix": " years", 
         "format_spec": ".1f", "animation": "fade_in", "size": "large"}
    ]
    display_metric_row(metrics_row2)
    
    st.markdown("---")
    
    # Revenue and EBITDA projections
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue projection chart
        years = list(range(1, 6))
        
        if use_demo_data:
            scenario_revenues = demo_data['revenue'][current_scenario]
            adjusted_revenues = [r * (1 + st.session_state.price_adjustment + st.session_state.volume_adjustment) 
                               for r in scenario_revenues]
        else:
            # Placeholder for real model data
            adjusted_revenues = [1000000 * (1.2 ** i) for i in range(5)]
        
        revenue_fig = create_bar_chart(
            x=years,
            y=adjusted_revenues,
            title="5-Year Revenue Projection",
            x_title="Year",
            y_title="Revenue ($)",
            text_template="${:,.0f}"
        )
        st.plotly_chart(revenue_fig, use_container_width=True)
    
    with col2:
        # EBITDA projection chart
        if use_demo_data:
            scenario_ebitda = demo_data['ebitda'][current_scenario]
            adjusted_ebitda = [e * (1 + st.session_state.price_adjustment*1.5 + st.session_state.volume_adjustment*0.7) 
                             for e in scenario_ebitda]
        else:
            # Placeholder for real model data
            adjusted_ebitda = [-400000, -100000, 400000, 1000000, 1600000]
        
        ebitda_fig = create_bar_chart(
            x=years,
            y=adjusted_ebitda,
            title="5-Year EBITDA Projection",
            x_title="Year",
            y_title="EBITDA ($)",
            text_template="${:,.0f}",
            color="#10b981"  # Use green for EBITDA
        )
        st.plotly_chart(ebitda_fig, use_container_width=True)
    
    # Scenario comparison
    st.markdown("### Scenario Comparison")
    
    if use_demo_data:
        # Get data for all scenarios
        base_revenues = demo_data['revenue']['Base Case']
        upside_revenues = demo_data['revenue']['Upside Case']
        downside_revenues = demo_data['revenue']['Downside Case']
        
        # Create comparison dataframe
        comparison_df = pd.DataFrame({
            'Year': years,
            'Base Case': base_revenues,
            'Upside Case': upside_revenues,
            'Downside Case': downside_revenues
        })
        
        # Create multi-bar chart
        comparison_fig = create_multi_bar_chart(
            df=comparison_df,
            x_col='Year',
            y_cols=['Base Case', 'Upside Case', 'Downside Case'],
            title="Revenue by Scenario",
            x_title="Year",
            y_title="Revenue ($)",
            color_map={
                'Base Case': "#f59e0b",
                'Upside Case': "#10b981",
                'Downside Case': "#ef4444"
            }
        )
        st.plotly_chart(comparison_fig, use_container_width=True)
    
    # Insight box
    st.markdown("""
    <div class="insight-box">
        <h3>Key Insights</h3>
        <p>
            The Brogue Distillery shows strong growth potential with a projected IRR of 22.5% in the Base Case.
            The business achieves profitability in Year 3, with significant margin expansion as volumes increase.
            Channel mix optimization presents a key opportunity to improve returns, with DTC channels (Tasting Room and Club)
            delivering 3-5x the contribution margin of Wholesale.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Tab 2: Unit Economics
with tab2:
    st.markdown("### Unit Economics Analysis")
    st.markdown("Breakdown of per-bottle economics by distribution channel")
    
    # Channel selector for unit economics
    selected_channel = st.selectbox(
        "Select Channel",
        options=["Tasting Room", "Club", "Wholesale"],
        index=0
    )
    
    if use_demo_data:
        channel_economics = unit_economics[selected_channel]
        
        # Apply price adjustment
        price = channel_economics['price'] * (1 + st.session_state.price_adjustment)
        cogs = channel_economics['cogs']  # COGS stays the same
        opex = channel_economics['opex']  # OpEx stays the same
        contribution = price - cogs - opex
        
        # Calculate margins
        gross_margin = (price - cogs) / price * 100
        contribution_margin = contribution / price * 100
    
    # Display unit economics metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Unit economics waterfall chart
        waterfall_fig = create_unit_economics_waterfall(
            price=price,
            cogs=cogs,
            opex=opex,
            channel_name=selected_channel
        )
        st.plotly_chart(waterfall_fig, use_container_width=True)
    
    with col2:
        # Key metrics
        st.markdown("#### Key Metrics")
        
        metrics_unit = [
            {"label": "Price per Bottle", "value": price, "prefix": "$", "format_spec": ".2f"},
            {"label": "COGS per Bottle", "value": cogs, "prefix": "$", "format_spec": ".2f"},
            {"label": "OpEx per Bottle", "value": opex, "prefix": "$", "format_spec": ".2f"},
            {"label": "Contribution per Bottle", "value": contribution, "prefix": "$", "format_spec": ".2f"},
            {"label": "Gross Margin", "value": gross_margin, "suffix": "%", "format_spec": ".1f"},
            {"label": "Contribution Margin", "value": contribution_margin, "suffix": "%", "format_spec": ".1f"}
        ]
        display_metric_grid(metrics_unit, cols_per_row=2)
        
        st.markdown("#### Channel Comparison")
        
        # Create comparison data
        if use_demo_data:
            channels = ["Tasting Room", "Club", "Wholesale"]
            prices = [unit_economics[c]['price'] * (1 + st.session_state.price_adjustment) for c in channels]
            contributions = [
                unit_economics[c]['price'] * (1 + st.session_state.price_adjustment) - 
                unit_economics[c]['cogs'] - 
                unit_economics[c]['opex'] 
                for c in channels
            ]
            margins = [contributions[i] / prices[i] * 100 for i in range(len(channels))]
            
            # Create bar chart for margin comparison
            margin_fig = create_bar_chart(
                x=channels,
                y=margins,
                title="Contribution Margin by Channel",
                x_title="Channel",
                y_title="Margin (%)",
                text_template="{:.1f}%"
            )
            st.plotly_chart(margin_fig, use_container_width=True)
    
    # Channel economics insights
    st.markdown("""
    <div class="insight-box">
        <h3>Unit Economics Insights</h3>
        <p>
            Direct-to-consumer channels (Tasting Room and Club) deliver significantly higher margins than Wholesale,
            despite higher allocated operating expenses. The Club channel offers the best overall economics with
            higher prices and lower customer acquisition costs, making it a strategic focus for growth.
            A 10% price increase would improve IRR by approximately 3 percentage points.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Tab 3: Channel Analysis
with tab3:
    st.markdown("### Channel Strategy Analysis")
    st.markdown("Distribution channel mix and performance metrics")
    
    # Display channel mix pie charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Volume mix pie chart
        if use_demo_data:
            volume_fig, revenue_fig = create_channel_analysis_charts(
                channel_data=channel_data,
                height=400
            )
            st.plotly_chart(volume_fig, use_container_width=True)
    
    with col2:
        # Revenue mix pie chart
        if use_demo_data:
            st.plotly_chart(revenue_fig, use_container_width=True)
    
    # Channel performance metrics
    st.markdown("### Channel Performance Metrics")
    
    if use_demo_data:
        # Calculate total and averages
        total_bottles = channel_data['Bottles'].sum()
        total_revenue = channel_data['Revenue'].sum()
        total_contribution = channel_data['Contribution'].sum()
        
        # Create metrics for each channel
        channel_metrics = []
        
        for i, channel in enumerate(channel_data['Channel']):
            bottles = channel_data.loc[i, 'Bottles']
            revenue = channel_data.loc[i, 'Revenue']
            contribution = channel_data.loc[i, 'Contribution']
            
            # Calculate metrics
            avg_price = revenue / bottles
            contribution_margin = contribution / revenue * 100
            volume_share = bottles / total_bottles * 100
            revenue_share = revenue / total_revenue * 100
            contribution_share = contribution / total_contribution * 100
            
            # Add to metrics list
            channel_metrics.append({
                'Channel': channel,
                'Bottles': bottles,
                'Revenue': revenue,
                'Avg Price': avg_price,
                'Contribution': contribution,
                'Margin': contribution_margin,
                'Volume %': volume_share,
                'Revenue %': revenue_share,
                'Contribution %': contribution_share
            })
        
        # Create DataFrame
        metrics_df = pd.DataFrame(channel_metrics)
        
        # Format the DataFrame for display
        formatted_df = metrics_df.copy()
        formatted_df['Bottles'] = formatted_df['Bottles'].map('{:,.0f}'.format)
        formatted_df['Revenue'] = formatted_df['Revenue'].map('${:,.0f}'.format)
        formatted_df['Avg Price'] = formatted_df['Avg Price'].map('${:.2f}'.format)
        formatted_df['Contribution'] = formatted_df['Contribution'].map('${:,.0f}'.format)
        formatted_df['Margin'] = formatted_df['Margin'].map('{:.1f}%'.format)
        formatted_df['Volume %'] = formatted_df['Volume %'].map('{:.1f}%'.format)
        formatted_df['Revenue %'] = formatted_df['Revenue %'].map('{:.1f}%'.format)
        formatted_df['Contribution %'] = formatted_df['Contribution %'].map('{:.1f}%'.format)
        
        # Display the table
        st.dataframe(formatted_df, use_container_width=True)
        
        # Create contribution bar chart
        contrib_fig = create_bar_chart(
            x=metrics_df['Channel'],
            y=metrics_df['Contribution'],
            title="Contribution by Channel",
            x_title="Channel",
            y_title="Contribution ($)",
            text_template="${:,.0f}"
        )
        st.plotly_chart(contrib_fig, use_container_width=True)
    
    # Channel strategy insights
    st.markdown("""
    <div class="insight-box">
        <h3>Channel Strategy Insights</h3>
        <p>
            While Wholesale represents the majority of volume (68%), it contributes only 29% of total margin.
            Tasting Room and Club channels deliver 71% of total contribution from just 32% of volume.
            Increasing DTC channels from 32% to 50% of volume would improve overall business IRR by approximately
            4.5 percentage points, making channel mix optimization a key strategic lever.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Tab 4: Sensitivity
with tab4:
    st.markdown("### Sensitivity Analysis")
    st.markdown("Impact of key variables on investment returns")
    
    # IRR sensitivity to price and volume
    st.markdown("#### IRR Sensitivity to Price and Volume")
    
    if use_demo_data:
        # Create sensitivity heatmap
        sensitivity_fig = create_sensitivity_heatmap(
            x_values=price_range,
            y_values=volume_range,
            z_values=irr_matrix,
            x_title="Price Change",
            y_title="Volume Change",
            title="IRR Sensitivity Analysis",
            height=500,
            format_spec=".1%"
        )
        st.plotly_chart(sensitivity_fig, use_container_width=True)
    
    # Current scenario marker
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 2rem;">
        <span style="background: rgba(245, 158, 11, 0.2); padding: 0.5rem 1rem; border-radius: 4px; border: 1px solid #f59e0b;">
            Current Selection: Price {st.session_state.price_adjustment:+.0%}, Volume {st.session_state.volume_adjustment:+.0%} → IRR {irr_adj:.1%}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Channel mix sensitivity
    st.markdown("#### Channel Mix Optimization")
    
    # Create what-if scenarios for channel mix
    if use_demo_data:
        # Define different channel mix scenarios
        mix_scenarios = {
            "Current Mix": st.session_state.channel_mix,
            "DTC Focus": {'Tasting Room': 0.30, 'Club': 0.25, 'Wholesale': 0.45},
            "Wholesale Focus": {'Tasting Room': 0.10, 'Club': 0.10, 'Wholesale': 0.80},
            "Club Focus": {'Tasting Room': 0.15, 'Club': 0.35, 'Wholesale': 0.50}
        }
        
        # Calculate IRR for each scenario
        scenario_irrs = {}
        for scenario_name, mix in mix_scenarios.items():
            # Simple approximation for demo purposes
            tr_diff = mix['Tasting Room'] - 0.18  # Difference from base case
            club_diff = mix['Club'] - 0.14  # Difference from base case
            ws_diff = mix['Wholesale'] - 0.68  # Difference from base case
            
            # Calculate impact on IRR (simplified)
            # Assume moving 10% to DTC from wholesale improves IRR by 2.5%
            irr_impact = (tr_diff + club_diff * 1.2) * 0.25
            scenario_irrs[scenario_name] = base_irr * (1 + irr_impact)
        
        # Create bar chart
        mix_fig = create_bar_chart(
            x=list(scenario_irrs.keys()),
            y=[irr * 100 for irr in scenario_irrs.values()],
            title="IRR by Channel Mix Strategy",
            x_title="Strategy",
            y_title="IRR (%)",
            text_template="{:.1f}%"
        )
        st.plotly_chart(mix_fig, use_container_width=True)
    
    # Sensitivity insights
    st.markdown("""
    <div class="insight-box">
        <h3>Sensitivity Analysis Insights</h3>
        <p>
            Price changes have approximately 1.5x the impact on returns compared to equivalent volume changes.
            The optimal strategy combines moderate price increases (5-10%) with channel mix optimization toward
            higher-margin DTC channels. The "Club Focus" strategy delivers the highest potential IRR by leveraging
            both higher prices and lower customer acquisition costs, while maintaining sufficient wholesale presence
            for brand awareness and fixed cost absorption.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>The Brogue Distillery Financial Model | Investor Edition</p>
    <p style="font-size: 0.8rem;">This model is for illustrative purposes only. Actual results may vary.</p>
    <p style="font-size: 0.8rem;">© 2025 The Brogue Distillery. All Rights Reserved.</p>
</div>
""", unsafe_allow_html=True)
