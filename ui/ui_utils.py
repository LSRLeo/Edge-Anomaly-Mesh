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


# Named ttk styles by semantic role.
TEXT_LABEL_STYLE = "UiText.TLabel"
HEADING_LABEL_STYLE = "UiHeading.TLabel"
CAPTION_LABEL_STYLE = "UiCaption.TLabel"
VALUE_LABEL_STYLE = "UiValue.TLabel"
ACTION_BUTTON_STYLE = "UiAction.TButton"
INPUT_COMBO_STYLE = "UiInput.TCombobox"


def _scaled_font(font_spec, scale: float):
    family, size, *rest = font_spec
    scaled_size = max(8, int(round(size * scale)))
    if rest:
        return (family, scaled_size, *rest)
    return (family, scaled_size)


def get_group_font(group: str, scale: float = 1.0):
    return _scaled_font(FONT_GROUPS[group], scale)


def configure_accessibility_styles(root: tk.Tk, scale: float = 1.0):
    """
    Apply grouped, global UI styles so accessibility changes can be made in one place.

    Args:
        root: Root tkinter window.
        scale: Font scale multiplier for larger/smaller UI text.
    """
    style = ttk.Style(root)

    # Global defaults by widget type.
    style.configure("TLabel", font=get_group_font("label", scale))
    style.configure("TButton", font=get_group_font("button", scale))
    style.configure("TCombobox", font=get_group_font("input", scale))
    style.configure("TNotebook.Tab", font=get_group_font("button", scale))
    style.configure("TLabelframe.Label", font=get_group_font("heading", scale))

    # Semantic styles for targeted widgets.
    style.configure(TEXT_LABEL_STYLE, font=get_group_font("label", scale))
    style.configure(HEADING_LABEL_STYLE, font=get_group_font("heading", scale))
    style.configure(CAPTION_LABEL_STYLE, font=get_group_font("caption", scale))
    style.configure(VALUE_LABEL_STYLE, font=get_group_font("label", scale))
    style.configure(ACTION_BUTTON_STYLE, font=get_group_font("button", scale))
    style.configure(INPUT_COMBO_STYLE, font=get_group_font("input", scale))

    # tk widgets (for example Menu/Canvas text) use option database.
    root.option_add("*Menu.Font", get_group_font("menu", scale))
    root.option_add("*Font", get_group_font("label", scale))


# Configures treeview style
def configure_treeview_style(scale: float = 1.0):
    style = ttk.Style()
    style.configure("Treeview", font=get_group_font("treeview", scale), rowheight=24)
    style.configure("Treeview.Heading", font=get_group_font("treeview_heading", scale))
    
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