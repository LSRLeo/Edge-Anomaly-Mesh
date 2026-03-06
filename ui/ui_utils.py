"""
ui_utils.py - Shared UI constants and utilities.

Contains color schemes, sizing constants, and helper functions
used across the UI components.
"""

import tkinter as tk
from tkinter import ttk


# Centralized, grouped UI font definitions for accessibility tuning.
# Update these values to change all widgets in a group at once.
FONT_GROUPS = {
    "label": ("Arial", 11),
    "button": ("Arial", 11),
    "input": ("Arial", 11),
    "heading": ("Arial", 12, "bold"),
    "caption": ("Arial", 9),
    "menu": ("Arial", 11),
    "treeview": ("Arial", 11),
    "treeview_heading": ("Arial", 11, "bold"),
}

# Configures treeview style
def configure_treeview_style():
    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 24), rowheight=24)
    style.configure("Treeview.Heading", font=("Arial", 24, "bold"))
    
# Window sizing constants
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 1000

# Refresh Rate
REFRESH_INTERVAL_MS = 10000

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