"""
dashboard_main.py - Main application entry point for the visualization dashboard.

This module contains:
- DashboardApp: Main application class with tab container
- Menu bar setup
- Refresh loop management
- Tab coordination

Usage:
    python3 ui/dashboard_main.py
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
import sys
import os
import redis
import threading
from redis_reader import RedisReader
# TODO setup redis sub and pub, redis.redis (host=39r2, port=9198, decoderesponses=True)
# within main loop
# redis reader object, sub and pub on a thread
# redis reader connect
# Add parent directory to path for imports
CHANNELNAME_QUERY = "ui:query"
CHANNELNAME_RESPONSE = "ui:responses"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui_utils import (
    WINDOW_WIDTH, WINDOW_HEIGHT, REFRESH_INTERVAL_MS,
    configure_treeview_style
)
from widgets.network_tab import NetworkTab
from widgets.anomalies_tab import AnomaliesTab
from widgets.analytics_tab import AnalyticsTab
from widgets.node_details_tab import NodeDetailsTab


class DashboardApp:
    """
    Main dashboard application.
    
    Manages the main window, tab notebook, menu bar, and refresh loop.
    Coordinates communication between tabs.
    """
    
    def __init__(self, root: tk.Tk, redis_reader: Optional[RedisReader], test_mode=False):
        """
        Initialize the dashboard application.
        
        Args:
            root: The root Tkinter window
            redis_reader: An instance of RedisReader for data access
            test_mode: If True, runs in test mode with mock data
        """
        self.root = root
        self.root.title("Edge Anomaly Mesh - Dashboard")
        self.redis_reader = redis_reader
        self.test_mode = test_mode
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # TODO: Set minimum window size
        self.root.minsize(800, 600)
        
        # TODO: Configure root grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Configure global styles
        configure_treeview_style()
        
        # Initialize components
        self.notebook: Optional[ttk.Notebook] = None
        self.network_tab: Optional[NetworkTab] = None
        self.anomalies_tab: Optional[AnomaliesTab] = None
        self.analytics_tab: Optional[AnalyticsTab] = None
        self.node_details_tab: Optional[NodeDetailsTab] = None
        
        # Refresh state
        self._refresh_job: Optional[str] = None
        self._is_refreshing: bool = False
        
        # Build UI
        self._setup_menu()
        self._setup_tabs()
        
        # Start refresh loop
        # self.start_refresh_loop()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _setup_menu(self):
        """
        Create the menu bar with File and View menus.
        
        Menu structure:
        - File
          - Refresh Now (Ctrl+R)
          - Separator
          - Exit (Ctrl+Q)
        - View
          - Network Tab
          - Anomalies Tab
          - Analytics Tab
          - Node Details Tab
        """
        # TODO: Implement menu bar
        
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        # file_menu.add_command(label="Refresh Now", command=self.refresh_all_tabs, accelerator="Ctrl+R")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close, accelerator="Ctrl+Q")
        
        # Bind keyboard shortcuts
        # self.root.bind('<Control-r>', lambda e: self.refresh_all_tabs())
        self.root.bind('<Control-q>', lambda e: self._on_close())
        
        # View menu - for switching tabs
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Network", command=lambda: self._select_tab(0))
        view_menu.add_command(label="Anomalies", command=lambda: self._select_tab(1))
        view_menu.add_command(label="Analytics", command=lambda: self._select_tab(2))
        view_menu.add_command(label="Node Details", command=lambda: self._select_tab(3))
        # pass
    
    def _setup_tabs(self):
        """
        Create the notebook widget and initialize all tabs.
        
        Tab order:
        1. Network - Visual map of nodes
        2. Anomalies - Live feed of detected anomalies
        3. Analytics - Charts and statistics
        4. Node Details - Drill-down view for selected node
        """
        # TODO: Implement tab setup
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create each tab, passing reference to self for callbacks
        self.network_tab = NetworkTab(self.notebook, dashboard=self, redis_reader=self.redis_reader, test_mode=self.test_mode)
        self.anomalies_tab = AnomaliesTab(self.notebook, dashboard=self, redis_reader=self.redis_reader, test_mode=self.test_mode)
        self.analytics_tab = AnalyticsTab(self.notebook, dashboard=self, redis_reader=self.redis_reader, test_mode=self.test_mode)
        self.node_details_tab = NodeDetailsTab(self.notebook, dashboard=self, redis_reader=self.redis_reader, test_mode=self.test_mode)
        
        # Add tabs to notebook
        self.notebook.add(self.network_tab, text='Network')
        self.notebook.add(self.anomalies_tab, text='Anomalies')
        self.notebook.add(self.analytics_tab, text='Analytics')
        self.notebook.add(self.node_details_tab, text='Node Details')
        
        # # TEMPORARY: Add placeholder tabs for testing
        # self.notebook = ttk.Notebook(self.root)
        # self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # for name in ["Network", "Anomalies", "Analytics", "Node Details"]:
        #     frame = ttk.Frame(self.notebook)
        #     self.notebook.add(frame, text=name)
        #     ttk.Label(frame, text=f"{name} tab - TODO: Implement").pack(pady=50)
    
    def _select_tab(self, index: int):
        """
        Switch to a specific tab by index.
        
        Args:
            index: Tab index (0-3)
        """
        # TODO: Implement
        self.notebook.select(index)
        # pass
    
    # def start_refresh_loop(self):
    #     """
    #     Start the periodic refresh loop.
        
    #     Schedules refresh_all_tabs() to run every REFRESH_INTERVAL_MS.
    #     """
    #     # TODO: Implement
        
    #     def loop():
    #         if not self._is_refreshing:
    #             self.refresh_all_tabs()
    #         self._refresh_job = self.root.after(REFRESH_INTERVAL_MS, loop)
        
    #     loop()
    #     # pass
    
    # def stop_refresh_loop(self):
    #     """
    #     Stop the periodic refresh loop.
        
    #     Call this before closing the application.
    #     """
    #     # TODO: Implement
        
    #     if self._refresh_job:
    #         self.root.after_cancel(self._refresh_job)
    #         self._refresh_job = None
    #     pass
    
    # def refresh_all_tabs(self):
    #     """
    #     Trigger a refresh on all tabs.
        
    #     Calls the refresh() method on each tab to update their data.
    #     Handles errors gracefully to prevent one tab from breaking others.
    #     """
    #     # TODO: Implement
        
    #     self._is_refreshing = True
    #     try:
    #         if self.network_tab:
    #             self.network_tab.refresh()
    #         if self.anomalies_tab:
    #             self.anomalies_tab.refresh()
    #         if self.analytics_tab:
    #             self.analytics_tab.refresh()
    #         if self.node_details_tab:
    #             self.node_details_tab.refresh()
    #     except Exception as e:
    #         print(f"Error during refresh: {e}")
    #     finally:
    #         self._is_refreshing = False
    #     # pass
    
    def show_node_details(self, node_id: str):
        """
        Switch to Node Details tab and load the specified node.
        
        This is called from other tabs (Network, Anomalies) when user
        clicks on a node and wants to see details.
        
        Args:
            node_id: The ID of the node to display
        """
        # TODO: Implement
        
        # Switch to Node Details tab (index 3)
        self.notebook.select(3)
        
        # Load the node data
        if self.node_details_tab:
            self.node_details_tab.display_node(node_id)
        # pass
    
    def _on_close(self):
        """
        Handle window close event.
        
        Stops the refresh loop and destroys the window.
        """
        # TODO: Implement
        
        # self.stop_refresh_loop()
        self.root.destroy()
        # self.root.destroy()


def main():
    """
    Application entry point.
    
    Creates the root window and starts the dashboard.
    """
    toggle_test_mode = True # Set to True to enable test mode with mock data
    if not toggle_test_mode:
        pub = redis.Redis(host="localhost",port=6379, decode_responses=True)
        sub = pub.pubsub()
        sub.subscribe(CHANNELNAME_RESPONSE) #subscribe to response channel for receiving data from redis
        redis_reader = RedisReader(CHANNELNAME_QUERY, CHANNELNAME_RESPONSE, pub, sub)
    
        redis_reader.refresh(instant=True) #initial refresh to populate data from redis before starting dashboard
        RedisThread = threading.Thread(target=redis_reader.refresh, daemon=True) 
        RedisThread.start
        root = tk.Tk()
    
        # Optional: Set application icon
        # root.iconbitmap('path/to/icon.ico')
        
        # Create dashboard
        app = DashboardApp(root, redis_reader=redis_reader)
        # Create Thread for main DashBoard


        # Create listener and pub on RedisThread
        

        
        # Start the Tkinter event loop
        root.mainloop()
        # DashboardThread = threading.Thread(target=root.mainloop)
        # DashboardThread.start()

        # close redis conn
        redis_reader.stop()
    else:
        # Test mode with mock data
        root = tk.Tk()
        app = DashboardApp(root, redis_reader=None, test_mode=True)
        root.mainloop()

    

if __name__ == '__main__':
    main()
