"""
anomalies_tab.py - Anomalies feed tab with filtering and table display.

This module contains:
- AnomaliesTab: Frame containing anomaly list with filters
- Treeview table for anomaly display
- Filter controls (node, severity, time range)
- Row selection handling

Features:
- Live feed of detected anomalies
- Filter by node ID, severity level, time range
- Color-coded severity (HIGH=red, MEDIUM=orange, LOW=blue)
- Click row to view node details
- Status tracking (NEW, ACKNOWLEDGED, RESOLVED)
"""

import json
import os
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from datetime import datetime, timedelta

from matplotlib import style
from redis_reader import RedisReader
from widgets.parent_classes import Node
from widgets.parent_classes import DashboardParents

# from ui.ui_utils import (
#     SEVERITY_COLORS, STATUS_COLORS,
#     format_timestamp, format_anomaly_score,
#     get_severity_color
# )

# Avoid circular import
if TYPE_CHECKING:
    from widgets.dashboard_main import DashboardApp


# =============================================================================
# MOCK DATA - Replace with database queries
# =============================================================================
#confidence_list is [IDLE, GROUND, MARITIME, LIFT, IDLE_ANOMALY, GROUND_ANOMALY, MARITIME_ANOMALY, LIFT_ANOMALY]
MOCK_ANOMALIES = [
    {
        
        'timestamp': datetime.now() - timedelta(minutes=5),
        'node_id': 'node_003',
        'motion_class': 'MARITIME_ANOMALY',
        'confidence_list': [.01,.01,.03,.01,.01,.92,.01,.01], #should sum to 1 will need to take max(confidence_list) for score
    },
    
    {
        
        'timestamp': datetime.now() - timedelta(minutes=12),
        'node_id': 'node_007',
        'motion_class': 'IDLE_ANOMALY',
        'confidence_list': [0.07, 0.01, 0.01, 0.01, 0.88, 0.01, 0.01, 0.00],  # max=0.88 (IDLE), anomaly label chosen by model rule
    },
    {
        
        'timestamp': datetime.now() - timedelta(minutes=18),
        'node_id': 'node_011',
        'motion_class': 'TERRESTRIAL_ANOMALY',
        'confidence_list': [0.02, 0.05, 0.02, 0.01, 0.02, 0.02, 0.84, 0.02],  # max=0.84
    },
    {
        
        'timestamp': datetime.now() - timedelta(minutes=27),
        'node_id': 'node_015',
        'motion_class': 'LIFT_ANOMALY',
        'confidence_list': [0.01, 0.01, 0.01, 0.03, 0.02, 0.02, 0.00, 0.90],  # max=0.90
    }

]
class RedisMonitorSection(ttk.Frame):
    def __init__(self, parent, dashboard: 'DashboardApp', title= "Redis Monitor"):

        super().__init__(parent)
        self.parent = parent
        self.dashboard = dashboard
        self.title = title
        # self._on_open_node = on_open_node
        self._canvas: Optional[tk.Canvas] = None
        self._rows_frame: Optional[ttk.Frame] = None
        self._status_var = tk.StringVar(value="Ready")
        self._rows: List[Dict[str, Any]] = []
        
        self.motion_states = ["IDLE", "TERRESTRIAL", "MARITIME", "LIFT", "IDLE_ANOMALY", "TERRESTRIAL_ANOMALY", "MARITIME_ANOMALY", "LIFT_ANOMALY"] #key for motion class index to string
        
        self._build_ui()
    def _build_ui(self):
        # --- Top bar ---
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Button(top, text="Refresh", command=self.parent.refresh()).pack(side="left")

        # --- Scrollable area ---
        outer = ttk.Frame(self)
        outer.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        self._canvas = tk.Canvas(outer, highlightthickness=0)
        self._canvas.grid(row=0, column=0, sticky="nsew")

        vscroll = ttk.Scrollbar(outer, orient="vertical", command=self._canvas.yview)
        vscroll.grid(row=0, column=1, sticky="ns")
        self._canvas.configure(yscrollcommand=vscroll.set)

        # Inner frame goes inside the canvas as a window
        self._inner = ttk.Frame(self._canvas)
        self._inner_window = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")


        # Bindings to make scrolling and resizing correct
        self._inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        

        # Build initial rows
        self._build_rows()
class AnomalySection(ttk.Frame):
    """
    Tab subsection for anomaly viewer, will be contained in the AnomaliesTab.
    There will be other tabs implemented in future sprints
    """
    def __init__(self, parent, dashboard: 'DashboardApp', title= "Anomalies"):

        super().__init__(parent)
        self.parent = parent
        self.dashboard = dashboard
        self.title = title
        # self._on_open_node = on_open_node
        self._canvas: Optional[tk.Canvas] = None
        self._rows_frame: Optional[ttk.Frame] = None
        self._status_var = tk.StringVar(value="Ready")
        self._rows: List[Dict[str, Any]] = []
        self.anomaly_data: List[Dict[str, Any]] = []
        
        self.motion_states = ["IDLE", "TERRESTRIAL", "MARITIME", "LIFT", "IDLE_ANOMALY", "TERRESTRIAL_ANOMALY", "MARITIME_ANOMALY", "LIFT_ANOMALY"] #key for motion class index to string
        
        self._build_ui()
    
    def _build_ui(self):
        # --- Top bar ---
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Button(top, text="Refresh", command=self.parent.refresh()).pack(side="left")

        # --- Scrollable area ---
        outer = ttk.Frame(self)
        outer.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        self._canvas = tk.Canvas(outer, highlightthickness=0)
        self._canvas.grid(row=0, column=0, sticky="nsew")

        vscroll = ttk.Scrollbar(outer, orient="vertical", command=self._canvas.yview)
        vscroll.grid(row=0, column=1, sticky="ns")
        self._canvas.configure(yscrollcommand=vscroll.set)

        # Inner frame goes inside the canvas as a window
        self._inner = ttk.Frame(self._canvas)
        self._inner_window = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")


        # Bindings to make scrolling and resizing correct
        self._inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        

        # Build initial rows
        self._build_rows()
    def _on_inner_configure(self, event):
        # Update scroll region to encompass the inner frame
        if self._canvas:
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        return
    def _on_canvas_configure(self, event):
        # Update the inner frame's width to match the canvas width
        if self._canvas and self._inner_window is not None:
            self._canvas.itemconfig(self._inner_window, width=event.width)
        return
    def _build_rows(self):
        # Clear existing rows
        for row in self._rows:
            row['frame'].destroy()
        self._rows.clear()
        # self.populate_test_nodes()
        self.parent.refresh()
        # Build new rows
        for node_id in list(self.parent.nodes.keys()):
            node = self.parent.nodes[node_id]
            if node.anomaly:
                self._build_single_row(node)
    
    def load_json(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError
        with open(filename, 'r') as file:
            return json.load(file)
    # def populate_test_nodes(self):
        file = self.load_json('widgets/test_nodes.json')
        

        for entry in file:
            try:
                self.load_node(entry["node_id"], entry)

            except Exception as e:
                print(f"[load_nodes] Failed to load entry {entry}: {e}")

  
    
    def _build_single_row(self, anomaly: Node):
        
        container = ttk.Frame(self._inner, padding=(10, 8))
        container.pack(fill="x", pady=4)

        # Optional subtle border style
        try:
            style = ttk.Style(container)
            style.configure("AnomRow.TFrame", relief="groove", borderwidth=1)
            container.configure(style="AnomRow.TFrame")
        except Exception:
            pass
        

    # Top line: node_id (bold) left, timestamp right
        top = ttk.Frame(container)
        top.pack(fill="x")
        node_lbl = ttk.Label(top, text=anomaly.getNodeID())
        try:
            node_lbl.configure(font=("TkDefaultFont", 10, "bold"))
        except Exception:
            pass
        node_lbl.pack(side="left")
        ttk.Label(top, text=self._fmt_ts(anomaly.timestampToStr())).pack(side="right")


        # Second line: anomaly type
        mid = ttk.Frame(container)
        mid.pack(fill="x", pady=(4, 0))
        ttk.Label(mid, text=f"Type: {anomaly.getMotionString()}").pack(side="left")

        # Actions
        actions = ttk.Frame(container)
        actions.pack(fill="x", pady=(6, 0))
        ttk.Button(actions, text="Open node", command=lambda r=anomaly.getNodeID(): self._open_node(r)).pack(side="left")

        # Make row clickable to open node
        container.bind("<Button-1>", lambda _e, r=anomaly.getNodeID(): self._open_node(r))
        top.bind("<Button-1>", lambda _e, r=anomaly.getNodeID(): self._open_node(r))
        mid.bind("<Button-1>", lambda _e, r=anomaly.getNodeID(): self._open_node(r))

    def _fmt_ts(self, iso_str: str) -> str:
        """Return a compact UTC display string."""
        from datetime import datetime, timezone
        try:
            v = iso_str
            if v.endswith("Z"):
                v = v[:-1] + "+00:00"
            dt = datetime.fromisoformat(v)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            dt = dt.astimezone(timezone.utc)
            return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            return iso_str
    def _open_node(self, node_id: str):
        """Callback when an anomaly row is clicked to open node details."""
        if self.dashboard.node_details_tab is None:
            print("Node Details tab not available")
            return
        self.dashboard._select_tab(3)  # Switch to Node Details tab
        self.dashboard.node_details_tab.display_node(node_id)






    


class AnomaliesTab(ttk.Frame, DashboardParents):
    """
    Anomalies feed tab.
    
    Displays a table of detected anomalies and click-to-view-details functionality.
    """
    
    def __init__(self, parent, dashboard: 'DashboardApp', redis_reader: RedisReader):
        """
        Initialize the Anomalies tab.
        
        Args:
            parent: Parent notebook widget
            dashboard: Reference to main dashboard for callbacks
        """
        super().__init__(parent)
        style = ttk.Style(self)
        style.layout('Tabless.TNotebook', [('Notebook.client', {'sticky': 'nswe'})])
        self.dashboard = dashboard

        self.redis_reader = redis_reader
        self.nodes = {}  # Store Node objects keyed by node_id
        self.rddict = {} #raw data dictionary
        self.mldict = {} #machine learning dictionary
        self._nav = ttk.Frame(self)
        self._nav.pack(fill="x", padx=10, pady=10)

        style.configure("Nav.TButton")
        style.configure("Nav.Active.TButton")

        # Internal notebook to allow multiple sections later
        self._sections_nb = ttk.Notebook(self, style='Tabless.TNotebook')
        self._sections_nb.pack(fill="both", expand=True)
        print("Inner notebook style:", self._sections_nb.cget("style"))
        # Create and add the initial anomalies list section
        self._list_section = AnomalySection(self, self.dashboard, title="Anomalies")
        self._sections_nb.add(self._list_section, text=self._list_section.title)
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
    def _parse_nodes(self):
        for node_id, rdentry in self.rddict.items():
            mlentry = self.mldict.get(node_id, [])
            try:
                self.load_node(node_id, rdentry, mlentry)
            except Exception as e:
                print(f"[NodeDetailsTab._parse_nodes] Error parsing node {node_id}: {e}")
    def refresh(self):
    #     """
    #     Refresh the anomalies table with latest data.
        
    #     Fetches current anomalies from database and updates display.

    #     Will be tied to a "Refresh" button in the UI to prevent excessive queries and ensure readability
    #     """
        try:
            self.rddict, self.mldict = self.redis_reader.getDicts() #get latest data from redis reader
            self._list_section._build_rows() #rebuild the anomaly rows with updated node data
        except Exception as e:
            print(f"Error refreshing anomalies tab: {e}")


# =============================================================================
# DEMO / TEST
# =============================================================================

# def demo():
#     """Demonstrate the AnomaliesTab independently."""
#     root = tk.Tk()
#     root.title("Anomalies Tab Demo")
#     root.geometry("900x500")
    
#     # Create a mock dashboard
#     class MockDashboard:
#         def show_node_details(self, node_id):
#             print(f"Show details for: {node_id}")
    
#     # notebook = ttk.Notebook(root)
#     # notebook.pack(fill='both', expand=True)
    
#     # tab = AnomaliesTab(notebook, dashboard=MockDashboard())
#     # notebook.add(tab, text='Anomalies')
    

#     container = ttk.Frame(root)
#     container.pack(fill="both", expand=True)

#     anomalies_tab = AnomaliesTab(container, dashboard=MockDashboard())  # your DashboardApp instance
#     anomalies_tab.pack(fill="both", expand=True)

#     root.mainloop()


# if __name__ == '__main__':
#     demo()
