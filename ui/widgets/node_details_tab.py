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

MOCK_NODES = ['node_001', 'node_002', 'node_003', 'node_004', 'node_005', 'node_006']

MOCK_NODE_INFO = {
    'node_id': 'node_003',
    'status': 'ACTIVE',
    'current_motion': 'MARITIME',
    'location': 'Hub B - Dock 4',
    'first_seen': datetime.now() - timedelta(days=7),
    'last_seen': datetime.now() - timedelta(seconds=30),
    'total_inferences': 8452,
    'total_anomalies': 12,
}

class NodeDetailsTab(ttk.Frame):
    """
    Node details drill-down tab.
    
    Shows comprehensive information about a single selected node,
    including metadata, motion history, and anomaly trends.
    """
    
    def __init__(self, parent: ttk.Notebook, dashboard: 'DashboardApp', selected_node_id: Optional[str] = None):
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
        # self._setup_history_table()
        # self._setup_anomaly_trend_chart()
        

    
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


    
    # def _setup_history_table(self):
        """
        Create the motion history treeview table.
        
        Columns:
        - Timestamp
        - Motion Class
        - Confidence
        - Anomaly Score
        """
        # TODO: Implement
        #
        # history_frame = ttk.LabelFrame(self, text="Motion History (Last 24 Hours)")
        # history_frame.grid(row=2, column=0, sticky='nsew', padx=10, pady=5)
        # history_frame.columnconfigure(0, weight=1)
        # history_frame.rowconfigure(0, weight=1)
        #
        # columns = ('timestamp', 'motion_class', 'confidence', 'anomaly_score')
        #
        # self.history_tree = ttk.Treeview(history_frame, columns=columns,
        #                                   show='headings', height=8)
        #
        # self.history_tree.heading('timestamp', text='Timestamp')
        # self.history_tree.heading('motion_class', text='Motion Class')
        # self.history_tree.heading('confidence', text='Confidence')
        # self.history_tree.heading('anomaly_score', text='Anomaly Score')
        #
        # self.history_tree.column('timestamp', width=150, anchor='center')
        # self.history_tree.column('motion_class', width=120, anchor='center')
        # self.history_tree.column('confidence', width=100, anchor='center')
        # self.history_tree.column('anomaly_score', width=100, anchor='center')
        #
        # self.history_tree.grid(row=0, column=0, sticky='nsew')
        #
        # # Scrollbar
        # scrollbar = ttk.Scrollbar(history_frame, orient='vertical',
        #                           command=self.history_tree.yview)
        # scrollbar.grid(row=0, column=1, sticky='ns')
        # self.history_tree.configure(yscrollcommand=scrollbar.set)
        #
        # # Configure row tags for motion class coloring
        # for motion_class, color in MOTION_COLORS.items():
        #     self.history_tree.tag_configure(motion_class, foreground=color)
        pass
    
    # def _setup_anomaly_trend_chart(self):
        """
        Create the anomaly score trend line chart.
        
        Shows anomaly score over time for the selected node.
        """
        # TODO: Implement
        #
        # chart_frame = ttk.LabelFrame(self, text="Anomaly Score Trend")
        # chart_frame.grid(row=3, column=0, sticky='nsew', padx=10, pady=5)
        #
        # self.trend_fig = Figure(figsize=(8, 3), dpi=100)
        # self.trend_ax = self.trend_fig.add_subplot(111)
        #
        # self.trend_canvas = FigureCanvasTkAgg(self.trend_fig, master=chart_frame)
        # self.trend_canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        pass
    
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

  
    def load_node(self, node_id: str, entry: Dict[str, Any]):
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
        node_id = entry["node_id"]
        lat = float(entry["lat"])
        lon = float(entry["lon"])
        # JSON uses an int for motion_class → convert to string
        motion_class_str = entry.get("motion_class", "")
        motion_class = self.motion_states.index(motion_class_str) if motion_class_str in self.motion_states else 0
    
        anomaly = entry.get("anomaly", False)
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
    def _load_node_info(self, node_id: str):
        """
        Load and display node metadata.
        
        Args:
            node_id: ID of the node
        """
        # TODO: Implement with real database query
        #
        # # node_info = db.get_node_info(node_id)
        # node_info = MOCK_NODE_INFO  # Temporary
        #
        # # Update info labels
        # self.info_labels['node_id'].config(text=node_info['node_id'])
        # self.info_labels['status'].config(text=node_info['status'])
        # self.info_labels['current_motion'].config(text=node_info['current_motion'])
        # self.info_labels['location'].config(text=node_info.get('location', 'Unknown'))
        # self.info_labels['first_seen'].config(text=format_timestamp(node_info['first_seen']))
        # self.info_labels['last_seen'].config(text=format_timestamp(node_info['last_seen']))
        # self.info_labels['total_inferences'].config(text=f"{node_info['total_inferences']:,}")
        # self.info_labels['total_anomalies'].config(text=str(node_info['total_anomalies']))
        pass
    
    # def _load_history(self, node_id: str):
        """
        Load and display motion classification history.
        
        Args:
            node_id: ID of the node
        """
        # TODO: Implement with real database query
        #
        # # Clear existing rows
        # for item in self.history_tree.get_children():
        #     self.history_tree.delete(item)
        #
        # # history = db.get_node_history(node_id, hours=24)
        # history = MOCK_HISTORY  # Temporary
        #
        # # Add rows
        # for i, record in enumerate(history):
        #     values = (
        #         format_timestamp(record['timestamp'], include_date=False),
        #         record['motion_class'],
        #         format_confidence(record['confidence']),
        #         format_anomaly_score(record['anomaly_score'])
        #     )
        #     self.history_tree.insert('', 'end', iid=str(i), values=values,
        #                              tags=(record['motion_class'],))
        pass
    
    # def _load_anomaly_trend(self, node_id: str):
        """
        Load and display anomaly score trend chart.
        
        Args:
            node_id: ID of the node
        """
        # TODO: Implement with real database query
        #
        # if not self.trend_ax:
        #     return
        #
        # # trend_data = db.get_node_anomaly_trend(node_id, hours=24)
        # trend_data = MOCK_ANOMALY_TREND  # Temporary
        #
        # self.trend_ax.clear()
        #
        # times = [t[0] for t in trend_data]
        # scores = [t[1] for t in trend_data]
        #
        # # Plot line
        # self.trend_ax.plot(times, scores, 'b-', linewidth=2, marker='o', markersize=4)
        # self.trend_ax.fill_between(times, scores, alpha=0.3)
        #
        # # Add threshold line
        # self.trend_ax.axhline(y=0.5, color='r', linestyle='--', alpha=0.7, label='Threshold')
        #
        # # Labels
        # self.trend_ax.set_xlabel('Time')
        # self.trend_ax.set_ylabel('Anomaly Score')
        # self.trend_ax.set_ylim(0, 1)
        # self.trend_ax.legend(loc='upper right')
        # self.trend_ax.grid(True, linestyle='--', alpha=0.7)
        #
        # # Format dates
        # self.trend_fig.autofmt_xdate()
        #
        # # Redraw
        # self.trend_fig.tight_layout()
        # self.trend_canvas.draw()
        pass
    
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
    
    def update_node_list(self, node_ids: List[str]):
        """
        Update the node selector dropdown with available nodes.
        
        Args:
            node_ids: List of all node IDs
        """
        # TODO: Implement
        #
        # if self.node_selector:
        #     current = self.node_selector.get()
        #     self.node_selector['values'] = sorted(node_ids)
        #     # Preserve selection if still valid
        #     if current in node_ids:
        #         self.node_selector.set(current)
        #     elif node_ids:
        #         self.node_selector.current(0)
        pass
    
    def refresh(self):
        """
        Refresh data for the currently selected node.
        """
        # TODO: Implement
        #
        # if self.current_node_id:
        #     self.load_node(self.current_node_id)
        pass


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
