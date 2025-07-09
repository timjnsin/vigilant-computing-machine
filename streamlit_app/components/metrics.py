import streamlit as st
import time
import uuid
import base64
from io import BytesIO
from typing import Optional, List, Dict, Union, Tuple, Literal
import json

# Color constants
GOLD_ACCENT = "#f59e0b"
GOLD_LIGHT = "#fbbf24"
GOLD_DARK = "#d97706"
BLUE_DARK = "#0f172a"
BLUE_MEDIUM = "#1e293b"
BLUE_LIGHT = "#334155"
TEXT_LIGHT = "#f8fafc"
TEXT_MUTED = "#94a3b8"
SUCCESS_COLOR = "#10b981"
DANGER_COLOR = "#ef4444"
NEUTRAL_COLOR = "#94a3b8"

# Format types
FORMAT_TYPES = {
    "number": {"prefix": "", "suffix": "", "format_spec": ",.0f"},
    "currency": {"prefix": "$", "suffix": "", "format_spec": ",.0f"},
    "percentage": {"prefix": "", "suffix": "%", "format_spec": ".1f"},
    "decimal": {"prefix": "", "suffix": "", "format_spec": ".2f"},
    "multiplier": {"prefix": "", "suffix": "x", "format_spec": ".1f"},
    "years": {"prefix": "", "suffix": " years", "format_spec": ".1f"}
}

# Animation CSS classes
ANIMATIONS = {
    "fade_in": "metric-fade-in",
    "slide_up": "metric-slide-up",
    "pulse": "metric-pulse",
    "glow": "metric-glow",
    "count": "metric-count",
    "none": ""
}

def inject_custom_css():
    """Inject custom CSS for metrics if not already injected."""
    if "metrics_css_injected" not in st.session_state:
        st.markdown("""
        <style>
        /* Metric Card Styling */
        .metric-card {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(245, 158, 11, 0.2);
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            margin-bottom: 1rem;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #f59e0b, #fbbf24, #f59e0b);
            z-index: 1;
            opacity: 0.8;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3), 0 0 15px rgba(245, 158, 11, 0.3);
            border: 1px solid rgba(245, 158, 11, 0.4);
        }
        
        .metric-card:hover .metric-value {
            text-shadow: 0 0 15px rgba(245, 158, 11, 0.5);
        }
        
        .metric-compact {
            padding: 1rem;
        }
        
        .metric-detailed {
            padding: 1.75rem;
        }
        
        .metric-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }
        
        .metric-label {
            color: #94a3b8;
            font-size: 0.9rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .metric-info-icon {
            color: rgba(245, 158, 11, 0.7);
            cursor: help;
            font-size: 0.8rem;
            transition: all 0.2s ease;
        }
        
        .metric-info-icon:hover {
            color: #f59e0b;
        }
        
        .metric-export-btn {
            background: none;
            border: none;
            color: rgba(245, 158, 11, 0.7);
            cursor: pointer;
            font-size: 0.8rem;
            padding: 2px;
            border-radius: 4px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .metric-export-btn:hover {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
        }
        
        .metric-tooltip {
            position: absolute;
            top: 100%;
            left: 0;
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 6px;
            padding: 0.75rem;
            width: 100%;
            z-index: 10;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            opacity: 0;
            transform: translateY(-10px);
            pointer-events: none;
            font-size: 0.85rem;
            color: #e2e8f0;
            backdrop-filter: blur(4px);
        }
        
        .metric-tooltip.show {
            opacity: 1;
            transform: translateY(5px);
        }
        
        .metric-value-container {
            position: relative;
            min-height: 3rem;
        }
        
        .metric-value {
            color: #f59e0b;
            font-weight: 600;
            font-size: 2rem;
            margin: 0.5rem 0;
            line-height: 1.2;
            text-shadow: 0 2px 10px rgba(245, 158, 11, 0.3);
            transition: all 0.5s ease;
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
            display: flex;
            align-items: center;
            gap: 0.25rem;
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
        
        .metric-delta-inverse-positive {
            color: #ef4444;
        }
        
        .metric-delta-inverse-negative {
            color: #10b981;
        }
        
        .metric-subtitle {
            color: #cbd5e1;
            font-size: 0.85rem;
            margin-top: 0.5rem;
        }
        
        .metric-comparison {
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: #94a3b8;
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .metric-comparison-label {
            font-weight: 500;
        }
        
        .metric-comparison-value {
            color: #cbd5e1;
        }
        
        /* Loading skeleton */
        .metric-skeleton {
            background: linear-gradient(90deg, 
                rgba(30, 41, 59, 0.6) 0%, 
                rgba(51, 65, 85, 0.6) 50%, 
                rgba(30, 41, 59, 0.6) 100%);
            background-size: 200% 100%;
            animation: skeleton-loading 1.5s infinite;
            border-radius: 4px;
            height: 2.5rem;
            width: 100%;
            margin: 0.5rem 0;
        }
        
        @keyframes skeleton-loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
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

def inject_js_for_metrics():
    """Inject JavaScript for advanced metric features."""
    if "metrics_js_injected" not in st.session_state:
        st.markdown("""
        <script>
        // Function to animate counting up to a value
        function animateCounter(elementId, startValue, endValue, duration, prefix, suffix, decimals) {
            const element = document.getElementById(elementId);
            if (!element) return;
            
            startValue = parseFloat(startValue) || 0;
            endValue = parseFloat(endValue) || 0;
            decimals = parseInt(decimals) || 0;
            
            const range = endValue - startValue;
            const minValue = Math.min(startValue, endValue);
            const increment = range / (duration / 16);
            let current = startValue;
            
            const formatNumber = (num) => {
                return num.toLocaleString('en-US', {
                    minimumFractionDigits: decimals,
                    maximumFractionDigits: decimals
                });
            };
            
            const timer = setInterval(() => {
                current += increment;
                if ((increment > 0 && current >= endValue) || 
                    (increment < 0 && current <= endValue)) {
                    clearInterval(timer);
                    current = endValue;
                }
                element.textContent = `${prefix}${formatNumber(current)}${suffix}`;
            }, 16);
        }
        
        // Function to toggle tooltip visibility
        function toggleTooltip(tooltipId) {
            const tooltip = document.getElementById(tooltipId);
            if (tooltip) {
                tooltip.classList.toggle('show');
            }
        }
        
        // Function to export metric card as image
        async function exportMetricCard(cardId) {
            // Check if html2canvas is loaded
            if (typeof html2canvas === 'undefined') {
                // Load html2canvas dynamically
                const script = document.createElement('script');
                script.src = 'https://html2canvas.hertzen.com/dist/html2canvas.min.js';
                script.onload = () => exportMetricCard(cardId);
                document.head.appendChild(script);
                return;
            }
            
            const card = document.getElementById(cardId);
            if (!card) return;
            
            try {
                const canvas = await html2canvas(card, {
                    backgroundColor: null,
                    scale: 2,
                    logging: false
                });
                
                const image = canvas.toDataURL('image/png');
                const link = document.createElement('a');
                link.href = image;
                link.download = `metric-${cardId}.png`;
                link.click();
            } catch (error) {
                console.error('Error exporting metric card:', error);
            }
        }
        
        // Initialize all counters when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            document.querySelectorAll('[data-counter="true"]').forEach(element => {
                const id = element.id;
                const start = parseFloat(element.dataset.start) || 0;
                const end = parseFloat(element.dataset.end) || 0;
                const duration = parseInt(element.dataset.duration) || 1000;
                const prefix = element.dataset.prefix || '';
                const suffix = element.dataset.suffix || '';
                const decimals = parseInt(element.dataset.decimals) || 0;
                
                setTimeout(() => {
                    animateCounter(id, start, end, duration, prefix, suffix, decimals);
                }, 300);
            });
        });
        
        // MutationObserver to detect new counters added to the DOM
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            const counters = node.querySelectorAll ? 
                                node.querySelectorAll('[data-counter="true"]') : [];
                            
                            counters.forEach(element => {
                                const id = element.id;
                                const start = parseFloat(element.dataset.start) || 0;
                                const end = parseFloat(element.dataset.end) || 0;
                                const duration = parseInt(element.dataset.duration) || 1000;
                                const prefix = element.dataset.prefix || '';
                                const suffix = element.dataset.suffix || '';
                                const decimals = parseInt(element.dataset.decimals) || 0;
                                
                                setTimeout(() => {
                                    animateCounter(id, start, end, duration, prefix, suffix, decimals);
                                }, 300);
                            });
                        }
                    });
                }
            });
        });
        
        // Start observing the document body for DOM changes
        observer.observe(document.body, { childList: true, subtree: true });
        </script>
        """, unsafe_allow_html=True)
        st.session_state.metrics_js_injected = True

def format_value(value: Union[int, float, str], prefix: str = "", suffix: str = "", 
                 format_spec: str = "") -> str:
    """Format a value with prefix and suffix."""
    if isinstance(value, (int, float)) and format_spec:
        formatted_value = f"{value:{format_spec}}"
    else:
        formatted_value = str(value)
    
    return f"{prefix}{formatted_value}{suffix}"

def get_delta_color(delta: float, inverse: bool = False) -> str:
    """Get the appropriate CSS class for a delta value."""
    if delta == 0:
        return "metric-delta-neutral"
    
    if inverse:
        return "metric-delta-inverse-positive" if delta > 0 else "metric-delta-inverse-negative"
    else:
        return "metric-delta-positive" if delta > 0 else "metric-delta-negative"

def get_delta_symbol(delta: float) -> str:
    """Get the appropriate symbol for a delta value."""
    if delta > 0:
        return "↑"
    elif delta < 0:
        return "↓"
    else:
        return "–"

class MetricCard:
    """
    A premium metric card component with advanced features.
    
    Features:
    - Animated counting effect
    - Gradient background
    - Comparison to previous value
    - Trend indicators with color coding
    - Hover state with additional details
    - Export functionality
    - Loading skeleton
    """
    
    def __init__(
        self,
        title: str,
        value: Union[int, float],
        format: Union[str, Dict] = "number",
        delta: Optional[float] = None,
        delta_color: str = "normal",
        previous_value: Optional[Union[int, float]] = None,
        previous_label: str = "Previous",
        help: Optional[str] = None,
        size: str = "medium",
        animation: str = "count",
        loading: bool = False,
        subtitle: Optional[str] = None,
        color_override: Optional[str] = None,
        id: Optional[str] = None
    ):
        """
        Initialize a new MetricCard.
        
        Parameters:
        -----------
        title : str
            The title/label for the metric
        value : int or float
            The value to display
        format : str or Dict, optional
            Predefined format ("number", "currency", "percentage", "decimal", "multiplier", "years")
            or a dict with custom format: {"prefix": "$", "suffix": "", "format_spec": ",.0f"}
        delta : float, optional
            Change value to display (e.g., +5.2%)
        delta_color : str, optional
            Color scheme for delta: "normal" (green for positive) or "inverse" (red for positive)
        previous_value : int or float, optional
            Previous value for comparison
        previous_label : str, optional
            Label for the previous value comparison
        help : str, optional
            Help text to display on hover
        size : str, optional
            Size of the metric card: "small", "medium", or "large"
        animation : str, optional
            Animation effect: "fade_in", "slide_up", "pulse", "glow", "count", or "none"
        loading : bool, optional
            Whether to show a loading skeleton
        subtitle : str, optional
            Additional text to display below the metric
        color_override : str, optional
            Override the default gold color with a custom hex color
        id : str, optional
            Custom ID for the card (auto-generated if not provided)
        """
        self.title = title
        self.value = value
        self.delta = delta
        self.delta_color = delta_color
        self.previous_value = previous_value
        self.previous_label = previous_label
        self.help = help
        self.size = size
        self.animation = animation
        self.loading = loading
        self.subtitle = subtitle
        self.color_override = color_override
        self.id = id or f"metric-{uuid.uuid4().hex[:8]}"
        
        # Process format
        if isinstance(format, str) and format in FORMAT_TYPES:
            self.format = FORMAT_TYPES[format]
        elif isinstance(format, dict):
            self.format = format
        else:
            self.format = FORMAT_TYPES["number"]
    
    def render(self):
        """Render the metric card."""
        # Inject required CSS and JS
        inject_custom_css()
        inject_js_for_metrics()
        
        # Determine size class
        size_class = ""
        card_class = "metric-card"
        if self.size == "small":
            size_class = "metric-value-sm"
            card_class += " metric-compact"
        elif self.size == "large":
            size_class = "metric-value-lg"
            card_class += " metric-detailed"
        
        # Determine animation class
        anim_class = ANIMATIONS.get(self.animation, "")
        
        # Format the value
        prefix = self.format.get("prefix", "")
        suffix = self.format.get("suffix", "")
        format_spec = self.format.get("format_spec", "")
        
        formatted_value = format_value(self.value, prefix, suffix, format_spec)
        
        # Get decimal places for animation
        decimals = 0
        if "." in format_spec:
            try:
                decimals = int(format_spec.split(".")[-1].rstrip("f"))
            except:
                decimals = 0
        
        # Determine delta styling
        delta_html = ""
        if self.delta is not None:
            inverse = self.delta_color == "inverse"
            delta_class = f"metric-delta {get_delta_color(self.delta, inverse)}"
            delta_symbol = get_delta_symbol(self.delta)
            
            delta_suffix = "%" if not suffix else ""
            delta_html = f'<div class="{delta_class}">{delta_symbol} {abs(self.delta)}{delta_suffix}</div>'
        
        # Previous value comparison
        comparison_html = ""
        if self.previous_value is not None:
            prev_formatted = format_value(self.previous_value, prefix, suffix, format_spec)
            comparison_html = f"""
            <div class="metric-comparison">
                <span class="metric-comparison-label">{self.previous_label}:</span>
                <span class="metric-comparison-value">{prev_formatted}</span>
            </div>
            """
        
        # Subtitle HTML
        subtitle_html = f'<div class="metric-subtitle">{self.subtitle}</div>' if self.subtitle else ""
        
        # Help tooltip
        tooltip_id = f"tooltip-{self.id}"
        tooltip_html = ""
        info_icon = ""
        if self.help:
            tooltip_html = f"""
            <div id="{tooltip_id}" class="metric-tooltip">
                {self.help}
            </div>
            """
            info_icon = f"""
            <span class="metric-info-icon" 
                  onmouseover="toggleTooltip('{tooltip_id}')" 
                  onmouseout="toggleTooltip('{tooltip_id}')">
                ℹ️
            </span>
            """
        
        # Export button
        export_btn = f"""
        <button class="metric-export-btn" onclick="exportMetricCard('{self.id}')">
            📷
        </button>
        """
        
        # Custom color styling
        color_style = f"color: {self.color_override};" if self.color_override else ""
        
        # Value display (counter or static)
        value_html = ""
        if self.loading:
            value_html = '<div class="metric-skeleton"></div>'
        elif self.animation == "count" and isinstance(self.value, (int, float)):
            counter_id = f"counter-{self.id}"
            start_value = 0
            if self.value > 1000:
                start_value = self.value * 0.5
            
            value_html = f"""
            <div id="{counter_id}" 
                 class="metric-value {size_class}" 
                 style="{color_style}"
                 data-counter="true"
                 data-start="{start_value}"
                 data-end="{self.value}"
                 data-duration="1500"
                 data-prefix="{prefix}"
                 data-suffix="{suffix}"
                 data-decimals="{decimals}">
                {prefix}0{suffix}
            </div>
            """
        else:
            value_html = f"""
            <div class="metric-value {size_class}" style="{color_style}">
                {formatted_value}
            </div>
            """
        
        # Render the metric card
        st.markdown(f"""
        <div id="{self.id}" class="{card_class} {anim_class}">
            <div class="metric-header">
                <div class="metric-label">
                    {self.title}
                    {info_icon}
                </div>
                {export_btn}
            </div>
            
            <div class="metric-value-container">
                {value_html}
                {delta_html}
                {subtitle_html}
            </div>
            
            {comparison_html}
            {tooltip_html}
        </div>
        """, unsafe_allow_html=True)

def display_metric(label: str, value: Union[int, float, str], 
                  prefix: str = "", suffix: str = "", 
                  delta: Optional[float] = None,
                  delta_suffix: str = "%",
                  size: str = "medium",
                  animation: str = "fade_in",
                  subtitle: Optional[str] = None,
                  format_spec: str = "",
                  color_override: Optional[str] = None,
                  help: Optional[str] = None) -> None:
    """
    Display a premium styled metric card (legacy function for backward compatibility).
    
    For new code, use the MetricCard class instead.
    """
    # Create and render a MetricCard
    format_dict = {"prefix": prefix, "suffix": suffix, "format_spec": format_spec}
    
    card = MetricCard(
        title=label,
        value=value,
        format=format_dict,
        delta=delta,
        help=help,
        size=size,
        animation=animation,
        subtitle=subtitle,
        color_override=color_override
    )
    
    card.render()

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
            
            # Check if we're using the new MetricCard class
            if isinstance(metric.get("value"), (MetricCard, type(MetricCard))):
                metric["value"].render()
            else:
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
    
    st.header("Basic MetricCard Examples")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Basic metric with animated counting
        MetricCard(
            title="Project IRR",
            value=0.47,
            format="percentage",
            delta=0.05,
            delta_color="inverse",
            help="5-year returns including exit"
        ).render()
    
    with col2:
        # Currency metric with previous value
        MetricCard(
            title="Revenue",
            value=2450000,
            format="currency",
            delta=12.5,
            previous_value=2175000,
            previous_label="Last Year"
        ).render()
    
    with col3:
        # Loading state example
        MetricCard(
            title="EBITDA Margin",
            value=31.8,
            format="percentage",
            loading=True
        ).render()
    
    st.header("Advanced Formatting")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Custom format
        MetricCard(
            title="MOIC",
            value=2.8,
            format={"prefix": "", "suffix": "x", "format_spec": ".1f"},
            delta=0.3,
            color_override="#4ade80"
        ).render()
    
    with col2:
        # Years format
        MetricCard(
            title="Payback Period",
            value=3.2,
            format="years",
            delta=-0.5,
            subtitle="Faster than industry average"
        ).render()
    
    with col3:
        # Decimal format
        MetricCard(
            title="Debt-to-EBITDA",
            value=2.45,
            format="decimal",
            delta=-0.3,
            delta_color="inverse",
            help="Lower is better for this metric"
        ).render()
    
    st.header("Legacy API Examples")
    
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
