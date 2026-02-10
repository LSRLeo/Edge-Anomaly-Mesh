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

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from datetime import datetime, timedelta

from matplotlib import style

# from ui.ui_utils import (
#     SEVERITY_COLORS, STATUS_COLORS,
#     format_timestamp, format_anomaly_score,
#     get_severity_color
# )

# Avoid circular import
if TYPE_CHECKING:
    from ui.widgets.dashboard_main import DashboardApp


# =============================================================================
# MOCK DATA - Replace with database queries
# =============================================================================
#confidence_list is [IDLE, GROUND, MARITIME, LIFT, IDLE_ANOMALY, GROUND_ANOMALY, MARITIME_ANOMALY, LIFT_ANOMALY]
MOCK_ANOMALIES = [
    {
        'id': 1,
        'timestamp': datetime.now() - timedelta(minutes=5),
        'node_id': 'node_003',
        'motion_class': 'MARITIME_ANOMALY',
        'confidence_list': [.01,.01,.03,.01,.01,.92,.01,.01], #should sum to 1 will need to take max(confidence_list) for score
    },
    
    {
        'id': 2,
        'timestamp': datetime.now() - timedelta(minutes=12),
        'node_id': 'node_007',
        'motion_class': 'IDLE_ANOMALY',
        'confidence_list': [0.07, 0.01, 0.01, 0.01, 0.88, 0.01, 0.01, 0.00],  # max=0.88 (IDLE), anomaly label chosen by model rule
    },
    {
        'id': 3,
        'timestamp': datetime.now() - timedelta(minutes=18),
        'node_id': 'node_011',
        'motion_class': 'TERRESTRIAL_ANOMALY',
        'confidence_list': [0.02, 0.05, 0.02, 0.01, 0.02, 0.02, 0.84, 0.02],  # max=0.84
    },
    {
        'id': 4,
        'timestamp': datetime.now() - timedelta(minutes=27),
        'node_id': 'node_015',
        'motion_class': 'LIFT_ANOMALY',
        'confidence_list': [0.01, 0.01, 0.01, 0.03, 0.02, 0.02, 0.00, 0.90],  # max=0.90
    }

]
class AnomalySection(ttk.Frame):
    """
    Tab subsection for anomaly viewer, will be contained in the AnomaliesTab.
    There will be other tabs implemented in future sprints
    """
    def __init__(self, parent: ttk.Frame, owner: AnomaliesTab, title= "Anomalies"):

        super().__init__(parent)
        self.parent = owner
        self.title = title
        # self._on_open_node = on_open_node
        self._canvas: Optional[tk.Canvas] = None
        self._rows_frame: Optional[ttk.Frame] = None
        self._status_var = tk.StringVar(value="Ready")
        self._rows: List[Dict[str, Any]] = []
        self.anomaly_data: List[Dict[str, Any]] = []
        self._build_ui()
    
    def _build_ui(self):
        # --- Top bar ---
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Button(top, text="Refresh", command=self._on_refresh_clicked).pack(side="left")

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

        # (Optional) Placeholder content to show the area is scrollable
        # Remove this later when you add real content
        placeholder = ttk.Label(self._inner, text="Scrollable content area (skeleton)")
        placeholder.pack(pady=16)
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
    def _on_refresh_clicked(self):
        pass



    


class AnomaliesTab(ttk.Frame):
    """
    Anomalies feed tab.
    
    Displays a table of detected anomalies and click-to-view-details functionality.
    """
    
    def __init__(self, parent, dashboard: 'DashboardApp'):
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


        self._nav = ttk.Frame(self)
        self._nav.pack(fill="x", padx=10, pady=10)

        style.configure("Nav.TButton")
        style.configure("Nav.Active.TButton")

        # Internal notebook to allow multiple sections later
        self._sections_nb = ttk.Notebook(self, style='Tabless.TNotebook')
        self._sections_nb.pack(fill="both", expand=True)
        print("Inner notebook style:", self._sections_nb.cget("style"))
        # Create and add the initial anomalies list section
        self._list_section = AnomalySection(self, self, title="Anomalies")
        self._sections_nb.add(self._list_section, text=self._list_section.title)

        # Build UI
        # self._setup_ui()
    
    # def _setup_ui(self):
    #     """
    #     Create the tab layout.
        
    #     Layout:
    #     ┌─────────────────────────────────────┐
    #     │  Node: [▼]  Severity: [▼]  Time: [▼]│
    #     ├─────────────────────────────────────┤
    #     │  Timestamp  │ Node │ Sev │ Score │  │
    #     │  ─────────────────────────────────  │
    #     │  10:30:00   │ 003  │ HIGH│ 0.92  │  │
    #     │  10:18:00   │ 005  │ MED │ 0.67  │  │
    #     │  ...        │ ...  │ ... │ ...   │  │
    #     └─────────────────────────────────────┘
    #     """
    #     # Configure grid
    #     self.columnconfigure(0, weight=1)
    #     self.rowconfigure(1, weight=1)
        
    #     # TODO: Create filter bar
    #     # self._setup_filters()
        
    #     # TODO: Create treeview table
    #     # self._setup_table()
        
    #     # TEMPORARY: Placeholder
    #     ttk.Label(self, text="Anomalies Tab - TODO: Implement filters and table").pack(pady=20)
    
    # def _setup_filters(self):
    # #     """
    # #     Create the filter controls bar.
        
    # #     Filters:
    # #     - Node ID: Dropdown with all node IDs + "All"
    # #     - Severity: Dropdown with HIGH, MEDIUM, LOW + "All"
    # #     - Time Range: Dropdown with preset time ranges
    # #     """
    # #     # TODO: Implement filters
    # #     #
    # #     # filter_frame = ttk.Frame(self)
    # #     # filter_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
    # #     #
    # #     # # Node filter
    # #     # ttk.Label(filter_frame, text="Node:").grid(row=0, column=0, padx=(0, 5))
    # #     # self.node_filter = ttk.Combobox(filter_frame, values=['All'], 
    # #     #                                  state='readonly', width=12)
    # #     # self.node_filter.current(0)
    # #     # self.node_filter.grid(row=0, column=1, padx=(0, 15))
    # #     # self.node_filter.bind('<<ComboboxSelected>>', self._on_filter_change)
    # #     #
    # #     # # Severity filter
    # #     # ttk.Label(filter_frame, text="Severity:").grid(row=0, column=2, padx=(0, 5))
    # #     # self.severity_filter = ttk.Combobox(
    # #     #     filter_frame, 
    # #     #     values=['All', 'HIGH', 'MEDIUM', 'LOW'],
    # #     #     state='readonly', width=10
    # #     # )
    # #     # self.severity_filter.current(0)
    # #     # self.severity_filter.grid(row=0, column=3, padx=(0, 15))
    # #     # self.severity_filter.bind('<<ComboboxSelected>>', self._on_filter_change)
    # #     #
    # #     # # Time range filter
    # #     # ttk.Label(filter_frame, text="Time:").grid(row=0, column=4, padx=(0, 5))
    # #     # self.time_filter = ttk.Combobox(
    # #     #     filter_frame,
    # #     #     values=['Last hour', 'Last 6 hours', 'Last 24 hours', 'Last 7 days', 'All time'],
    # #     #     state='readonly', width=15
    # #     # )
    # #     # self.time_filter.current(2)  # Default: Last 24 hours
    # #     # self.time_filter.grid(row=0, column=5, padx=(0, 15))
    # #     # self.time_filter.bind('<<ComboboxSelected>>', self._on_filter_change)
    # #     #
    # #     # # Refresh button
    # #     # ttk.Button(filter_frame, text="Refresh", 
    # #     #            command=self.refresh).grid(row=0, column=6, padx=(15, 0))
    #     pass
    
    # def _setup_table(self):
    #     """
    #     Create the Treeview table for displaying anomalies.
        
    #     Columns:
    #     - Timestamp (150px)
    #     - Node ID (100px)
    #     - Motion Class (100px)
    #     - Confidence Score (80px)
    #     """
    #     # TODO: Implement table
    #     #
    #     # # Frame for treeview and scrollbar
    #     # table_frame = ttk.Frame(self)
    #     # table_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))
    #     # table_frame.columnconfigure(0, weight=1)
    #     # table_frame.rowconfigure(0, weight=1)
    #     #
    #     # # Define columns
    #     # columns = ('timestamp', 'node_id', 'motion_class', 'confidence_score')
    #     #
    #     # # Create treeview
    #     # self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
    #     #                          selectmode='browse')
    #     #
    #     # # Configure columns
    #     # self.tree.heading('timestamp', text='Timestamp')
    #     # self.tree.heading('node_id', text='Node ID')
    #     # self.tree.heading('motion_class', text='Motion Class')
    #     # self.tree.heading('confidence_score', text='Confidence Score')
    #     # 
    #     # self.tree.column('timestamp', width=150, anchor='center')
    #     # self.tree.column('node_id', width=100, anchor='center')
    #     # self.tree.column('motion_class', width=100, anchor='center')
    #     # self.tree.column('confidence_score', width=80, anchor='center')
    #     # 
    #     # self.tree.grid(row=0, column=0, sticky='nsew')
    #     #
    #     # # Scrollbar
    #     # scrollbar = ttk.Scrollbar(table_frame, orient='vertical', 
    #     #                           command=self.tree.yview)
    #     # scrollbar.grid(row=0, column=1, sticky='ns')
    #     # self.tree.configure(yscrollcommand=scrollbar.set)
    #     #
    #     # # Bind selection event
    #     # self.tree.bind('<<TreeviewSelect>>', self._on_row_select)
    #     #
    #     # # Configure row tags for coloring
    #     # self.tree.tag_configure('HIGH', foreground=SEVERITY_COLORS['HIGH'])
    #     # self.tree.tag_configure('MEDIUM', foreground=SEVERITY_COLORS['MEDIUM'])
    #     # self.tree.tag_configure('LOW', foreground=SEVERITY_COLORS['LOW'])
    #     pass
    
    # def load_anomalies(self, anomalies: List[Dict[str, Any]]):
    #     """
    #     Load anomalies into the table.
        
    #     Args:
    #         anomalies: List of anomaly dictionaries
    #     """
    #     # TODO: Implement
    #     #
    #     # # Clear existing rows
    #     # for item in self.tree.get_children():
    #     #     self.tree.delete(item)
    #     #
    #     # # Add new rows
    #     # for anomaly in anomalies:
    #     #     self._add_anomaly_row(anomaly)
    #     pass
    
    # def _add_anomaly_row(self, anomaly: Dict[str, Any]):
    # #     """
    # #     Add a single anomaly row to the table.
        
    # #     Args:
    # #         anomaly: Anomaly dictionary
    # #     """
    # #     # TODO: Implement
    # #     #
    # #     # values = (
    # #     #     format_timestamp(anomaly['timestamp']),
    # #     #     anomaly['node_id'],
    # #     #     anomaly['severity'],
    # #     #     anomaly['motion_class'],
    # #     #     format_anomaly_score(anomaly['score']),
    # #     #     anomaly['status'],
    # #     #     anomaly.get('description', '')
    # #     # )
    # #     #
    # #     # # Insert with severity tag for coloring
    # #     # self.tree.insert('', 'end', iid=str(anomaly['id']), values=values,
    # #     #                  tags=(anomaly['severity'],))
    #     pass
    
    # def apply_filters(self):
    # #     """
    # #     Re-query data with current filter settings.
        
    # #     Reads filter values from UI and fetches matching anomalies.
    # #     """
    # #     # TODO: Implement
    # #     #
    # #     # # Get current filter values
    # #     # self.current_filters['node_id'] = self.node_filter.get()
    # #     # self.current_filters['severity'] = self.severity_filter.get()
    # #     # self.current_filters['time_range'] = self.time_filter.get()
    # #     #
    # #     # # Convert time range to datetime
    # #     # time_ranges = {
    # #     #     'Last hour': timedelta(hours=1),
    # #     #     'Last 6 hours': timedelta(hours=6),
    # #     #     'Last 24 hours': timedelta(hours=24),
    # #     #     'Last 7 days': timedelta(days=7),
    # #     #     'All time': None
    # #     # }
    # #     # time_delta = time_ranges.get(self.current_filters['time_range'])
    # #     #
    # #     # # Fetch filtered data from database
    # #     # # anomalies = db.get_anomalies(
    # #     # #     node_id=None if self.current_filters['node_id'] == 'All' else self.current_filters['node_id'],
    # #     # #     severity=None if self.current_filters['severity'] == 'All' else self.current_filters['severity'],
    # #     # #     since=datetime.now() - time_delta if time_delta else None
    # #     # # )
    # #     #
    # #     # # For now, filter mock data
    # #     # anomalies = self._filter_mock_data()
    # #     #
    # #     # # Update table
    # #     # self.load_anomalies(anomalies)
    #     pass
    
    # def _filter_mock_data(self) -> List[Dict[str, Any]]:
    # #     """
    # #     Filter mock data based on current filters (temporary).
        
    # #     Returns:
    # #         Filtered list of anomalies
    # #     """
    # #     # TODO: Remove when real database is connected
    # #     filtered = MOCK_ANOMALIES.copy()
        
    # #     # Apply node filter
    # #     if self.current_filters['node_id'] != 'All':
    # #         filtered = [a for a in filtered 
    # #                    if a['node_id'] == self.current_filters['node_id']]
        
    # #     # Apply severity filter
    # #     if self.current_filters['severity'] != 'All':
    # #         filtered = [a for a in filtered 
    # #                    if a['severity'] == self.current_filters['severity']]
        
    # #     return filtered
    #  pass
    
    # def _on_filter_change(self, event):
    # #     """
    # #     Handle filter dropdown change.
        
    # #     Args:
    # #         event: Combobox selection event
    # #     """
    # #     # TODO: Implement
    # #     # self.apply_filters()
    #     pass
    
    # def _on_row_select(self, event):
    # #     """
    # #     Handle row selection in the table.
        
    # #     Navigates to Node Details tab for the selected anomaly's node.
        
    # #     Args:
    # #         event: Treeview selection event
    # #     """
    # #     # TODO: Implement
    # #     #
    # #     # selection = self.tree.selection()
    # #     # if not selection:
    # #     #     return
    # #     #
    # #     # # Get the selected row's values
    # #     # item = self.tree.item(selection[0])
    # #     # values = item['values']
    # #     # node_id = values[1]  # node_id is column index 1
    # #     #
    # #     # # Navigate to node details
    # #     # self.dashboard.show_node_details(node_id)
    #     pass
    
    # def update_node_filter_options(self, node_ids: List[str]):
    # #     """
    # #     Update the node filter dropdown with available node IDs.
        
    # #     Args:
    # #         node_ids: List of all node IDs
    # #     """
    # #     # TODO: Implement
    # #     #
    # #     # if self.node_filter:
    # #     #     current = self.node_filter.get()
    # #     #     self.node_filter['values'] = ['All'] + sorted(node_ids)
    # #     #     # Preserve selection if still valid
    # #     #     if current in ['All'] + node_ids:
    # #     #         self.node_filter.set(current)
    # #     #     else:
    # #     #         self.node_filter.current(0)
    #     pass
    
    # def refresh(self):
    #     """
    #     Refresh the anomalies table with latest data.
        
    #     Fetches current anomalies from database and updates display.

    #     Will be tied to a "Refresh" button in the UI to prevent excessive queries and ensure readability
    #     """
    #     # TODO: Implement with real database queries
    #     #
    #     # try:
    #     #     # Update node filter options
    #     #     # node_ids = db.get_all_node_ids()
    #     #     # self.update_node_filter_options(node_ids)
    #     #     
    #     #     # Apply current filters and reload
    #     #     self.apply_filters()
    #     #     
    #     # except Exception as e:
    #     #     print(f"Error refreshing anomalies tab: {e}")
    #     pass


# =============================================================================
# DEMO / TEST
# =============================================================================

def demo():
    """Demonstrate the AnomaliesTab independently."""
    root = tk.Tk()
    root.title("Anomalies Tab Demo")
    root.geometry("900x500")
    
    # Create a mock dashboard
    class MockDashboard:
        def show_node_details(self, node_id):
            print(f"Show details for: {node_id}")
    
    # notebook = ttk.Notebook(root)
    # notebook.pack(fill='both', expand=True)
    
    # tab = AnomaliesTab(notebook, dashboard=MockDashboard())
    # notebook.add(tab, text='Anomalies')
    

    container = ttk.Frame(root)
    container.pack(fill="both", expand=True)

    anomalies_tab = AnomaliesTab(container, dashboard=MockDashboard())  # your DashboardApp instance
    anomalies_tab.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == '__main__':
    demo()
