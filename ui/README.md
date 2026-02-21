Team 4: Visualization Dashboard

Goal: Display real-time network status, annomalies, and analytics.

To Build:
Tabs
Netowork - Visual map showing all nodes; color-coded by motion state (IDLE=gray, TERRESTRIAL=blue, MARITIME=green, LIFT=red); anomalies highlighted
Anomalies - Live feed of detected anomalies with timestamp, node, severity, status; filter by node/severity/time
Analytics - Motion class pie chart, anomaly rate trend line, top anomalous nodes bar chart, processing statistics
Node Detials - Drill-down view: select node, see motion history table, anomaly score trend, feature heatmap


## Sprint 1:
    network_tab.py
        json/node parsing
        implemented node drawing on a blank canvas
        anomaly toggling with right click
        node highlighting (blue outline when left clicked) and displaying details in a popout window
        legend integration
        different node outline for anomalous and non anomalous

        to run starting from edge-anomaly-mesh folder
        source venv/bin/activate
        cd ui
        pip3 install -r requirements.txt
        cd widgets
        python3 network_tab.py

        (note that there is an issue that broke anomaly toggling but thats been fixed in sprint 2 already)
    anomalies_tab.py
        json/node parsing with example hardcoded nodes
        implemented a scrollable field that displays all active anamolous nodes.
        divided into a wrapper widget which contains the scrollable area, will be used to divide different sections in future sprints.
        Will allow for navigation directly to the node viewer tab to view a specific node

        to run starting from edge-anomaly-mesh folder
        source venv/bin/activate
        cd ui
        pip3 install -r requirements.txt
        cd widgets
        python3 anomalies_tab.py
    node_details_tab.py
        parses hardcoded node data
        displays relevant data associated with node
        can be opened in future sprints from home dashboard, network tab, or anomalies tab.
        will allow in future sprints to change anomaly status

        to run startig from edge-anomaly-mesh folder:
        source venv/bin/activate
        cd ui
        pip3 install -r requirements.txt
        cd widgets
        python3 node_details_tab.py
