import streamlit as st
import time
from typing import Optional, List, Dict, Union, Tuple

# Color constants
GOLD_ACCENT = "#f59e0b"
BLUE_DARK = "#0f172a"
BLUE_MEDIUM = "#1e293b"
TEXT_LIGHT = "#f8fafc"
TEXT_MUTED = "#94a3b8"

# Animation CSS classes
ANIMATIONS = {
    "fade_in": "metric-fade-in",
    "slide_up": "metric-slide-up",
    "pulse": "metric-pulse",
    "glow": "metric-glow",
    "none": ""
}

def inject_custom_css():
    """Inject custom CSS for metrics if not already injected."""
    if "metrics_css_injected" not in st.session_state:
        st.markdown("""
        <style>
        /* Metric Card Styling */
        .metric-card {
            background: rgba(30, 41, 59, 0.7);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(245, 158, 11, 0.2);
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            margin-bottom: 1rem;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(245, 158, 11, 0.4);
        }
        
        .metric-compact {
            padding: 1rem;
        }
        
        .metric-detailed {
            padding: 1.75rem;
        }
        
        .metric-label {
            color: #94a3b8;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        .metric-value {
            color: #f59e0b;
            font-weight: 600;
            font-size: 2rem;
            margin: 0.5rem 0;
            line-height: 1.2;
            text-shadow: 0 2px 10px rgba(245, 158, 11, 0.3);
        }
        
        .metric-value-sm {
            font-size: 1.5rem;
        }
        
        .metric-value-lg {
            font-size: 2.5rem;
        }
        
        .metric-delta {
            font-size: 0.9rem;
            margin-top: 0.5rem;
            font-weight: 500;
        }
        
        .metric-delta-positive {
            color: #10b981;
        }
        
        .metric-delta-negative {
            color: #ef4444;
        }
        
        .metric-delta-neutral {
            color: #94a3b8;
        }
        
        .metric-subtitle {
            color: #cbd5e1;
            font-size: 0.85rem;
            margin-top: 0.5rem;
        }
        
        /* Animation Classes */
        .metric-fade-in {
            animation: metricFadeIn 0.7s ease-in-out forwards;
        }
        
        @keyframes metricFadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .metric-slide-up {
            animation: metricSlideUp 0.5s ease-out forwards;
        }
        
        @keyframes metricSlideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .metric-pulse {
            animation: metricPulse 2s infinite;
        }
        
        @keyframes metricPulse {
            0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(245, 158, 11, 0); }
            100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
        }
        
        .metric-glow {
            animation: metricGlow 1.5s ease-in-out infinite alternate;
        }
        
        @keyframes metricGlow {
            from { text-shadow: 0 0 5px rgba(245, 158, 11, 0.3); }
            to { text-shadow: 0 0 15px rgba(245, 158, 11, 0.6); }
        }
        
        /* Responsive adjustments */
        @media screen and (max-width: 768px) {
            .metric-card {
                padding: 1rem;
            }
            
            .metric-value {
                font-size: 1.5rem;
            }
            
            .metric-value-lg {
                font-size: 1.8rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        st.session_state.metrics_css_injected = True

def format_value(value: Union[int, float, str], prefix: str = "", suffix: str = "", 
                 format_spec: str = "") -> str:
    """Format a value with prefix and suffix."""
    if isinstance(value, (int, float)) and format_spec:
        formatted_value = f"{value:{format_spec}}"
    else:
        formatted_value = str(value)
    
    return f"{prefix}{formatted_value}{suffix}"

def display_metric(label: str, value: Union[int, float, str], 
                  prefix: str = "", suffix: str = "", 
                  delta: Optional[float] = None,
                  delta_suffix: str = "%",
                  size: str = "medium",
                  animation: str = "fade_in",
                  subtitle: Optional[str] = None,
                  format_spec: str = "",
                  color_override: Optional[str] = None) -> None:
    """
    Display a premium styled metric card.
    
    Parameters:
    -----------
    label : str
        The label for the metric
    value : int, float, or str
        The value to display
    prefix : str, optional
        Prefix to add before the value (e.g., "$")
    suffix : str, optional
        Suffix to add after the value (e.g., "%")
    delta : float, optional
        Change value to display (e.g., +5.2%)
    delta_suffix : str, optional
        Suffix for the delta value, defaults to "%"
    size : str, optional
        Size of the metric card: "small", "medium", or "large"
    animation : str, optional
        Animation effect: "fade_in", "slide_up", "pulse", "glow", or "none"
    subtitle : str, optional
        Additional text to display below the metric
    format_spec : str, optional
        Format specification for numeric values (e.g., ",.0f" for thousands separator)
    color_override : str, optional
        Override the default gold color with a custom hex color
    """
    # Inject custom CSS if not already done
    inject_custom_css()
    
    # Determine size class
    size_class = ""
    card_class = "metric-card"
    if size == "small":
        size_class = "metric-value-sm"
        card_class += " metric-compact"
    elif size == "large":
        size_class = "metric-value-lg"
        card_class += " metric-detailed"
    
    # Determine animation class
    anim_class = ANIMATIONS.get(animation, "")
    
    # Format the value
    formatted_value = format_value(value, prefix, suffix, format_spec)
    
    # Determine delta styling
    delta_html = ""
    if delta is not None:
        delta_class = "metric-delta "
        delta_symbol = ""
        
        if delta > 0:
            delta_class += "metric-delta-positive"
            delta_symbol = "↑"
        elif delta < 0:
            delta_class += "metric-delta-negative"
            delta_symbol = "↓"
        else:
            delta_class += "metric-delta-neutral"
        
        delta_html = f'<div class="{delta_class}">{delta_symbol} {abs(delta)}{delta_suffix}</div>'
    
    # Subtitle HTML
    subtitle_html = f'<div class="metric-subtitle">{subtitle}</div>' if subtitle else ""
    
    # Custom color styling
    color_style = f"color: {color_override};" if color_override else ""
    
    # Render the metric card
    st.markdown(f"""
    <div class="{card_class} {anim_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value {size_class}" style="{color_style}">{formatted_value}</div>
        {delta_html}
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)

def display_metric_row(metrics: List[Dict], columns: Optional[List[int]] = None,
                      animation_stagger: bool = True) -> None:
    """
    Display multiple metrics in a row with equal or custom column widths.
    
    Parameters:
    -----------
    metrics : List[Dict]
        List of dictionaries, each containing parameters for display_metric
    columns : List[int], optional
        List of column widths that sum to 12 (Streamlit's grid system)
        If None, columns will be equally sized
    animation_stagger : bool, optional
        If True, metrics will animate with a slight delay between each
    """
    # Default to equal columns if not specified
    if columns is None:
        columns = [12 // len(metrics)] * len(metrics)
        # Adjust last column if there's a remainder
        columns[-1] += 12 - sum(columns)
    
    # Create columns
    cols = st.columns(columns)
    
    # Display metrics in columns with staggered animations if requested
    for i, (col, metric) in enumerate(zip(cols, metrics)):
        with col:
            # Add staggered animation delay if requested
            if animation_stagger and "animation" in metric and metric["animation"] != "none":
                time.sleep(0.1 * i)
            
            # Pass all parameters to display_metric
            display_metric(**metric)

def display_metric_grid(metrics: List[Dict], cols_per_row: int = 3,
                       animation_stagger: bool = True) -> None:
    """
    Display metrics in a grid layout with the specified number of columns per row.
    
    Parameters:
    -----------
    metrics : List[Dict]
        List of dictionaries, each containing parameters for display_metric
    cols_per_row : int, optional
        Number of columns per row (default: 3)
    animation_stagger : bool, optional
        If True, metrics will animate with a slight delay between each
    """
    # Calculate how many rows we need
    num_metrics = len(metrics)
    num_rows = (num_metrics + cols_per_row - 1) // cols_per_row
    
    # Process each row
    for row_idx in range(num_rows):
        start_idx = row_idx * cols_per_row
        end_idx = min(start_idx + cols_per_row, num_metrics)
        row_metrics = metrics[start_idx:end_idx]
        
        # If this is the last row and it's not full, adjust column widths
        if end_idx - start_idx < cols_per_row:
            columns = [12 // (end_idx - start_idx)] * (end_idx - start_idx)
            columns[-1] += 12 - sum(columns)
        else:
            columns = None
        
        # Display the row
        display_metric_row(row_metrics, columns, animation_stagger)

def display_kpi_dashboard(kpis: Dict[str, Dict], layout: str = "grid",
                         cols_per_row: int = 3) -> None:
    """
    Display a complete KPI dashboard with named metrics.
    
    Parameters:
    -----------
    kpis : Dict[str, Dict]
        Dictionary mapping metric names to their configuration dictionaries
    layout : str, optional
        Layout style: "grid" or "row"
    cols_per_row : int, optional
        Number of columns per row when using grid layout
    """
    # Convert dictionary to list for display functions
    metrics_list = list(kpis.values())
    
    if layout == "grid":
        display_metric_grid(metrics_list, cols_per_row)
    else:
        display_metric_row(metrics_list)
    
    # Store KPIs in session state for potential reuse
    st.session_state.kpis = kpis

# Example usage
if __name__ == "__main__":
    st.title("Metric Components Demo")
    
    # Basic metric
    display_metric("Revenue", 2450000, prefix="$", format_spec=",.0f")
    
    # Metric with delta
    display_metric("Profit Margin", 23.4, suffix="%", delta=2.1)
    
    # Metric row example
    display_metric_row([
        {"label": "Revenue", "value": 2450000, "prefix": "$", "format_spec": ",.0f"},
        {"label": "EBITDA", "value": 780000, "prefix": "$", "format_spec": ",.0f", "delta": 5.2},
        {"label": "Margin", "value": 31.8, "suffix": "%", "delta": 1.5}
    ])
    
    # Metric grid example
    display_metric_grid([
        {"label": "Revenue", "value": 2450000, "prefix": "$", "format_spec": ",.0f"},
        {"label": "EBITDA", "value": 780000, "prefix": "$", "format_spec": ",.0f", "delta": 5.2},
        {"label": "Margin", "value": 31.8, "suffix": "%", "delta": 1.5},
        {"label": "IRR", "value": 22.5, "suffix": "%", "animation": "glow"},
        {"label": "MOIC", "value": 2.8, "suffix": "x", "size": "large"},
        {"label": "Payback", "value": 3.2, "suffix": " years", "delta": -0.3, "delta_suffix": " years"}
    ])
