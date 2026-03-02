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
        # self.populate_test_nodes() #populate the nodes dict with test data from test_nodes.json
        self.refresh() #initial refresh to populate data from redis
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
            "seq": tk.StringVar(value="—"),
            "accel_x": tk.StringVar(value="—"),
            "accel_y": tk.StringVar(value="—"),
            "accel_z": tk.StringVar(value="—"),
            "gyro_x": tk.StringVar(value="—"),
            "gyro_y": tk.StringVar(value="—"),
            "gyro_z": tk.StringVar(value="—"),
        }

        # Helper to add a labeled row
        def add_row(r, label_text, var):
            lbl = ttk.Label(content, text=f"{label_text}:", anchor="w")
            val = ttk.Label(content, textvariable=var, anchor="w")
            lbl.grid(row=r, column=0, sticky="w", padx=(0, 12), pady=6)
            val.grid(row=r, column=1, sticky="w", pady=6)

        r = 1
        add_row(r, "Node ID", self.vars["node_id"]); r += 1
        add_row(r, "Timestamp", self.vars["timestamp"]); r += 1
        add_row(r, "Sequence", self.vars["seq"]); r += 1
        add_row(r, "Accel X", self.vars["accel_x"]); r += 1
        add_row(r, "Accel Y", self.vars["accel_y"]); r += 1
        add_row(r, "Accel Z", self.vars["accel_z"]); r += 1
        add_row(r, "Gyro X", self.vars["gyro_x"]); r += 1
        add_row(r, "Gyro Y", self.vars["gyro_y"]); r += 1
        add_row(r, "Gyro Z", self.vars["gyro_z"]); r += 1
        add_row(r, "Latitude", self.vars["lat"]); r += 1
        add_row(r, "Longitude", self.vars["lon"]); r += 1
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
    # def populate_test_nodes(self):
    #     file = self.load_json('widgets/test_nodes.json')
        

    #     for entry in file:
    #         try:
    #             self.load_node(entry["node_id"], entry)

    #         except Exception as e:
    #             print(f"[load_nodes] Failed to load entry {entry}: {e}")

  
    def load_node(self, node_id: str, rdentry: Dict[str, Any], mlentry):
        """
        Load data for a specific node.
        
        Called when node list is populated
        
        Args:
            node_id: ID of the node to display
        """
        if node_id is None:
            raise ValueError("Node ID cannot be None")
        if rdentry is None:
            raise ValueError(f"Raw data entry for node {node_id} cannot be None")
        if mlentry is None:
            raise ValueError(f"Machine learning entry for node {node_id} cannot be None")
        if node_id not in rdentry:
            raise ValueError(f"Node ID {node_id} not found in raw data entry")
        node_id = rdentry.get("node_id", node_id) #use node_id from raw data entry if available, otherwise use provided node_id
        
        #raw data fields with defaults if missing
        timestamp = rdentry.get("timestamp", datetime.now().isoformat())
        seq = rdentry.get("seq", 0)
        accel = rdentry.get("accel")
        accel_x = accel.get("x", 0) if accel else 0
        accel_y = accel.get("y", 0) if accel else 0
        accel_z = accel.get("z", 0) if accel else 0
        gyro = rdentry.get("gyro_rads")
        gyro_x = gyro.get("x", 0) if gyro else 0
        gyro_y = gyro.get("y", 0) if gyro else 0
        gyro_z = gyro.get("z", 0) if gyro else 0
        gps = rdentry.get("gps")
        lat = gps.get("lat_deg", 0) if gps else 0
        lon = gps.get("lon_deg", 0) if gps else 0
        #inference output fields with defaults if missing
        motion_class = max(range(len(mlentry)), key=lambda i: mlentry[i]) if mlentry else 0 #get index of max confidence motion class, default to 0 if mlentry is empty
        confidence = mlentry[motion_class] if mlentry else 0 #get confidence of predicted motion class, default to 0 if mlentry is empty
        anomaly = motion_class >= 4 #assuming motion classes 4-7 are anomalies, might change depending on team discourse. (2/27/2026) -TE
        # Build Node object
        node = Node(
            node_id=node_id,
            timestamp=timestamp,
            seq=seq,
            accel_x=accel_x,
            accel_y=accel_y,
            accel_z=accel_z,
            gyro_x=gyro_x,
            gyro_y=gyro_y,
            gyro_z=gyro_z,
            lat=lat,
            lon=lon,
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
        self.vars["timestamp"].set(node.getTimestamp().strftime("%Y-%m-%d %H:%M:%S"))
        self.vars["seq"].set(str(node.seq))
        self.vars["accel_x"].set(f"{node.accel_x:.2f}")
        self.vars["accel_y"].set(f"{node.accel_y:.2f}")
        self.vars["accel_z"].set(f"{node.accel_z:.2f}")
        self.vars["gyro_x"].set(f"{node.gyro_x:.2f}")
        self.vars["gyro_y"].set(f"{node.gyro_y:.2f}")
        self.vars["gyro_z"].set(f"{node.gyro_z:.2f}")
        self.vars["lat"].set(f"{node.lat:.6f}")
        self.vars["lon"].set(f"{node.lon:.6f}")
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
        for node_id, rdentry in self.rddict.items():
            mlentry = self.mldict.get(node_id, [])
            try:
                self.load_node(node_id, rdentry, mlentry)
            except Exception as e:
                print(f"[NodeDetailsTab._parse_nodes] Error parsing node {node_id}: {e}")
    def refresh_dropdown(self):
        """
        Refresh the node selector dropdown with current nodes.
        """
        if self.node_selector is None:
            return
        node_ids = list(self.nodes.keys())
        self.node_selector['values'] = node_ids
        if self.current_node_id in node_ids:
            self.node_selector.set(self.current_node_id)
        elif node_ids:
            self.node_selector.set(node_ids[0])
            self.display_node(node_ids[0])
    def refresh(self):
        """
        Refresh data for the currently selected node.
        """
        try:
            self.rddict, self.mldict = self.redis_reader.getDicts() #get latest data from redis reader
            self._parse_nodes()
            self.refresh_dropdown()
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
