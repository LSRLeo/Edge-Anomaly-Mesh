"""
node_details_tab.py - Node details drill-down tab.

This module contains:
- NodeDetailsTab: Frame for viewing detailed info about a single node
- Node selector dropdown
- Info panel with metadata
- Motion history table
- Anomaly score trend chart

Features:
- Select node from dropdown
- View node metadata (status, first/last seen)
- Motion classification history table
- Anomaly score trend line chart
- Called from other tabs when user clicks a node
"""

import json
import os
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
from datetime import datetime, timedelta
from widgets.parent_classes import Node
from widgets.parent_classes import DashboardParents
from redis_reader import RedisReader

# Matplotlib imports
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# from ui.ui_utils import (
#     MOTION_COLORS,
#     format_timestamp, format_confidence, format_anomaly_score,
#     get_motion_color
# )

# Avoid circular import
if TYPE_CHECKING:
    from widgets.dashboard_main import DashboardApp


# =============================================================================
# MOCK DATA - Replace with database queries
# =============================================================================

# MOCK_NODES = ['node_001', 'node_002', 'node_003', 'node_004', 'node_005', 'node_006']

# MOCK_NODE_INFO = {
#     'node_id': 'node_003',
#     'status': 'ACTIVE',
#     'current_motion': 'MARITIME',
#     'location': 'Hub B - Dock 4',
#     'first_seen': datetime.now() - timedelta(days=7),
#     'last_seen': datetime.now() - timedelta(seconds=30),
#     'total_inferences': 8452,
#     'total_anomalies': 12,
# }

class NodeDetailsTab(ttk.Frame, DashboardParents):
    """
    Node details drill-down tab.
    
    Shows comprehensive information about a single selected node,
    including metadata, motion history, and anomaly trends.
    """
    
    def __init__(self, parent: ttk.Notebook, dashboard: 'DashboardApp', redis_reader: RedisReader, selected_node_id: Optional[str] = None):
        """
        Initialize the Node Details tab.
        
        Args:
            parent: Parent notebook widget
            dashboard: Reference to main dashboard for callbacks
            selected_node_id: Optional node ID to display on load
        """
        super().__init__(parent)
        
        self.dashboard = dashboard
        
        # Current node
        self.current_node_id: Optional[str] = None
        
        # UI components
        self.node_selector: Optional[ttk.Combobox] = None
        self.info_labels: Dict[str, ttk.Label] = {}
        # self.history_tree: Optional[ttk.Treeview] = None
        if selected_node_id:
            self.selected_node_id = selected_node_id
        else:
            self.selected_node_id = None
        
        # # Chart components
        # self.trend_fig: Optional[Figure] = None
        # self.trend_ax = None
        # self.trend_canvas: Optional[FigureCanvasTkAgg] = None
        self.mldict = {} #machine learning dictionary
        self.rddict = {} #raw data dictionary
        self.nodes = {} #dict of node_id to Node object
        self.motion_states = ["IDLE", "TERRESTRIAL", "MARITIME", "LIFT", "IDLE_ANOMALY", "TERRESTRIAL_ANOMALY", "MARITIME_ANOMALY", "LIFT_ANOMALY"] #key for motion class index to string
        self.populate_test_nodes() #populate the nodes dict with test data from test_nodes.json
        # Build UI
        self._setup_ui()
        
    
    def _setup_ui(self):
        """
        Create the tab layout.
        
        Layout:
        ┌─────────────────────────────────────┐
        │  Node: [node_003 ▼]                 │
        ├─────────────────────────────────────┤
        │  Status: ACTIVE  │ Motion: MARITIME │
        │  First: ...      │ Last: ...        │
        ├─────────────────────────────────────┤
        │  Motion History (last 24h)          │
        │  ┌─────────────────────────────┐    │
        │  │ Time  │ Motion │ Conf │ Anom│    │
        │  │ ...   │ ...    │ ...  │ ... │    │
        │  └─────────────────────────────┘    │
        ├─────────────────────────────────────┤
        │  Anomaly Score Trend                │
        │  [═══════ Line Chart ═══════]       │
        └─────────────────────────────────────┘
        """
        
        
        self._setup_node_selector()
        self._setup_info_panel()
        

    
    def _setup_node_selector(self):
        """
        Create the node selection dropdown.
        
        Shows all available nodes in a combobox.
        When selection changes, loads that node's data.
        """

        selector_frame = ttk.Frame(self)
        selector_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        
        ttk.Label(selector_frame, text="Node:", font=('Arial', 12)).pack(side='left', padx=(0, 10))
        
        self.node_selector = ttk.Combobox(selector_frame, values=list(self.nodes.keys()),
                                           state='readonly', width=20, font=('Arial', 12))
        self.node_selector.pack(side='left')
        self.node_selector.bind('<<ComboboxSelected>>', self._on_node_select)
        
        # Refresh button
        ttk.Button(selector_frame, text="Refresh",
                   command=self.refresh).pack(side='right', padx=10)
        

    
    def _setup_info_panel(self):
        """
        Create the node information panel.
        
        Displays:
        - Status (ACTIVE/INACTIVE)
        - Current motion class
        - Location
        - First seen timestamp
        - Last seen timestamp
        - Total inferences
        - Total anomalies
        """

        # Ensure main grid stretches properly
        self.columnconfigure(0, weight=1)
        # Row 0 is the header; row 1 is content
        self.rowconfigure(1, weight=1)

        # Outer content container
        content_outer = ttk.Frame(self)
        content_outer.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        content_outer.columnconfigure(0, weight=1)
        content_outer.rowconfigure(0, weight=1)

        # Inner grouped frame
        content = ttk.Frame(content_outer, padding=(14, 12))
        try:
            style = ttk.Style(content)
            style.configure("Group.TFrame", relief="groove", borderwidth=1)
            content.configure(style="Group.TFrame")
        except Exception:
            pass
        content.grid(row=0, column=0, sticky="nsew")
        content.columnconfigure(0, weight=0)
        content.columnconfigure(1, weight=1)

        # Title
        ttk.Label(content, text="Node Details", font=("TkDefaultFont", 11, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )

        # Placeholder StringVars
        self.vars = {
            "node_id": tk.StringVar(value="—"),
            "lat": tk.StringVar(value="—"),
            "lon": tk.StringVar(value="—"),
            "timestamp": tk.StringVar(value="—"),
            "motion_class": tk.StringVar(value="—"),
            "confidence": tk.StringVar(value="—"),
        }

        # Helper to add a labeled row
        def add_row(r, label_text, var):
            lbl = ttk.Label(content, text=f"{label_text}:", anchor="w")
            val = ttk.Label(content, textvariable=var, anchor="w")
            lbl.grid(row=r, column=0, sticky="w", padx=(0, 12), pady=6)
            val.grid(row=r, column=1, sticky="w", pady=6)

        r = 1
        add_row(r, "Node ID", self.vars["node_id"]); r += 1
        add_row(r, "Latitude", self.vars["lat"]); r += 1
        add_row(r, "Longitude", self.vars["lon"]); r += 1
        add_row(r, "Timestamp", self.vars["timestamp"]); r += 1
        add_row(r, "Motion Class", self.vars["motion_class"]); r += 1
        add_row(r, "Confidence", self.vars["confidence"]); r += 1

        # Spacer to keep bottom tidy
        content.rowconfigure(r, weight=1)
        if self.selected_node_id is not None:
            self.display_node(self.selected_node_id)
        else:
            self.selected_node_id = list(self.nodes.keys())[0]
            self.display_node(self.selected_node_id)

    
    def load_json(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError
        with open(filename, 'r') as file:
            return json.load(file)
    def populate_test_nodes(self):
        file = self.load_json('widgets/test_nodes.json')
        

        for entry in file:
            try:
                self.load_node(entry["node_id"], entry)

            except Exception as e:
                print(f"[load_nodes] Failed to load entry {entry}: {e}")

  
    def load_node(self, node_id: str, rdentry: Dict[str, Any], mlentry: Dict[str, Any]):
        """
        Load data for a specific node.
        
        Called when node list is populated
        
        Args:
            node_id: ID of the node to display
        """
        # TODO: Implement
        #
        # self.current_node_id = node_id
        #
        # # Update selector to show this node
        # if self.node_selector:
        #     self.node_selector.set(node_id)
        #
        # # Fetch and display data
        # self._load_node_info(node_id)
        # self._load_history(node_id)
        # self._load_anomaly_trend(node_id)
        node_id = rdentry["node_id"]
        lat = float(rdentry["lat"])
        lon = float(rdentry["lon"])
        # JSON uses an int for motion_class → convert to string
        motion_class_str = rdentry.get("motion_class", "")
        motion_class = self.motion_states.index(motion_class_str) if motion_class_str in self.motion_states else 0
    
        anomaly = rdentry.get("anomaly", False)
        if anomaly:
            motion_class += 4 #convert to anomaly motion class index
        # Insert placeholder fields
        timestamp = datetime.now()
        confidence = 1.0

        # Build Node object
        node = Node(
            node_id=node_id,
            lat=lat,
            lon=lon,
            timestamp=timestamp,
            motion_class=motion_class,
            anomaly= anomaly,
            confidence=confidence,
        )

        # Store it
        self.nodes[node_id] = node
    
    def display_node(self, node_id: str):
        """
        Update the UI to display the given node's data.
        
        Args:
            node_id: ID of the node to display
        """
        if node_id not in self.nodes:
            print(f"[display_node] Node ID {node_id} not found in loaded nodes.")
            return
        
        node = self.nodes[node_id]
        self.vars["node_id"].set(node.getNodeID())
        self.vars["lat"].set(f"{node.lat:.6f}")
        self.vars["lon"].set(f"{node.lon:.6f}")
        self.vars["timestamp"].set(node.getTimestamp().strftime("%Y-%m-%d %H:%M:%S"))
        self.vars["motion_class"].set(node.motionString())
        self.vars["confidence"].set(f"{node.confidence:.2f}")
    
    def _on_node_select(self, event):
        """
        Handle node selection from dropdown.
        
        Args:
            event: Combobox selection event
        """
        if self.node_selector is None:
            return
        node_id = self.node_selector.get()
        self.display_node(node_id)
    def _parse_nodes(self):
        for node_id in self.rddict:
            rdentry = self.rddict[node_id]
            mlentry = self.mldict.get(node_id, {})
            self.load_node(node_id, rdentry, mlentry)
    def refresh(self):
        """
        Refresh data for the currently selected node.
        """
        # TODO: Implement
        #
        # if self.current_node_id:
        #     self.load_node(self.current_node_id)
        try:
            self.rddict = self.redis_reader.getRDDict() #get the raw data dictionary from the redis reader
            self.mldict = self.redis_reader.getMLDict() #get the machine learning dictionary from the redis reader
            self._parse_nodes()

            if self.current_node_id:
                self.display_node(self.current_node_id)
        except Exception as e:
            print(f"[NodeDetailsTab.refresh] Error refreshing data: {e}")


        
# =============================================================================
# DEMO / TEST
# =============================================================================

# def demo():
#     """Demonstrate the NodeDetailsTab independently."""
#     root = tk.Tk()
#     root.title("Node Details Tab Demo")
#     root.geometry("800x700")
    
#     # Create a mock dashboard
#     class MockDashboard:
#         pass
    
#     notebook = ttk.Notebook(root)
#     notebook.pack(fill='both', expand=True)
    
#     tab = NodeDetailsTab(notebook, dashboard=MockDashboard())
#     notebook.add(tab, text='Node Details')
    
#     # Load a node
#     # tab.load_node('node_003')
    
#     root.mainloop()


# if __name__ == '__main__':
#     demo()
