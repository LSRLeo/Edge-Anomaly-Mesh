"""
ui_utils.py - Shared UI constants and utilities.

Contains color schemes, sizing constants, and helper functions
used across the UI components.
"""

import tkinter as tk
from tkinter import ttk

# High-contrast light palette (optimized for readability).
UI_COLORS = {
    "bg": "#F4F7FB",
    "surface": "#FFFFFF",
    "surface_alt": "#E8EEF5",
    "border": "#B6C2CF",
    "text": "#111827",
    "text_muted": "#4B5563",
    "accent": "#1D4ED8",
    "accent_hover": "#1E40AF",
    "danger": "#C62828",
    "input_bg": "#FFFFFF",
    "selection_bg": "#2563EB",
    "selection_text": "#FFFFFF",
}

# Centralized, grouped UI font definitions for accessibility tuning.
# Update these values to change all widgets in a group at once.
FONT_GROUPS = {
    "label": ("Arial", 14),
    "button": ("Arial", 14),
    "input": ("Arial", 14),
    "heading": ("Arial", 18, "bold"),
    "caption": ("Arial", 12),
    "menu": ("Arial", 14),
    "treeview": ("Arial", 14),
    "treeview_heading": ("Arial", 14, "bold"),
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
    style.theme_use("clam")

    root.configure(bg=UI_COLORS["bg"])

    # Global defaults by widget type.
    style.configure("TFrame", background=UI_COLORS["bg"])
    style.configure(
        "TLabel",
        font=get_group_font("label", scale),
        background=UI_COLORS["bg"],
        foreground=UI_COLORS["text"],
    )
    style.configure(
        "TButton",
        font=get_group_font("button", scale),
        background=UI_COLORS["surface_alt"],
        foreground=UI_COLORS["text"],
        bordercolor=UI_COLORS["border"],
        focuscolor=UI_COLORS["accent"],
        padding=(10, 6),
    )
    style.map(
        "TButton",
        background=[("active", UI_COLORS["accent"]), ("pressed", UI_COLORS["accent"])],
        foreground=[("active", UI_COLORS["selection_text"]), ("pressed", UI_COLORS["selection_text"])],
    )
    style.configure(
        "TCombobox",
        font=get_group_font("input", scale),
        foreground=UI_COLORS["text"],
        fieldbackground=UI_COLORS["input_bg"],
        background=UI_COLORS["surface_alt"],
        bordercolor=UI_COLORS["border"],
        arrowcolor=UI_COLORS["text"],
        lightcolor=UI_COLORS["border"],
        darkcolor=UI_COLORS["border"],
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", UI_COLORS["input_bg"])],
        foreground=[("readonly", UI_COLORS["text"])],
        selectbackground=[("readonly", UI_COLORS["selection_bg"])],
        selectforeground=[("readonly", UI_COLORS["selection_text"])],
    )
    style.configure("TNotebook", background=UI_COLORS["bg"], bordercolor=UI_COLORS["border"])
    style.configure(
        "TNotebook.Tab",
        font=get_group_font("button", scale),
        background=UI_COLORS["surface"],
        foreground=UI_COLORS["text_muted"],
        bordercolor=UI_COLORS["border"],
        padding=(12, 8),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", UI_COLORS["surface_alt"])],
        foreground=[("selected", UI_COLORS["text"])],
    )
    style.configure(
        "TLabelframe",
        background=UI_COLORS["surface"],
        bordercolor=UI_COLORS["border"],
        relief="solid",
    )
    style.configure(
        "TLabelframe.Label",
        font=get_group_font("heading", scale),
        background=UI_COLORS["surface"],
        foreground=UI_COLORS["text"],
    )
    style.configure(
        "Vertical.TScrollbar",
        background=UI_COLORS["surface_alt"],
        troughcolor=UI_COLORS["bg"],
        bordercolor=UI_COLORS["border"],
        arrowcolor=UI_COLORS["text"],
    )
    style.configure(
        "Horizontal.TScrollbar",
        background=UI_COLORS["surface_alt"],
        troughcolor=UI_COLORS["bg"],
        bordercolor=UI_COLORS["border"],
        arrowcolor=UI_COLORS["text"],
    )

    # Semantic styles for targeted widgets.
    style.configure(
        TEXT_LABEL_STYLE,
        font=get_group_font("label", scale),
        background=UI_COLORS["bg"],
        foreground=UI_COLORS["text"],
    )
    style.configure(
        HEADING_LABEL_STYLE,
        font=get_group_font("heading", scale),
        background=UI_COLORS["bg"],
        foreground=UI_COLORS["text"],
    )
    style.configure(
        CAPTION_LABEL_STYLE,
        font=get_group_font("caption", scale),
        background=UI_COLORS["bg"],
        foreground=UI_COLORS["text_muted"],
    )
    style.configure(
        VALUE_LABEL_STYLE,
        font=get_group_font("label", scale),
        background=UI_COLORS["bg"],
        foreground=UI_COLORS["text"],
    )
    style.configure(ACTION_BUTTON_STYLE, font=get_group_font("button", scale))
    style.configure(INPUT_COMBO_STYLE, font=get_group_font("input", scale))

    # tk widgets (for example Menu/Canvas text) use option database.
    root.option_add("*Menu.Font", get_group_font("menu", scale))
    root.option_add("*Menu.Background", UI_COLORS["surface"])
    root.option_add("*Menu.Foreground", UI_COLORS["text"])
    root.option_add("*Menu.ActiveBackground", UI_COLORS["accent"])
    root.option_add("*Menu.ActiveForeground", UI_COLORS["selection_text"])
    root.option_add("*Canvas.Background", UI_COLORS["bg"])
    root.option_add("*Canvas.HighlightBackground", UI_COLORS["border"])
    root.option_add("*Canvas.HighlightColor", UI_COLORS["accent"])
    root.option_add("*Font", get_group_font("label", scale))


# Configures treeview style
def configure_treeview_style(scale: float = 1.0):
    style = ttk.Style()
    style.configure(
        "Treeview",
        font=get_group_font("treeview", scale),
        background=UI_COLORS["surface"],
        fieldbackground=UI_COLORS["surface"],
        foreground=UI_COLORS["text"],
        rowheight=24,
    )
    style.configure(
        "Treeview.Heading",
        font=get_group_font("treeview_heading", scale),
        background=UI_COLORS["surface_alt"],
        foreground=UI_COLORS["text"],
    )
    style.map(
        "Treeview",
        background=[("selected", UI_COLORS["selection_bg"])],
        foreground=[("selected", UI_COLORS["selection_text"])],
    )
    
# Window sizing constants
WINDOW_WIDTH = 1067
WINDOW_HEIGHT = 850

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
