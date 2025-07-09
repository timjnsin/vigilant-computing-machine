import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import uuid
import base64
import io
from typing import List, Dict, Optional, Union, Tuple, Any, Callable
import json
import time

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
    "neutral": "#94a3b8",
    
    # Channel colors (matching Excel model)
    "tasting": "#4472C4",  # Blue
    "club": "#FFD966",     # Gold
    "wholesale": "#A5A5A5", # Gray
    
    # Cost components
    "price": "#10b981",    # Green for price
    "cogs": "#ef4444",     # Red for costs
    "opex": "#f59e0b",     # Gold for opex
    "margin": "#4472C4"    # Blue for margin
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
            ],
            "hoverlabel": {
                "bgcolor": "rgba(15, 23, 42, 0.9)",
                "font_color": COLORS["text_primary"],
                "font_size": 12,
                "bordercolor": COLORS["gold_light"]
            },
            "updatemenus": [
                {
                    "type": "buttons",
                    "showactive": False,
                    "buttons": [
                        {
                            "label": "⬇️ Export",
                            "method": "relayout",
                            "args": ["exportenabled", True]
                        }
                    ],
                    "x": 1.0,
                    "y": 1.0,
                    "xanchor": "right",
                    "yanchor": "top",
                    "bgcolor": "rgba(30, 41, 59, 0.7)",
                    "bordercolor": COLORS["gold_light"],
                    "font": {"color": COLORS["gold"]}
                }
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
    "contribution_waterfall": {
        "price": {"marker": {"color": COLORS["price"]}},
        "cogs": {"marker": {"color": COLORS["cogs"]}},
        "opex": {"marker": {"color": COLORS["opex"]}},
        "margin": {"marker": {"color": COLORS["margin"]}},
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
    "donut": {
        "hole": 0.7,
        "textinfo": "percent",
        "textfont": {"color": COLORS["text_primary"], "size": 14},
        "marker": {
            "line": {"color": COLORS["background"], "width": 1.5}
        },
        "insidetextorientation": "horizontal"
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
    },
    "area": {
        "line": {"width": 2, "color": COLORS["gold"]},
        "fillcolor": f"rgba(245, 158, 11, 0.2)",
        "gradient": {
            "type": "radial",
            "stops": [
                [0, "rgba(245, 158, 11, 0.5)"],
                [1, "rgba(245, 158, 11, 0.1)"]
            ]
        }
    }
}

def inject_chart_js():
    """Inject JavaScript for chart animations and interactivity."""
    if "chart_js_injected" not in st.session_state:
        st.markdown("""
        <script>
        // Function to handle chart animations
        function animateChart(chartId, duration) {
            const chartDiv = document.getElementById(chartId);
            if (!chartDiv) return;
            
            // Add animation class
            chartDiv.classList.add('chart-animate');
            
            // For waterfall charts - animate each bar sequentially
            if (chartDiv.classList.contains('waterfall-chart')) {
                const bars = chartDiv.querySelectorAll('.plotly .bars .point');
                if (bars.length > 0) {
                    bars.forEach((bar, i) => {
                        setTimeout(() => {
                            bar.style.opacity = 1;
                        }, i * (duration / bars.length));
                    });
                }
            }
        }
        
        // Function to export chart as PNG
        function exportChartAsPng(chartId, width, height) {
            const chartDiv = document.getElementById(chartId);
            if (!chartDiv) return;
            
            Plotly.downloadImage(chartDiv, {
                format: 'png',
                width: width || 1200,
                height: height || 800,
                filename: `chart-${chartId}`
            });
        }
        
        // Function to export chart as SVG
        function exportChartAsSvg(chartId) {
            const chartDiv = document.getElementById(chartId);
            if (!chartDiv) return;
            
            Plotly.downloadImage(chartDiv, {
                format: 'svg',
                filename: `chart-${chartId}`
            });
        }
        
        // Function to export chart as PDF
        function exportChartAsPdf(chartId) {
            const chartDiv = document.getElementById(chartId);
            if (!chartDiv) return;
            
            Plotly.downloadImage(chartDiv, {
                format: 'pdf',
                width: 1200,
                height: 800,
                filename: `chart-${chartId}`
            });
        }
        
        // Function to handle chart click events
        function handleChartClick(chartId, data) {
            // Send data to Streamlit component
            if (window.parent.postMessage) {
                const payload = {
                    chartId: chartId,
                    type: 'chart_click',
                    data: data
                };
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: JSON.stringify(payload)
                }, '*');
            }
        }
        
        // Add export buttons to charts
        function addExportButtons() {
            document.querySelectorAll('.js-plotly-plot').forEach(chart => {
                if (chart.querySelector('.export-buttons')) return;
                
                const chartId = chart.id;
                const buttonContainer = document.createElement('div');
                buttonContainer.className = 'export-buttons';
                buttonContainer.style.position = 'absolute';
                buttonContainer.style.top = '5px';
                buttonContainer.style.right = '5px';
                buttonContainer.style.zIndex = '999';
                buttonContainer.style.display = 'flex';
                buttonContainer.style.gap = '5px';
                
                const pngButton = document.createElement('button');
                pngButton.innerHTML = '📷';
                pngButton.title = 'Export as PNG';
                pngButton.className = 'export-button';
                pngButton.style.background = 'rgba(30, 41, 59, 0.7)';
                pngButton.style.border = '1px solid rgba(245, 158, 11, 0.3)';
                pngButton.style.borderRadius = '4px';
                pngButton.style.color = '#f59e0b';
                pngButton.style.cursor = 'pointer';
                pngButton.style.padding = '3px 6px';
                pngButton.style.fontSize = '12px';
                pngButton.onclick = () => exportChartAsPng(chartId);
                
                const svgButton = document.createElement('button');
                svgButton.innerHTML = '📊';
                svgButton.title = 'Export as SVG';
                svgButton.className = 'export-button';
                svgButton.style.background = 'rgba(30, 41, 59, 0.7)';
                svgButton.style.border = '1px solid rgba(245, 158, 11, 0.3)';
                svgButton.style.borderRadius = '4px';
                svgButton.style.color = '#f59e0b';
                svgButton.style.cursor = 'pointer';
                svgButton.style.padding = '3px 6px';
                svgButton.style.fontSize = '12px';
                svgButton.onclick = () => exportChartAsSvg(chartId);
                
                const pdfButton = document.createElement('button');
                pdfButton.innerHTML = '📄';
                pdfButton.title = 'Export as PDF';
                pdfButton.className = 'export-button';
                pdfButton.style.background = 'rgba(30, 41, 59, 0.7)';
                pdfButton.style.border = '1px solid rgba(245, 158, 11, 0.3)';
                pdfButton.style.borderRadius = '4px';
                pdfButton.style.color = '#f59e0b';
                pdfButton.style.cursor = 'pointer';
                pdfButton.style.padding = '3px 6px';
                pdfButton.style.fontSize = '12px';
                pdfButton.onclick = () => exportChartAsPdf(chartId);
                
                buttonContainer.appendChild(pngButton);
                buttonContainer.appendChild(svgButton);
                buttonContainer.appendChild(pdfButton);
                
                chart.style.position = 'relative';
                chart.appendChild(buttonContainer);
            });
        }
        
        // Initialize charts when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            // Add export buttons after a short delay to ensure charts are loaded
            setTimeout(addExportButtons, 1000);
            
            // Animate charts with animation class
            document.querySelectorAll('.chart-animate').forEach(chart => {
                animateChart(chart.id, 1000);
            });
        });
        
        // MutationObserver to detect new charts added to the DOM
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                    setTimeout(addExportButtons, 500);
                }
            });
        });
        
        // Start observing the document body for DOM changes
        observer.observe(document.body, { childList: true, subtree: true });
        </script>
        
        <style>
        /* Chart animations */
        .chart-animate {
            animation: fadeIn 0.5s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Waterfall chart animations */
        .waterfall-chart .bars .point {
            opacity: 0;
            transition: opacity 0.5s ease-in-out;
        }
        
        /* Export buttons hover effect */
        .export-button:hover {
            background: rgba(245, 158, 11, 0.2) !important;
            transform: translateY(-2px);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        
        /* Tooltip styling */
        .plotly-tooltip {
            background-color: rgba(15, 23, 42, 0.95) !important;
            border: 1px solid rgba(245, 158, 11, 0.3) !important;
            border-radius: 4px !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3) !important;
            padding: 8px 12px !important;
            font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif !important;
            font-size: 12px !important;
            color: #f8fafc !important;
        }
        </style>
        """, unsafe_allow_html=True)
        st.session_state.chart_js_injected = True

def apply_premium_styling(fig: go.Figure, title: Optional[str] = None, 
                         height: int = 450, template: str = "default",
                         chart_id: Optional[str] = None,
                         animate: bool = False,
                         export_format: str = "png") -> go.Figure:
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
    chart_id : str, optional
        Unique ID for the chart (auto-generated if not provided)
    animate : bool, optional
        Whether to apply animation to the chart
    export_format : str, optional
        Default export format: "png", "svg", or "pdf"
        
    Returns:
    --------
    go.Figure
        The styled figure
    """
    # Inject JavaScript for chart animations and export
    inject_chart_js()
    
    # Generate a unique ID if not provided
    if not chart_id:
        chart_id = f"chart-{uuid.uuid4().hex[:8]}"
    
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
    
    # Add chart ID and animation class
    layout["div_id"] = chart_id
    layout["className"] = "chart-animate" if animate else ""
    
    # Update the figure layout
    fig.update_layout(**layout)
    
    # Add export buttons
    fig.update_layout(
        modebar=dict(
            bgcolor="rgba(30, 41, 59, 0.7)",
            color=COLORS["gold"],
            activecolor=COLORS["gold_dark"]
        )
    )
    
    return fig

def create_waterfall_chart(
    x_labels: List[str],
    y_values: List[float],
    measures: List[str],
    title: Optional[str] = None,
    height: int = 450,
    text_template: str = "${:,.2f}",
    connector_visible: bool = True,
    totals_marker_color: Optional[str] = None,
    chart_id: Optional[str] = None,
    animate: bool = True
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
    chart_id : str, optional
        Unique ID for the chart (auto-generated if not provided)
    animate : bool, optional
        Whether to apply animation to the chart
        
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
        totals=waterfall_template["totals"],
        hovertemplate="<b>%{x}</b><br>%{text}<extra></extra>"
    ))
    
    # Apply premium styling
    chart_id = chart_id or f"waterfall-{uuid.uuid4().hex[:8]}"
    fig = apply_premium_styling(
        fig, 
        title=title, 
        height=height, 
        chart_id=chart_id,
        animate=animate
    )
    
    # Add waterfall-specific class for animations
    fig.update_layout(className=f"waterfall-chart {fig.layout.className}")
    
    return fig

def contribution_waterfall(
    price: float,
    cogs: List[Dict[str, Union[str, float]]],
    opex: List[Dict[str, Union[str, float]]],
    channel_name: str = "Channel",
    height: int = 450,
    show_percentages: bool = True,
    drill_down_callback: Optional[Callable] = None,
    chart_id: Optional[str] = None,
    animate: bool = True
) -> go.Figure:
    """
    Create an animated contribution waterfall chart with drill-down capability.
    
    Parameters:
    -----------
    price : float
        Price per bottle
    cogs : List[Dict[str, Union[str, float]]]
        List of COGS components with name and value
        Example: [{"name": "Materials", "value": 3.45}, {"name": "Labor", "value": 2.71}]
    opex : List[Dict[str, Union[str, float]]]
        List of OpEx components with name and value
    channel_name : str, optional
        Name of the channel
    height : int, optional
        Chart height in pixels
    show_percentages : bool, optional
        Whether to show percentages along with dollar values
    drill_down_callback : Callable, optional
        Function to call when a bar is clicked
    chart_id : str, optional
        Unique ID for the chart (auto-generated if not provided)
    animate : bool, optional
        Whether to apply animation to the chart
        
    Returns:
    --------
    go.Figure
        The contribution waterfall chart figure
    """
    # Generate chart ID if not provided
    chart_id = chart_id or f"contribution-waterfall-{uuid.uuid4().hex[:8]}"
    
    # Calculate totals
    total_cogs = sum(item["value"] for item in cogs)
    total_opex = sum(item["value"] for item in opex)
    margin = price - total_cogs - total_opex
    margin_percent = (margin / price) * 100 if price > 0 else 0
    
    # Prepare data for the chart
    x_labels = ["Price"]
    y_values = [price]
    measures = ["relative"]
    colors = [COLORS["price"]]
    hover_texts = []
    
    # Add price hover text
    if show_percentages:
        hover_texts.append(f"<b>Price</b><br>${price:.2f}<br>100%")
    else:
        hover_texts.append(f"<b>Price</b><br>${price:.2f}")
    
    # Add COGS items
    for item in cogs:
        name = item["name"]
        value = -item["value"]  # Negative for costs
        percent = abs(value / price) * 100 if price > 0 else 0
        
        x_labels.append(name)
        y_values.append(value)
        measures.append("relative")
        colors.append(COLORS["cogs"])
        
        if show_percentages:
            hover_texts.append(f"<b>{name}</b><br>${abs(value):.2f}<br>{percent:.1f}% of price")
        else:
            hover_texts.append(f"<b>{name}</b><br>${abs(value):.2f}")
    
    # Add OpEx items
    for item in opex:
        name = item["name"]
        value = -item["value"]  # Negative for costs
        percent = abs(value / price) * 100 if price > 0 else 0
        
        x_labels.append(name)
        y_values.append(value)
        measures.append("relative")
        colors.append(COLORS["opex"])
        
        if show_percentages:
            hover_texts.append(f"<b>{name}</b><br>${abs(value):.2f}<br>{percent:.1f}% of price")
        else:
            hover_texts.append(f"<b>{name}</b><br>${abs(value):.2f}")
    
    # Add margin (total)
    x_labels.append("Margin")
    y_values.append(margin)
    measures.append("total")
    colors.append(COLORS["margin"])
    
    if show_percentages:
        hover_texts.append(f"<b>Margin</b><br>${margin:.2f}<br>{margin_percent:.1f}% of price")
    else:
        hover_texts.append(f"<b>Margin</b><br>${margin:.2f}")
    
    # Create the waterfall chart
    fig = go.Figure()
    
    # Add the waterfall trace
    fig.add_trace(go.Waterfall(
        name="",
        orientation="v",
        measure=measures,
        x=x_labels,
        y=y_values,
        textposition="outside",
        text=[f"${abs(val):.2f}" for val in y_values],
        connector={"visible": True, "line": {"color": "rgba(255, 255, 255, 0.5)", "width": 1}},
        hoverinfo="text",
        hovertext=hover_texts,
        marker={"color": colors}
    ))
    
    # Add percentage annotations if requested
    if show_percentages:
        for i, (x, y) in enumerate(zip(x_labels, y_values)):
            if i == 0:  # Price
                fig.add_annotation(
                    x=i,
                    y=y,
                    text="100%",
                    showarrow=False,
                    yshift=25,
                    font=dict(color=COLORS["text_secondary"], size=10)
                )
            elif i == len(x_labels) - 1:  # Margin
                fig.add_annotation(
                    x=i,
                    y=y,
                    text=f"{margin_percent:.1f}%",
                    showarrow=False,
                    yshift=25,
                    font=dict(color=COLORS["text_secondary"], size=10)
                )
            else:  # Costs
                percent = abs(y / price) * 100 if price > 0 else 0
                fig.add_annotation(
                    x=i,
                    y=y/2,  # Position in the middle of the bar
                    text=f"{percent:.1f}%",
                    showarrow=False,
                    font=dict(color=COLORS["text_primary"], size=10)
                )
    
    # Apply premium styling
    fig = apply_premium_styling(
        fig, 
        title=f"{channel_name} - Contribution Analysis", 
        height=height,
        chart_id=chart_id,
        animate=animate
    )
    
    # Add waterfall-specific class for animations
    fig.update_layout(className=f"waterfall-chart {fig.layout.className}")
    
    # Add click event handling for drill-down
    if drill_down_callback:
        fig.update_traces(
            customdata=list(range(len(x_labels))),
            clickmode='event+select'
        )
        
        # Add JavaScript for click handling
        fig.update_layout(
            clickmode='event',
            annotations=[
                dict(
                    x=0.5,
                    y=-0.15,
                    xref="paper",
                    yref="paper",
                    text="Click on any segment to see detailed breakdown",
                    showarrow=False,
                    font=dict(size=10, color=COLORS["text_secondary"]),
                    align="center"
                )
            ]
        )
    
    return fig

def create_pie_chart(
    labels: List[str],
    values: List[float],
    title: Optional[str] = None,
    height: int = 450,
    hole: float = 0.4,
    color_map: Optional[Dict[str, str]] = None,
    pull_index: Optional[int] = None,
    legend_title: Optional[str] = None,
    chart_id: Optional[str] = None,
    animate: bool = True
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
    chart_id : str, optional
        Unique ID for the chart (auto-generated if not provided)
    animate : bool, optional
        Whether to apply animation to the chart
        
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
        pull=pull,
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} (%{percent})<extra></extra>"
    ))
    
    # Apply premium styling
    chart_id = chart_id or f"pie-{uuid.uuid4().hex[:8]}"
    fig = apply_premium_styling(
        fig, 
        title=title, 
        height=height,
        chart_id=chart_id,
        animate=animate
    )
    
    # Update legend title if provided
    if legend_title:
        fig.update_layout(legend_title_text=legend_title)
    
    return fig

def channel_mix_donuts(
    channel_data: pd.DataFrame,
    title: Optional[str] = None,
    height: int = 450,
    insight_text: Optional[str] = None,
    color_map: Optional[Dict[str, str]] = None,
    chart_id: Optional[str] = None,
    animate: bool = True,
    export_resolution: Tuple[int, int] = (3840, 2160)  # 4K resolution
) -> go.Figure:
    """
    Create side-by-side donut charts for volume and revenue mix with center insight text.
    
    Parameters:
    -----------
    channel_data : pd.DataFrame
        DataFrame with columns: Channel, Bottles, Revenue
    title : str, optional
        Chart title
    height : int, optional
        Chart height in pixels
    insight_text : str, optional
        Text to display in the center of the charts
    color_map : Dict[str, str], optional
        Mapping of channel names to colors
    chart_id : str, optional
        Unique ID for the chart (auto-generated if not provided)
    animate : bool, optional
        Whether to apply animation to the chart
    export_resolution : Tuple[int, int], optional
        Resolution for exported images (width, height)
        
    Returns:
    --------
    go.Figure
        The figure containing both donut charts
    """
    # Generate chart ID if not provided
    chart_id = chart_id or f"channel-mix-{uuid.uuid4().hex[:8]}"
    
    # Set up default color map if not provided
    if not color_map:
        default_colors = {
            "Tasting Room": COLORS["tasting"],
            "Club": COLORS["club"],
            "Wholesale": COLORS["wholesale"]
        }
        color_map = default_colors
    
    # Extract data
    channels = channel_data["Channel"].tolist()
    bottles = channel_data["Bottles"].tolist()
    revenue = channel_data["Revenue"].tolist()
    
    # Calculate total volume and revenue
    total_bottles = sum(bottles)
    total_revenue = sum(revenue)
    
    # Calculate average price per bottle by channel
    avg_prices = []
    for i in range(len(channels)):
        if bottles[i] > 0:
            avg_price = revenue[i] / bottles[i]
        else:
            avg_price = 0
        avg_prices.append(avg_price)
    
    # Create figure with subplots
    fig = go.Figure()
    
    # Add volume donut chart
    fig.add_trace(go.Pie(
        labels=channels,
        values=bottles,
        domain={"x": [0, 0.48], "y": [0, 1]},
        hole=0.7,
        textinfo="percent",
        textfont={"color": COLORS["text_primary"], "size": 14},
        marker=dict(
            colors=[color_map.get(channel, COLORS["gold"]) for channel in channels],
            line={"color": COLORS["background"], "width": 1.5}
        ),
        hovertemplate="<b>%{label}</b><br>Volume: %{value:,.0f} bottles<br>%{percent}<extra></extra>",
        name="Volume"
    ))
    
    # Add revenue donut chart
    fig.add_trace(go.Pie(
        labels=channels,
        values=revenue,
        domain={"x": [0.52, 1], "y": [0, 1]},
        hole=0.7,
        textinfo="percent",
        textfont={"color": COLORS["text_primary"], "size": 14},
        marker=dict(
            colors=[color_map.get(channel, COLORS["gold"]) for channel in channels],
            line={"color": COLORS["background"], "width": 1.5}
        ),
        hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>%{percent}<extra></extra>",
        name="Revenue"
    ))
    
    # Add titles for each donut
    fig.add_annotation(
        x=0.24,
        y=1.1,
        text="Volume Mix",
        showarrow=False,
        font=dict(size=16, color=COLORS["text_primary"]),
        xref="paper",
        yref="paper"
    )
    
    fig.add_annotation(
        x=0.76,
        y=1.1,
        text="Revenue Mix",
        showarrow=False,
        font=dict(size=16, color=COLORS["text_primary"]),
        xref="paper",
        yref="paper"
    )
    
    # Add center text for volume donut
    fig.add_annotation(
        x=0.24,
        y=0.5,
        text=f"{total_bottles:,.0f}",
        showarrow=False,
        font=dict(size=20, color=COLORS["gold"]),
        xref="paper",
        yref="paper"
    )
    
    fig.add_annotation(
        x=0.24,
        y=0.44,
        text="Total Bottles",
        showarrow=False,
        font=dict(size=12, color=COLORS["text_secondary"]),
        xref="paper",
        yref="paper"
    )
    
    # Add center text for revenue donut
    fig.add_annotation(
        x=0.76,
        y=0.5,
        text=f"${total_revenue:,.0f}",
        showarrow=False,
        font=dict(size=20, color=COLORS["gold"]),
        xref="paper",
        yref="paper"
    )
    
    fig.add_annotation(
        x=0.76,
        y=0.44,
        text="Total Revenue",
        showarrow=False,
        font=dict(size=12, color=COLORS["text_secondary"]),
        xref="paper",
        yref="paper"
    )
    
    # Add insight text if provided
    if insight_text:
        fig.add_annotation(
            x=0.5,
            y=-0.15,
            text=insight_text,
            showarrow=False,
            font=dict(size=14, color=COLORS["gold"]),
            xref="paper",
            yref="paper",
            align="center",
            bgcolor="rgba(30, 41, 59, 0.7)",
            bordercolor=COLORS["gold_light"],
            borderwidth=1,
            borderpad=10,
            width=500
        )
    else:
        # Generate default insight based on data
        # Find channel with highest avg price
        max_price_idx = avg_prices.index(max(avg_prices))
        max_price_channel = channels[max_price_idx]
        max_price = avg_prices[max_price_idx]
        
        # Find channel with highest volume
        max_vol_idx = bottles.index(max(bottles))
        max_vol_channel = channels[max_vol_idx]
        
        insight = f"{max_price_channel} has the highest price point (${max_price:.2f}/bottle), "
        insight += f"while {max_vol_channel} represents the largest volume share."
        
        fig.add_annotation(
            x=0.5,
            y=-0.15,
            text=insight,
            showarrow=False,
            font=dict(size=14, color=COLORS["gold"]),
            xref="paper",
            yref="paper",
            align="center",
            bgcolor="rgba(30, 41, 59, 0.7)",
            bordercolor=COLORS["gold_light"],
            borderwidth=1,
            borderpad=10,
            width=500
        )
    
    # Apply premium styling
    fig = apply_premium_styling(
        fig, 
        title=title or "Channel Mix Analysis", 
        height=height,
        chart_id=chart_id,
        animate=animate
    )
    
    # Add export button with 4K resolution
    fig.update_layout(
        updatemenus=[
            {
                "type": "buttons",
                "showactive": False,
                "buttons": [
                    {
                        "label": "⬇️ Export 4K",
                        "method": "relayout",
                        "args": ["", ""]  # Placeholder, handled by custom JS
                    }
                ],
                "x": 1.0,
                "y": 1.0,
                "xanchor": "right",
                "yanchor": "top",
                "bgcolor": "rgba(30, 41, 59, 0.7)",
                "bordercolor": COLORS["gold_light"],
                "font": {"color": COLORS["gold"]}
            }
        ]
    )
    
    # Add custom JavaScript for 4K export
    width, height = export_resolution
    export_js = f"""
    <script>
    document.addEventListener('DOMContentLoaded', () => {{
        const chartDiv = document.getElementById('{chart_id}');
        if (!chartDiv) return;
        
        const exportButton = chartDiv.querySelector('.updatemenu-item-text');
        if (exportButton) {{
            exportButton.addEventListener('click', () => {{
                Plotly.downloadImage(chartDiv, {{
                    format: 'png',
                    width: {width},
                    height: {height},
                    filename: 'channel-mix-4k'
                }});
            }});
        }}
    }});
    </script>
    """
    
    # Inject the export JS
    st.markdown(export_js, unsafe_allow_html=True)
    
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
    show_grid: bool = True,
    chart_id: Optional[str] = None,
    animate: bool = True
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
    chart_id : str, optional
        Unique ID for the chart (auto-generated if not provided)
    animate : bool, optional
        Whether to apply animation to the chart
        
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
        ),
        hovertemplate="%{x}<br>%{text}<extra></extra>" if text else None
    ))
    
    # Apply premium styling
    chart_id = chart_id or f"bar-{uuid.uuid4().hex[:8]}"
    fig = apply_premium_styling(
        fig, 
        title=title, 
        height=height,
        chart_id=chart_id,
        animate=animate
    )
    
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
    y_title: Optional[str] = None,
    chart_id: Optional[str] = None,
    animate: bool = True
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
    chart_id : str, optional
        Unique ID for the chart (auto-generated if not provided)
    animate : bool, optional
        Whether to apply animation to the chart
        
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
            textposition='outside',
            hovertemplate="%{x}<br>%{text}<extra></extra>"
        ))
    
    # Apply premium styling
    chart_id = chart_id or f"multi-bar-{uuid.uuid4().hex[:8]}"
    fig = apply_premium_styling(
        fig, 
        title=title, 
        height=height,
        chart_id=chart_id,
        animate=animate
    )
    
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
    show_values: bool = True,
    chart_id: Optional[str] = None,
    animate: bool = True
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
    chart_id : str, optional
        Unique ID for the chart (auto-generated if not provided)
    animate : bool, optional
        Whether to apply animation to the chart
        
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
    chart_id = chart_id or f"heatmap-{uuid.uuid4().hex[:8]}"
    fig = apply_premium_styling(
        fig, 
        title=title, 
        height=height,
        chart_id=chart_id,
        animate=animate
    )
    
    # Update axis titles if provided
    if x_title:
        fig.update_xaxes(title_text=x_title)
    if y_title:
        fig.update_yaxes(title_text=y_title)
    
    # Update colorbar title if provided
    if colorbar_title:
        fig.update_traces(colorbar_title=colorbar_title)
    
    return fig

def sensitivity_heatmap(
    x_values: List[float],
    y_values: List[float],
    z_values: List[List[float]],
    current_x: Optional[float] = None,
    current_y: Optional[float] = None,
    x_title: str = "Price Change",
    y_title: str = "Volume Change",
    title: str = "IRR Sensitivity Analysis",
    height: int = 450,
    format_spec: str = ".1%",
    on_click_callback: Optional[Callable] = None,
    chart_id: Optional[str] = None,
    animate: bool = True
) -> go.Figure:
    """
    Create an enhanced sensitivity heatmap with current selection highlight and click-to-set functionality.
    
    Parameters:
    -----------
    x_values : List[float]
        Values for the x-axis
    y_values : List[float]
        Values for the y-axis
    z_values : List[List[float]]
        2D array of result values (IRR)
    current_x : float, optional
        Current x-axis selection
    current_y : float, optional
        Current y-axis selection
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
    on_click_callback : Callable, optional
        Function to call when a cell is clicked
    chart_id : str, optional
        Unique ID for the chart (auto-generated if not provided)
    animate : bool, optional
        Whether to apply animation to the chart
        
    Returns:
    --------
    go.Figure
        The heatmap figure
    """
    # Generate chart ID if not provided
    chart_id = chart_id or f"sensitivity-{uuid.uuid4().hex[:8]}"
    
    # Format x and y labels
    x_labels = [f"{x:.0%}" for x in x_values]
    y_labels = [f"{y:.0%}" for y in y_values]
    
    # Create hover text with detailed information
    hover_text = []
    for i, y_val in enumerate(y_values):
        hover_row = []
        for j, x_val in enumerate(x_values):
            irr = z_values[i][j]
            hover_row.append(
                f"<b>IRR: {irr:.1%}</b><br>" +
                f"Price Change: {x_val:.0%}<br>" +
                f"Volume Change: {y_val:.0%}<br>" +
                f"Click to set this scenario"
            )
        hover_text.append(hover_row)
    
    # Create the heatmap
    fig = go.Figure(go.Heatmap(
        z=z_values,
        x=x_labels,
        y=y_labels,
        colorscale=[
            [0, COLORS["danger"]],
            [0.5, COLORS["warning"]],
            [1, COLORS["success"]]
        ],
        text=[[f"{val:.1%}" for val in row] for row in z_values],
        texttemplate="%{text}",
        textfont={"color": COLORS["text_primary"], "size": 12},
        hoverinfo="text",
        hovertext=hover_text,
        customdata=[[{"x": x_values[j], "y": y_values[i]} for j in range(len(x_values))] for i in range(len(y_values))],
        colorbar=dict(
            title="IRR",
            titlefont=dict(size=14, color=COLORS["text_primary"]),
            tickfont=dict(size=12, color=COLORS["text_secondary"]),
            tickformat=".0%"
        )
    ))
    
    # Add marker for current selection if provided
    if current_x is not None and current_y is not None:
        # Find the closest indices
        x_idx = min(range(len(x_values)), key=lambda i: abs(x_values[i] - current_x))
        y_idx = min(range(len(y_values)), key=lambda i: abs(y_values[i] - current_y))
        
        # Add a marker at the current selection
        fig.add_trace(go.Scatter(
            x=[x_labels[x_idx]],
            y=[y_labels[y_idx]],
            mode="markers",
            marker=dict(
                symbol="circle",
                size=15,
                color="rgba(0,0,0,0)",
                line=dict(color=COLORS["gold"], width=2)
            ),
            name="Current Selection",
            hoverinfo="skip"
        ))
        
        # Add annotation to show current IRR
        current_irr = z_values[y_idx][x_idx]
        fig.add_annotation(
            x=x_labels[x_idx],
            y=y_labels[y_idx],
            text=f"Current: {current_irr:.1%}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowcolor=COLORS["gold"],
            arrowwidth=2,
            bgcolor="rgba(30, 41, 59, 0.8)",
            bordercolor=COLORS["gold"],
            borderwidth=1,
            borderpad=4,
            font=dict(color=COLORS["gold"], size=12)
        )
    
    # Apply premium styling
    fig = apply_premium_styling(
        fig, 
        title=title, 
        height=height,
        chart_id=chart_id,
        animate=animate
    )
    
    # Update axis titles
    fig.update_xaxes(title_text=x_title)
    fig.update_yaxes(title_text=y_title)
    
    # Add click event handling if callback provided
    if on_click_callback:
        fig.update_layout(
            clickmode='event',
            annotations=fig.layout.annotations + (
                [dict(
                    x=0.5,
                    y=-0.15,
                    xref="paper",
                    yref="paper",
                    text="Click on any cell to set that scenario",
                    showarrow=False,
                    font=dict(size=12, color=COLORS["text_secondary"]),
                    align="center"
                )]
            )
        )
    
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
    line_width: int = 2,
    chart_id: Optional[str] = None,
    animate: bool = True
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
    chart_id : str, optional
        Unique ID for the chart (auto-generated if not provided)
    animate : bool, optional
        Whether to apply animation to the chart
        
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
            fill=fill,
            hovertemplate=f"<b>{name}</b><br>%{{x}}<br>%{{y:,.2f}}<extra></extra>"
        ))
    
    # Apply premium styling
    chart_id = chart_id or f"line-{uuid.uuid4().hex[:8]}"
    fig = apply_premium_styling(
        fig, 
        title=title, 
        height=height,
        chart_id=chart_id,
        animate=animate
    )
    
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
    fill_opacity: float = 0.5,
    chart_id: Optional[str] = None,
    animate: bool = True
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
    chart_id : str, optional
        Unique ID for the chart (auto-generated if not provided)
    animate : bool, optional
        Whether to apply animation to the chart
        
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
        fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, {fill_opacity})",
        hovertemplate="%{x}<br>%{y:,.2f}<extra></extra>"
    ))
    
    # Apply premium styling
    chart_id = chart_id or f"area-{uuid.uuid4().hex[:8]}"
    fig = apply_premium_styling(
        fig, 
        title=title, 
        height=height,
        chart_id=chart_id,
        animate=animate
    )
    
    # Update axis titles if provided
    if x_title:
        fig.update_xaxes(title_text=x_title)
    if y_title:
        fig.update_yaxes(title_text=y_title)
    
    return fig

def cash_runway(
    dates: List[Any],
    cash_balance: List[float],
    burn_rate: Optional[List[float]] = None,
    title: str = "Cash Runway Analysis",
    height: int = 450,
    danger_threshold: float = 0,
    breakeven_date: Optional[Any] = None,
    show_monthly_markers: bool = True,
    chart_id: Optional[str] = None,
    animate: bool = True
) -> go.Figure:
    """
    Create a cash runway area chart with gradient fill, breakeven annotation, and danger zone.
    
    Parameters:
    -----------
    dates : List[Any]
        List of dates for the x-axis
    cash_balance : List[float]
        Cash balance values for each date
    burn_rate : List[float], optional
        Monthly burn rate (negative for cash outflow)
    title : str, optional
        Chart title
    height : int, optional
        Chart height in pixels
    danger_threshold : float, optional
        Threshold below which to show danger zone (usually 0)
    breakeven_date : Any, optional
        Date when the company reaches breakeven
    show_monthly_markers : bool, optional
        Whether to show markers for the first 24 months
    chart_id : str, optional
        Unique ID for the chart (auto-generated if not provided)
    animate : bool, optional
        Whether to apply animation to the chart
        
    Returns:
    --------
    go.Figure
        The cash runway chart figure
    """
    # Generate chart ID if not provided
    chart_id = chart_id or f"cash-runway-{uuid.uuid4().hex[:8]}"
    
    # Create figure
    fig = go.Figure()
    
    # Add the cash balance area chart
    fig.add_trace(go.Scatter(
        x=dates,
        y=cash_balance,
        mode="lines",
        fill="tozeroy",
        line=dict(
            color=COLORS["gold"],
            width=2,
            shape="spline"
        ),
        fillcolor="rgba(245, 158, 11, 0.3)",
        name="Cash Balance",
        hovertemplate="<b>%{x}</b><br>Cash: $%{y:,.0f}<extra></extra>"
    ))
    
    # Add burn rate if provided
    if burn_rate:
        # Only show burn rate for the first 24 months or until breakeven
        show_months = min(24, len(dates))
        
        # Create hover text with burn rate info
        hover_text = []
        for i in range(show_months):
            if i < len(burn_rate):
                hover_text.append(
                    f"<b>{dates[i]}</b><br>" +
                    f"Cash: ${cash_balance[i]:,.0f}<br>" +
                    f"Burn Rate: ${burn_rate[i]:,.0f}/mo"
                )
            else:
                hover_text.append(f"<b>{dates[i]}</b><br>Cash: ${cash_balance[i]:,.0f}")
        
        # Add markers for the first N months
        fig.add_trace(go.Scatter(
            x=dates[:show_months],
            y=cash_balance[:show_months],
            mode="markers",
            marker=dict(
                size=8,
                color=COLORS["gold"],
                line=dict(width=1, color=COLORS["background"])
            ),
            name="Monthly Detail",
            hoverinfo="text",
            hovertext=hover_text,
            showlegend=False
        ))
    elif show_monthly_markers:
        # Show markers for the first 24 months without burn rate info
        show_months = min(24, len(dates))
        
        fig.add_trace(go.Scatter(
            x=dates[:show_months],
            y=cash_balance[:show_months],
            mode="markers",
            marker=dict(
                size=8,
                color=COLORS["gold"],
                line=dict(width=1, color=COLORS["background"])
            ),
            name="Monthly Detail",
            showlegend=False
        ))
    
    # Add danger zone (area below threshold)
    min_y = min(min(cash_balance), danger_threshold)
    danger_y = [min(val, danger_threshold) for val in cash_balance]
    
    # Only add danger zone if there are values below threshold
    if any(val < danger_threshold for val in cash_balance):
        fig.add_trace(go.Scatter(
            x=dates,
            y=[danger_threshold] * len(dates),
            fill="tonexty",
            fillcolor="rgba(239, 68, 68, 0.2)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False,
            hoverinfo="skip"
        ))
        
        # Add a line at the danger threshold
        fig.add_shape(
            type="line",
            x0=dates[0],
            y0=danger_threshold,
            x1=dates[-1],
            y1=danger_threshold,
            line=dict(
                color=COLORS["danger"],
                width=1,
                dash="dash"
            )
        )
        
        # Add annotation for danger threshold
        fig.add_annotation(
            x=dates[0],
            y=danger_threshold,
            text="Danger Zone",
            showarrow=False,
            xshift=10,
            yshift=-15,
            xanchor="left",
            font=dict(size=12, color=COLORS["danger"])
        )
    
    # Add breakeven annotation if provided
    if breakeven_date:
        # Find the closest date in the dataset
        if breakeven_date in dates:
            date_idx = dates.index(breakeven_date)
        else:
            # Find the closest date
            date_idx = min(range(len(dates)), key=lambda i: abs((dates[i] - breakeven_date).total_seconds()))
        
        # Get the cash balance at breakeven
        breakeven_cash = cash_balance[date_idx]
        
        # Add a vertical line at breakeven
        fig.add_shape(
            type="line",
            x0=dates[date_idx],
            y0=min_y,
            x1=dates[date_idx],
            y1=breakeven_cash,
            line=dict(
                color=COLORS["success"],
                width=2,
                dash="dash"
            )
        )
        
        # Add breakeven annotation
        fig.add_annotation(
            x=dates[date_idx],
            y=breakeven_cash,
            text="Breakeven",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowcolor=COLORS["success"],
            arrowwidth=2,
            bgcolor="rgba(30, 41, 59, 0.8)",
            bordercolor=COLORS["success"],
            borderwidth=1,
            borderpad=4,
            font=dict(size=12, color=COLORS["success"])
        )
    
    # Apply premium styling
    fig = apply_premium_styling(
        fig, 
        title=title, 
        height=height,
        chart_id=chart_id,
        animate=animate
    )
    
    # Update axis titles
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Cash Balance ($)")
    
    # Format y-axis as currency
    fig.update_yaxes(tickprefix="$", tickformat=",")
    
    return fig

def create_channel_analysis_charts(
    channel_data: pd.DataFrame,
    title: Optional[str] = None,
    height: int = 400,
    chart_id: Optional[str] = None,
    animate: bool = True
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
    chart_id : str, optional
        Unique ID for the chart (auto-generated if not provided)
    animate : bool, optional
        Whether to apply animation to the chart
        
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
    
    # Generate chart IDs if not provided
    volume_chart_id = f"{chart_id}-volume" if chart_id else f"volume-mix-{uuid.uuid4().hex[:8]}"
    revenue_chart_id = f"{chart_id}-revenue" if chart_id else f"revenue-mix-{uuid.uuid4().hex[:8]}"
    
    # Create volume mix pie chart
    volume_fig = create_pie_chart(
        labels=channel_data["Channel"].tolist(),
        values=channel_data["Bottles"].tolist(),
        title=f"{title} - Volume Mix" if title else "Volume Mix",
        height=height,
        color_map=color_map,
        chart_id=volume_chart_id,
        animate=animate
    )
    
    # Create revenue mix pie chart
    revenue_fig = create_pie_chart(
        labels=channel_data["Channel"].tolist(),
        values=channel_data["Revenue"].tolist(),
        title=f"{title} - Revenue Mix" if title else "Revenue Mix",
        height=height,
        color_map=color_map,
        chart_id=revenue_chart_id,
        animate=animate
    )
    
    return volume_fig, revenue_fig

def create_unit_economics_waterfall(
    price: float,
    cogs: float,
    opex: float,
    channel_name: str = "Channel",
    height: int = 450,
    chart_id: Optional[str] = None,
    animate: bool = True
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
    chart_id : str, optional
        Unique ID for the chart (auto-generated if not provided)
    animate : bool, optional
        Whether to apply animation to the chart
        
    Returns:
    --------
    go.Figure
        The waterfall chart figure
    """
    # Calculate contribution
    contribution = price + (-cogs) + (-opex)
    
    # Create waterfall chart
    chart_id = chart_id or f"unit-economics-{uuid.uuid4().hex[:8]}"
    fig = create_waterfall_chart(
        x_labels=["Price", "COGS", "Allocated OpEx", "Contribution"],
        y_values=[price, -cogs, -opex, contribution],
        measures=["relative", "relative", "relative", "total"],
        title=f"{channel_name} - Unit Economics",
        height=height,
        text_template="${:.2f}",
        chart_id=chart_id,
        animate=animate
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
    format_spec: str = ".1%",
    chart_id: Optional[str] = None,
    animate: bool = True
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
    chart_id : str, optional
        Unique ID for the chart (auto-generated if not provided)
    animate : bool, optional
        Whether to apply animation to the chart
        
    Returns:
    --------
    go.Figure
        The heatmap figure
    """
    # Format x and y labels
    x_labels = [f"{x:.0%}" for x in x_values]
    y_labels = [f"{y:.0%}" for y in y_values]
    
    # Create enhanced sensitivity heatmap
    chart_id = chart_id or f"sensitivity-{uuid.uuid4().hex[:8]}"
    fig = sensitivity_heatmap(
        x_values=x_values,
        y_values=y_values,
        z_values=