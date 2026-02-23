Team 4: Visualization Dashboard

Goal: Display real-time network status, annomalies, and analytics.

To Build:
Tabs
Netowork - Visual map showing all nodes; color-coded by motion state (IDLE=gray, TERRESTRIAL=blue, MARITIME=green, LIFT=red); anomalies highlighted
Anomalies - Live feed of detected anomalies with timestamp, node, severity, status; filter by node/severity/time
Analytics - Motion class pie chart, anomaly rate trend line, top anomalous nodes bar chart, processing statistics
Node Detials - Drill-down view: select node, see motion history table, anomaly score trend, feature heatmap

Redis Channel
Channel: dashboard:updates:*
Publisher: Database
Subscriber: UI

Channel: dashboard:anomalies:*
Publisher: Database
Subscriber: UI