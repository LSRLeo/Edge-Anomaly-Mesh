# Issue Report: W26-Sprint 2

**Repository:** edge-anomaly-mesh
**Report Generated:** 2026-03-03 14:38:58
**Target per Person:** 10 issues
**Total Issues:** 139

---

## Summary

| Team | Open | Closed | Total |
|------|------|--------|-------|
| ML TEAM | 5 | 35 | 40 |
| DB TEAM | 0 | 28 | 28 |
| DE TEAM | 3 | 35 | 38 |
| UI TEAM | 3 | 30 | 33 |
| (No Team Label) | 0 | 0 | 0 |
| **Total** | **11** | **128** | **139** |

---

## ML TEAM (40/40)

### Alyssa Bulai (10)

- ~~[#54](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/54): Add functionality to load and process data from all motion types~~
- ~~[#55](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/55): Predict terrain type~~
- ~~[#56](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/56): Confidence score of terrain type prediction~~
- ~~[#58](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/58): Initialize neural network with PyTorch~~
- ~~[#208](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/208): Fix output of model~~
- ~~[#232](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/232): Implement functionality to save a PyTorch model~~
- ~~[#233](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/233): Update README~~
- ~~[#234](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/234): Fix training data being input to the model~~
- ~~[#255](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/255): Add data validation / filtering~~
- ~~[#256](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/256): Validate label distribution before training~~

### Daniel Kaplan (10)

- ~~[#235](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/235): Implement Redis Subscriber for Live Data Ingestion~~
- ~~[#236](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/236): Develop Node Specific Hash Map for Buffer Management~~
- ~~[#237](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/237): Integrate Real Time Sliding Window Queue~~
- ~~[#238](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/238): Apply Stride and Overlap Logic to Stream Handler~~
- ~~[#239](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/239): Refactor Data Pipeline for NumPy Conversion Reusability~~
- ~~[#240](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/240): Implement Handling for Out-of-Order Packets~~
- ~~[#241](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/241): Preserve Ground Truth and Metadata in Stream Context~~
- ~~[#242](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/242): Create Node Cleanup Routine for Memory Management~~
- ~~[#273](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/273): Implement Latency Monitoring~~
- ~~[#274](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/274): Duplicate Packet Filtering~~

### Tristian Bradley (10)

- [#266](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/266): State-Persistence Hash Map for Asset Tracking
- [#269](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/269): Logic & State Smoothing
- [#270](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/270): Implement Metadata Mapping & TS-Preservation for Database
- [#271](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/271): Implement Redis TTL and Asset Eviction Policy
- ~~[#259](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/259): Output Formatting & Standardization~~
- ~~[#262](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/262): Data Persistence & Logging~~
- ~~[#265](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/265): Implement Redis Publisher for Inference Distribution~~
- ~~[#307](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/307): Define the standard JSON schema~~
- ~~[#311](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/311): Real-time Result Publishing~~
- ~~[#312](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/312): Implement Pydantic Schema Validation for Output Integrity~~

### Truman Davis (9)

- [#304](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/304): Fix accuracies upon model training
- ~~[#297](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/297): Fix bug where 8 classifications have same label~~
- ~~[#314](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/314): Fix hard-coded Hidden Layers~~
- ~~[#316](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/316): Create Normalization scale/stats~~
- ~~[#317](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/317): Use normalization stats to normalize confusion matrix data~~
- ~~[#318](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/318): Fix hardcoded data destination~~
- ~~[#323](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/323): Fix requirements.txt for ML Team~~
- ~~[#333](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/333): Create safety check for empty json files~~
- ~~[#334](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/334): Change verbose default value~~

### Unassigned (1)

- ~~[#309](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/309): Clear session in model to prevent overwrites/edits~~


---

## DB TEAM (28/30)

### Diego Ramirez (10 individual, 1 shared)

- ~~[#158](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/158): Merge DB Creation Files into one deliverable (schema.py)~~
- ~~[#211](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/211): Ensure sessions are commited properly in ML tables~~
- ~~[#219](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/219): Merge Table Managers into a singular Manager Class~~
- ~~[#244](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/244): Update raw data table to DE team output format~~
- ~~[#252](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/252): Create all the Tables in a singular file that can be run~~
- ~~[#254](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/254): Make sure the database is accessible to the REDIS listeners~~
- ~~[#258](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/258): Merge the DB managers into a class (possibly a new file)~~
- ~~[#260](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/260): Make sure the implemented functions of each manager class can be run.~~
- ~~[#261](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/261): Create subclasses of Manager (if needed)~~
- ~~[#264](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/264): Create README for interaction with data~~
- ~~[#342](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/342): Update README DB~~

### Hannah Caldini (11 individual, 1 shared)

- ~~[#231](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/231): DB Message Manager~~
- ~~[#322](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/322): Base Message Class~~
- ~~[#324](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/324): MessageResponse Class~~
- ~~[#325](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/325): MessageRequest Class~~
- ~~[#326](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/326): MessageRequest Subclasses~~
- ~~[#327](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/327): MessageData Class~~
- ~~[#328](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/328): Message Factory~~
- ~~[#329](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/329): Test Usage~~
- ~~[#330](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/330): udpate DBMessageManager~~
- ~~[#331](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/331): ErrorResponse~~
- ~~[#342](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/342): Update README DB~~
- ~~[#390](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/390): MessageData Subclasses~~

### Kailar Hayes (6 individual, 1 shared)

- ~~[#277](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/277): Create a thread-safe query class.~~
- ~~[#279](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/279): Add queries to the class~~
- ~~[#293](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/293): Update gitignore with DB team specifics~~
- ~~[#303](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/303): Update ML tables format with ML team output format~~
- ~~[#342](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/342): Update README DB~~
- ~~[#392](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/392): Return all node id's~~
- ~~[#410](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/410): Test queries~~


---

## DE TEAM (38/30)

### Aldo Rios (8 individual, 4 shared)

- [#9](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/9): DE - Multiple Nodes Compatability
- ~~[#7](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/7): DE - Raw Data Distributor~~
- ~~[#10](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/10): DE - Labels for Mode and Anomalies~~
- ~~[#20](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/20): Anomaly Label~~
- ~~[#25](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/25): Redis Channels~~
- ~~[#26](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/26): Redis~~
- ~~[#220](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/220): Batching messages to channels~~
- ~~[#384](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/384): Arg Parse For Training data vs Real Data~~
- ~~[#385](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/385): Arg Parse for redis output vs file output~~
- ~~[#386](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/386): arg parse redis to choose what channel to subscribe to and add maybe some config for that channel publishing~~
- ~~[#406](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/406): Update README~~
- ~~[#426](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/426): Update raw_data and update what data is passed in it~~

### Leo Liu (14 individual, 4 shared)

- [#9](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/9): DE - Multiple Nodes Compatability
- [#424](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/424): Add anomaly_type to Label
- [#425](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/425): Add Location to Label
- ~~[#7](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/7): DE - Raw Data Distributor~~
- ~~[#10](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/10): DE - Labels for Mode and Anomalies~~
- ~~[#20](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/20): Anomaly Label~~
- ~~[#222](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/222): Waypoint~~
- ~~[#223](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/223): Build Waypoint Abstract/Interface Class~~
- ~~[#224](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/224): Refine Route Definitions and Node class~~
- ~~[#225](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/225): Refractor Hub~~
- ~~[#227](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/227): Package stuck in Traffic~~
- ~~[#373](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/373): Create Waypoint class~~
- ~~[#375](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/375): Refractor Route to generate waypoints between hubs~~
- ~~[#377](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/377): Refractor Node class~~
- ~~[#413](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/413): time_at_hub needed for every Motion ?~~
- ~~[#422](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/422): ADD Motion Type in Label ~~
- ~~[#423](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/423): Add is_Anamoly to Label~~
- ~~[#442](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/442): Hub Idle time data generation~~

### Sean Osman (11 individual, 4 shared)

- [#9](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/9): DE - Multiple Nodes Compatability
- ~~[#7](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/7): DE - Raw Data Distributor~~
- ~~[#8](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/8): DE - Anomalies~~
- ~~[#10](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/10): DE - Labels for Mode and Anomalies~~
- ~~[#20](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/20): Anomaly Label~~
- ~~[#209](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/209): LIFT - Crane stops working, acceleration no longer happens~~
- ~~[#210](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/210): MARITIME - Ship sinks, package falls into ocean~~
- ~~[#212](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/212): TERRESTRIAL - Car/Truck crashes, package is left stagnant~~
- ~~[#214](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/214): TERRESTRIAL - Car/Truck caught in traffic, package moves very slow/stops~~
- ~~[#215](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/215): IDLE - Package stolen~~
- ~~[#216](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/216): MARITIME - Rocky Seas~~
- ~~[#218](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/218): Create "inject_anomalies" method in each mode class~~
- ~~[#230](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/230): Function for the probability of anomalies appearance~~
- ~~[#302](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/302): refractor LIFT~~
- ~~[#310](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/310): LIFT - Package falls from shelf in storage center~~

### Unassigned (1)

- ~~[#354](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/354): Refractor Generate Reading method method~~


---

## UI TEAM (33/30)

### George Rumsey (8 individual, 5 shared)

- [#306](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/306): Adjust aesthetics in ui.utils to conform to client requirements
- [#308](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/308): Ensure Live Data Support for Analytics Tab
- [#315](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/315): Increase Accessibility
- ~~[#251](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/251): Integrate Redis~~
- ~~[#263](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/263): Create OOP Structure for Analytics Tab~~
- ~~[#267](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/267): Create Base Class for AnalyticsComponent~~
- ~~[#272](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/272): Create Class for Pie Chart~~
- ~~[#275](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/275): Create Class for Line Chart~~
- ~~[#276](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/276): Create Class for Bar Chart~~
- ~~[#278](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/278): Create Class for Numerical Stats~~
- ~~[#287](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/287): Setup Main Dashboard~~
- ~~[#313](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/313): Implement File to Hold Parent classes~~
- ~~[#344](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/344): Create ReadMe~~

### Owen Conlon (11 individual, 7 shared)

- [#306](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/306): Adjust aesthetics in ui.utils to conform to client requirements
- [#315](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/315): Increase Accessibility
- ~~[#36](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/36): Issue: Integrate Network Tab with Database to Load Node Data~~
- ~~[#202](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/202): Change visuals~~
- ~~[#217](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/217): Dynamic Sizing Windows~~
- ~~[#243](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/243): Implement Background Map~~
- ~~[#245](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/245): Implement scaling for the map~~
- ~~[#248](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/248): Transition node selection details to Node detials tab~~
- ~~[#251](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/251): Integrate Redis~~
- ~~[#268](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/268): Fix item_id management~~
- ~~[#281](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/281): Fix multiple nodes being drawn~~
- ~~[#284](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/284): Clean up code~~
- ~~[#291](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/291): OOP Conversions~~
- ~~[#292](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/292): Update json reading~~
- ~~[#296](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/296): Anomaly inverting bug~~
- ~~[#313](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/313): Implement File to Hold Parent classes~~
- ~~[#344](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/344): Create ReadMe~~
- ~~[#345](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/345): Implement RedisReader class~~

### Ty Esmond (7 individual, 7 shared)

- [#306](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/306): Adjust aesthetics in ui.utils to conform to client requirements
- [#315](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/315): Increase Accessibility
- ~~[#213](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/213): Link node viewer to network and anomalies tab~~
- ~~[#246](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/246): Implement REDIS into Anomalies viewer tab~~
- ~~[#248](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/248): Transition node selection details to Node detials tab~~
- ~~[#249](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/249): Implement REDIS into Node_Viewer tab~~
- ~~[#250](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/250): Implement UI skeleton for REDIS message monitoring tab~~
- ~~[#251](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/251): Integrate Redis~~
- ~~[#294](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/294): Refactor Anomalies tab to integrate Node class etc.~~
- ~~[#295](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/295): Finalize Node Class in Node_viewer and refactor~~
- ~~[#313](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/313): Implement File to Hold Parent classes~~
- ~~[#344](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/344): Create ReadMe~~
- ~~[#345](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/345): Implement RedisReader class~~
- ~~[#434](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/434): review pathways and resolve slight merge issues~~

