import streamlit as st
import time
import threading
import functools
import json
import uuid
import inspect
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast, Union, Tuple
import numpy as np
import pandas as pd

# Type variables for better type hinting
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

# -----------------------------------------------------------------------------
# Lazy Loading Components
# -----------------------------------------------------------------------------

def lazy_load(
    placeholder_func: Callable[[], None], 
    load_func: Callable[[], T], 
    key: Optional[str] = None,
    show_loading: bool = True,
    auto_load_threshold: Optional[float] = None
) -> Optional[T]:
    """
    Lazy load a component only when it's needed to improve initial page load time.
    
    Parameters:
    -----------
    placeholder_func : Callable[[], None]
        Function to create a placeholder UI (shown until component is loaded)
    load_func : Callable[[], T]
        Function that loads and returns the actual component
    key : str, optional
        Unique key for this lazy loading instance
    show_loading : bool, optional
        Whether to show a loading spinner during loading
    auto_load_threshold : float, optional
        If set, automatically load the component after this many seconds
    
    Returns:
    --------
    Optional[T]
        Result of the load_func when loaded, None otherwise
    
    Example:
    --------
    def placeholder():
        st.info("Click to load the sensitivity heatmap")
        if st.button("Load Heatmap"):
            st.session_state.load_heatmap = True
    
    def load_heatmap():
        return create_sensitivity_heatmap(data)
    
    heatmap = lazy_load(placeholder, load_heatmap, "sensitivity_heatmap")
    if heatmap is not None:
        st.plotly_chart(heatmap)
    """
    # Generate a key if not provided
    if key is None:
        key = f"lazy_load_{uuid.uuid4().hex[:8]}"
    
    load_key = f"load_{key}"
    result_key = f"result_{key}"
    timer_key = f"timer_{key}"
    
    # Set up auto-loading timer if threshold is provided
    if auto_load_threshold is not None and timer_key not in st.session_state:
        def trigger_load():
            time.sleep(auto_load_threshold)
            st.session_state[load_key] = True
            st.experimental_rerun()
        
        timer = threading.Thread(target=trigger_load, daemon=True)
        st.session_state[timer_key] = timer
        timer.start()
    
    # Check if we should load the component
    if not st.session_state.get(load_key, False):
        # Show placeholder
        placeholder_func()
        return None
    
    # Check if we've already loaded the result
    if result_key not in st.session_state:
        # Show loading spinner if requested
        if show_loading:
            with st.spinner(f"Loading component..."):
                st.session_state[result_key] = load_func()
        else:
            st.session_state[result_key] = load_func()
    
    # Return the loaded result
    return st.session_state[result_key]

def lazy_load_tabs(
    tab_configs: Dict[str, Callable[[], Any]],
    default_tab: Optional[str] = None,
    key: Optional[str] = None
) -> str:
    """
    Lazy load tab content only when a tab is selected to improve performance.
    
    Parameters:
    -----------
    tab_configs : Dict[str, Callable[[], Any]]
        Dictionary mapping tab names to functions that render tab content
    default_tab : str, optional
        Name of the default tab to show
    key : str, optional
        Unique key for this lazy loading tabs instance
    
    Returns:
    --------
    str
        Name of the currently selected tab
    
    Example:
    --------
    tab_configs = {
        "Overview": render_overview_tab,
        "Financial Details": render_financial_tab,
        "Sensitivity Analysis": render_sensitivity_tab
    }
    
    selected_tab = lazy_load_tabs(tab_configs, default_tab="Overview")
    """
    # Generate a key if not provided
    if key is None:
        key = f"lazy_tabs_{uuid.uuid4().hex[:8]}"
    
    active_tab_key = f"{key}_active_tab"
    
    # Initialize active tab if not already set
    if active_tab_key not in st.session_state:
        st.session_state[active_tab_key] = default_tab or list(tab_configs.keys())[0]
    
    # Create tabs
    tab_names = list(tab_configs.keys())
    tabs = st.tabs(tab_names)
    
    # Render content only for the active tab
    for i, (tab_name, tab_content_func) in enumerate(tab_configs.items()):
        with tabs[i]:
            if st.session_state[active_tab_key] == tab_name:
                # This is the active tab, render its content
                tab_content_func()
                
                # Update active tab in session state
                st.session_state[active_tab_key] = tab_name
    
    return st.session_state[active_tab_key]

def visibility_based_loading(
    content_func: Callable[[], T],
    container_key: str,
    check_interval: float = 0.5,
    key: Optional[str] = None
) -> Optional[T]:
    """
    Load content only when its container becomes visible in the viewport.
    
    Parameters:
    -----------
    content_func : Callable[[], T]
        Function that generates the content
    container_key : str
        CSS selector for the container to check visibility
    check_interval : float, optional
        How often to check for visibility (in seconds)
    key : str, optional
        Unique key for this instance
    
    Returns:
    --------
    Optional[T]
        Result of content_func when loaded, None otherwise
    
    Example:
    --------
    chart = visibility_based_loading(
        lambda: create_complex_chart(data),
        container_key="#chart-container"
    )
    if chart is not None:
        st.plotly_chart(chart)
    """
    # Generate a key if not provided
    if key is None:
        key = f"visibility_{uuid.uuid4().hex[:8]}"
    
    loaded_key = f"{key}_loaded"
    result_key = f"{key}_result"
    
    # Inject visibility detection JavaScript
    if loaded_key not in st.session_state:
        js_code = f"""
        <script>
        // Function to check if element is in viewport
        function isElementInViewport(el) {{
            var rect = el.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        }}
        
        // Set up intersection observer for the container
        function setupObserver() {{
            var container = document.querySelector('{container_key}');
            if (!container) {{
                setTimeout(setupObserver, {int(check_interval * 1000)});
                return;
            }}
            
            var observer = new IntersectionObserver(function(entries) {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        // Container is visible, notify Streamlit
                        if (window.parent.postMessage) {{
                            window.parent.postMessage({{
                                type: 'streamlit:setComponentValue',
                                value: JSON.stringify({{
                                    key: '{loaded_key}',
                                    value: true
                                }})
                            }}, '*');
                        }}
                        
                        // Disconnect observer after triggering load
                        observer.disconnect();
                    }}
                }});
            }}, {{ threshold: 0.1 }});
            
            observer.observe(container);
        }}
        
        // Start observing when the DOM is ready
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', setupObserver);
        }} else {{
            setupObserver();
        }}
        </script>
        """
        
        st.markdown(js_code, unsafe_allow_html=True)
    
    # Check if the container is visible
    if st.session_state.get(loaded_key, False) and result_key not in st.session_state:
        with st.spinner("Loading content..."):
            st.session_state[result_key] = content_func()
    
    # Return the result if loaded
    return st.session_state.get(result_key)

# -----------------------------------------------------------------------------
# Input Debouncing
# -----------------------------------------------------------------------------

def debounce(wait_time: float = 0.3) -> Callable[[F], F]:
    """
    Decorator to debounce a function call, preventing excessive recalculations.
    
    Parameters:
    -----------
    wait_time : float, optional
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
            if timer_key in st.session_state and hasattr(st.session_state[timer_key], 'cancel'):
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

def debounced_callback(
    callback: Callable[..., Any],
    wait_time: float = 0.3,
    key: Optional[str] = None
) -> Callable[..., None]:
    """
    Create a debounced version of a callback function.
    
    Parameters:
    -----------
    callback : Callable
        The callback function to debounce
    wait_time : float, optional
        Time to wait in seconds before executing the function
    key : str, optional
        Unique key for this debounced callback
    
    Returns:
    --------
    Callable
        Debounced version of the callback
    
    Example:
    --------
    def update_chart(value):
        st.session_state.chart_data = calculate_data(value)
    
    debounced_update = debounced_callback(update_chart, 0.3, "chart_update")
    
    value = st.slider("Parameter", 0, 100, 50, on_change=debounced_update)
    """
    # Generate a key if not provided
    if key is None:
        key = f"debounced_{uuid.uuid4().hex[:8]}"
    
    last_call_time_key = f"{key}_last_call_time"
    timer_key = f"{key}_timer"
    
    def debounced_func(*args, **kwargs):
        # Record the current time
        current_time = time.time()
        st.session_state[last_call_time_key] = current_time
        
        # Define a function to execute after the wait time
        def execute_callback():
            # Only execute if this is still the most recent call
            if st.session_state.get(last_call_time_key) == current_time:
                callback(*args, **kwargs)
        
        # Cancel any existing timer
        if timer_key in st.session_state and hasattr(st.session_state[timer_key], 'cancel'):
            st.session_state[timer_key].cancel()
        
        # Create a new timer
        timer = threading.Timer(wait_time, execute_callback)
        timer.daemon = True
        st.session_state[timer_key] = timer
        timer.start()
    
    return debounced_func

def throttle(interval: float = 0.1) -> Callable[[F], F]:
    """
    Decorator to throttle a function call, ensuring it's not called more than once per interval.
    
    Parameters:
    -----------
    interval : float, optional
        Minimum time between function calls in seconds
    
    Returns:
    --------
    Callable
        Decorated function that will be throttled
    
    Example:
    --------
    @throttle(0.1)
    def on_mouse_move(x, y):
        # This won't be called more than 10 times per second
        update_hover_info(x, y)
    """
    def decorator(func: F) -> F:
        # Use function name as part of the key to avoid conflicts
        func_name = func.__name__
        last_call_time_key = f"throttle_last_call_time_{func_name}"
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            last_call_time = st.session_state.get(last_call_time_key, 0)
            
            # Check if enough time has passed since the last call
            if current_time - last_call_time >= interval:
                # Update the last call time
                st.session_state[last_call_time_key] = current_time
                # Call the function
                return func(*args, **kwargs)
            
            # Skip this call
            return None
        
        return cast(F, wrapper)
    
    return decorator

# -----------------------------------------------------------------------------
# Calculation Caching
# -----------------------------------------------------------------------------

def smart_cache_data(
    ttl: Optional[int] = None,
    max_entries: Optional[int] = None,
    show_spinner: bool = True
) -> Callable[[F], F]:
    """
    Enhanced version of st.cache_data with additional features.
    
    Parameters:
    -----------
    ttl : int, optional
        Time to live in seconds
    max_entries : int, optional
        Maximum number of entries to keep in cache
    show_spinner : bool, optional
        Whether to show a spinner during computation
    
    Returns:
    --------
    Callable
        Decorated function with smart caching
    
    Example:
    --------
    @smart_cache_data(ttl=3600, show_spinner=True)
    def fetch_financial_data(ticker):
        # Expensive API call or computation
        return data
    """
    def decorator(func: F) -> F:
        # Use st.cache_data as the base
        cached_func = st.cache_data(
            ttl=ttl,
            max_entries=max_entries,
            show_spinner=show_spinner
        )(func)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Convert args to a stable representation for cache key
            cache_key = str(bound_args.arguments)
            
            # Add cache hit/miss tracking
            if "cache_stats" not in st.session_state:
                st.session_state.cache_stats = {}
            
            if func.__name__ not in st.session_state.cache_stats:
                st.session_state.cache_stats[func.__name__] = {
                    "hits": 0,
                    "misses": 0,
                    "last_access": time.time(),
                    "computation_time": 0
                }
            
            # Check if this is a cache hit (approximate)
            is_hit = cache_key in getattr(st.session_state, f"_cache_keys_{func.__name__}", set())
            
            if is_hit:
                st.session_state.cache_stats[func.__name__]["hits"] += 1
            else:
                st.session_state.cache_stats[func.__name__]["misses"] += 1
                
                # Track computation time for cache misses
                start_time = time.time()
                result = cached_func(*args, **kwargs)
                computation_time = time.time() - start_time
                
                st.session_state.cache_stats[func.__name__]["computation_time"] = computation_time
                
                # Store cache key for hit/miss tracking
                if not hasattr(st.session_state, f"_cache_keys_{func.__name__}"):
                    setattr(st.session_state, f"_cache_keys_{func.__name__}", set())
                
                getattr(st.session_state, f"_cache_keys_{func.__name__}").add(cache_key)
                
                return result
            
            # Update last access time
            st.session_state.cache_stats[func.__name__]["last_access"] = time.time()
            
            # Call the cached function
            return cached_func(*args, **kwargs)
        
        return cast(F, wrapper)
    
    return decorator

def get_cache_stats() -> Dict[str, Dict[str, Any]]:
    """
    Get statistics about cache usage.
    
    Returns:
    --------
    Dict[str, Dict[str, Any]]
        Dictionary with cache statistics for each cached function
    """
    return st.session_state.get("cache_stats", {})

def clear_function_cache(func_name: Optional[str] = None) -> None:
    """
    Clear the cache for a specific function or all functions.
    
    Parameters:
    -----------
    func_name : str, optional
        Name of the function to clear cache for, or None to clear all
    """
    if func_name is None:
        # Clear all caches
        st.cache_data.clear()
        # Reset cache stats
        st.session_state.cache_stats = {}
    else:
        # Clear specific function cache
        st.cache_data.clear(func_name)
        # Reset cache stats for this function
        if "cache_stats" in st.session_state and func_name in st.session_state.cache_stats:
            st.session_state.cache_stats[func_name] = {
                "hits": 0,
                "misses": 0,
                "last_access": time.time(),
                "computation_time": 0
            }

# -----------------------------------------------------------------------------
# Pre-computation of Common Scenarios
# -----------------------------------------------------------------------------

def pre_calculate_scenarios(
    calc_func: Callable[..., T], 
    scenarios: List[Dict[str, Any]],
    key: Optional[str] = None
) -> Callable[..., T]:
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
    
    @pre_calculate_scenarios(scenarios)
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
            for i, scenario in enumerate(scenarios):
                # Create a cache key from the scenario parameters
                scenario_key = json.dumps(scenario, sort_keys=True)
                
                # Calculate and store the result
                with st.spinner(f"Pre-calculating scenario {i+1}/{len(scenarios)}..."):
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

def generate_parameter_grid(
    param_ranges: Dict[str, List[Any]], 
    base_params: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Generate a grid of parameter combinations for pre-calculation.
    
    Parameters:
    -----------
    param_ranges : Dict[str, List[Any]]
        Dictionary mapping parameter names to lists of values
    base_params : Dict[str, Any], optional
        Base parameters to include in all combinations
    
    Returns:
    --------
    List[Dict[str, Any]]
        List of parameter dictionaries for all combinations
    
    Example:
    --------
    param_ranges = {
        "growth_rate": [0.05, 0.1, 0.15],
        "margin": [0.3, 0.4, 0.5]
    }
    base_params = {"years": 5, "initial_investment": 1000000}
    
    scenarios = generate_parameter_grid(param_ranges, base_params)
    """
    # Start with an empty list
    scenarios = [{}]
    
    # Generate all combinations
    for param_name, param_values in param_ranges.items():
        new_scenarios = []
        for scenario in scenarios:
            for value in param_values:
                new_scenario = scenario.copy()
                new_scenario[param_name] = value
                new_scenarios.append(new_scenario)
        scenarios = new_scenarios
    
    # Add base parameters to all scenarios
    if base_params:
        for scenario in scenarios:
            for key, value in base_params.items():
                if key not in scenario:
                    scenario[key] = value
    
    return scenarios

def memoize_expensive_operation(max_size: int = 128) -> Callable[[F], F]:
    """
    Decorator to memoize expensive operations with LRU cache.
    
    Parameters:
    -----------
    max_size : int, optional
        Maximum number of results to cache
    
    Returns:
    --------
    Callable
        Decorated function with memoization
    
    Example:
    --------
    @memoize_expensive_operation(max_size=64)
    def calculate_monte_carlo(iterations=1000, volatility=0.2):
        # Expensive simulation
        return results
    """
    def decorator(func: F) -> F:
        # Use function name as part of the key to avoid conflicts
        func_name = func.__name__
        cache_key = f"memoize_{func_name}"
        
        # Initialize cache if needed
        if cache_key not in st.session_state:
            st.session_state[cache_key] = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from the arguments
            arg_key = str(args) + str(sorted(kwargs.items()))
            arg_hash = hash(arg_key)
            
            # Check if result is in cache
            if arg_hash in st.session_state[cache_key]:
                return st.session_state[cache_key][arg_hash]["result"]
            
            # Calculate the result
            result = func(*args, **kwargs)
            
            # Store in cache with timestamp
            st.session_state[cache_key][arg_hash] = {
                "result": result,
                "timestamp": time.time()
            }
            
            # Trim cache if it's too large
            if len(st.session_state[cache_key]) > max_size:
                # Remove oldest entries
                sorted_entries = sorted(
                    st.session_state[cache_key].items(),
                    key=lambda x: x[1]["timestamp"]
                )
                
                # Keep only the newest max_size entries
                st.session_state[cache_key] = dict(sorted_entries[-max_size:])
            
            return result
        
        return cast(F, wrapper)
    
    return decorator

# -----------------------------------------------------------------------------
# Batch Processing and Parallel Computation
# -----------------------------------------------------------------------------

def batch_process(
    items: List[Any],
    process_func: Callable[[Any], T],
    batch_size: int = 10,
    show_progress: bool = True
) -> List[T]:
    """
    Process a large list of items in batches to prevent UI freezing.
    
    Parameters:
    -----------
    items : List[Any]
        List of items to process
    process_func : Callable[[Any], T]
        Function to process each item
    batch_size : int, optional
        Number of items to process in each batch
    show_progress : bool, optional
        Whether to show a progress bar
    
    Returns:
    --------
    List[T]
        List of processed items
    
    Example:
    --------
    def process_transaction(tx):
        # Complex processing
        return processed_data
    
    processed_data = batch_process(transactions, process_transaction)
    """
    results = []
    total_items = len(items)
    
    # Create progress bar if requested
    progress_bar = None
    if show_progress:
        progress_bar = st.progress(0.0)
    
    # Process in batches
    for i in range(0, total_items, batch_size):
        # Get current batch
        batch = items[i:i+batch_size]
        
        # Process batch
        batch_results = [process_func(item) for item in batch]
        results.extend(batch_results)
        
        # Update progress
        if progress_bar is not None:
            progress_bar.progress((i + len(batch)) / total_items)
        
        # Yield to UI thread briefly to prevent freezing
        time.sleep(0.01)
    
    # Clear progress bar
    if progress_bar is not None:
        progress_bar.empty()
    
    return results

def parallel_map(
    func: Callable[[Any], T],
    items: List[Any],
    max_workers: int = 4,
    show_progress: bool = True
) -> List[T]:
    """
    Process items in parallel using multiple threads.
    
    Parameters:
    -----------
    func : Callable[[Any], T]
        Function to apply to each item
    items : List[Any]
        List of items to process
    max_workers : int, optional
        Maximum number of worker threads
    show_progress : bool, optional
        Whether to show a progress bar
    
    Returns:
    --------
    List[T]
        List of results
    
    Example:
    --------
    def process_data_chunk(chunk):
        # CPU-bound processing
        return processed_chunk
    
    results = parallel_map(process_data_chunk, data_chunks)
    """
    from concurrent.futures import ThreadPoolExecutor
    
    total_items = len(items)
    results = [None] * total_items
    completed = [0]  # Mutable object to track progress
    
    # Create progress bar if requested
    progress_bar = None
    if show_progress:
        progress_bar = st.progress(0.0)
    
    def update_progress(future):
        completed[0] += 1
        if progress_bar is not None:
            progress_bar.progress(completed[0] / total_items)
    
    # Process in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = []
        for i, item in enumerate(items):
            future = executor.submit(func, item)
            future.add_done_callback(update_progress)
            futures.append((i, future))
        
        # Collect results in order
        for i, future in futures:
            results[i] = future.result()
    
    # Clear progress bar
    if progress_bar is not None:
        progress_bar.empty()
    
    return results

# -----------------------------------------------------------------------------
# Memory Optimization
# -----------------------------------------------------------------------------

def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize a DataFrame's memory usage by downcasting numeric types.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to optimize
    
    Returns:
    --------
    pd.DataFrame
        Optimized DataFrame
    
    Example:
    --------
    df = optimize_dataframe(large_dataframe)
    """
    # Make a copy to avoid modifying the original
    result = df.copy()
    
    # Optimize integer types
    int_cols = result.select_dtypes(include=['int']).columns
    for col in int_cols:
        col_min = result[col].min()
        col_max = result[col].max()
        
        # Determine the smallest integer type that can hold the data
        if col_min >= 0:
            if col_max < 2**8:
                result[col] = result[col].astype(np.uint8)
            elif col_max < 2**16:
                result[col] = result[col].astype(np.uint16)
            elif col_max < 2**32:
                result[col] = result[col].astype(np.uint32)
        else:
            if col_min > -2**7 and col_max < 2**7:
                result[col] = result[col].astype(np.int8)
            elif col_min > -2**15 and col_max < 2**15:
                result[col] = result[col].astype(np.int16)
            elif col_min > -2**31 and col_max < 2**31:
                result[col] = result[col].astype(np.int32)
    
    # Optimize float types
    float_cols = result.select_dtypes(include=['float']).columns
    for col in float_cols:
        result[col] = result[col].astype(np.float32)
    
    # Optimize object types (strings)
    obj_cols = result.select_dtypes(include=['object']).columns
    for col in obj_cols:
        # Check if the column contains only strings
        if result[col].apply(lambda x: isinstance(x, str)).all():
            # Check if the column has a small number of unique values
            if result[col].nunique() / len(result) < 0.5:
                result[col] = result[col].astype('category')
    
    return result

def cleanup_memory(keep_keys: Optional[List[str]] = None) -> None:
    """
    Clean up memory by removing unnecessary items from session state.
    
    Parameters:
    -----------
    keep_keys : List[str], optional
        Keys to keep in session state
    
    Example:
    --------
    # Keep only important state variables
    cleanup_memory(['user_settings', 'current_model'])
    """
    if keep_keys is None:
        keep_keys = []
    
    # Add keys that should always be kept
    always_keep = [
        "cache_stats",
        "analytics_initialized",
        "keyboard_shortcuts_initialized",
        "error_handler_initialized"
    ]
    
    keep_keys = set(keep_keys + always_keep)
    
    # Get all keys in session state
    all_keys = list(st.session_state.keys())
    
    # Remove keys that are not in the keep list
    for key in all_keys:
        if key not in keep_keys:
            # Skip keys that start with underscore (Streamlit internal)
            if key.startswith('_'):
                continue
                
            # Remove the key
            del st.session_state[key]

# -----------------------------------------------------------------------------
# Performance Monitoring
# -----------------------------------------------------------------------------

def measure_execution_time(func: F) -> F:
    """
    Decorator to measure and log the execution time of a function.
    
    Parameters:
    -----------
    func : Callable
        Function to measure
    
    Returns:
    --------
    Callable
        Decorated function with execution time measurement
    
    Example:
    --------
    @measure_execution_time
    def complex_calculation():
        # Expensive operation
        return result
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Store execution time in session state
        if "execution_times" not in st.session_state:
            st.session_state.execution_times = {}
        
        func_name = func.__name__
        if func_name not in st.session_state.execution_times:
            st.session_state.execution_times[func_name] = []
        
        st.session_state.execution_times[func_name].append({
            "time": execution_time,
            "timestamp": time.time()
        })
        
        # Keep only the last 100 measurements
        if len(st.session_state.execution_times[func_name]) > 100:
            st.session_state.execution_times[func_name] = st.session_state.execution_times[func_name][-100:]
        
        return result
    
    return cast(F, wrapper)

def get_execution_stats() -> Dict[str, Dict[str, float]]:
    """
    Get statistics about function execution times.
    
    Returns:
    --------
    Dict[str, Dict[str, float]]
        Dictionary with execution time statistics for each measured function
    """
    stats = {}
    
    if "execution_times" not in st.session_state:
        return stats
    
    for func_name, measurements in st.session_state.execution_times.items():
        if not measurements:
            continue
            
        times = [m["time"] for m in measurements]
        stats[func_name] = {
            "min": min(times),
            "max": max(times),
            "avg": sum(times) / len(times),
            "median": sorted(times)[len(times) // 2],
            "count": len(times),
            "last": times[-1]
        }
    
    return stats

# Example usage
if __name__ == "__main__":
    st.title("Performance Optimization Demo")
    
    st.header("1. Lazy Loading")
    
    def placeholder_func():
        st.info("This chart will only load when you need it")
        if st.button("Load Chart", key="load_chart_btn"):
            st.session_state.load_chart = True
    
    def load_chart_func():
        # Simulate expensive operation
        time.sleep(1)
        
        # Create a simple chart
        chart_data = pd.DataFrame({
            'x': range(10),
            'y': [i**2 for i in range(10)]
        })
        
        return chart_data
    
    chart_data = lazy_load(placeholder_func, load_chart_func, "demo_chart")
    if chart_data is not None:
        st.line_chart(chart_data, x='x', y='y')
    
    st.header("2. Input Debouncing")
    
    if "slider_value" not in st.session_state:
        st.session_state.slider_value = 50
        st.session_state.processed_value = 50
    
    @debounce(0.5)
    def process_slider_change():
        # Simulate processing
        time.sleep(0.2)
        st.session_state.processed_value = st.session_state.slider_value
    
    slider_value = st.slider(
        "Move this slider",
        0, 100, 50,
        key="slider_value",
        on_change=process_slider_change
    )
    
    st.write(f"Raw value: {slider_value}")
    st.write(f"Processed value (debounced): {st.session_state.processed_value}")
    
    st.header("3. Smart Caching")
    
    @smart_cache_data(ttl=60, show_spinner=True)
    def expensive_calculation(a, b):
        # Simulate expensive calculation
        time.sleep(2)
        return a * b
    
    col1, col2 = st.columns(2)
    with col1:
        a = st.number_input("Value A", value=5)
    with col2:
        b = st.number_input("Value B", value=10)
    
    result = expensive_calculation(a, b)
    st.write(f"Result: {result}")
    
    # Show cache stats
    cache_stats = get_cache_stats()
    if cache_stats:
        st.write("Cache Stats:", cache_stats)
    
    st.header("4. Pre-calculation of Common Scenarios")
    
    # Define common scenarios
    scenarios = generate_parameter_grid({
        "growth": [0.05, 0.1, 0.15],
        "years": [5, 10]
    }, {"base_value": 1000})
    
    @pre_calculate_scenarios(scenarios)
    def calculate_future_value(base_value, growth, years):
        # Simulate complex calculation
        time.sleep(1)
        return base_value * (1 + growth) ** years
    
    col1, col2 = st.columns(2)
    with col1:
        growth = st.selectbox("Growth Rate", [0.05, 0.1, 0.15, 0.2])
    with col2:
        years = st.selectbox("Years", [5, 10, 15])
    
    future_value = calculate_future_value(base_value=1000, growth=growth, years=years)
    st.write(f"Future Value: ${future_value:.2f}")
