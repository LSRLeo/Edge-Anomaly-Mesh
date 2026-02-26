"""
analytics_tab.py - Analytics tab with charts and statistics.

This module contains:
- AnalyticsTab: Frame containing multiple charts and stats
- Matplotlib integration for pie, line, and bar charts
- Statistics panel

Features:
- Motion class distribution pie chart
- Anomaly rate trend line chart
- Top anomalous nodes bar chart
- Processing statistics panel
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
from datetime import datetime, timedelta

from abc import ABC, abstractmethod

import json
from collections import Counter, defaultdict

# Matplotlib imports for embedding in Tkinter
import matplotlib
matplotlib.use('TkAgg')  # Must be before importing pyplot
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

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

# Avoid circular import
if TYPE_CHECKING:
    from ui.dashboard_main import DashboardApp


STATE_INDEX = {
    0: ("IDLE", False),
    1: ("TERRESTRIAL", False),
    2: ("MARITIME", False),
    3: ("LIFT", False),
    4: ("IDLE", True),
    5: ("TERRESTRIAL", True),
    6: ("MARITIME", True),
    7: ("LIFT", True),
}



class AnalyticsComponent(ABC):
    """
    Abstract base class for analytics components.
    
    Defines interface for updating with new data.
    """
    
    def __init__(self, parent: ttk.Frame, title: str, row: int, col: int):
        self.parent = parent
        self.frame = ttk.LabelFrame(parent, text=title)
        self.frame.grid(row=row, column=col, sticky='nsew', padx=5, pady=5)
        self.setup()
        
    @abstractmethod
    def parse(self, records: List[Dict]) -> Any:
        """Extract the data needed for this component from the raw records."""
    
    @abstractmethod
    def setup(self) -> None:
        """Create the initial UI elements for this component."""
        
    @abstractmethod
    def update(self, data: Any) -> None:
        """Update the component with the parsed data."""
        
        

def load_ml_json(path: str) -> List[Dict]:
    with open(path, "r") as f:
        return json.load(f)["data"]




class PieChartComponent(AnalyticsComponent):
    """Pie chart motion class distribution"""
    
    def __init__(self, parent: ttk.Frame, row: int, col: int):
        self.fig: Optional[Figure] = None
        self.ax = None
        self.canvas: Optional[FigureCanvasTkAgg]
        super().__init__(parent, "Motion Distribution", row, col)
        
    def parse(self, records: List[Dict]) -> Dict[str, float]:
        counts = Counter()
        
        for r in records:
            # Pick the single most likely state (normal or anomalous variant).
            dominant_idx = max(range(8), key=lambda i: r["state_confidence"][i])
            # Collapse the 8-state model into the 4 motion classes for display.
            motion, _ = STATE_INDEX[dominant_idx]
            counts[motion] += 1
            
        # Guard against division by zero when no records are available.
        total = max(sum(counts.values()), 1)
        return {k: round((v / total) * 100, 1) for k, v in counts.items()}
    
    def setup(self) -> None:
        # Embed a Matplotlib figure inside the Tkinter frame once at setup time.
        self.fig = Figure(figsize=CHART_FIGSIZE, dpi=CHART_DPI)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def update(self, records: List[Dict]) -> None:
        distribution = self.parse(records)
        if not self.ax:
            return
        
        # Clear and fully redraw the pie chart on each refresh.
        self.ax.clear()
        labels = list(distribution.keys())
        sizes = list(distribution.values())
        colors = [MOTION_COLORS.get(label, "#808080") for label in labels]
        
        self.ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
        )
        # Keep the plot circular instead of stretching with the frame size.
        self.ax.axis("equal")
        self.fig.tight_layout()
        self.canvas.draw()
        
        
class LineChartComponent(AnalyticsComponent):
    """Line chart for anomaly rate trend"""
    
    def __init__(self, parent: ttk.Frame, row: int, col: int):
        self.fig: Optional[Figure] = None
        self.ax = None
        self.canvas: Optional[FigureCanvasTkAgg]
        super().__init__(parent, "Anomaly Rate Trend (24h)", row, col)
        
    def parse(self, records: List[Dict]) -> List[Tuple[datetime, float]]:
        bucket_minutes = 3
        buckets = defaultdict(list)
        
        for r in records:
            # Normalize timestamps into fixed-size buckets for a smoother trend line.
            ts = datetime.fromisoformat(r["timestamp"].replace("Z", ""))
            bucket = ts.replace(
                minute=(ts.minute // bucket_minutes) * bucket_minutes,
                second=0,
                microsecond=0
            )
            # Treat the anomalous-state confidence mass as the anomaly score.
            anomaly_score = sum(r["state_confidence"][4:])
            buckets[bucket].append(anomaly_score)
        
        # Average anomaly score per bucket and return points in time order.
        return sorted(
            [(t, round(sum(v) / len(v), 3)) for t, v in buckets.items()],
            key=lambda x: x[0]
        )
        
    def setup(self) -> None:
        # Embed a Matplotlib figure inside the Tkinter frame once at setup time.
        self.fig = Figure(figsize=CHART_FIGSIZE, dpi=CHART_DPI)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def update(self, records: List[Dict]) -> None:
        trend_data = self.parse(records)
        if not self.ax:
            return
        
        # Clear and fully redraw the chart on each refresh.
        self.ax.clear()
        times = [t[0] for t in trend_data]
        rates = [t[1] for t in trend_data]
        
        self.ax.plot(times, rates, "b-", linewidth=2, marker="o", markersize=4)
        if times and rates:
            # Shade under the curve to make trend magnitude easier to read.
            self.ax.fill_between(times, rates, alpha=0.3)
            
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Anomaly Rate")
        # Rotate/align datetime tick labels so they fit in the embedded canvas.
        self.fig.autofmt_xdate()
        self.ax.grid(True, linestyle="--", alpha=0.7)
        self.fig.tight_layout()
        self.canvas.draw()



class BarChartComponent(AnalyticsComponent):
    """Bar chart for top anomalous nodes"""
    
    def __init__(self, parent: ttk.Frame, row: int, col: int):
        self.fig: Optional[Figure] = None
        self.ax = None
        self.canvas: Optional[FigureCanvasTkAgg]
        super().__init__(parent, "Top Anomalous Nodes", row, col)
    
    def parse(self, records: List[Dict]) -> List[Tuple[str, int]]:
        threshold = 0.5
        node_counts = Counter()
        
        for r in records:
            # Sum anomalous-state confidence to score how anomalous this record is.
            anomaly_score = sum(r["state_confidence"][4:])
            if anomaly_score >= threshold:
                # Count only records that cross the anomaly threshold.
                node_counts[r["node_id"]] += 1
        
        # Keep only the highest-frequency anomalous nodes for a compact chart.
        return node_counts.most_common(5)
    
    def setup(self) -> None:
        # Embed a Matplotlib figure inside the Tkinter frame once at setup time.
        self.fig = Figure(figsize=CHART_FIGSIZE, dpi=CHART_DPI)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def update(self, records: List[Dict]) -> None:
        node_data = self.parse(records)
        if not self.ax:
            return
        
        # Clear and fully redraw the bar chart on each refresh.
        self.ax.clear()
        nodes = [d[0] for d in node_data]
        counts = [d[1] for d in node_data]
        
        bars = self.ax.barh(nodes, counts, color="#e74c3c")
        for bar, count in zip(bars, counts):
            # Label each bar with its exact count for quick scanning.
            self.ax.text(
                bar.get_width() + 0.3,
                bar.get_y() + bar.get_height() / 2,
                str(count),
                va="center"
            )
        
        self.ax.set_xlabel("Anomaly Count")
        # Show the highest-count node at the top of the chart.
        self.ax.invert_yaxis()
        self.fig.tight_layout()
        self.canvas.draw()

def parse_motion_distribution(records):
    counts = Counter()

    for r in records:
        dominant_idx = max(range(8), key=lambda i: r["state_confidence"][i])
        motion, _ = STATE_INDEX[dominant_idx]
        counts[motion] += 1

    total = sum(counts.values())
    return {
        k: round((v / total) * 100, 1)
        for k, v in counts.items()
    }
    
    
def parse_anomaly_trend(records, bucket_minutes=3):
    buckets = defaultdict(list)

    for r in records:
        ts = datetime.fromisoformat(r["timestamp"].replace("Z", ""))
        bucket = ts.replace(
            minute=(ts.minute // bucket_minutes) * bucket_minutes,
            second=0,
            microsecond=0
        )

        anomaly_score = sum(r["state_confidence"][4:])
        buckets[bucket].append(anomaly_score)

    return sorted(
        [(t, round(sum(v) / len(v), 3)) for t, v in buckets.items()],
        key=lambda x: x[0]
    )


def parse_top_anomalous_nodes(records, threshold=0.5, top_n=5):
    node_counts = Counter()

    for r in records:
        anomaly_score = sum(r["state_confidence"][4:])
        if anomaly_score >= threshold:
            node_counts[r["node_id"]] += 1

    return node_counts.most_common(top_n)


def parse_stats(records):
    nodes = {r["node_id"] for r in records}

    total_anomalies = sum(
        1 for r in records if sum(r["state_confidence"][4:]) >= 0.5
    )

    uptime_hours = (
        len(records) / len(nodes) * 10 / 3600
        if nodes else 0
    )

    return {
        "total_inferences": len(records),
        "total_anomalies": total_anomalies,
        "avg_processing_time_ms": 42.3,
        "active_nodes": len(nodes),
        "uptime_hours": round(uptime_hours, 1),
    }



class AnalyticsTab(ttk.Frame):
    """
    Analytics tab with charts and statistics.
    
    Displays multiple visualizations of system performance
    and anomaly patterns.
    """
    
    def __init__(self, parent: ttk.Notebook, dashboard: 'DashboardApp'):
        """
        Initialize the Analytics tab.
        
        Args:
            parent: Parent notebook widget
            dashboard: Reference to main dashboard for callbacks
        """
        super().__init__(parent)
        
        self.dashboard = dashboard
        
        # Chart figures and canvases
        self.pie_fig: Optional[Figure] = None
        self.pie_ax = None
        self.pie_canvas: Optional[FigureCanvasTkAgg] = None
        
        self.line_fig: Optional[Figure] = None
        self.line_ax = None
        self.line_canvas: Optional[FigureCanvasTkAgg] = None
        
        self.bar_fig: Optional[Figure] = None
        self.bar_ax = None
        self.bar_canvas: Optional[FigureCanvasTkAgg] = None
        
        # Stats labels
        self.stats_labels: Dict[str, ttk.Label] = {}
        
        # Build UI
        self._setup_ui()
    
    def _setup_ui(self):
        """
        Create the tab layout.
        
        Layout:
        ┌─────────────────┬─────────────────┐
        │   Pie Chart     │   Line Chart    │
        │  (motion dist)  │ (anomaly trend) │
        ├─────────────────┼─────────────────┤
        │   Bar Chart     │  Stats Panel    │
        │ (top anomalous) │  (numbers)      │
        └─────────────────┴─────────────────┘
        """
        # Configure 2x2 grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # TODO: Create all four quadrants
        self._setup_pie_chart()
        self._setup_line_chart()
        self._setup_bar_chart()
        self._setup_stats_panel()
        
        # TEMPORARY: Placeholder
        # ttk.Label(self, text="Analytics Tab - TODO: Implement charts").pack(pady=20)
    
    def _setup_pie_chart(self):
        """
        Create the motion class distribution pie chart.
        
        Shows percentage of time spent in each motion class.
        Colors match MOTION_COLORS scheme.
        """
        # TODO: Implement
        #
        # Create frame for chart
        frame = ttk.LabelFrame(self, text="Motion Distribution")
        frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Create matplotlib figure
        self.pie_fig = Figure(figsize=CHART_FIGSIZE, dpi=CHART_DPI)
        self.pie_ax = self.pie_fig.add_subplot(111)
        
        # Create canvas
        self.pie_canvas = FigureCanvasTkAgg(self.pie_fig, master=frame)
        self.pie_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Initial draw
        # self.update_pie_chart(MOCK_MOTION_DISTRIBUTION)
        #pass
    
    def _setup_line_chart(self):
        """
        Create the anomaly rate trend line chart.
        
        Shows anomaly rate over time (last 24 hours).
        """
        # TODO: Implement
        #
        frame = ttk.LabelFrame(self, text="Anomaly Rate Trend (24h)")
        frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        self.line_fig = Figure(figsize=CHART_FIGSIZE, dpi=CHART_DPI)
        self.line_ax = self.line_fig.add_subplot(111)
        
        self.line_canvas = FigureCanvasTkAgg(self.line_fig, master=frame)
        self.line_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # self.update_line_chart(MOCK_ANOMALY_TREND)
        # pass
    
    def _setup_bar_chart(self):
        """
        Create the top anomalous nodes bar chart.
        
        Shows nodes with most anomalies detected.
        """
        # TODO: Implement
        #
        frame = ttk.LabelFrame(self, text="Top Anomalous Nodes")
        frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        self.bar_fig = Figure(figsize=CHART_FIGSIZE, dpi=CHART_DPI)
        self.bar_ax = self.bar_fig.add_subplot(111)
        
        self.bar_canvas = FigureCanvasTkAgg(self.bar_fig, master=frame)
        self.bar_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # self.update_bar_chart(MOCK_TOP_ANOMALOUS_NODES)
        # pass
    
    def _setup_stats_panel(self):
        """
        Create the statistics panel.
        
        Shows key metrics:
        - Total inferences processed
        - Total anomalies detected
        - Average processing time
        - Active nodes
        - System uptime
        """
        # TODO: Implement
        #
        frame = ttk.LabelFrame(self, text="Statistics")
        frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        
        # Create stat rows
        stats_config = [
            ('total_inferences', 'Total Inferences:'),
            ('total_anomalies', 'Total Anomalies:'),
            ('avg_processing_time_ms', 'Avg Processing Time:'),
            ('active_nodes', 'Active Nodes:'),
            ('uptime_hours', 'Uptime:'),
        ]
        
        for i, (key, label_text) in enumerate(stats_config):
            ttk.Label(frame, text=label_text, font=('Arial', 11)).grid(
                row=i, column=0, sticky='w', padx=10, pady=8
            )
            value_label = ttk.Label(frame, text='--', font=('Arial', 11, 'bold'))
            value_label.grid(row=i, column=1, sticky='e', padx=10, pady=8)
            self.stats_labels[key] = value_label
        
        # Configure column weights
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        
        # Initial update
        # self.update_stats_panel(MOCK_STATS)
        # pass
    
    def update_pie_chart(self, distribution: Dict[str, int]):
        """
        Update the pie chart with new data.
        
        Args:
            distribution: Dict mapping motion class to count
        """
        # TODO: Implement
        #
        if not self.pie_ax:
            return
        
        self.pie_ax.clear()
        
        # Prepare data
        labels = list(distribution.keys())
        sizes = list(distribution.values())
        colors = [MOTION_COLORS.get(label, '#808080') for label in labels]
        
        # Create pie chart
        self.pie_ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                        startangle=90)
        self.pie_ax.axis('equal')  # Equal aspect ratio ensures circular pie
        
        # Redraw canvas
        self.pie_fig.tight_layout()
        self.pie_canvas.draw()
        # pass
    
    def update_line_chart(self, trend_data: List[Tuple[datetime, float]]):
        """
        Update the line chart with new data.
        
        Args:
            trend_data: List of (timestamp, anomaly_rate) tuples
        """
        # TODO: Implement
        #
        if not self.line_ax:
            return
        
        self.line_ax.clear()
        
        # Prepare data
        times = [t[0] for t in trend_data]
        rates = [t[1] for t in trend_data]
        
        # Create line plot
        self.line_ax.plot(times, rates, 'b-', linewidth=2, marker='o', markersize=4)
        self.line_ax.fill_between(times, rates, alpha=0.3)
        
        # Format x-axis
        self.line_ax.set_xlabel('Time')
        self.line_ax.set_ylabel('Anomaly Rate')
        self.line_fig.autofmt_xdate()  # Rotate date labels
        
        # Add grid
        self.line_ax.grid(True, linestyle='--', alpha=0.7)
        
        # Redraw
        self.line_fig.tight_layout()
        self.line_canvas.draw()
        # pass
    
    def update_bar_chart(self, node_data: List[Tuple[str, int]]):
        """
        Update the bar chart with new data.
        
        Args:
            node_data: List of (node_id, anomaly_count) tuples, sorted descending
        """
        # TODO: Implement
        #
        if not self.bar_ax:
            return
        
        self.bar_ax.clear()
        
        # Prepare data
        nodes = [d[0] for d in node_data]
        counts = [d[1] for d in node_data]
        
        # Create horizontal bar chart
        bars = self.bar_ax.barh(nodes, counts, color='#e74c3c')
        
        # Add value labels
        for bar, count in zip(bars, counts):
            self.bar_ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                             str(count), va='center')
        
        # Labels
        self.bar_ax.set_xlabel('Anomaly Count')
        self.bar_ax.invert_yaxis()  # Top node at top
        
        # Redraw
        self.bar_fig.tight_layout()
        self.bar_canvas.draw()
        # pass
    
    def update_stats_panel(self, stats: Dict[str, Any]):
        """
        Update the statistics panel with new values.
        
        Args:
            stats: Dict with stat keys and values
        """
        # TODO: Implement
        #
        formatters = {
            'total_inferences': lambda v: f"{v:,}",
            'total_anomalies': lambda v: f"{v:,}",
            'avg_processing_time_ms': lambda v: f"{v:.1f} ms",
            'active_nodes': lambda v: str(v),
            'uptime_hours': lambda v: f"{v:.1f} hours",
        }
        
        for key, label in self.stats_labels.items():
            if key in stats:
                formatter = formatters.get(key, str)
                label.config(text=formatter(stats[key]))
        # pass
    
    def refresh(self):
        """
        Refresh all charts with latest data from ML JSON.
        """
        try:
            records = load_ml_json("../sample_data/sample_anomaly_data.json")

            motion_dist = parse_motion_distribution(records)
            trend = parse_anomaly_trend(records)
            top_nodes = parse_top_anomalous_nodes(records)
            stats = parse_stats(records)

            self.update_pie_chart(motion_dist)
            self.update_line_chart(trend)
            self.update_bar_chart(top_nodes)
            self.update_stats_panel(stats)

        except Exception as e:
            print(f"Error refreshing analytics tab: {e}")



# =============================================================================
# DEMO / TEST
# =============================================================================

def demo():
    """Demonstrate the AnalyticsTab independently."""
    root = tk.Tk()
    root.title("Analytics Tab Demo")
    root.geometry("900x700")
    
    # Create a mock dashboard
    class MockDashboard:
        pass
    
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)
    
    tab = AnalyticsTab(notebook, dashboard=MockDashboard())
    notebook.add(tab, text='Analytics')
    
    tab.refresh()
    
    root.mainloop()


if __name__ == '__main__':
    demo()
