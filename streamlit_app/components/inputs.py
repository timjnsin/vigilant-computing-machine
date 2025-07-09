import streamlit as st
import pandas as pd
import numpy as np
import uuid
import json
from typing import List, Dict, Optional, Union, Callable, Tuple, Any

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
    
    # Scenario colors
    "base": "#f59e0b",      # Gold for base
    "upside": "#10b981",    # Green for upside
    "downside": "#ef4444",  # Red for downside
    "custom": "#6366f1",    # Purple for custom
}

def inject_custom_css():
    """Inject custom CSS for premium input widgets."""
    if "inputs_css_injected" not in st.session_state:
        st.markdown("""
        <style>
        /* Premium Input Styling */
        .premium-input-container {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(245, 158, 11, 0.2);
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            margin-bottom: 1rem;
            position: relative;
            overflow: hidden;
        }
        
        .premium-input-container::before {
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
        
        .premium-input-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3), 0 0 15px rgba(245, 158, 11, 0.3);
            border: 1px solid rgba(245, 158, 11, 0.4);
        }
        
        .premium-input-label {
            color: #94a3b8;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .premium-input-value {
            color: #f59e0b;
            font-weight: 600;
            font-size: 1.2rem;
            margin: 0.25rem 0;
        }
        
        /* Percentage Allocator */
        .percentage-allocator {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .percentage-row {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .percentage-label {
            width: 100px;
            color: #94a3b8;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .percentage-slider {
            flex-grow: 1;
            position: relative;
        }
        
        .percentage-value {
            width: 60px;
            color: #f59e0b;
            font-weight: 600;
            font-size: 1rem;
            text-align: right;
        }
        
        .percentage-lock {
            width: 30px;
            color: #94a3b8;
            cursor: pointer;
            font-size: 1rem;
            text-align: center;
            transition: all 0.2s ease;
        }
        
        .percentage-lock:hover {
            color: #f59e0b;
        }
        
        .percentage-lock.locked {
            color: #f59e0b;
        }
        
        .percentage-preview {
            width: 120px;
            height: 120px;
            margin: 0 auto;
        }
        
        /* Scenario Toggle */
        .scenario-toggle-container {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            padding: 0.5rem;
        }
        
        .scenario-toggle {
            display: flex;
            background: rgba(15, 23, 42, 0.6);
            border-radius: 10px;
            padding: 0.25rem;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }
        
        .scenario-option {
            flex: 1;
            text-align: center;
            padding: 0.75rem 1rem;
            cursor: pointer;
            position: relative;
            z-index: 2;
            transition: all 0.3s ease;
            color: #94a3b8;
            font-weight: 500;
            border-radius: 8px;
        }
        
        .scenario-option.active {
            color: #f8fafc;
            font-weight: 600;
        }
        
        .scenario-slider {
            position: absolute;
            height: calc(100% - 0.5rem);
            top: 0.25rem;
            border-radius: 8px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 1;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }
        
        .scenario-delta {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 0.5rem;
            font-size: 0.9rem;
            color: #94a3b8;
        }
        
        .scenario-delta-value {
            font-weight: 600;
        }
        
        .scenario-delta-positive {
            color: #10b981;
        }
        
        .scenario-delta-negative {
            color: #ef4444;
        }
        
        /* Price Input */
        .price-input-container {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }
        
        .price-input-row {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .price-input-field {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(245, 158, 11, 0.2);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            color: #f8fafc;
            font-size: 1.1rem;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s ease;
        }
        
        .price-input-field:focus {
            outline: none;
            border-color: rgba(245, 158, 11, 0.6);
            box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.2);
        }
        
        .price-input-prefix {
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: #94a3b8;
            font-weight: 500;
            pointer-events: none;
        }
        
        .price-input-wrapper {
            position: relative;
            flex-grow: 1;
        }
        
        .price-input-field.with-prefix {
            padding-left: 1.5rem;
        }
        
        .price-reference {
            display: flex;
            justify-content: space-between;
            color: #94a3b8;
            font-size: 0.85rem;
            padding: 0 0.25rem;
        }
        
        .price-reference-value {
            color: #cbd5e1;
        }
        
        .price-margin {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin-top: 0.5rem;
        }
        
        .price-margin-label {
            color: #94a3b8;
            font-size: 0.9rem;
        }
        
        .price-margin-value {
            color: #10b981;
            font-weight: 600;
            margin-left: auto;
        }
        
        .price-margin.negative {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        
        .price-margin.negative .price-margin-value {
            color: #ef4444;
        }
        
        /* Quick Actions */
        .quick-actions-container {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .quick-actions-row {
            display: flex;
            gap: 1rem;
        }
        
        .quick-action-button {
            flex: 1;
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(245, 158, 11, 0.2);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            color: #f8fafc;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .quick-action-button:hover {
            background: rgba(30, 41, 59, 0.9);
            border-color: rgba(245, 158, 11, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        .quick-action-button.conservative {
            border-color: rgba(16, 185, 129, 0.3);
        }
        
        .quick-action-button.conservative:hover {
            border-color: rgba(16, 185, 129, 0.6);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
        }
        
        .quick-action-button.aggressive {
            border-color: rgba(239, 68, 68, 0.3);
        }
        
        .quick-action-button.aggressive:hover {
            border-color: rgba(239, 68, 68, 0.6);
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
        }
        
        .quick-action-button.reset {
            border-color: rgba(99, 102, 241, 0.3);
        }
        
        .quick-action-button.reset:hover {
            border-color: rgba(99, 102, 241, 0.6);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
        }
        
        .quick-action-icon {
            font-size: 1.2rem;
        }
        
        /* File Uploader */
        .file-upload-container {
            margin-top: 1rem;
            border: 2px dashed rgba(245, 158, 11, 0.3);
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .file-upload-container:hover {
            border-color: rgba(245, 158, 11, 0.6);
            background: rgba(245, 158, 11, 0.05);
        }
        
        .file-upload-icon {
            font-size: 2rem;
            color: rgba(245, 158, 11, 0.6);
            margin-bottom: 0.5rem;
        }
        
        .file-upload-text {
            color: #94a3b8;
            font-size: 0.9rem;
        }
        
        .file-upload-button {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.4);
            border-radius: 6px;
            padding: 0.5rem 1rem;
            margin-top: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            display: inline-block;
        }
        
        .file-upload-button:hover {
            background: rgba(245, 158, 11, 0.3);
            transform: translateY(-2px);
        }
        
        /* Confirmation Dialog */
        .confirmation-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(15, 23, 42, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            backdrop-filter: blur(4px);
            animation: fadeIn 0.3s ease-in-out;
        }
        
        .confirmation-dialog {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
            border-radius: 12px;
            border: 1px solid rgba(245, 158, 11, 0.3);
            padding: 1.5rem;
            width: 400px;
            max-width: 90vw;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            animation: slideUp 0.3s ease-in-out;
        }
        
        .confirmation-title {
            color: #f8fafc;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        .confirmation-message {
            color: #cbd5e1;
            margin-bottom: 1.5rem;
        }
        
        .confirmation-buttons {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
        }
        
        .confirmation-button {
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .confirmation-button.confirm {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.4);
        }
        
        .confirmation-button.confirm:hover {
            background: rgba(239, 68, 68, 0.3);
            transform: translateY(-2px);
        }
        
        .confirmation-button.cancel {
            background: rgba(148, 163, 184, 0.2);
            color: #cbd5e1;
            border: 1px solid rgba(148, 163, 184, 0.4);
        }
        
        .confirmation-button.cancel:hover {
            background: rgba(148, 163, 184, 0.3);
            transform: translateY(-2px);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
        """, unsafe_allow_html=True)
        st.session_state.inputs_css_injected = True

def inject_js_for_inputs():
    """Inject JavaScript for premium input widgets."""
    if "inputs_js_injected" not in st.session_state:
        st.markdown("""
        <script>
        // Helper function to format currency
        function formatCurrency(value) {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(value);
        }
        
        // Helper function to format percentage
        function formatPercentage(value) {
            return new Intl.NumberFormat('en-US', {
                style: 'percent',
                minimumFractionDigits: 1,
                maximumFractionDigits: 1
            }).format(value / 100);
        }
        
        // Function to handle percentage allocation
        function handlePercentageChange(id, value, locks) {
            const container = document.getElementById(id);
            if (!container) return;
            
            const sliders = container.querySelectorAll('.percentage-slider input');
            const values = container.querySelectorAll('.percentage-value');
            const locks = container.querySelectorAll('.percentage-lock');
            
            // Get current values and locked status
            const currentValues = [];
            const lockedStatus = [];
            let lockedSum = 0;
            let unlockedCount = 0;
            
            sliders.forEach((slider, i) => {
                const val = parseFloat(slider.value);
                const locked = locks[i].classList.contains('locked');
                currentValues.push(val);
                lockedStatus.push(locked);
                
                if (locked) {
                    lockedSum += val;
                } else {
                    unlockedCount++;
                }
            });
            
            // Calculate remaining percentage for unlocked sliders
            const remaining = 100 - lockedSum;
            const perUnlocked = unlockedCount > 0 ? remaining / unlockedCount : 0;
            
            // Adjust unlocked sliders
            sliders.forEach((slider, i) => {
                if (!lockedStatus[i]) {
                    slider.value = perUnlocked;
                    values[i].textContent = formatPercentage(perUnlocked);
                }
            });
            
            // Update pie chart if present
            updatePercentagePie(id, currentValues);
            
            // Send data to Streamlit
            if (window.parent.postMessage) {
                const payload = {
                    id: id,
                    type: 'percentage_allocator',
                    data: currentValues
                };
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: JSON.stringify(payload)
                }, '*');
            }
        }
        
        // Function to toggle percentage lock
        function togglePercentageLock(id, index) {
            const container = document.getElementById(id);
            if (!container) return;
            
            const locks = container.querySelectorAll('.percentage-lock');
            locks[index].classList.toggle('locked');
            
            // Count locked sliders
            let lockedCount = 0;
            locks.forEach(lock => {
                if (lock.classList.contains('locked')) {
                    lockedCount++;
                }
            });
            
            // If all are locked, unlock the last one toggled
            if (lockedCount === locks.length) {
                locks[index].classList.remove('locked');
            }
            
            // Recalculate percentages
            handlePercentageChange(id);
        }
        
        // Function to update percentage pie chart
        function updatePercentagePie(id, values) {
            const container = document.getElementById(id);
            if (!container) return;
            
            const canvas = container.querySelector('.percentage-preview canvas');
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            const colors = ['#4472C4', '#FFD966', '#A5A5A5'];
            
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw pie chart
            let startAngle = 0;
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const radius = Math.min(centerX, centerY) * 0.9;
            
            values.forEach((value, i) => {
                const endAngle = startAngle + (value / 100) * Math.PI * 2;
                
                ctx.beginPath();
                ctx.moveTo(centerX, centerY);
                ctx.arc(centerX, centerY, radius, startAngle, endAngle);
                ctx.closePath();
                
                ctx.fillStyle = colors[i % colors.length];
                ctx.fill();
                
                startAngle = endAngle;
            });
            
            // Draw center circle for donut effect
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius * 0.6, 0, Math.PI * 2);
            ctx.fillStyle = '#0f172a';
            ctx.fill();
        }
        
        // Function to handle scenario toggle
        function setScenario(id, scenario) {
            const container = document.getElementById(id);
            if (!container) return;
            
            const options = container.querySelectorAll('.scenario-option');
            const slider = container.querySelector('.scenario-slider');
            
            // Remove active class from all options
            options.forEach(option => {
                option.classList.remove('active');
            });
            
            // Add active class to selected option
            let index = 0;
            options.forEach((option, i) => {
                if (option.getAttribute('data-scenario') === scenario) {
                    option.classList.add('active');
                    index = i;
                }
            });
            
            // Move slider
            if (slider) {
                const width = 100 / options.length;
                slider.style.left = `${width * index}%`;
                slider.style.width = `${width}%`;
                
                // Set slider color based on scenario
                switch (scenario) {
                    case 'base':
                        slider.style.background = '#f59e0b';
                        break;
                    case 'upside':
                        slider.style.background = '#10b981';
                        break;
                    case 'downside':
                        slider.style.background = '#ef4444';
                        break;
                    case 'custom':
                        slider.style.background = '#6366f1';
                        break;
                }
            }
            
            // Send data to Streamlit
            if (window.parent.postMessage) {
                const payload = {
                    id: id,
                    type: 'scenario_toggle',
                    data: scenario
                };
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: JSON.stringify(payload)
                }, '*');
            }
        }
        
        // Function to handle price input
        function handlePriceInput(id, value) {
            const container = document.getElementById(id);
            if (!container) return;
            
            // Format the input as currency
            const numericValue = parseFloat(value.replace(/[^0-9.-]+/g, ''));
            if (!isNaN(numericValue)) {
                // Format the display value
                const formattedValue = formatCurrency(numericValue);
                container.querySelector('input').value = formattedValue;
                
                // Calculate and update margin if cost data is available
                const costElement = container.querySelector('[data-cost]');
                if (costElement) {
                    const cost = parseFloat(costElement.getAttribute('data-cost'));
                    const margin = numericValue - cost;
                    const marginPercent = (margin / numericValue) * 100;
                    
                    const marginElement = container.querySelector('.price-margin-value');
                    const marginContainer = container.querySelector('.price-margin');
                    
                    if (marginElement) {
                        marginElement.textContent = `${formatCurrency(margin)} (${marginPercent.toFixed(1)}%)`;
                        
                        // Update margin color based on value
                        if (margin > 0) {
                            marginContainer.classList.remove('negative');
                        } else {
                            marginContainer.classList.add('negative');
                        }
                    }
                }
                
                // Send data to Streamlit
                if (window.parent.postMessage) {
                    const payload = {
                        id: id,
                        type: 'price_input',
                        data: numericValue
                    };
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: JSON.stringify(payload)
                    }, '*');
                }
            }
        }
        
        // Function to show confirmation dialog
        function showConfirmation(id, message, callback) {
            // Create overlay
            const overlay = document.createElement('div');
            overlay.className = 'confirmation-overlay';
            
            // Create dialog
            const dialog = document.createElement('div');
            dialog.className = 'confirmation-dialog';
            
            // Create title
            const title = document.createElement('div');
            title.className = 'confirmation-title';
            title.textContent = 'Confirm Action';
            
            // Create message
            const messageElement = document.createElement('div');
            messageElement.className = 'confirmation-message';
            messageElement.textContent = message;
            
            // Create buttons container
            const buttons = document.createElement('div');
            buttons.className = 'confirmation-buttons';
            
            // Create confirm button
            const confirmButton = document.createElement('button');
            confirmButton.className = 'confirmation-button confirm';
            confirmButton.textContent = 'Confirm';
            confirmButton.onclick = () => {
                document.body.removeChild(overlay);
                
                // Send confirmation to Streamlit
                if (window.parent.postMessage) {
                    const payload = {
                        id: id,
                        type: 'confirmation',
                        data: true
                    };
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: JSON.stringify(payload)
                    }, '*');
                }
            };
            
            // Create cancel button
            const cancelButton = document.createElement('button');
            cancelButton.className = 'confirmation-button cancel';
            cancelButton.textContent = 'Cancel';
            cancelButton.onclick = () => {
                document.body.removeChild(overlay);
            };
            
            // Assemble dialog
            buttons.appendChild(cancelButton);
            buttons.appendChild(confirmButton);
            dialog.appendChild(title);
            dialog.appendChild(messageElement);
            dialog.appendChild(buttons);
            overlay.appendChild(dialog);
            
            // Add to body
            document.body.appendChild(overlay);
        }
        
        // Initialize all percentage allocators
        document.addEventListener('DOMContentLoaded', () => {
            document.querySelectorAll('.percentage-allocator').forEach(container => {
                const id = container.id;
                const sliders = container.querySelectorAll('.percentage-slider input');
                const values = container.querySelectorAll('.percentage-value');
                const locks = container.querySelectorAll('.percentage-lock');
                
                // Initialize pie chart
                const canvas = container.querySelector('.percentage-preview canvas');
                if (canvas) {
                    const currentValues = [];
                    sliders.forEach(slider => {
                        currentValues.push(parseFloat(slider.value));
                    });
                    updatePercentagePie(id, currentValues);
                }
                
                // Add event listeners
                sliders.forEach((slider, i) => {
                    slider.addEventListener('input', () => {
                        values[i].textContent = formatPercentage(slider.value);
                        handlePercentageChange(id);
                    });
                });
                
                locks.forEach((lock, i) => {
                    lock.addEventListener('click', () => {
                        togglePercentageLock(id, i);
                    });
                });
            });
            
            // Initialize scenario toggles
            document.querySelectorAll('.scenario-toggle-container').forEach(container => {
                const id = container.id;
                const options = container.querySelectorAll('.scenario-option');
                
                options.forEach(option => {
                    option.addEventListener('click', () => {
                        const scenario = option.getAttribute('data-scenario');
                        setScenario(id, scenario);
                    });
                });
            });
            
            // Initialize price inputs
            document.querySelectorAll('.price-input-container').forEach(container => {
                const id = container.id;
                const input = container.querySelector('input');
                
                input.addEventListener('input', (e) => {
                    handlePriceInput(id, e.target.value);
                });
                
                input.addEventListener('focus', () => {
                    input.select();
                });
                
                // Format initial value
                if (input.value) {
                    handlePriceInput(id, input.value);
                }
            });
            
            // Initialize quick actions
            document.querySelectorAll('.quick-action-button').forEach(button => {
                const action = button.getAttribute('data-action');
                const id = button.closest('.quick-actions-container').id;
                
                button.addEventListener('click', () => {
                    if (action === 'reset') {
                        showConfirmation(id, 'Are you sure you want to reset all values to defaults?');
                    } else {
                        // Send action to Streamlit
                        if (window.parent.postMessage) {
                            const payload = {
                                id: id,
                                type: 'quick_action',
                                data: action
                            };
                            window.parent.postMessage({
                                type: 'streamlit:setComponentValue',
                                value: JSON.stringify(payload)
                            }, '*');
                        }
                    }
                });
            });
        });
        
        // MutationObserver to detect new input widgets added to the DOM
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // Check for percentage allocators
                            const allocators = node.querySelectorAll ? 
                                node.querySelectorAll('.percentage-allocator') : [];
                            
                            allocators.forEach(container => {
                                const id = container.id;
                                const sliders = container.querySelectorAll('.percentage-slider input');
                                const values = container.querySelectorAll('.percentage-value');
                                const locks = container.querySelectorAll('.percentage-lock');
                                
                                // Initialize pie chart
                                const canvas = container.querySelector('.percentage-preview canvas');
                                if (canvas) {
                                    const currentValues = [];
                                    sliders.forEach(slider => {
                                        currentValues.push(parseFloat(slider.value));
                                    });
                                    updatePercentagePie(id, currentValues);
                                }
                                
                                // Add event listeners
                                sliders.forEach((slider, i) => {
                                    slider.addEventListener('input', () => {
                                        values[i].textContent = formatPercentage(slider.value);
                                        handlePercentageChange(id);
                                    });
                                });
                                
                                locks.forEach((lock, i) => {
                                    lock.addEventListener('click', () => {
                                        togglePercentageLock(id, i);
                                    });
                                });
                            });
                            
                            // Check for scenario toggles
                            const toggles = node.querySelectorAll ? 
                                node.querySelectorAll('.scenario-toggle-container') : [];
                            
                            toggles.forEach(container => {
                                const id = container.id;
                                const options = container.querySelectorAll('.scenario-option');
                                
                                options.forEach(option => {
                                    option.addEventListener('click', () => {
                                        const scenario = option.getAttribute('data-scenario');
                                        setScenario(id, scenario);
                                    });
                                });
                            });
                            
                            // Check for price inputs
                            const priceInputs = node.querySelectorAll ? 
                                node.querySelectorAll('.price-input-container') : [];
                            
                            priceInputs.forEach(container => {
                                const id = container.id;
                                const input = container.querySelector('input');
                                
                                input.addEventListener('input', (e) => {
                                    handlePriceInput(id, e.target.value);
                                });
                                
                                input.addEventListener('focus', () => {
                                    input.select();
                                });
                                
                                // Format initial value
                                if (input.value) {
                                    handlePriceInput(id, input.value);
                                }
                            });
                            
                            // Check for quick actions
                            const quickActions = node.querySelectorAll ? 
                                node.querySelectorAll('.quick-action-button') : [];
                            
                            quickActions.forEach(button => {
                                const action = button.getAttribute('data-action');
                                const id = button.closest('.quick-actions-container').id;
                                
                                button.addEventListener('click', () => {
                                    if (action === 'reset') {
                                        showConfirmation(id, 'Are you sure you want to reset all values to defaults?');
                                    } else {
                                        // Send action to Streamlit
                                        if (window.parent.postMessage) {
                                            const payload = {
                                                id: id,
                                                type: 'quick_action',
                                                data: action
                                            };
                                            window.parent.postMessage({
                                                type: 'streamlit:setComponentValue',
                                                value: JSON.stringify(payload)
                                            }, '*');
                                        }
                                    }
                                });
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
        st.session_state.inputs_js_injected = True

class PercentageAllocator:
    """
    A premium percentage allocator with three sliders that always sum to 100%.
    
    Features:
    - Auto-adjust other sliders when one changes
    - Visual pie preview showing the allocation
    - Lock option for fixed percentages
    """
    
    def __init__(
        self,
        labels: List[str],
        default_values: List[float],
        key: Optional[str] = None,
        title: Optional[str] = None,
        show_preview: bool = True,
        on_change: Optional[Callable] = None,
    ):
        """
        Initialize a new PercentageAllocator.
        
        Parameters:
        -----------
        labels : List[str]
            Labels for each percentage slider
        default_values : List[float]
            Default percentage values (should sum to 100)
        key : str, optional
            Unique key for the component
        title : str, optional
            Title for the allocator
        show_preview : bool, optional
            Whether to show the pie chart preview
        on_change : Callable, optional
            Function to call when percentages change
        """
        self.labels = labels
        self.default_values = self._normalize_values(default_values)
        self.key = key or f"percentage-allocator-{uuid.uuid4().hex[:8]}"
        self.title = title
        self.show_preview = show_preview
        self.on_change = on_change
        
        # Initialize session state
        if self.key not in st.session_state:
            st.session_state[self.key] = {
                "values": self.default_values,
                "locks": [False] * len(labels)
            }
    
    def _normalize_values(self, values: List[float]) -> List[float]:
        """Normalize values to ensure they sum to 100."""
        total = sum(values)
        if total == 0:
            return [100 / len(values)] * len(values)
        return [val * 100 / total for val in values]
    
    def render(self) -> List[float]:
        """
        Render the percentage allocator.
        
        Returns:
        --------
        List[float]
            The current percentage values
        """
        # Inject required CSS and JS
        inject_custom_css()
        inject_js_for_inputs()
        
        # Generate HTML
        component_id = f"percentage-allocator-{self.key}"
        
        # Create the component HTML
        html = f"""
        <div id="{component_id}" class="premium-input-container percentage-allocator">
        """
        
        # Add title if provided
        if self.title:
            html += f'<div class="premium-input-label">{self.title}</div>'
        
        # Create layout based on preview option
        if self.show_preview:
            html += '<div style="display: flex; gap: 1.5rem;">'
            html += '<div style="flex: 1;">'
        
        # Add sliders
        for i, (label, value) in enumerate(zip(self.labels, st.session_state[self.key]["values"])):
            locked = st.session_state[self.key]["locks"][i]
            lock_class = "locked" if locked else ""
            
            html += f"""
            <div class="percentage-row">
                <div class="percentage-label">{label}</div>
                <div class="percentage-slider">
                    <input type="range" min="0" max="100" value="{value}" step="1" 
                           {'disabled' if locked else ''}>
                </div>
                <div class="percentage-value">{value:.1f}%</div>
                <div class="percentage-lock {lock_class}" data-index="{i}">🔒</div>
            </div>
            """
        
        # Close the flex container if showing preview
        if self.show_preview:
            html += '</div>'
            
            # Add pie chart preview
            html += """
            <div class="percentage-preview">
                <canvas width="120" height="120"></canvas>
            </div>
            </div>
            """
        
        # Close the main container
        html += '</div>'
        
        # Render the component
        st.markdown(html, unsafe_allow_html=True)
        
        # Handle component events via streamlit callback
        component_value = st.empty()
        component_value.markdown("", unsafe_allow_html=True)
        
        # Return current values
        return st.session_state[self.key]["values"]

class ScenarioToggle:
    """
    A premium toggle between Base/Upside/Downside scenarios.
    
    Features:
    - Beautiful toggle with smooth animation
    - Shows delta from base case
    - Optional custom mode
    """
    
    def __init__(
        self,
        default_scenario: str = "base",
        include_custom: bool = False,
        key: Optional[str] = None,
        title: Optional[str] = None,
        base_values: Optional[Dict[str, float]] = None,
        on_change: Optional[Callable] = None,
    ):
        """
        Initialize a new ScenarioToggle.
        
        Parameters:
        -----------
        default_scenario : str, optional
            Default scenario ("base", "upside", "downside", or "custom")
        include_custom : bool, optional
            Whether to include a "custom" option
        key : str, optional
            Unique key for the component
        title : str, optional
            Title for the toggle
        base_values : Dict[str, float], optional
            Base case values for calculating deltas
        on_change : Callable, optional
            Function to call when scenario changes
        """
        self.default_scenario = default_scenario
        self.include_custom = include_custom
        self.key = key or f"scenario-toggle-{uuid.uuid4().hex[:8]}"
        self.title = title
        self.base_values = base_values or {}
        self.on_change = on_change
        
        # Initialize session state
        if self.key not in st.session_state:
            st.session_state[self.key] = {
                "scenario": self.default_scenario,
                "deltas": {}
            }
    
    def render(self) -> str:
        """
        Render the scenario toggle.
        
        Returns:
        --------
        str
            The current scenario
        """
        # Inject required CSS and JS
        inject_custom_css()
        inject_js_for_inputs()
        
        # Generate HTML
        component_id = f"scenario-toggle-{self.key}"
        
        # Create the component HTML
        html = f"""
        <div id="{component_id}" class="premium-input-container scenario-toggle-container">
        """
        
        # Add title if provided
        if self.title:
            html += f'<div class="premium-input-label">{self.title}</div>'
        
        # Add scenario toggle
        html += '<div class="scenario-toggle">'
        
        # Base scenario
        active_class = "active" if st.session_state[self.key]["scenario"] == "base" else ""
        html += f'<div class="scenario-option {active_class}" data-scenario="base">Base Case</div>'
        
        # Upside scenario
        active_class = "active" if st.session_state[self.key]["scenario"] == "upside" else ""
        html += f'<div class="scenario-option {active_class}" data-scenario="upside">Upside</div>'
        
        # Downside scenario
        active_class = "active" if st.session_state[self.key]["scenario"] == "downside" else ""
        html += f'<div class="scenario-option {active_class}" data-scenario="downside">Downside</div>'
        
        # Custom scenario (optional)
        if self.include_custom:
            active_class = "active" if st.session_state[self.key]["scenario"] == "custom" else ""
            html += f'<div class="scenario-option {active_class}" data-scenario="custom">Custom</div>'
        
        # Add slider element
        current_scenario = st.session_state[self.key]["scenario"]
        num_options = 4 if self.include_custom else 3
        width = 100 / num_options
        
        # Calculate position based on current scenario
        position = 0
        if current_scenario == "base":
            position = 0
        elif current_scenario == "upside":
            position = 1
        elif current_scenario == "downside":
            position = 2
        elif current_scenario == "custom":
            position = 3
        
        # Set color based on scenario
        color = COLORS[current_scenario]
        
        html += f"""
        <div class="scenario-slider" style="left: {width * position}%; width: {width}%; background: {color};"></div>
        """
        
        # Close the toggle container
        html += '</div>'
        
        # Add delta information if base values are provided
        if self.base_values and current_scenario != "base":
            # Get the key metric to display
            key_metric = list(self.base_values.keys())[0] if self.base_values else None
            
            if key_metric and key_metric in self.base_values:
                base_value = self.base_values[key_metric]
                
                # Calculate delta based on scenario
                delta = 0
                if current_scenario == "upside":
                    delta = 0.15  # +15% for upside
                elif current_scenario == "downside":
                    delta = -0.10  # -10% for downside
                
                # Calculate the actual value
                scenario_value = base_value * (1 + delta)
                
                # Format the delta
                delta_class = "scenario-delta-positive" if delta > 0 else "scenario-delta-negative"
                delta_symbol = "+" if delta > 0 else ""
                
                html += f"""
                <div class="scenario-delta">
                    <span>Delta from Base:</span>
                    <span class="scenario-delta-value {delta_class}">{delta_symbol}{delta:.1%}</span>
                </div>
                """
        
        # Close the main container
        html += '</div>'
        
        # Render the component
        st.markdown(html, unsafe_allow_html=True)
        
        # Handle component events via streamlit callback
        component_value = st.empty()
        component_value.markdown("", unsafe_allow_html=True)
        
        # Return current scenario
        return st.session_state[self.key]["scenario"]

class PriceInput:
    """
    A premium price input with currency formatting and validation.
    
    Features:
    - Currency-formatted input
    - Min/max validation
    - Historical price reference
    - Margin preview in real-time
    """
    
    def __init__(
        self,
        default_value: float,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        key: Optional[str] = None,
        title: Optional[str] = None,
        historical_price: Optional[float] = None,
        historical_label: str = "Last Year",
        cost: Optional[float] = None,
        on_change: Optional[Callable] = None,
    ):
        """
        Initialize a new PriceInput.
        
        Parameters:
        -----------
        default_value : float
            Default price value
        min_value : float, optional
            Minimum allowed price
        max_value : float, optional
            Maximum allowed price
        key : str, optional
            Unique key for the component
        title : str, optional
            Title for the input
        historical_price : float, optional
            Historical price for reference
        historical_label : str, optional
            Label for the historical price
        cost : float, optional
            Cost for calculating margin
        on_change : Callable, optional
            Function to call when price changes
        """
        self.default_value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.key = key or f"price-input-{uuid.uuid4().hex[:8]}"
        self.title = title
        self.historical_price = historical_price
        self.historical_label = historical_label
        self.cost = cost
        self.on_change = on_change
        
        # Initialize session state
        if self.key not in st.session_state:
            st.session_state[self.key] = {
                "value": self.default_value
            }
    
    def render(self) -> float:
        """
        Render the price input.
        
        Returns:
        --------
        float
            The current price value
        """
        # Inject required CSS and JS
        inject_custom_css()
        inject_js_for_inputs()
        
        # Generate HTML
        component_id = f"price-input-{self.key}"
        
        # Create the component HTML
        html = f"""
        <div id="{component_id}" class="premium-input-container price-input-container">
        """
        
        # Add title if provided
        if self.title:
            html += f'<div class="premium-input-label">{self.title}</div>'
        
        # Add input field
        html += f"""
        <div class="price-input-row">
            <div class="price-input-wrapper">
                <span class="price-input-prefix">$</span>
                <input type="text" class="price-input-field with-prefix" value="{self.default_value:.2f}"
                       {'min="' + str(self.min_value) + '"' if self.min_value is not None else ''}
                       {'max="' + str(self.max_value) + '"' if self.max_value is not None else ''}>
            </div>
        </div>
        """
        
        # Add historical reference if provided
        if self.historical_price is not None:
            html += f"""
            <div class="price-reference">
                <span>{self.historical_label}:</span>
                <span class="price-reference-value">${self.historical_price:.2f}</span>
            </div>
            """
        
        # Add margin preview if cost is provided
        if self.cost is not None:
            margin = self.default_value - self.cost
            margin_percent = (margin / self.default_value) * 100 if self.default_value > 0 else 0
            margin_class = "negative" if margin < 0 else ""
            
            html += f"""
            <div class="price-margin {margin_class}" data-cost="{self.cost}">
                <span class="price-margin-label">Margin:</span>
                <span class="price-margin-value">${margin:.2f} ({margin_percent:.1f}%)</span>
            </div>
            """
        
        # Close the main container
        html += '</div>'
        
        # Render the component
        st.markdown(html, unsafe_allow_html=True)
        
        # Handle component events via streamlit callback
        component_value = st.empty()
        component_value.markdown("", unsafe_allow_html=True)
        
        # Return current value
        return st.session_state[self.key]["value"]

class QuickActions:
    """
    A set of premium quick action buttons.
    
    Features:
    - "Set Conservative" button
    - "Set Aggressive" button
    - "Reset to Defaults" with confirmation
    - "Load from Excel" file uploader
    """
    
    def __init__(
        self,
        key: Optional[str] = None,
        title: Optional[str] = None,
        show_conservative: bool = True,
        show_aggressive: bool = True,
        show_reset: bool = True,
        show_upload: bool = True,
        on_conservative: Optional[Callable] = None,
        on_aggressive: Optional[Callable] = None,
        on_reset: Optional[Callable] = None,
        on_upload: Optional[Callable] = None,
        accepted_file_types: List[str] = ["xlsx", "xls"],
    ):
        """
        Initialize a new QuickActions component.
        
        Parameters:
        -----------
        key : str, optional
            Unique key for the component
        title : str, optional
            Title for the component
        show_conservative : bool, optional
            Whether to show the "Set Conservative" button
        show_aggressive : bool, optional
            Whether to show the "Set Aggressive" button
        show_reset : bool, optional
            Whether to show the "Reset to Defaults" button
        show_upload : bool, optional
            Whether to show the file uploader
        on_conservative : Callable, optional
            Function to call when "Set Conservative" is clicked
        on_aggressive : Callable, optional
            Function to call when "Set Aggressive" is clicked
        on_reset : Callable, optional
            Function to call when "Reset to Defaults" is confirmed
        on_upload : Callable, optional
            Function to call when a file is uploaded
        accepted_file_types : List[str], optional
            List of accepted file extensions
        """
        self.key = key or f"quick-actions-{uuid.uuid4().hex[:8]}"
        self.title = title
        self.show_conservative = show_conservative
        self.show_aggressive = show_aggressive
        self.show_reset = show_reset
        self.show_upload = show_upload
        self.on_conservative = on_conservative
        self.on_aggressive = on_aggressive
        self.on_reset = on_reset
        self.on_upload = on_upload
        self.accepted_file_types = accepted_file_types
        
        # Initialize session state
        if self.key not in st.session_state:
            st.session_state[self.key] = {
                "action": None,
                "confirmed": False,
                "uploaded_file": None
            }
    
    def render(self) -> Dict[str, Any]:
        """
        Render the quick actions.
        
        Returns:
        --------
        Dict[str, Any]
            Dictionary with action and file data
        """
        # Inject required CSS and JS
        inject_custom_css()
        inject_js_for_inputs()
        
        # Generate HTML
        component_id = f"quick-actions-{self.key}"
        
        # Create the component HTML
        html = f"""
        <div id="{component_id}" class="premium-input-container quick-actions-container">
        """
        
        # Add title if provided
        if self.title:
            html += f'<div class="premium-input-label">{self.title}</div>'
        
        # Add action buttons
        html += '<div class="quick-actions-row">'
        
        # Conservative button
        if self.show_conservative:
            html += """
            <div class="quick-action-button conservative" data-action="conservative">
                <span class="quick-action-icon">🛡️</span>
                <span>Conservative</span>
            </div>
            """
        
        # Aggressive button
        if self.show_aggressive:
            html += """
            <div class="quick-action-button aggressive" data-action="aggressive">
                <span class="quick-action-icon">🚀</span>
                <span>Aggressive</span>
            </div>
            """
        
        # Reset button
        if self.show_reset:
            html += """
            <div class="quick-action-button reset" data-action="reset">
                <span class="quick-action-icon">↩️</span>
                <span>Reset</span>
            </div>
            """
        
        # Close the action buttons row
        html += '</div>'
        
        # Add file uploader if enabled
        if self.show_upload:
            extensions = ", ".join(f".{ext}" for ext in self.accepted_file_types)
            
            html += f"""
            <div class="file-upload-container">
                <div class="file-upload-icon">📊</div>
                <div class="file-upload-text">Drop Excel file here or click to upload</div>
                <div class="file-upload-button">Choose File</div>
                <input type="file" accept="{extensions}" style="display: none;" id="file-upload-{self.key}">
            </div>
            """
        
        # Close the main container
        html += '</div>'
        
        # Render the component
        st.markdown(html, unsafe_allow_html=True)
        
        # Add standard file uploader for actual functionality
        # (hidden but needed for Streamlit's file handling)
        if self.show_upload:
            uploaded_file = st.file_uploader(
                "Upload Excel file", 
                type=self.accepted_file_types,
                key=f"uploader-{self.key}",
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                st.session_state[self.key]["uploaded_file"] = uploaded_file
                if self.on_upload:
                    self.on_upload(uploaded_file)
        
        # Handle component events via streamlit callback
        component_value = st.empty()
        component_value.markdown("", unsafe_allow_html=True)
        
        # Return current state
        return {
            "action": st.session_state[self.key].get("action"),
            "confirmed": st.session_state[self.key].get("confirmed", False),
            "uploaded_file": st.session_state[self.key].get("uploaded_file")
        }

# Example usage
if __name__ == "__main__":
    st.title("Premium Input Components Demo")
    
    st.header("Percentage Allocator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        allocator = PercentageAllocator(
            labels=["Tasting Room", "Club", "Wholesale"],
            default_values=[20, 15, 65],
            title="Channel Mix",
            show_preview=True
        )
        values = allocator.render()
        st.write(f"Current values: {values}")
    
    with col2:
        allocator2 = PercentageAllocator(
            labels=["Marketing", "R&D", "Operations"],
            default_values=[30, 20, 50],
            title="Budget Allocation",
            show_preview=True
        )
        values2 = allocator2.render()
        st.write(f"Current values: {values2}")
    
    st.header("Scenario Toggle")
    
    toggle = ScenarioToggle(
        default_scenario="base",
        include_custom=True,
        title="Forecast Scenario",
        base_values={"Revenue": 2450000}
    )
    scenario = toggle.render()
    st.write(f"Current scenario: {scenario}")
    
    st.header("Price Input")
    
    col1, col2 = st.columns(2)
    
    with col1:
        price_input = PriceInput(
            default_value=80.00,
            min_value=50.00,
            max_value=120.00,
            title="Bottle Price",
            historical_price=75.00,
            cost=22.00
        )
        price = price_input.render()
        st.write(f"Current price: ${price:.2f}")
    
    with col2:
        price_input2 = PriceInput(
            default_value=24.00,
            min_value=18.00,
            max_value=36.00,
            title="Wholesale Price",
            historical_price=22.50,
            cost=6.16
        )
        price2 = price_input2.render()
        st.write(f"Current price: ${price2:.2f}")
    
    st.header("Quick Actions")
    
    actions = QuickActions(
        title="Scenario Actions",
        show_conservative=True,
        show_aggressive=True,
        show_reset=True,
        show_upload=True
    )
    result = actions.render()
    
    if result["action"] == "conservative":
        st.success("Conservative settings applied!")
    elif result["action"] == "aggressive":
        st.success("Aggressive settings applied!")
    elif result["action"] == "reset" and result["confirmed"]:
        st.info("Settings reset to defaults!")
    
    if result["uploaded_file"] is not None:
        st.success(f"File uploaded: {result['uploaded_file'].name}")
