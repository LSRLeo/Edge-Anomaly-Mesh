"""
network_tab.py - Network visualization tab showing all nodes on a canvas.

This module contains:
- NetworkTab: Frame containing the node visualization canvas
- Node rendering with motion state colors
- Anomaly highlighting
- Click handling for node selection

Features:
- Visual map showing all nodes as colored circles
- Color-coded by motion state (IDLE=gray, TERRESTRIAL=blue, MARITIME=green, LIFT=red)
- Anomalous nodes highlighted with red border
- Click node to view details
- Legend showing color meanings
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Any, TYPE_CHECKING

#from ui.ui_utils import (
#    MOTION_COLORS, NODE_RADIUS, NODE_BORDER_WIDTH,
#    ANOMALY_BORDER_COLOR, ANOMALY_BORDER_WIDTH,
#    get_motion_color
#)

# Avoid circular import
#if TYPE_CHECKING:
#    from ui.dashboard_main import DashboardApp


# =============================================================================
# MOCK DATA - Replace with database queries
# =============================================================================

MOCK_NODES = [
    {'node_id': 'node_001', 'x': 150, 'y': 150, 'motion_class': 'IDLE', 'anomaly': False},
    {'node_id': 'node_002', 'x': 300, 'y': 200, 'motion_class': 'TERRESTRIAL', 'anomaly': False},
    {'node_id': 'node_003', 'x': 450, 'y': 150, 'motion_class': 'MARITIME', 'anomaly': True},
    {'node_id': 'node_004', 'x': 250, 'y': 350, 'motion_class': 'LIFT', 'anomaly': False},
    {'node_id': 'node_005', 'x': 400, 'y': 300, 'motion_class': 'IDLE', 'anomaly': True},
    {'node_id': 'node_006', 'x': 550, 'y': 350, 'motion_class': 'TERRESTRIAL', 'anomaly': False},
]


class NetworkTab(ttk.Frame):
    """
    Network visualization tab.
    
    Displays all nodes on a canvas, color-coded by motion state.
    Highlights anomalous nodes and allows clicking to view details.
    """
    
    def __init__(self, parent: ttk.Notebook, dashboard: 'DashboardApp'):
        """
        Initialize the Network tab.
        
        Args:
            parent: Parent notebook widget
            dashboard: Reference to main dashboard for callbacks
        """
        super().__init__(parent)
        
        self.dashboard = dashboard
        
        # Canvas for drawing nodes
        self.canvas: Optional[tk.Canvas] = None
        
        # Track drawn node items: {node_id: canvas_item_id}
        self.node_items: Dict[str, int] = {}
        
        # Currently selected node
        self.selected_node: Optional[str] = None
        
        # Build UI
        self._setup_ui()
    
    def _setup_ui(self):
        """
        Create the tab layout.
        
        Layout:
        ┌─────────────────────────────────────┐
        │  [Legend]                           │
        ├─────────────────────────────────────┤
        │                                     │
        │           Canvas                    │
        │        (node map)                   │
        │                                     │
        └─────────────────────────────────────┘
        """
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        self._setup_legend()
        self._setup_canvas()
        ttk.Label(self, text="Network Tab - TODO: Implement canvas and legend").grid(row=2, column=0, pady=20)
        # TODO: Create legend frame at top
        # self._setup_legend()
        
        # TODO: Create main canvas
        # self._setup_canvas()
        
        # TEMPORARY: Placeholder
        #ttk.Label(self, text="Network Tab - TODO: Implement canvas and legend").pack(pady=20)
    
    def _setup_legend(self):
        """
        Create the legend showing motion state colors.
        
        Should display:
        - IDLE (gray circle)
        - TERRESTRIAL (blue circle)
        - MARITIME (green circle)
        - LIFT (red circle)
        - Anomaly indicator (red border)
        """

        MOTION_COLORS = {
        'IDLE' : 'gray',
        'TERRESTRIAL' : 'blue',
        'MARITIME' : 'green',
        'LIFT' : 'red',
        'Anomaly indicator' : 'red'
        }

        legend_frame = ttk.Frame(self)
        legend_frame.grid(row=0, column=0,sticky='ew',padx=10,pady=5)

        # Mini canvas for each key/value pair
        for i, (motion,color) in enumerate(MOTION_COLORS.items()):
            if motion == 'UNKNOWN':
                continue

            # Reusable mini canvas
            mini_canvas = tk.Canvas(legend_frame, width=20, height=20, 
                                    highlightthickness=0)
            if motion != 'Anomaly indicator':
                mini_canvas.create_oval(2, 2, 18, 18, fill=color, outline='black')
            elif motion == 'Anomaly indicator':
                mini_canvas.create_oval(2, 2, 18, 18, fill = color, outline='red')
            mini_canvas.grid(row=0,column=i*2,padx=(10,2))
            
            ttk.Label(legend_frame, text=motion).grid(row=0,column=i*2+1,padx=(0, 10))

        # TODO: Implement legend
        #
        # legend_frame = ttk.Frame(self)
        # legend_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        #
        # # Create a small canvas for each legend item
        # for i, (motion, color) in enumerate(MOTION_COLORS.items()):
        #     if motion == 'UNKNOWN':
        #         continue
        #     
        #     # Small canvas for the colored circle
        #     mini_canvas = tk.Canvas(legend_frame, width=20, height=20, 
        #                             highlightthickness=0)
        #     mini_canvas.create_oval(2, 2, 18, 18, fill=color, outline='black')
        #     mini_canvas.grid(row=0, column=i*2, padx=(10, 2))
        #     
        #     # Label
        #     ttk.Label(legend_frame, text=motion).grid(row=0, column=i*2+1, padx=(0, 10))
        pass
    
    def _setup_canvas(self):
        """
        Create the main canvas for node visualization.
        
        Features:
        - White background
        - Scrollbars if content exceeds visible area
        - Click binding for node selection
        """

       
        canvas_frame = ttk.Frame(self)
        canvas_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=1,
                                highlightbackground='gray')
        self.canvas.grid(row=0, column=0, sticky='nsew')
        # Scrollbars (optional)
        v_scroll = ttk.Scrollbar(canvas_frame, orient='vertical', 
                                 command=self.canvas.yview)
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll = ttk.Scrollbar(canvas_frame, orient='horizontal',
                                 command=self.canvas.xview)
        h_scroll.grid(row=1, column=0, sticky='ew')
        self.canvas.configure(yscrollcommand=v_scroll.set,
                              xscrollcommand=h_scroll.set)
        # Bind click event
        self.canvas.bind('<Button-1>', self._on_canvas_click)
        #
        
        # TODO: Implement canvas
        #
        # # Frame to hold canvas and scrollbars
        # canvas_frame = ttk.Frame(self)
        # canvas_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        # canvas_frame.columnconfigure(0, weight=1)
        # canvas_frame.rowconfigure(0, weight=1)
        #
        # # Create canvas
        # self.canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=1,
        #                         highlightbackground='gray')
        # self.canvas.grid(row=0, column=0, sticky='nsew')
        #
        # # Scrollbars (optional)
        # v_scroll = ttk.Scrollbar(canvas_frame, orient='vertical', 
        #                          command=self.canvas.yview)
        # v_scroll.grid(row=0, column=1, sticky='ns')
        # h_scroll = ttk.Scrollbar(canvas_frame, orient='horizontal',
        #                          command=self.canvas.xview)
        # h_scroll.grid(row=1, column=0, sticky='ew')
        #
        # self.canvas.configure(yscrollcommand=v_scroll.set,
        #                       xscrollcommand=h_scroll.set)
        #
        # # Bind click event
        # self.canvas.bind('<Button-1>', self._on_canvas_click)
        pass
    
    def draw_nodes(self, nodes: List[Dict[str, Any]]):
        """
        Draw all nodes on the canvas.
        
        Args:
            nodes: List of node dictionaries with keys:
                   - node_id: str
                   - x: int (canvas x coordinate)
                   - y: int (canvas y coordinate)
                   - motion_class: str
                   - anomaly: bool
        """
        # TODO: Implement
        #
        # # Clear existing nodes
        # self.canvas.delete('node')
        # self.node_items.clear()
        #
        # for node in nodes:
        #     self._draw_single_node(node)
        pass
    
    def _draw_single_node(self, node: Dict[str, Any]):
        """
        Draw a single node on the canvas.
        
        Args:
            node: Node dictionary with position and state info
        """
        node_id = node['node_id']
        x = node['x']
        y = node['y']
        motion_class = node.get['motion_class','UNKNOWN']
        is_anomaly = node.get['anomaly', 'FALSE']
        # TODO: implement color and legend
        # TODO: Implement
        #
        # node_id = node['node_id']
        # x, y = node['x'], node['y']
        # motion_class = node.get('motion_class', 'UNKNOWN')
        # is_anomaly = node.get('anomaly', False)
        #
        # # Get color based on motion class
        # fill_color = get_motion_color(motion_class)
        #
        # # Determine border
        # if is_anomaly:
        #     outline_color = ANOMALY_BORDER_COLOR
        #     outline_width = ANOMALY_BORDER_WIDTH
        # else:
        #     outline_color = 'black'
        #     outline_width = NODE_BORDER_WIDTH
        #
        # # Draw circle
        # r = NODE_RADIUS
        # item_id = self.canvas.create_oval(
        #     x - r, y - r, x + r, y + r,
        #     fill=fill_color,
        #     outline=outline_color,
        #     width=outline_width,
        #     tags=('node', node_id)
        # )
        #
        # # Draw label below node
        # self.canvas.create_text(
        #     x, y + r + 10,
        #     text=node_id,
        #     font=('Arial', 8),
        #     tags=('node', f'{node_id}_label')
        # )
        #
        # self.node_items[node_id] = item_id
        pass
    
    def update_node_color(self, node_id: str, motion_class: str):
        """
        Update the color of a specific node.
        
        Args:
            node_id: ID of the node to update
            motion_class: New motion class for coloring
        """
        # TODO: Implement
        #
        # if node_id in self.node_items:
        #     item_id = self.node_items[node_id]
        #     color = get_motion_color(motion_class)
        #     self.canvas.itemconfig(item_id, fill=color)
        pass
    
    def highlight_anomaly(self, node_id: str, is_anomaly: bool):
        """
        Add or remove anomaly highlighting from a node.
        
        Args:
            node_id: ID of the node
            is_anomaly: True to highlight, False to remove highlight
        """
        # TODO: Implement
        #
        # if node_id in self.node_items:
        #     item_id = self.node_items[node_id]
        #     if is_anomaly:
        #         self.canvas.itemconfig(item_id, 
        #                                outline=ANOMALY_BORDER_COLOR,
        #                                width=ANOMALY_BORDER_WIDTH)
        #     else:
        #         self.canvas.itemconfig(item_id,
        #                                outline='black',
        #                                width=NODE_BORDER_WIDTH)
        pass
    
    def select_node(self, node_id: str):
        """
        Visually select a node (e.g., with a highlight ring).
        
        Args:
            node_id: ID of the node to select
        """
        # TODO: Implement
        #
        # # Deselect previous
        # if self.selected_node and self.selected_node in self.node_items:
        #     # Remove selection indicator
        #     self.canvas.delete(f'{self.selected_node}_selection')
        #
        # # Select new
        # self.selected_node = node_id
        # if node_id in self.node_items:
        #     item_id = self.node_items[node_id]
        #     coords = self.canvas.coords(item_id)
        #     # Draw selection ring
        #     self.canvas.create_oval(
        #         coords[0] - 3, coords[1] - 3,
        #         coords[2] + 3, coords[3] + 3,
        #         outline='#3498db', width=2,
        #         tags=(f'{node_id}_selection',)
        #     )
        pass
    
    def _on_canvas_click(self, event):
        """
        Handle click events on the canvas.
        
        Finds the clicked node and triggers navigation to Node Details.
        
        Args:
            event: Tkinter event object with x, y coordinates
        """
        # TODO: Implement
        #
        # # Find item at click location
        # items = self.canvas.find_closest(event.x, event.y)
        # if not items:
        #     return
        #
        # # Get tags of clicked item
        # tags = self.canvas.gettags(items[0])
        # if 'node' not in tags:
        #     return
        #
        # # Find node_id from tags
        # for tag in tags:
        #     if tag.startswith('node_') and not tag.endswith('_label'):
        #         node_id = tag
        #         break
        #     elif tag not in ('node', 'current'):
        #         node_id = tag
        #         break
        # else:
        #     return
        #
        # # Select the node
        # self.select_node(node_id)
        #
        # # Navigate to details
        # self.dashboard.show_node_details(node_id)
        pass
    
    def refresh(self):
        """
        Refresh the network visualization with latest data.
        
        Fetches current node states from database and redraws.
        """
        # TODO: Implement with real database queries
        #
        # try:
        #     # Fetch nodes from database
        #     # nodes = db.get_all_nodes()
        #     
        #     # For now, use mock data
        #     nodes = MOCK_NODES
        #     
        #     # Redraw all nodes
        #     self.draw_nodes(nodes)
        #     
        # except Exception as e:
        #     print(f"Error refreshing network tab: {e}")
        pass


# =============================================================================
# DEMO / TEST
# =============================================================================

def demo():
    """Demonstrate the NetworkTab independently."""
    root = tk.Tk()
    root.title("Network Tab Demo")
    root.geometry("800x600")
    
    # Create a mock dashboard
    class MockDashboard:
        def show_node_details(self, node_id):
            print(f"Show details for: {node_id}")
    
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)
    
    tab = NetworkTab(notebook, dashboard=MockDashboard())
    notebook.add(tab, text='Network')
    
    # Draw mock nodes
    # tab.draw_nodes(MOCK_NODES)
    
    root.mainloop()


if __name__ == '__main__':
    demo()
