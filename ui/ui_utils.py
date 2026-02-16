"""
ui_utils.py - Shared UI constants and utilities.

Contains color schemes, sizing constants, and helper functions
used across the UI components.
"""

# Motion class color scheme for charts
MOTION_COLORS = {
    'IDLE': '#3498db',        # Blue
    'TERRESTRIAL': '#2ecc71', # Green
    'MARITIME': '#9b59b6',    # Purple
    'LIFT': '#e74c3c'         # Red
}

# Chart sizing constants
CHART_FIGSIZE = (6, 4)  # Width, height in inches
CHART_DPI = 100         # Dots per inch for chart resolution
