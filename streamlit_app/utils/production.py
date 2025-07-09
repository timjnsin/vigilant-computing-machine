import streamlit as st
import time
import uuid
import json
import functools
import traceback
import os
import threading
from typing import Any, Callable, Dict, List, Optional, Union, TypeVar, cast
from datetime import datetime

# Type variables for better type hinting
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

# -----------------------------------------------------------------------------
# Google Analytics Integration
# -----------------------------------------------------------------------------

def init_analytics():
    """Initialize Google Analytics tracking."""
    # Check if GA tracking ID is set
    tracking_id = os.environ.get("GA_TRACKING_ID")
    if not tracking_id:
        return
    
    # Inject GA4 tracking code
    ga_js = f"""
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={tracking_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{tracking_id}', {{ 'anonymize_ip': true }});
      
      // Custom dimension for user session
      gtag('set', {{'session_id': '{str(uuid.uuid4())[:8]}'}});
      
      // Function to track custom events
      window.trackEvent = function(category, action, label, value) {{
        gtag('event', action, {{
          'event_category': category,
          'event_label': label,
          'value': value
        }});
      }}
    </script>
    <!-- End Google Analytics -->
    """
    
    # Inject the script
    st.markdown(ga_js, unsafe_allow_html=True)
    
    # Store in session state that analytics is initialized
    st.session_state.analytics_initialized = True

def track_event(category: str, action: str, label: Optional[str] = None, value: Optional[float] = None):
    """
    Track a custom event in Google Analytics.
    
    Parameters:
    -----------
    category : str
        Event category (e.g., 'Button', 'Chart', 'Export')
    action : str
        Event action (e.g., 'Click', 'Generate', 'Download')
    label : str, optional
        Event label for additional context
    value : float, optional
        Numeric value associated with the event
    """
    if not st.session_state.get("analytics_initialized", False):
        return
    
    # Create JavaScript to track the event
    js_code = f"""
    <script>
    if (window.trackEvent) {{
        window.trackEvent('{category}', '{action}', '{label or ""}', {value or 0});
    }}
    </script>
    """
    
    # Inject the script
    st.markdown(js_code, unsafe_allow_html=True)

def track_page_view(page_name: str):
    """
    Track a page view in Google Analytics.
    
    Parameters:
    -----------
    page_name : str
        Name of the page being viewed
    """
    if not st.session_state.get("analytics_initialized", False):
        return
    
    # Create JavaScript to track the page view
    js_code = f"""
    <script>
    if (window.gtag) {{
        gtag('event', 'page_view', {{
            'page_title': '{page_name}',
            'page_location': window.location.href,
            'page_path': window.location.pathname
        }});
    }}
    </script>
    """
    
    # Inject the script
    st.markdown(js_code, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Error Boundary with Friendly Messages
# -----------------------------------------------------------------------------

class ErrorBoundary:
    """
    Context manager for catching and handling errors with user-friendly messages.
    
    Example:
    --------
    with ErrorBoundary("Failed to calculate IRR"):
        result = complex_calculation()
    """
    
    def __init__(self, friendly_message: str, fallback_value: Any = None):
        """
        Initialize the error boundary.
        
        Parameters:
        -----------
        friendly_message : str
            User-friendly message to display if an error occurs
        fallback_value : Any, optional
            Value to return if an error occurs
        """
        self.friendly_message = friendly_message
        self.fallback_value = fallback_value
        self.error_occurred = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error_occurred = True
            
            # Log the error for debugging
            error_details = traceback.format_exc()
            print(f"Error caught by ErrorBoundary: {error_details}")
            
            # Show friendly error message to user
            st.error(f"💫 {self.friendly_message}")
            
            # Add option to show technical details in expander
            with st.expander("Technical Details"):
                st.code(error_details)
            
            # Return True to suppress the exception
            return True
        
        return False

def error_boundary(friendly_message: str, fallback_value: Any = None) -> Callable[[F], F]:
    """
    Decorator for wrapping functions with error handling.
    
    Parameters:
    -----------
    friendly_message : str
        User-friendly message to display if an error occurs
    fallback_value : Any, optional
        Value to return if an error occurs
    
    Returns:
    --------
    Callable
        Decorated function with error handling
    
    Example:
    --------
    @error_boundary("Failed to calculate IRR", fallback_value=0)
    def calculate_irr(cash_flows):
        # Complex calculation that might fail
        return npf.irr(cash_flows)
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with ErrorBoundary(friendly_message, fallback_value) as eb:
                result = func(*args, **kwargs)
                if eb.error_occurred:
                    return eb.fallback_value
                return result
        return cast(F, wrapper)
    return decorator

# -----------------------------------------------------------------------------
# Loading States
# -----------------------------------------------------------------------------

def show_loading(message: str = "Loading...") -> Dict[str, Any]:
    """
    Display a loading spinner with a custom message.
    
    Parameters:
    -----------
    message : str, optional
        Message to display with the spinner
    
    Returns:
    --------
    Dict[str, Any]
        Dictionary with spinner and message placeholders
    
    Example:
    --------
    loading = show_loading("Calculating IRR...")
    # Do some work
    hide_loading(loading)
    """
    # Create unique keys for this loading instance
    spinner_key = f"spinner_{uuid.uuid4().hex[:8]}"
    message_key = f"message_{uuid.uuid4().hex[:8]}"
    
    # Create placeholders
    spinner = st.empty()
    message_placeholder = st.empty()
    
    # Show spinner and message
    with spinner:
        st.spinner("")
    with message_placeholder:
        st.markdown(f"<div class='loading-message'>{message}</div>", unsafe_allow_html=True)
    
    # Return references to the placeholders
    return {
        "spinner": spinner,
        "message": message_placeholder,
        "start_time": time.time()
    }

def hide_loading(loading_state: Dict[str, Any], success_message: Optional[str] = None):
    """
    Hide a loading spinner and optionally show a success message.
    
    Parameters:
    -----------
    loading_state : Dict[str, Any]
        Dictionary returned by show_loading()
    success_message : str, optional
        Success message to display briefly before clearing
    """
    # Calculate duration for analytics
    duration = time.time() - loading_state["start_time"]
    
    # Clear spinner
    loading_state["spinner"].empty()
    
    # Show success message if provided
    if success_message:
        loading_state["message"].success(success_message)
        
        # Clear success message after a delay
        def clear_message():
            time.sleep(3)
            loading_state["message"].empty()
        
        # Start a thread to clear the message
        threading.Thread(target=clear_message, daemon=True).start()
    else:
        # Clear message immediately
        loading_state["message"].empty()
    
    # Track loading duration for performance monitoring
    if st.session_state.get("analytics_initialized", False):
        track_event("Performance", "Loading", "Duration", duration)

def loading_state(message: str = "Loading...") -> Callable[[F], F]:
    """
    Decorator for adding loading state to functions.
    
    Parameters:
    -----------
    message : str, optional
        Message to display during loading
    
    Returns:
    --------
    Callable
        Decorated function with loading state
    
    Example:
    --------
    @loading_state("Calculating financial metrics...")
    def calculate_metrics(data):
        time.sleep(2)  # Simulate work
        return {"irr": 0.15, "moic": 2.5}
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            loading = show_loading(message)
            try:
                result = func(*args, **kwargs)
                hide_loading(loading)
                return result
            except Exception as e:
                hide_loading(loading)
                raise e
        return cast(F, wrapper)
    return decorator

# -----------------------------------------------------------------------------
# Keyboard Shortcuts
# -----------------------------------------------------------------------------

def init_keyboard_shortcuts():
    """Initialize keyboard shortcuts for the application."""
    js_code = """
    <script>
    // Wait for the DOM to be fully loaded
    document.addEventListener('DOMContentLoaded', function() {
        // Add event listener for keyboard shortcuts
        document.addEventListener('keydown', function(event) {
            // Command/Ctrl + K for quick actions
            if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
                event.preventDefault();
                // Send message to Streamlit
                if (window.parent.postMessage) {
                    window.parent.postMessage({
                        type: 'streamlit:keyboardShortcut',
                        shortcut: 'cmd+k'
                    }, '*');
                }
            }
            
            // Left/Right arrows for scenario toggle
            if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
                // Check if we're focused on a scenario toggle
                const activeElement = document.activeElement;
                const isToggle = activeElement && activeElement.closest('.scenario-toggle-container');
                
                if (isToggle || document.querySelector('.scenario-toggle-container:hover')) {
                    event.preventDefault();
                    
                    // Find all scenario options
                    const container = isToggle ? activeElement.closest('.scenario-toggle-container') : 
                                               document.querySelector('.scenario-toggle-container:hover');
                    const options = container.querySelectorAll('.scenario-option');
                    const activeOption = container.querySelector('.scenario-option.active');
                    
                    if (activeOption) {
                        let index = Array.from(options).indexOf(activeOption);
                        
                        // Calculate new index based on arrow key
                        if (event.key === 'ArrowLeft') {
                            index = (index - 1 + options.length) % options.length;
                        } else {
                            index = (index + 1) % options.length;
                        }
                        
                        // Activate the new option
                        options[index].click();
                    }
                }
            }
            
            // Escape key for closing dialogs
            if (event.key === 'Escape') {
                // Close any open dialogs
                const dialogs = document.querySelectorAll('.confirmation-overlay');
                dialogs.forEach(dialog => {
                    const cancelButton = dialog.querySelector('.confirmation-button.cancel');
                    if (cancelButton) {
                        cancelButton.click();
                    }
                });
            }
        });
    });
    
    // Register a listener for Streamlit messages
    window.addEventListener('message', function(event) {
        if (event.data.type === 'streamlit:keyboardShortcut' && event.data.shortcut === 'cmd+k') {
            // Show quick action palette
            const quickActionButton = document.querySelector('[data-testid="baseButton-headerNoPadding"]');
            if (quickActionButton) {
                quickActionButton.click();
            }
        }
    });
    </script>
    """
    
    # Inject the script
    st.markdown(js_code, unsafe_allow_html=True)
    
    # Store in session state that shortcuts are initialized
    st.session_state.keyboard_shortcuts_initialized = True

def handle_keyboard_shortcut(shortcut: str) -> bool:
    """
    Handle a keyboard shortcut event.
    
    Parameters:
    -----------
    shortcut : str
        The shortcut that was triggered (e.g., 'cmd+k')
    
    Returns:
    --------
    bool
        True if the shortcut was handled, False otherwise
    """
    # Check if shortcuts are initialized
    if not st.session_state.get("keyboard_shortcuts_initialized", False):
        return False
    
    # Handle different shortcuts
    if shortcut == "cmd+k":
        # Show quick action palette
        st.session_state.show_quick_actions = True
        return True
    
    return False

# -----------------------------------------------------------------------------
# Performance Optimizations
# -----------------------------------------------------------------------------

def lazy_load(placeholder_func: Callable[[], None], 
              load_func: Callable[[], T], 
              key: Optional[str] = None) -> T:
    """
    Lazy load a component only when it's needed.
    
    Parameters:
    -----------
    placeholder_func : Callable[[], None]
        Function to create a placeholder UI
    load_func : Callable[[], T]
        Function that loads and returns the actual component
    key : str, optional
        Unique key for this lazy loading instance
    
    Returns:
    --------
    T
        Result of the load_func when loaded
    
    Example:
    --------
    def placeholder():
        st.info("Click to load the chart")
        if st.button("Load Chart"):
            st.session_state.load_chart = True
    
    def load_chart():
        return create_complex_chart(data)
    
    chart = lazy_load(placeholder, load_chart, "chart")
    """
    # Generate a key if not provided
    if key is None:
        key = f"lazy_load_{uuid.uuid4().hex[:8]}"
    
    load_key = f"load_{key}"
    result_key = f"result_{key}"
    
    # Check if we should load the component
    if not st.session_state.get(load_key, False):
        # Show placeholder
        placeholder_func()
        return None
    
    # Check if we've already loaded the result
    if result_key not in st.session_state:
        # Load the component
        loading = show_loading("Loading component...")
        try:
            st.session_state[result_key] = load_func()
        finally:
            hide_loading(loading)
    
    # Return the loaded result
    return st.session_state[result_key]

def debounce(wait_time: float) -> Callable[[F], F]:
    """
    Decorator to debounce a function call.
    
    Parameters:
    -----------
    wait_time : float
        Time to wait in seconds before executing the function
    
    Returns:
    --------
    Callable
        Decorated function that will be debounced
    
    Example:
    --------
    @debounce(0.3)
    def on_slider_change():
        # This won't execute until the slider has stopped changing for 300ms
        recalculate_expensive_operation()
    """
    def decorator(func: F) -> F:
        # Use function name as part of the key to avoid conflicts
        func_name = func.__name__
        last_call_time_key = f"debounce_last_call_time_{func_name}"
        timer_key = f"debounce_timer_{func_name}"
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Record the current time
            current_time = time.time()
            st.session_state[last_call_time_key] = current_time
            
            # Define a function to execute after the wait time
            def execute_func():
                # Only execute if this is still the most recent call
                if st.session_state.get(last_call_time_key) == current_time:
                    func(*args, **kwargs)
            
            # Cancel any existing timer
            if timer_key in st.session_state:
                st.session_state[timer_key].cancel()
            
            # Create a new timer
            timer = threading.Timer(wait_time, execute_func)
            timer.daemon = True
            st.session_state[timer_key] = timer
            timer.start()
            
            # Return None as we're executing asynchronously
            return None
        
        return cast(F, wrapper)
    
    return decorator

def pre_calculate_common_scenarios(calc_func: Callable[..., T], 
                                  scenarios: List[Dict[str, Any]],
                                  key: Optional[str] = None) -> Callable[..., T]:
    """
    Pre-calculate results for common scenarios and cache them.
    
    Parameters:
    -----------
    calc_func : Callable
        Function that performs the calculation
    scenarios : List[Dict[str, Any]]
        List of parameter dictionaries for common scenarios
    key : str, optional
        Unique key for this cache
    
    Returns:
    --------
    Callable
        Wrapped function that uses pre-calculated results when possible
    
    Example:
    --------
    scenarios = [
        {"growth_rate": 0.05, "margin": 0.3},
        {"growth_rate": 0.1, "margin": 0.3},
        {"growth_rate": 0.05, "margin": 0.4}
    ]
    
    @pre_calculate_common_scenarios(scenarios)
    def calculate_financials(growth_rate, margin):
        # Complex calculation
        return result
    """
    # Generate a key if not provided
    if key is None:
        key = f"precalc_{calc_func.__name__}"
    
    cache_key = f"{key}_cache"
    
    def initialize_cache():
        """Initialize the cache with pre-calculated results."""
        if cache_key not in st.session_state:
            st.session_state[cache_key] = {}
            
            # Pre-calculate for each scenario
            for scenario in scenarios:
                # Create a cache key from the scenario parameters
                scenario_key = json.dumps(scenario, sort_keys=True)
                
                # Calculate and store the result
                st.session_state[cache_key][scenario_key] = calc_func(**scenario)
    
    # Initialize cache on first run
    initialize_cache()
    
    @functools.wraps(calc_func)
    def wrapper(*args, **kwargs):
        # Check if we have a pre-calculated result
        scenario_key = json.dumps(kwargs, sort_keys=True)
        
        if scenario_key in st.session_state[cache_key]:
            # Use pre-calculated result
            return st.session_state[cache_key][scenario_key]
        
        # Calculate and return the result
        return calc_func(*args, **kwargs)
    
    return wrapper

# -----------------------------------------------------------------------------
# Production Setup
# -----------------------------------------------------------------------------

def setup_production_features():
    """Initialize all production features."""
    # Initialize analytics
    if not st.session_state.get("analytics_initialized", False):
        init_analytics()
    
    # Initialize keyboard shortcuts
    if not st.session_state.get("keyboard_shortcuts_initialized", False):
        init_keyboard_shortcuts()
    
    # Inject custom error handler
    if not st.session_state.get("error_handler_initialized", False):
        js_code = """
        <script>
        // Global error handler
        window.addEventListener('error', function(event) {
            // Send error to Streamlit
            if (window.parent.postMessage) {
                window.parent.postMessage({
                    type: 'streamlit:clientError',
                    error: {
                        message: event.message,
                        filename: event.filename,
                        lineno: event.lineno,
                        colno: event.colno,
                        stack: event.error ? event.error.stack : null
                    }
                }, '*');
            }
            
            // Show toast notification
            const toast = document.createElement('div');
            toast.className = 'error-toast';
            toast.innerHTML = `
                <div class="error-toast-content">
                    <div class="error-toast-icon">⚠️</div>
                    <div class="error-toast-message">
                        Something went wrong. Please try again or refresh the page.
                    </div>
                    <div class="error-toast-close" onclick="this.parentNode.parentNode.remove()">×</div>
                </div>
            `;
            document.body.appendChild(toast);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                toast.remove();
            }, 5000);
            
            // Don't prevent default error handling
            return false;
        });
        </script>
        
        <style>
        .error-toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
            animation: slideIn 0.3s ease-in-out;
        }
        
        .error-toast-content {
            background: rgba(239, 68, 68, 0.9);
            color: white;
            padding: 12px 16px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .error-toast-icon {
            margin-right: 12px;
            font-size: 20px;
        }
        
        .error-toast-message {
            flex: 1;
            font-size: 14px;
        }
        
        .error-toast-close {
            cursor: pointer;
            font-size: 20px;
            margin-left: 12px;
        }
        
        @keyframes slideIn {
            from { transform: translateY(100%); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        </style>
        """
        
        # Inject the script
        st.markdown(js_code, unsafe_allow_html=True)
        st.session_state.error_handler_initialized = True

# -----------------------------------------------------------------------------
# Quick Action Palette
# -----------------------------------------------------------------------------

def show_quick_action_palette(actions: List[Dict[str, Any]]):
    """
    Show a quick action palette triggered by Cmd+K.
    
    Parameters:
    -----------
    actions : List[Dict[str, Any]]
        List of actions, each with 'name', 'description', and 'callback' keys
    
    Example:
    --------
    actions = [
        {
            'name': 'Export PDF',
            'description': 'Export current view as PDF',
            'callback': lambda: export_pdf()
        },
        {
            'name': 'Reset Model',
            'description': 'Reset all inputs to defaults',
            'callback': lambda: reset_model()
        }
    ]
    
    show_quick_action_palette(actions)
    """
    # Check if we should show the palette
    if not st.session_state.get("show_quick_actions", False):
        return
    
    # Create a modal dialog
    with st.container():
        st.markdown("""
        <div class="quick-action-overlay">
            <div class="quick-action-palette">
                <div class="quick-action-header">
                    <h3>Quick Actions</h3>
                    <div class="quick-action-search">
                        <input type="text" placeholder="Search actions..." id="quick-action-search">
                    </div>
                </div>
                <div class="quick-action-list">
        """, unsafe_allow_html=True)
        
        # Add each action as a button
        for i, action in enumerate(actions):
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(action["name"], key=f"quick_action_{i}"):
                    # Hide the palette
                    st.session_state.show_quick_actions = False
                    # Execute the callback
                    action["callback"]()
            with col2:
                st.caption(action["description"])
        
        st.markdown("""
                </div>
                <div class="quick-action-footer">
                    <div class="quick-action-tip">
                        Press <span class="keyboard-shortcut">Esc</span> to close
                    </div>
                </div>
            </div>
        </div>
        
        <style>
        .quick-action-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(15, 23, 42, 0.8);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(4px);
        }
        
        .quick-action-palette {
            background: var(--color-surface);
            border-radius: 8px;
            width: 500px;
            max-width: 90vw;
            max-height: 80vh;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            display: flex;
            flex-direction: column;
        }
        
        .quick-action-header {
            padding: 16px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.2);
        }
        
        .quick-action-header h3 {
            margin: 0 0 8px 0;
            color: var(--color-primary);
        }
        
        .quick-action-search input {
            width: 100%;
            padding: 8px 12px;
            border-radius: 4px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            background: var(--color-background);
            color: var(--color-text);
        }
        
        .quick-action-list {
            padding: 8px 16px;
            overflow-y: auto;
            flex: 1;
        }
        
        .quick-action-footer {
            padding: 12px 16px;
            border-top: 1px solid rgba(148, 163, 184, 0.2);
            display: flex;
            justify-content: flex-end;
        }
        
        .quick-action-tip {
            font-size: 12px;
            color: var(--color-text-secondary);
        }
        </style>
        
        <script>
        // Focus search input when palette opens
        document.getElementById('quick-action-search').focus();
        
        // Close on Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                // Send message to Streamlit to close the palette
                if (window.parent.postMessage) {
                    window.parent.postMessage({
                        type: 'streamlit:closeQuickActions'
                    }, '*');
                }
            }
        });
        
        // Handle search filtering
        document.getElementById('quick-action-search').addEventListener('input', function(event) {
            const searchTerm = event.target.value.toLowerCase();
            const actionButtons = document.querySelectorAll('.quick-action-list button');
            
            actionButtons.forEach(button => {
                const actionName = button.textContent.toLowerCase();
                const actionRow = button.closest('.row-widget');
                
                if (actionName.includes(searchTerm)) {
                    actionRow.style.display = 'flex';
                } else {
                    actionRow.style.display = 'none';
                }
            });
        });
        </script>
        """, unsafe_allow_html=True)
    
    # Add a way to close the palette by clicking outside
    if st.button("Close", key="close_quick_actions"):
        st.session_state.show_quick_actions = False
        st.experimental_rerun()

# Example usage
if __name__ == "__main__":
    st.title("Production Features Demo")
    
    # Setup production features
    setup_production_features()
    
    # Track page view
    track_page_view("Demo Page")
    
    # Demo error boundary
    st.header("Error Boundary")
    
    @error_boundary("Failed to divide numbers", fallback_value=0)
    def divide(a, b):
        return a / b
    
    col1, col2 = st.columns(2)
    with col1:
        a = st.number_input("Numerator", value=10)
    with col2:
        b = st.number_input("Denominator", value=2)
    
    result = divide(a, b)
    st.write(f"Result: {result}")
    
    # Demo loading state
    st.header("Loading State")
    
    @loading_state("Performing complex calculation...")
    def complex_calculation():
        time.sleep(3)  # Simulate work
        return 42
    
    if st.button("Start Calculation"):
        result = complex_calculation()
        st.success(f"Calculation complete! Result: {result}")
    
    # Demo keyboard shortcuts
    st.header("Keyboard Shortcuts")
    st.info("Press Cmd+K (or Ctrl+K) to open the quick action palette")
    
    # Demo lazy loading
    st.header("Lazy Loading")
    
    def placeholder():
        st.info("This chart will only load when you need it")
        if st.button("Load Chart"):
            st.session_state.load_chart = True
    
    def load_chart():
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Create a chart
        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        ax.set_title("Sine Wave")
        
        return fig
    
    chart = lazy_load(placeholder, load_chart, "chart")
    if chart is not None:
        st.pyplot(chart)
    
    # Demo debounced input
    st.header("Debounced Input")
    
    @debounce(0.3)
    def on_slider_change(value):
        st.session_state.slider_result = value * 2
    
    slider_value = st.slider("Adjust slider", 0, 100, 50, 
                            on_change=lambda: on_slider_change(st.session_state.slider))
    
    st.write(f"Debounced result: {st.session_state.get('slider_result', 100)}")
    
    # Demo quick action palette
    actions = [
        {
            'name': 'Export PDF',
            'description': 'Export as PDF',
            'callback': lambda: st.success("PDF exported!")
        },
        {
            'name': 'Reset Model',
            'description': 'Reset to defaults',
            'callback': lambda: st.info("Model reset!")
        },
        {
            'name': 'Share Link',
            'description': 'Generate shareable URL',
            'callback': lambda: st.success("Link copied to clipboard!")
        }
    ]
    
    show_quick_action_palette(actions)
