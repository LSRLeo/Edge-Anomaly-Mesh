# Issue Report: W26-Sprint 2

**Repository:** edge-anomaly-mesh
**Report Generated:** 2026-02-24 14:00:15
**Target per Person:** 10 issues
**Total Issues:** 128

---

## Summary

| Team | Open | Closed | Total |
|------|------|--------|-------|
| ML TEAM | 33 | 7 | 40 |
| DB TEAM | 32 | 3 | 35 |
| DE TEAM | 17 | 2 | 19 |
| UI TEAM | 23 | 10 | 33 |
| (No Team Label) | 0 | 1 | 1 |
| **Total** | **105** | **23** | **128** |

---

## ML TEAM (40/40)

### Alyssa Bulai (10/10)

- #56: Confidence score of terrain type prediction
- #208: Fix output of model
- #232: Implement functionality to save a PyTorch model
- #234: Fix training data being input to the model
- #255: Add data validation / filtering
- #256: Validate label distribution before training
- ~~#54: Add functionality to load and process data from all motion types~~
- ~~#55: Predict terrain type~~
- ~~#58: Initialize neural network with PyTorch~~
- ~~#233: Update README~~

### Daniel Kaplan (10/10)

- #238: Apply Stride and Overlap Logic to Stream Handler
- #239: Refactor Data Pipeline for NumPy Conversion Reusability
- #240: Implement Handling for Out-of-Order Packets
- #241: Preserve Ground Truth and Metadata in Stream Context
- #242: Create Node Cleanup Routine for Memory Management
- #273: Implement Latency Monitoring
- #274: Duplicate Packet Filtering
- ~~#235: Implement Redis Subscriber for Live Data Ingestion~~
- ~~#236: Develop Node Specific Hash Map for Buffer Management~~
- ~~#237: Integrate Real Time Sliding Window Queue~~

### Tristian Bradley (10/10)

- #259: Output Formatting & Standardization
- #262: Data Persistence & Logging
- #265: Implement Redis Publisher for Inference Distribution
- #266: State-Persistence Hash Map for Asset Tracking
- #269: Logic & State Smoothing
- #270: Implement Metadata Mapping & TS-Preservation for Database
- #271: Implement Redis TTL and Asset Eviction Policy
- #307: Define the standard JSON schema
- #311: Real-time Result Publishing
- #312: Implement Pydantic Schema Validation for Output Integrity

### Truman Davis (9/10)

- #297: Fix bug where 8 classifications have same label
- #304: Fix accuracies upon model training
- #314: Fix hard-coded Hidden Layers
- #316: Create Normalization scale/stats
- #317: Use normalization stats to normalize confusion matrix data
- #318: Fix hardcoded data destination
- #323: Fix requirements.txt for ML Team
- #333: Create safety check for empty json files
- #334: Change verbose default value

### Unassigned (1)

- #309: Clear session in model to prevent overwrites/edits


---

## DB TEAM (35/30)

### Diego Ramirez (9/10)

- #158: Merge DB Creation Files into one deliverable (schema.py)
- #211: Ensure sessions are commited properly in ML tables
- #219: Merge Table Managers into a singular Manager Class
- #244: Update raw data table to DE team output format
- #254: Make sure the database is accessible to the REDIS listeners
- #258: Merge the DB managers into a class (possibly a new file)
- #260: Make sure the implemented functions of each manager class can be run.
- #261: Create subclasses of Manager (if needed)
- ~~#252: Create all the Tables in a singular file that can be run~~

### Hannah Caldini (14/10)

- #70: Scripts for receiving data
- #84: Add in functionality to read in JSON from REDIS
- #231: DB Message Manager
- #247: Insert REDIS JSON message to the database
- #290: Handle duplicate messages
- #325: MessageRequest Class
- #326: MessageRequest Subclasses
- #327: MessageData Class
- #328: Message Factory
- #329: Test Usage
- #330: udpate DBMessageManager
- #331: ErrorResponse
- ~~#322: Base Message Class~~
- ~~#324: MessageResponse Class~~

### Kailar Hayes (12/10)

- #62: Receive raw data from DG team
- #64: Return if node is anomalous or not
- #66: Return node data when requested
- #67: Return if node is delayed
- #68: Implement functions to return specific data
- #96: Create script that returns active nodes in JSON
- #264: Create README for interaction with data
- #277: Create a thread-safe query class.
- #279: Add queries to the class
- #282: Create an aggregations class for aggregated queries
- #293: Update gitignore with DB team specifics
- #303: Update ML tables format with ML team output format


---

## DE TEAM (19/30)

### Aldo Rios (8/10)

- #7: DE - Raw Data Distributor
- #8: DE - Anomalies
- #9: DE - Multiple Nodes Compatability
- #10: DE - Labels for Mode and Anomalies
- #20: Anomaly Label
- #25: Redis Channels
- #26: Redis
- #220: Batching messages to channels

### Leo Liu (14/10)

- #7: DE - Raw Data Distributor
- #8: DE - Anomalies
- #9: DE - Multiple Nodes Compatability
- #10: DE - Labels for Mode and Anomalies
- #20: Anomaly Label
- #182: Abstract Class for All Transportation Class
- #222: Waypoint
- #224: Refine Route Definitions and Node class
- #226: Terrestrial Add-on
- #227: Package stuck in Traffic
- #228: Add Stops
- #229: Add vehicle going up/down a hill
- ~~#223: Build Waypoint Abstract/Interface Class~~
- ~~#225: Refractor Hub~~

### Sean Osman (7/10)

- #7: DE - Raw Data Distributor
- #8: DE - Anomalies
- #9: DE - Multiple Nodes Compatability
- #10: DE - Labels for Mode and Anomalies
- #20: Anomaly Label
- #230: Function for the probability of anomalies appearance
- #310: LIFT - Package falls from shelf in storage center


---

## UI TEAM (33/30)

### George Rumsey (13/10)

- #251: Integrate Redis
- #263: Create OOP Structure for Analytics Tab
- #267: Create Base Class for AnalyticsComponent
- #272: Create Class for Pie Chart
- #275: Create Class for Line Chart
- #276: Create Class for Bar Chart
- #278: Create Class for Numerical Stats
- #287: Setup Main Dashboard
- #306: Adjust aesthetics in ui.utils to conform to client requirements
- #308: Ensure Live Data Support for Analytics Tab
- #315: Increase Accessibility
- ~~#313: Implement File to Hold Parent classes~~
- ~~#344: Create ReadMe~~

### Owen Conlon (18/10)

- #36: Issue: Integrate Network Tab with Database to Load Node Data
- #217: Dynamic Sizing Windows
- #248: Transition node selection details to Node detials tab
- #251: Integrate Redis
- #291: OOP Conversions
- #292: Update json reading
- #306: Adjust aesthetics in ui.utils to conform to client requirements
- #315: Increase Accessibility
- ~~#202: Change visuals~~
- ~~#243: Implement Background Map~~
- ~~#245: Implement scaling for the map~~
- ~~#268: Fix item_id management~~
- ~~#281: Fix multiple nodes being drawn~~
- ~~#284: Clean up code~~
- ~~#296: Anomaly inverting bug~~
- ~~#313: Implement File to Hold Parent classes~~
- ~~#344: Create ReadMe~~
- ~~#345: Implement RedisReader class~~

### Ty Esmond (13/10)

- #213: Link node viewer to network and anomalies tab
- #246: Implement REDIS into Anomalies viewer tab
- #249: Implement REDIS into Node_Viewer tab
- #250: Implement UI skeleton for REDIS message monitoring tab
- #251: Integrate Redis
- #253: Link REDIS subscription channel to REDIS monitor tab
- #294: Refactor Anomalies tab to integrate Node class etc.
- #295: Finalize Node Class in Node_viewer and refactor
- #306: Adjust aesthetics in ui.utils to conform to client requirements
- #315: Increase Accessibility
- ~~#313: Implement File to Hold Parent classes~~
- ~~#344: Create ReadMe~~
- ~~#345: Implement RedisReader class~~


---

## Issues Without Team Label

### Unassigned (1)

- ~~#354: Refractor Generate Reading method method~~

