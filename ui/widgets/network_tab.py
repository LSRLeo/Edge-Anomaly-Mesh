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
import os
import json
from datetime import datetime
from datetime import timedelta
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import math

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

  {"node_id": "node_001", "lat": 40.2548, "lon": 105.6161, "motion_class": "IDLE", "anomaly": False},
  {"node_id": "node_002", "lat": 51.5074, "lon": -0.1278, "motion_class": "TERRESTRIAL", "anomaly": False},
  {"node_id": "node_003", "lat": 35.6762, "lon": 139.6503, "motion_class": "MARITIME", "anomaly": True},
  {"node_id": "node_004", "lat": -33.8688, "lon": 151.2093, "motion_class": "LIFT", "anomaly": False},
  {"node_id": "node_005", "lat": 48.8566, "lon": 2.3522, "motion_class": "IDLE", "anomaly": False},
  {"node_id": "node_006", "lat": -23.5505, "lon": -46.6333, "motion_class": "TERRESTRIAL", "anomaly": False}
]
# confidence list is [IDLE, GROUND, MARITIME, LIFT, IDLE_ANOMALY, TERRESTRIAL_ANOMALY, MARITIME_ANOMALY, LIFT_ANOMALY]

class MercatorProjection:
    """Convert Lat/Lon to pixel coords so Mercator map image can be displayed"""

    def __init__(self, img_width, img_height, lat_min=-80.05, long_min=-180.0, long_max=180, lat_max=80.05):
        self.img_width = img_width
        self.img_height = img_height
        self.long_min = long_min
        self.long_max = long_max
        self.merc_y_min = self._mercator_y(lat_min)
        self.merc_y_max = self._mercator_y(lat_max)
    
    @staticmethod
    def _mercator_y(lat_deg):
        lat_deg = max(-85.05, min(85.05, lat_deg))
        lat_rad = math.radians(lat_deg)
        return math.log(math.tan(math.pi / 4 + lat_rad / 2))

    def latlong_to_pixel(self, lat,long):
        x = (long - self.long_min) / (self.long_max - self.long_min) * self.img_width
        merc_y = self._mercator_y(lat)
        y = (1 - (merc_y - self.merc_y_min) / (self.merc_y_max - self.merc_y_min)) * self.img_height
        return x,y

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
        # Dict[node_id: str, node_data: dict]
        self.test_nodes: Dict[str, dict] = {} 
        # Canvas for drawing nodes
        self.canvas: Optional[tk.Canvas] = None
        
        # Track drawn node items: {node_id: canvas_item_id}
        self.node_items: Dict[str, int] = {}
        
        # Currently selected node
        self.selected_node: Optional[str] = None
        
        #Dict of colors
        self.MOTION_COLORS = {
        'IDLE' : ('gray', False),
        'TERRESTRIAL' : ('green', False),
        'MARITIME' : ('blue', False),
        'LIFT' : ('red', False),
        'ANOMALOUS IDLE' : ('gray', True),
        'ANOMALOUS TERRESTRIAL' : ('green', True),
        'ANOMALOUS MARITIME' : ('blue', True),
        'ANOMALOUS LIFT' : ('red', True)
        #'Anomaly indicator' : 'red'
        }
        self.ANOMALY_BORDER_COLOR = 'red'
        # Border width for node
        self.ANOMALY_BORDER_WIDTH = 3
        self.NODE_BORDER_WIDTH = 3

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




        legend_frame = ttk.Frame(self)
        legend_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        # Arrange legend items in two rows
        items_per_row = 4
        filtered_items = [(motion, color, is_anomalous) for motion, (color, is_anomalous) in self.MOTION_COLORS.items() if motion != 'UNKNOWN']
        for idx, (motion, color, is_anomalous) in enumerate(filtered_items):
            row = idx // items_per_row
            col = (idx % items_per_row) * 2
            mini_canvas = tk.Canvas(legend_frame, width=20, height=20, highlightthickness=0)
            if not is_anomalous:
                mini_canvas.create_oval(2, 2, 18, 18, fill=color, outline='black')
            else:
                mini_canvas.create_oval(2, 2, 18, 18, fill=color, outline='red')
            mini_canvas.grid(row=row, column=col, padx=(10, 2), pady=2)
            ttk.Label(legend_frame, text=motion).grid(row=row, column=col+1, padx=(0, 10), pady=2)


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
        # Implement Background
        # Load Map
        map_image = Image.open("widgetextras/mercator.jpg")
        self.map_photo = ImageTk.PhotoImage(map_image)
        self.projection = MercatorProjection(map_image.width, map_image.height)
        self.canvas.create_image(0,0,image=self.map_photo, anchor='nw')

        # Draw Nodes

        # Bind click event
        self.canvas.bind('<Button-2>', self._on_canvas_click)
        self.canvas.bind('<Button-3>', self._on_canvas_click)

        self.canvas.bind('<Button-1>', self._on_canvas_click)
        self.populate_test_nodes()


    
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

        self.canvas.delete('node')
        self.node_items.clear()
        for node in nodes:
            self._draw_single_node(node)
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
        node_id = node.get('node_id', 'unknown')
        old_item = self.node_items.get(node_id)
        if old_item:
            self.canvas.delete(old_item)
            self.canvas.delete(f'{node_id}_label')
        px, py = self.projection.latlong_to_pixel(node['lat'], node['lon'])
        motion_class = node.get('motion_class','UNKNOWN')
        is_anomaly = node.get('anomaly', False)
        
        fill_color = self.get_motion_color(motion_class)
        r = 10

        if is_anomaly:
            outline_col = 'red'
            outline_width = self.ANOMALY_BORDER_WIDTH
            item_id = self.canvas.create_polygon(px,py+10,px-10,py-10,px+10,py-10,
            fill=fill_color,
            outline=outline_col,
            width=outline_width,
            tags=('node', node_id))
            
        else:
            outline_col = 'black'
            outline_width = self.NODE_BORDER_WIDTH
            item_id = self.canvas.create_oval(
            px - r, py - r, px + r, py + r,
            fill=fill_color,
            outline=outline_col,
            width=outline_width,
            tags=('node', node_id)
        )
        # Draw circle

        # Draw label below node
        self.canvas.create_text(
            px, py + r + 10,
            text=node_id,
            font=('Arial', 8),
            tags=('node', f'{node_id}_label -- anomaly: {is_anomaly} motion_class: {motion_class}'),
            fill='white'
        )
        self.node_items[node_id] = item_id

    
    def update_node_color(self, node_id: str, motion_class: str):
        """
        Update the color of a specific node.
        
        Args:
            node_id: ID of the node to update
            motion_class: New motion class for coloring
        """
        if node_id in self.node_items:
            item_id = self.node_items[node_id]
            color = self.get_motion_color(motion_class)
            self._draw_single_node(self.node_items)
        

    def get_motion_color(self, motion_class):
        color_tuple = self.MOTION_COLORS.get(motion_class, ('gray', False))
        # Always return just the color string
        return color_tuple[0]
    
    def highlight_anomaly(self, node_id: str, is_anomaly: bool):
        """
        Add or remove anomaly highlighting from a node.
        
        Args:
            node_id: ID of the node
            is_anomaly: True to highlight, False to remove highlight
        """
        if node_id in self.node_items:
            item_id = self.node_items[node_id]
            if is_anomaly:
                self.canvas.itemconfig(item_id, 
                                       outline=self.ANOMALY_BORDER_COLOR,
                                       width=self.ANOMALY_BORDER_WIDTH)
            else:
                self.canvas.itemconfig(item_id,
                                       outline='black',
                                       width=self.NODE_BORDER_WIDTH)
       
    
    def select_node(self, node_id: str):
        """
        Visually select a node (e.g., with a highlight ring).
        Args:
            node_id: ID of the node to select
        """
        # Deselect previous
        if self.selected_node and self.selected_node in self.node_items:
            self.canvas.delete(f'{self.selected_node}_selection')

        self.selected_node = node_id
        if node_id in self.node_items:
            item_id = self.node_items[node_id]
            item_type = self.canvas.type(item_id)
            coords = self.canvas.coords(item_id)
            xs = coords[0::2]
            ys = coords[1::2]
        if item_type == 'oval':
            pad = 4  # spacing around the shape
            self.canvas.create_oval(
                coords[0] - pad, coords[1] - pad,
                coords[2] + pad, coords[3] + pad,
                outline='blue',
                width=4,
                tags=(f'{node_id}_selection',)
            )
        elif item_type == 'polygon':
            # Scale polygon outward from its centroid
            xs = coords[0::2]
            ys = coords[1::2]

            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)
            # How much bigger the highlight is
            scale = 1.25  
            scaled_coords = []

            for x, y in zip(xs, ys):
                sx = cx + (x - cx) * scale
                sy = cy + (y - cy) * scale
                scaled_coords.extend([sx, sy])

            self.canvas.create_polygon(
                scaled_coords,
                outline='#3498db',
                fill='',
                width=4,
                joinstyle='round',
                tags=(f'{node_id}_selection',)
            )
    def _on_canvas_click(self, event):
        """
        Handle click events on the canvas.
        Toggle anomaly status visually for the clicked node.
        """
        
        # Find item at click location
        items = self.canvas.find_closest(event.x, event.y)
        if not items:
            return
        # Get tags of clicked item
        tags = self.canvas.gettags(items[0])
        # Find node_id from tags (skip 'node' and 'current')
        node_id = None
        for tag in tags:
            if tag not in ('node', 'current') and not tag.endswith('_label'):
                node_id = tag
                break
        if not node_id:
            return
        # Toggle anomaly status in self.test_nodes only if right clicked

        node = self.test_nodes.get(node_id)

        if node is not None and event.num == 1:
            self.select_node(node_id)
            self.dashboard.show_node_details(node_id)

        elif node is not None and event.num == 2 or event.num==3:
            node['anomaly'] = not node.get('anomaly')
            # Redraw just this node
            self._draw_single_node(node)
        
    

    def load_json(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError
        with open(filename, 'r') as file:
            return json.load(file)
    def populate_test_nodes(self):
        file = self.load_json('test_nodes.json')

        self.test_nodes.clear()
        for node_data in file:
            node_id = node_data['node_id']
            self.test_nodes[node_id] = node_data

        self.draw_nodes(list(self.test_nodes.values()))

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
    root.geometry("1020x1600")
    
    # Create a mock dashboard
    class MockDashboard:
        def __init__(self, network_tab):
            self.network_tab = network_tab
        def show_node_details(self, node_id):
            print(f"Show details for: {node_id}")
            # Create popout window with node details
            node_data = self.network_tab.test_nodes.get(node_id)
            if node_data is None:
                print(f"Node {node_id} not found")
                return
            
            # Create popout window with node details
            details_window = tk.Toplevel(root)
            details_window.title(f"Node Details - {node_id}")
            details_window.geometry("400x500")
            
            # Create a frame with padding
            frame = ttk.Frame(details_window, padding=20)
            frame.pack(fill='both', expand=True)
            
            # Add a title
            title_label = ttk.Label(frame, text=f"Details for {node_id}", 
                                   font=('Arial', 14, 'bold'))
            title_label.pack(pady=(0, 15))
            
            # Display each field from node_data
            for key, value in node_data.items():
                # Create a frame for each key-value pair
                row_frame = ttk.Frame(frame)
                row_frame.pack(fill='x', pady=3, anchor='w')
                
                # Key label (bold)
                key_label = ttk.Label(row_frame, text=f"{key}:", 
                                     font=('Arial', 10, 'bold'), width=20, anchor='w')
                key_label.pack(side='left')
                
                # Value label
                value_str = str(value)
                # Truncate long values
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."
                value_label = ttk.Label(row_frame, text=value_str, anchor='w')
                value_label.pack(side='left', padx=(5, 0))
            
    
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)
    
    # Create the tab first, then create dashboard with reference to it
    tab = NetworkTab(notebook, dashboard=None)
    dashboard = MockDashboard(tab)
    tab.dashboard = dashboard  # Set the dashboard reference
    notebook.add(tab, text='Network')
    # Draw mock nodes
    # tab.draw_nodes(MOCK_NODES)
    
    root.mainloop()

    # TODO Named Tuple node class

if __name__ == '__main__':
    demo()