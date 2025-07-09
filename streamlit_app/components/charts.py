import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Union, Tuple, Any

# Color constants for consistent styling
COLORS = {
    # Base theme colors
    "background": "#0f172a",
    "surface": "#1e293b",
    "card": "rgba(30, 41, 59, 0.7)",
    
    # Accent colors
    "gold": "#f59e0b",
    "gold_light": "rgba(245, 158, 11, 0.3)",
    "gold_dark": "#d97706",
    
    # Text colors
    "text_primary": "#f8fafc",
    "text_secondary": "#94a3b8",
    
    # Status colors
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    
    # Channel colors (matching Excel model)
    "tasting": "#4472C4",  # Blue
    "club": "#FFD966",     # Gold
    "wholesale": "#A5A5A5" # Gray
}

# Chart type templates
CHART_TEMPLATES = {
    "default": {
        "layout": {
            "plot_bgcolor": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "font_color": COLORS["text_primary"],
            "font_family": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
            "margin": dict(l=20, r=20, t=40, b=20),
            "legend": dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(size=12),
                bgcolor="rgba(30, 41, 59, 0.5)",
                bordercolor="rgba(245, 158, 11, 0.3)",
                borderwidth=1
            ),
            "colorway": [
                COLORS["gold"], COLORS["tasting"], COLORS["club"], 
                COLORS["wholesale"], COLORS["success"], COLORS["danger"]
            ]
        },
        "xaxis": {
            "showgrid": False,
            "zeroline": False,
            "title_font": dict(size=14),
            "tickfont": dict(size=12),
            "color": COLORS["text_secondary"]
        },
        "yaxis": {
            "showgrid": True,
            "gridcolor": "rgba(255,255,255,0.1)",
            "zeroline": True,
            "zerolinecolor": "rgba(255,255,255,0.3)",
            "title_font": dict(size=14),
            "tickfont": dict(size=12),
            "color": COLORS["text_secondary"]
        }
    },
    "waterfall": {
        "increasing": {"marker": {"color": COLORS["success"]}},
        "decreasing": {"marker": {"color": COLORS["danger"]}},
        "totals": {"marker": {"color": COLORS["gold"]}},
        "connector": {"line": {"color": "rgba(255, 255, 255, 0.5)", "width": 1}}
    },
    "pie": {
        "hole": 0.4,
        "textinfo": "percent+label",
        "textfont": {"color": COLORS["text_primary"], "size": 14},
        "marker": {
            "line": {"color": COLORS["background"], "width": 1.5}
        },
        "pull": [0.01, 0.01, 0.01]
    },
    "bar": {
        "marker": {
            "line": {"width": 0},
            "opacity": 0.9
        },
        "texttemplate": "%{y:,.0f}",
        "textposition": "outside"
    },
    "heatmap": {
        "colorscale": [
            [0, COLORS["danger"]],
            [0.5, COLORS["warning"]],
            [1, COLORS["success"]]
        ],
        "colorbar": {
            "title": {"text": "", "font": {"size": 14}},
            "tickfont": {"size": 12, "color": COLORS["text_secondary"]}
        }
    }
}

def apply_premium_styling(fig: go.Figure, title: Optional[str] = None, 
                         height: int = 450, template: str = "default") -> go.Figure:
    """
    Apply premium styling to a Plotly figure.
    
    Parameters:
    -----------
    fig : go.Figure
        The Plotly figure to style
    title : str, optional
        Chart title
    height : int, optional
        Chart height in pixels
    template : str, optional
        Template name from CHART_TEMPLATES
        
    Returns:
    --------
    go.Figure
        The styled figure
    """
    # Apply base template
    base_template = CHART_TEMPLATES["default"]
    
    # Create a deep copy of the layout to avoid modifying the template
    layout = {**base_template["layout"]}
    
    # Set height and title if provided
    layout["height"] = height
    if title:
        layout["title"] = {
            "text": title,
            "font": {"size": 18, "color": COLORS["text_primary"]},
            "x": 0.5,
            "xanchor": "center"
        }
    
    # Apply xaxis and yaxis styling
    layout["xaxis"] = {**base_template["xaxis"]}
    layout["yaxis"] = {**base_template["yaxis"]}
    
    # Update the figure layout
    fig.update_layout(**layout)
    
    return fig

def create_waterfall_chart(
    x_labels: List[str],
    y_values: List[float],
    measures: List[str],
    title: Optional[str] = None,
    height: int = 450,
    text_template: str = "${:,.2f}",
    connector_visible: bool = True,
    totals_marker_color: Optional[str] = None
) -> go.Figure:
    """
    Create a premium waterfall chart for financial data.
    
    Parameters:
    -----------
    x_labels : List[str]
        Labels for the x-axis
    y_values : List[float]
        Values for each bar
    measures : List[str]
        List of measure types: "relative", "total", or "absolute"
    title : str, optional
        Chart title
    height : int, optional
        Chart height in pixels
    text_template : str, optional
        Template for text labels
    connector_visible : bool, optional
        Whether to show connectors between bars
    totals_marker_color : str, optional
        Custom color for total bars
        
    Returns:
    --------
    go.Figure
        The waterfall chart figure
    """
    # Format text based on template
    text = [text_template.format(val) if isinstance(val, (int, float)) else val for val in y_values]
    
    # Create waterfall chart
    waterfall_template = CHART_TEMPLATES["waterfall"]
    
    # Override totals color if specified
    if totals_marker_color:
        waterfall_template = {**waterfall_template}
        waterfall_template["totals"] = {"marker": {"color": totals_marker_color}}
    
    fig = go.Figure(go.Waterfall(
        name="",
        orientation="v",
        measure=measures,
        x=x_labels,
        textposition="outside",
        text=text,
        y=y_values,
        connector={"visible": connector_visible, "line": waterfall_template["connector"]["line"]},
        increasing=waterfall_template["increasing"],
        decreasing=waterfall_template["decreasing"],
        totals=waterfall_template["totals"]
    ))
    
    # Apply premium styling
    fig = apply_premium_styling(fig, title=title, height=height)
    
    return fig

def create_pie_chart(
    labels: List[str],
    values: List[float],
    title: Optional[str] = None,
    height: int = 450,
    hole: float = 0.4,
    color_map: Optional[Dict[str, str]] = None,
    pull_index: Optional[int] = None,
    legend_title: Optional[str] = None
) -> go.Figure:
    """
    Create a premium pie chart for distribution analysis.
    
    Parameters:
    -----------
    labels : List[str]
        Category labels
    values : List[float]
        Values for each category
    title : str, optional
        Chart title
    height : int, optional
        Chart height in pixels
    hole : float, optional
        Size of the hole (0 for pie, >0 for donut)
    color_map : Dict[str, str], optional
        Mapping of labels to colors
    pull_index : int, optional
        Index of slice to pull out slightly
    legend_title : str, optional
        Title for the legend
        
    Returns:
    --------
    go.Figure
        The pie chart figure
    """
    # Set up default color map if not provided
    if not color_map and len(labels) <= 3:
        default_colors = [COLORS["tasting"], COLORS["club"], COLORS["wholesale"]]
        color_map = {label: default_colors[i] for i, label in enumerate(labels)}
    
    # Create pull array if pull_index is specified
    pull = None
    if pull_index is not None:
        pull = [0.01] * len(labels)
        pull[pull_index] = 0.1
    
    # Create pie chart
    pie_template = CHART_TEMPLATES["pie"]
    
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=hole,
        textinfo=pie_template["textinfo"],
        textfont=pie_template["textfont"],
        marker=dict(
            colors=[color_map.get(label, COLORS["gold"]) for label in labels] if color_map else None,
            line=pie_template["marker"]["line"]
        ),
        pull=pull
    ))
    
    # Apply premium styling
    fig = apply_premium_styling(fig, title=title, height=height)
    
    # Update legend title if provided
    if legend_title:
        fig.update_layout(legend_title_text=legend_title)
    
    return fig

def create_bar_chart(
    x: List[Any],
    y: List[float],
    title: Optional[str] = None,
    height: int = 450,
    orientation: str = "v",
    color: Optional[str] = None,
    color_discrete_map: Optional[Dict[str, str]] = None,
    text_template: str = "${:,.0f}",
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    show_grid: bool = True
) -> go.Figure:
    """
    Create a premium bar chart for financial data.
    
    Parameters:
    -----------
    x : List[Any]
        X-axis values
    y : List[float]
        Y-axis values (heights of bars)
    title : str, optional
        Chart title
    height : int, optional
        Chart height in pixels
    orientation : str, optional
        "v" for vertical bars, "h" for horizontal bars
    color : str, optional
        Color for all bars
    color_discrete_map : Dict[str, str], optional
        Mapping of categories to colors
    text_template : str, optional
        Template for text labels
    x_title : str, optional
        X-axis title
    y_title : str, optional
        Y-axis title
    show_grid : bool, optional
        Whether to show grid lines
        
    Returns:
    --------
    go.Figure
        The bar chart figure
    """
    # Format text based on template
    if isinstance(y[0], (int, float)):
        text = [text_template.format(val) if isinstance(val, (int, float)) else val for val in y]
    else:
        text = None
    
    # Create bar chart
    bar_template = CHART_TEMPLATES["bar"]
    
    fig = go.Figure(go.Bar(
        x=x,
        y=y,
        orientation=orientation,
        text=text,
        textposition=bar_template["textposition"],
        marker=dict(
            color=color or COLORS["gold"],
            line=bar_template["marker"]["line"],
            opacity=bar_template["marker"]["opacity"]
        )
    ))
    
    # Apply premium styling
    fig = apply_premium_styling(fig, title=title, height=height)
    
    # Update axis titles if provided
    if x_title:
        fig.update_xaxes(title_text=x_title)
    if y_title:
        fig.update_yaxes(title_text=y_title)
    
    # Update grid visibility
    fig.update_yaxes(showgrid=show_grid)
    
    return fig

def create_multi_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_cols: List[str],
    title: Optional[str] = None,
    height: int = 450,
    color_map: Optional[Dict[str, str]] = None,
    barmode: str = "group",
    text_template: str = "${:,.0f}",
    x_title: Optional[str] = None,
    y_title: Optional[str] = None
) -> go.Figure:
    """
    Create a premium multi-bar chart for comparing multiple series.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the data
    x_col : str
        Column name for x-axis values
    y_cols : List[str]
        List of column names for the different bar series
    title : str, optional
        Chart title
    height : int, optional
        Chart height in pixels
    color_map : Dict[str, str], optional
        Mapping of series names to colors
    barmode : str, optional
        "group" for grouped bars, "stack" for stacked bars
    text_template : str, optional
        Template for text labels
    x_title : str, optional
        X-axis title
    y_title : str, optional
        Y-axis title
        
    Returns:
    --------
    go.Figure
        The multi-bar chart figure
    """
    # Create figure
    fig = go.Figure()
    
    # Default colors if not provided
    if not color_map:
        default_colors = [COLORS["gold"], COLORS["tasting"], COLORS["club"], COLORS["wholesale"]]
        color_map = {col: default_colors[i % len(default_colors)] for i, col in enumerate(y_cols)}
    
    # Add bars for each series
    for i, y_col in enumerate(y_cols):
        fig.add_trace(go.Bar(
            x=df[x_col],
            y=df[y_col],
            name=y_col,
            marker_color=color_map.get(y_col, COLORS["gold"]),
            text=df[y_col].apply(lambda x: text_template.format(x) if isinstance(x, (int, float)) else x),
            textposition='outside'
        ))
    
    # Apply premium styling
    fig = apply_premium_styling(fig, title=title, height=height)
    
    # Set barmode (grouped or stacked)
    fig.update_layout(barmode=barmode)
    
    # Update axis titles if provided
    if x_title:
        fig.update_xaxes(title_text=x_title)
    if y_title:
        fig.update_yaxes(title_text=y_title)
    
    return fig

def create_heatmap(
    z: List[List[float]],
    x: List[Any],
    y: List[Any],
    title: Optional[str] = None,
    height: int = 450,
    colorscale: Optional[List[List[Union[float, str]]]] = None,
    text_template: str = "{:.1%}",
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    colorbar_title: Optional[str] = None,
    show_values: bool = True
) -> go.Figure:
    """
    Create a premium heatmap for sensitivity analysis.
    
    Parameters:
    -----------
    z : List[List[float]]
        2D array of values to plot
    x : List[Any]
        X-axis labels
    y : List[Any]
        Y-axis labels
    title : str, optional
        Chart title
    height : int, optional
        Chart height in pixels
    colorscale : List[List[Union[float, str]]], optional
        Custom colorscale
    text_template : str, optional
        Template for text labels
    x_title : str, optional
        X-axis title
    y_title : str, optional
        Y-axis title
    colorbar_title : str, optional
        Title for the colorbar
    show_values : bool, optional
        Whether to show text values in cells
        
    Returns:
    --------
    go.Figure
        The heatmap figure
    """
    # Format text based on template if showing values
    text = None
    if show_values:
        text = [[text_template.format(val) if isinstance(val, (int, float)) else val for val in row] for row in z]
    
    # Use default colorscale if not provided
    if not colorscale:
        colorscale = CHART_TEMPLATES["heatmap"]["colorscale"]
    
    # Create heatmap
    fig = go.Figure(go.Heatmap(
        z=z,
        x=x,
        y=y,
        colorscale=colorscale,
        text=text,
        texttemplate="%{text}" if show_values else None,
        textfont={"color": COLORS["text_primary"], "size": 12},
        hoverinfo="text",
        hovertext=[[f"{y[i]}, {x[j]}: {text_template.format(z[i][j])}" for j in range(len(x))] for i in range(len(y))],
    ))
    
    # Apply premium styling
    fig = apply_premium_styling(fig, title=title, height=height)
    
    # Update axis titles if provided
    if x_title:
        fig.update_xaxes(title_text=x_title)
    if y_title:
        fig.update_yaxes(title_text=y_title)
    
    # Update colorbar title if provided
    if colorbar_title:
        fig.update_traces(colorbar_title=colorbar_title)
    
    return fig

def create_line_chart(
    x: List[Any],
    y: Union[List[float], List[List[float]]],
    names: Optional[List[str]] = None,
    title: Optional[str] = None,
    height: int = 450,
    color_map: Optional[Dict[str, str]] = None,
    mode: str = "lines+markers",
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    show_legend: bool = True,
    fill: Optional[str] = None,
    markers: bool = True,
    line_width: int = 2
) -> go.Figure:
    """
    Create a premium line chart for time series data.
    
    Parameters:
    -----------
    x : List[Any]
        X-axis values (usually dates)
    y : List[float] or List[List[float]]
        Y-axis values for one or multiple series
    names : List[str], optional
        Names for each series (required if y is a list of lists)
    title : str, optional
        Chart title
    height : int, optional
        Chart height in pixels
    color_map : Dict[str, str], optional
        Mapping of series names to colors
    mode : str, optional
        "lines", "markers", or "lines+markers"
    x_title : str, optional
        X-axis title
    y_title : str, optional
        Y-axis title
    show_legend : bool, optional
        Whether to show the legend
    fill : str, optional
        Fill style: "tozeroy", "tonexty", etc.
    markers : bool, optional
        Whether to show markers
    line_width : int, optional
        Width of the lines
        
    Returns:
    --------
    go.Figure
        The line chart figure
    """
    # Create figure
    fig = go.Figure()
    
    # Handle single series vs multiple series
    if isinstance(y[0], (int, float)):
        y_data = [y]
        names = names or ["Series 1"]
    else:
        y_data = y
        names = names or [f"Series {i+1}" for i in range(len(y))]
    
    # Default colors if not provided
    if not color_map:
        default_colors = [COLORS["gold"], COLORS["tasting"], COLORS["club"], COLORS["wholesale"]]
        color_map = {name: default_colors[i % len(default_colors)] for i, name in enumerate(names)}
    
    # Add lines for each series
    for i, (y_series, name) in enumerate(zip(y_data, names)):
        fig.add_trace(go.Scatter(
            x=x,
            y=y_series,
            name=name,
            mode=mode,
            line=dict(
                color=color_map.get(name, COLORS["gold"]),
                width=line_width
            ),
            marker=dict(
                size=6,
                line=dict(width=1, color=COLORS["background"])
            ) if markers else None,
            fill=fill
        ))
    
    # Apply premium styling
    fig = apply_premium_styling(fig, title=title, height=height)
    
    # Update axis titles if provided
    if x_title:
        fig.update_xaxes(title_text=x_title)
    if y_title:
        fig.update_yaxes(title_text=y_title)
    
    # Show/hide legend
    fig.update_layout(showlegend=show_legend)
    
    return fig

def create_area_chart(
    x: List[Any],
    y: List[float],
    title: Optional[str] = None,
    height: int = 450,
    color: Optional[str] = None,
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    fill_opacity: float = 0.5
) -> go.Figure:
    """
    Create a premium area chart for cumulative data.
    
    Parameters:
    -----------
    x : List[Any]
        X-axis values
    y : List[float]
        Y-axis values
    title : str, optional
        Chart title
    height : int, optional
        Chart height in pixels
    color : str, optional
        Color for the area
    x_title : str, optional
        X-axis title
    y_title : str, optional
        Y-axis title
    fill_opacity : float, optional
        Opacity of the fill (0-1)
        
    Returns:
    --------
    go.Figure
        The area chart figure
    """
    # Use default color if not provided
    color = color or COLORS["gold"]
    
    # Create area chart
    fig = go.Figure(go.Scatter(
        x=x,
        y=y,
        mode="lines",
        fill="tozeroy",
        line=dict(color=color, width=2),
        fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, {fill_opacity})"
    ))
    
    # Apply premium styling
    fig = apply_premium_styling(fig, title=title, height=height)
    
    # Update axis titles if provided
    if x_title:
        fig.update_xaxes(title_text=x_title)
    if y_title:
        fig.update_yaxes(title_text=y_title)
    
    return fig

def create_channel_analysis_charts(
    channel_data: pd.DataFrame,
    title: Optional[str] = None,
    height: int = 400
) -> Tuple[go.Figure, go.Figure]:
    """
    Create volume and revenue mix pie charts for channel analysis.
    
    Parameters:
    -----------
    channel_data : pd.DataFrame
        DataFrame with columns: Channel, Bottles, Revenue
    title : str, optional
        Chart title prefix
    height : int, optional
        Chart height in pixels
        
    Returns:
    --------
    Tuple[go.Figure, go.Figure]
        Volume mix pie chart and Revenue mix pie chart
    """
    # Create color map
    color_map = {
        "Tasting Room": COLORS["tasting"],
        "Club": COLORS["club"],
        "Wholesale": COLORS["wholesale"]
    }
    
    # Create volume mix pie chart
    volume_fig = create_pie_chart(
        labels=channel_data["Channel"].tolist(),
        values=channel_data["Bottles"].tolist(),
        title=f"{title} - Volume Mix" if title else "Volume Mix",
        height=height,
        color_map=color_map
    )
    
    # Create revenue mix pie chart
    revenue_fig = create_pie_chart(
        labels=channel_data["Channel"].tolist(),
        values=channel_data["Revenue"].tolist(),
        title=f"{title} - Revenue Mix" if title else "Revenue Mix",
        height=height,
        color_map=color_map
    )
    
    return volume_fig, revenue_fig

def create_unit_economics_waterfall(
    price: float,
    cogs: float,
    opex: float,
    channel_name: str = "Channel",
    height: int = 450
) -> go.Figure:
    """
    Create a unit economics waterfall chart.
    
    Parameters:
    -----------
    price : float
        Price per bottle
    cogs : float
        Cost of goods sold per bottle
    opex : float
        Operating expenses per bottle
    channel_name : str, optional
        Name of the channel
    height : int, optional
        Chart height in pixels
        
    Returns:
    --------
    go.Figure
        The waterfall chart figure
    """
    # Calculate contribution
    contribution = price + (-cogs) + (-opex)
    
    # Create waterfall chart
    fig = create_waterfall_chart(
        x_labels=["Price", "COGS", "Allocated OpEx", "Contribution"],
        y_values=[price, -cogs, -opex, contribution],
        measures=["relative", "relative", "relative", "total"],
        title=f"{channel_name} - Unit Economics",
        height=height,
        text_template="${:.2f}"
    )
    
    return fig

def create_sensitivity_heatmap(
    x_values: List[float],
    y_values: List[float],
    z_values: List[List[float]],
    x_title: str = "Variable 1",
    y_title: str = "Variable 2",
    title: str = "Sensitivity Analysis",
    height: int = 450,
    format_spec: str = ".1%"
) -> go.Figure:
    """
    Create a sensitivity analysis heatmap.
    
    Parameters:
    -----------
    x_values : List[float]
        Values for the x-axis
    y_values : List[float]
        Values for the y-axis
    z_values : List[List[float]]
        2D array of result values
    x_title : str, optional
        X-axis title
    y_title : str, optional
        Y-axis title
    title : str, optional
        Chart title
    height : int, optional
        Chart height in pixels
    format_spec : str, optional
        Format specification for values
        
    Returns:
    --------
    go.Figure
        The heatmap figure
    """
    # Format x and y labels
    x_labels = [f"{x:.0%}" for x in x_values]
    y_labels = [f"{y:.0%}" for y in y_values]
    
    # Create heatmap
    fig = create_heatmap(
        z=z_values,
        x=x_labels,
        y=y_labels,
        title=title,
        height=height,
        text_template="{:" + format_spec + "}",
        x_title=x_title,
        y_title=y_title,
        colorbar_title="IRR"
    )
    
    return fig

# Example usage
if __name__ == "__main__":
    st.title("Premium Financial Charts Demo")
    
    st.header("Unit Economics Waterfall Chart")
    waterfall_fig = create_unit_economics_waterfall(
        price=80,
        cogs=6.16,
        opex=15.84,
        channel_name="Tasting Room"
    )
    st.plotly_chart(waterfall_fig, use_container_width=True)
    
    st.header("Channel Analysis")
    channel_data = pd.DataFrame({
        "Channel": ["Tasting Room", "Club", "Wholesale"],
        "Bottles": [9000, 7000, 34000],
        "Revenue": [720000, 630000, 816000]
    })
    volume_fig, revenue_fig = create_channel_analysis_charts(channel_data)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(volume_fig, use_container_width=True)
    with col2:
        st.plotly_chart(revenue_fig, use_container_width=True)
    
    st.header("Sensitivity Heatmap")
    x_changes = np.linspace(-0.2, 0.2, 9)
    y_changes = np.linspace(-0.2, 0.2, 9)
    X, Y = np.meshgrid(x_changes, y_changes)
    Z = np.zeros(X.shape)
    
    # Sample calculation for IRR sensitivity
    base_irr = 0.22
    for i in range(len(y_changes)):
        for j in range(len(x_changes)):
            x_effect = 1.5 * x_changes[j]
            y_effect = 1.2 * y_changes[i]
            Z[i, j] = base_irr * (1 + x_effect + y_effect)
    
    sensitivity_fig = create_sensitivity_heatmap(
        x_values=x_changes,
        y_values=y_changes,
        z_values=Z,
        x_title="Price Change",
        y_title="Volume Change"
    )
    st.plotly_chart(sensitivity_fig, use_container_width=True)
    
    st.header("Revenue Projection")
    years = list(range(1, 6))
    revenue = [2450000 * (1 + 0.25) ** (i-1) for i in years]
    
    bar_fig = create_bar_chart(
        x=years,
        y=revenue,
        title="5-Year Revenue Projection",
        x_title="Year",
        y_title="Revenue ($)",
        text_template="${:,.0f}"
    )
    st.plotly_chart(bar_fig, use_container_width=True)
