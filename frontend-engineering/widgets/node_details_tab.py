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

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
from datetime import datetime, timedelta

# Matplotlib imports
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ui.ui_utils import (
    MOTION_COLORS,
    format_timestamp, format_confidence, format_anomaly_score,
    get_motion_color
)

# Avoid circular import
if TYPE_CHECKING:
    from ui.dashboard_main import DashboardApp


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

MOCK_HISTORY = [
    {'timestamp': datetime.now() - timedelta(minutes=1), 'motion_class': 'MARITIME', 'confidence': 0.92, 'anomaly_score': 0.15},
    {'timestamp': datetime.now() - timedelta(minutes=3), 'motion_class': 'MARITIME', 'confidence': 0.88, 'anomaly_score': 0.12},
    {'timestamp': datetime.now() - timedelta(minutes=5), 'motion_class': 'LIFT', 'confidence': 0.95, 'anomaly_score': 0.08},
    {'timestamp': datetime.now() - timedelta(minutes=7), 'motion_class': 'IDLE', 'confidence': 0.97, 'anomaly_score': 0.05},
    {'timestamp': datetime.now() - timedelta(minutes=9), 'motion_class': 'IDLE', 'confidence': 0.96, 'anomaly_score': 0.04},
    {'timestamp': datetime.now() - timedelta(minutes=11), 'motion_class': 'TERRESTRIAL', 'confidence': 0.91, 'anomaly_score': 0.11},
]

MOCK_ANOMALY_TREND = [
    (datetime.now() - timedelta(hours=6), 0.08),
    (datetime.now() - timedelta(hours=5), 0.12),
    (datetime.now() - timedelta(hours=4), 0.45),  # Spike
    (datetime.now() - timedelta(hours=3), 0.15),
    (datetime.now() - timedelta(hours=2), 0.09),
    (datetime.now() - timedelta(hours=1), 0.11),
    (datetime.now(), 0.15),
]


class NodeDetailsTab(ttk.Frame):
    """
    Node details drill-down tab.
    
    Shows comprehensive information about a single selected node,
    including metadata, motion history, and anomaly trends.
    """
    
    def __init__(self, parent: ttk.Notebook, dashboard: 'DashboardApp'):
        """
        Initialize the Node Details tab.
        
        Args:
            parent: Parent notebook widget
            dashboard: Reference to main dashboard for callbacks
        """
        super().__init__(parent)
        
        self.dashboard = dashboard
        
        # Current node
        self.current_node_id: Optional[str] = None
        
        # UI components
        self.node_selector: Optional[ttk.Combobox] = None
        self.info_labels: Dict[str, ttk.Label] = {}
        self.history_tree: Optional[ttk.Treeview] = None
        
        # Chart components
        self.trend_fig: Optional[Figure] = None
        self.trend_ax = None
        self.trend_canvas: Optional[FigureCanvasTkAgg] = None
        
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
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)  # History table expands
        self.rowconfigure(3, weight=1)  # Chart expands
        
        # TODO: Create all sections
        # self._setup_node_selector()
        # self._setup_info_panel()
        # self._setup_history_table()
        # self._setup_anomaly_trend_chart()
        
        # TEMPORARY: Placeholder
        ttk.Label(self, text="Node Details Tab - TODO: Implement").pack(pady=20)
    
    def _setup_node_selector(self):
        """
        Create the node selection dropdown.
        
        Shows all available nodes in a combobox.
        When selection changes, loads that node's data.
        """
        # TODO: Implement
        #
        # selector_frame = ttk.Frame(self)
        # selector_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        #
        # ttk.Label(selector_frame, text="Node:", font=('Arial', 12)).pack(side='left', padx=(0, 10))
        #
        # self.node_selector = ttk.Combobox(selector_frame, values=MOCK_NODES,
        #                                    state='readonly', width=20, font=('Arial', 12))
        # self.node_selector.pack(side='left')
        # self.node_selector.bind('<<ComboboxSelected>>', self._on_node_select)
        #
        # # Refresh button
        # ttk.Button(selector_frame, text="Refresh",
        #            command=self.refresh).pack(side='right', padx=10)
        pass
    
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
        # TODO: Implement
        #
        # info_frame = ttk.LabelFrame(self, text="Node Information")
        # info_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=5)
        #
        # # Configure 2-column layout
        # info_frame.columnconfigure(0, weight=1)
        # info_frame.columnconfigure(1, weight=1)
        #
        # # Left column
        # left_frame = ttk.Frame(info_frame)
        # left_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=5)
        #
        # info_items_left = [
        #     ('status', 'Status:'),
        #     ('location', 'Location:'),
        #     ('first_seen', 'First Seen:'),
        #     ('total_inferences', 'Total Inferences:'),
        # ]
        #
        # for i, (key, label_text) in enumerate(info_items_left):
        #     ttk.Label(left_frame, text=label_text).grid(row=i, column=0, sticky='w', pady=2)
        #     value_label = ttk.Label(left_frame, text='--', font=('Arial', 10, 'bold'))
        #     value_label.grid(row=i, column=1, sticky='w', padx=10, pady=2)
        #     self.info_labels[key] = value_label
        #
        # # Right column
        # right_frame = ttk.Frame(info_frame)
        # right_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=5)
        #
        # info_items_right = [
        #     ('current_motion', 'Current Motion:'),
        #     ('node_id', 'Node ID:'),
        #     ('last_seen', 'Last Seen:'),
        #     ('total_anomalies', 'Total Anomalies:'),
        # ]
        #
        # for i, (key, label_text) in enumerate(info_items_right):
        #     ttk.Label(right_frame, text=label_text).grid(row=i, column=0, sticky='w', pady=2)
        #     value_label = ttk.Label(right_frame, text='--', font=('Arial', 10, 'bold'))
        #     value_label.grid(row=i, column=1, sticky='w', padx=10, pady=2)
        #     self.info_labels[key] = value_label
        pass
    
    def _setup_history_table(self):
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
    
    def _setup_anomaly_trend_chart(self):
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
    
    def load_node(self, node_id: str):
        """
        Load and display data for a specific node.
        
        Called when:
        - User selects node from dropdown
        - User clicks node in Network tab
        - User clicks anomaly row in Anomalies tab
        
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
        pass
    
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
    
    def _load_history(self, node_id: str):
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
    
    def _load_anomaly_trend(self, node_id: str):
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
        # TODO: Implement
        #
        # node_id = self.node_selector.get()
        # if node_id:
        #     self.load_node(node_id)
        pass
    
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

def demo():
    """Demonstrate the NodeDetailsTab independently."""
    root = tk.Tk()
    root.title("Node Details Tab Demo")
    root.geometry("800x700")
    
    # Create a mock dashboard
    class MockDashboard:
        pass
    
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)
    
    tab = NodeDetailsTab(notebook, dashboard=MockDashboard())
    notebook.add(tab, text='Node Details')
    
    # Load a node
    # tab.load_node('node_003')
    
    root.mainloop()


if __name__ == '__main__':
    demo()
