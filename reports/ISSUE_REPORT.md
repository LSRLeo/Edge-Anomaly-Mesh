# Issue Report: All Sprints

**Repository:** edge-anomaly-mesh
**Report Generated:** 2026-03-15 15:22:08
**Milestones:** W26-Sprint-1, W26-Sprint-2, W26-Sprint-3
**Target per Person:** 10 issues
**Total Issues:** 320

---

## Summary

| Team | Open | Closed | Total |
|------|------|--------|-------|
| ML TEAM | 2 | 88 | 90 |
| DB TEAM | 12 | 61 | 73 |
| DE TEAM | 1 | 80 | 81 |
| UI TEAM | 2 | 74 | 76 |
| (No Team Label) | 0 | 0 | 0 |
| **Total** | **17** | **303** | **320** |

---

## ML TEAM (90/40)

### Alyssa Bulai (27 individual, 1 shared)

- ~~[#45](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/45): Separate the train_classifier.py file into two separate files~~
- ~~[#53](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/53): Implement PyTorch Dataset - MotionDataset Class~~
- ~~[#54](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/54): Add functionality to load and process data from all motion types~~
- ~~[#55](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/55): Predict terrain type~~
- ~~[#56](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/56): Confidence score of terrain type prediction~~
- ~~[#57](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/57): Implement confusion matrix for model training purposes~~
- ~~[#58](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/58): Initialize neural network with PyTorch~~
- ~~[#59](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/59): Implement functionality to train neural network~~
- ~~[#60](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/60): Implement functionality to test neural network~~
- ~~[#193](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/193): Normalize features~~
- ~~[#208](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/208): Fix output of model~~
- ~~[#232](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/232): Implement functionality to save a PyTorch model~~
- ~~[#233](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/233): Update README~~
- ~~[#234](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/234): Fix training data being input to the model~~
- ~~[#255](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/255): Add data validation / filtering~~
- ~~[#256](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/256): Validate label distribution before training~~
- ~~[#257](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/257): Add class-weighted loss~~
- ~~[#477](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/477): Increase anomaly_rate in generate_data.py script~~
- ~~[#493](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/493): Change generate_data.py script to generate samples in the updated format~~
- ~~[#495](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/495): Update README with Sprint 2 changes~~
- ~~[#516](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/516): Delete old training data~~
- ~~[#517](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/517): Regenerate training data with new format~~
- ~~[#532](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/532): Fix motion_type label lookup in load_json_data to match training data format~~
- ~~[#533](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/533): Ensure DB team is receiving metadata with inference result~~
- ~~[#537](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/537): Edit generate_training_data.py file to generate more balanced data~~
- ~~[#566](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/566): Add missing idle_anom classification~~
- ~~[#568](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/568): Regenerate training data with idle_anom classifications~~
- ~~[#582](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/582): Fix double backslash in training_classifier.py folder~~

### Daniel Kaplan (28 individual, 2 shared)

- ~~[#46](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/46): Load Sensor Data from JSON~~
- ~~[#47](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/47): Segment Sensor Data into Sliding Windows~~
- ~~[#48](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/48): Save Extracted Features and Labels~~
- ~~[#49](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/49): Run Demo of Full Feature Extraction Pipeline~~
- ~~[#50](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/50): Configure Pipeline via Command Line Arguments~~
- ~~[#51](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/51): Move data manipulation functions to a separate module~~
- ~~[#97](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/97): Rename load_csv_data to load_json_data~~
- ~~[#165](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/165): Comment Clean Up~~
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
- ~~[#464](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/464): Validate Windowing Logic for Edge Case Sample Sizes~~
- ~~[#465](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/465): Implement Tie Breaking Logic for Majority Labeling~~
- ~~[#466](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/466): Verify Window Count Accuracy Against Overlap Parameter~~
- ~~[#467](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/467): Unit Test Event Sorting for Out-of-Order Sequence Buffers~~
- ~~[#468](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/468): Verify Duplicate Packet Filtering via Seen Sequences~~
- ~~[#469](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/469): Align Terrain Mapping between Pipeline and Streamer~~
- ~~[#470](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/470): Debug Fallback for Nested and Flat JSON Formats~~
- ~~[#471](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/471): Implement Integration Test for Streamer and Pipeline~~
- ~~[#472](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/472): Fix Inactivity Cleanup and Memory Purge Logic~~
- ~~[#473](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/473): Update README with Live Stream and Inference Usage~~
- ~~[#539](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/539): Verify redis for DE to instream~~
- ~~[#540](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/540): Connect the publishing between isntream and outstream~~

### Tristian Bradley (17 individual, 2 shared)

- ~~[#80](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/80): Create  get_feature_name function~~
- ~~[#83](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/83): Create _time_domain_features function~~
- ~~[#85](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/85): Create _frequency_domain_features function~~
- ~~[#87](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/87): Create _cross_axis_features function~~
- ~~[#89](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/89): Create extract_batch Function~~
- ~~[#91](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/91): Create extract function~~
- ~~[#166](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/166): Documentation and dead space in feature_extraction file~~
- ~~[#259](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/259): Output Formatting & Standardization~~
- ~~[#262](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/262): Data Persistence & Logging~~
- ~~[#265](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/265): Implement Redis Publisher for Inference Distribution~~
- ~~[#266](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/266): State-Persistence Hash Map for Asset Tracking~~
- ~~[#269](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/269): Logic & State Smoothing~~
- ~~[#270](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/270): Implement Metadata Mapping & TS-Preservation for Database~~
- ~~[#271](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/271): Implement Redis TTL and Asset Eviction Policy~~
- ~~[#307](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/307): Define the standard JSON schema~~
- ~~[#311](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/311): Real-time Result Publishing~~
- ~~[#312](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/312): Implement Pydantic Schema Validation for Output Integrity~~
- ~~[#539](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/539): Verify redis for DE to instream~~
- ~~[#540](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/540): Connect the publishing between isntream and outstream~~

### Truman Davis (15 individual, 1 shared)

- [#304](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/304): Fix accuracies upon model training
- [#305](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/305): Find optimal batch sizes/epochs
- ~~[#53](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/53): Implement PyTorch Dataset - MotionDataset Class~~
- ~~[#78](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/78): Implement class MotionDataset~~
- ~~[#151](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/151): Complete print_classification_report() function in model_training.py~~
- ~~[#297](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/297): Fix bug where 8 classifications have same label~~
- ~~[#309](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/309): Clear session in model to prevent overwrites/edits~~
- ~~[#314](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/314): Fix hard-coded Hidden Layers~~
- ~~[#316](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/316): Create Normalization scale/stats~~
- ~~[#317](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/317): Use normalization stats to normalize confusion matrix data~~
- ~~[#318](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/318): Fix hardcoded data destination~~
- ~~[#323](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/323): Fix requirements.txt for ML Team~~
- ~~[#333](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/333): Create safety check for empty json files~~
- ~~[#334](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/334): Change verbose default value~~
- ~~[#481](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/481): Sync data output with DB team~~
- ~~[#542](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/542): Fix missing idle_anom classification in data~~


---

## DB TEAM (73/30)

### Diego Ramirez (18 individual, 5 shared)

- [#288](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/288): Create a REDIS Listener class for handling transactions
- [#289](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/289): Create listeners on the DE and ML team channels
- [#383](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/383): Send overriden anomaly events to ML team for training
- [#570](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/570): add update node anomaly status
- [#595](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/595): Allow UI to acknowledge or override anomaly events
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
- ~~[#412](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/412): Add a check to update node status~~
- ~~[#474](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/474): Message Format~~
- ~~[#475](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/475): Channel Naming~~
- ~~[#512](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/512): Adjust tables for agreed raw data format~~
- ~~[#514](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/514): Update table manager to handle new data formats~~
- ~~[#525](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/525): Quick fix naming conventions~~
- ~~[#574](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/574): update message parsing for inference~~

### Hannah Caldini (32 individual, 7 shared)

- [#290](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/290): Handle duplicate messages
- [#570](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/570): add update node anomaly status
- [#604](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/604): test/sample usage
- ~~[#100](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/100): create nodes table~~
- ~~[#103](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/103): create main request manager~~
- ~~[#104](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/104): read in raw data~~
- ~~[#105](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/105): update or insert into node table~~
- ~~[#121](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/121): Add SQLalchemy functionality~~
- ~~[#135](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/135): get_node_status function~~
- ~~[#136](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/136): test node table ~~
- ~~[#146](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/146): Map each message type to its corresponding handler function~~
- ~~[#147](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/147): Validate Message~~
- ~~[#148](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/148): Process Messages and route them their handlers~~
- ~~[#149](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/149): Implement Handler stubs~~
- ~~[#161](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/161): update docstrings and tidy up~~
- ~~[#170](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/170): Columns in table creation~~
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
- ~~[#462](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/462): method to generate a unique m_id for each message response~~
- ~~[#463](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/463): update readme for sprint 2 changes~~
- ~~[#474](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/474): Message Format~~
- ~~[#475](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/475): Channel Naming~~
- ~~[#476](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/476): Update DB Redis listener~~
- ~~[#494](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/494): Update Names in File so it matches message definitions~~
- ~~[#518](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/518): update DB Messages to match new format~~
- ~~[#534](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/534): ML -> inference-output -> DB (inference results sent for storage) - Truman, Alyssa, Hannah~~
- ~~[#543](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/543): redis ml to db~~
- ~~[#574](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/574): update message parsing for inference~~
- ~~[#575](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/575): Fix logging info and message~~

### Kailar Hayes (16 individual, 5 shared)

- [#63](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/63): Return list of active nodes
- [#96](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/96): Create script that returns active nodes in JSON
- [#280](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/280): Make sure class is thread-safe for multiple accessses
- [#282](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/282): Create an aggregations class for aggregated queries
- [#482](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/482): Update READme with REDIS testing commands
- [#570](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/570): add update node anomaly status
- ~~[#82](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/82): Create raw data table~~
- ~~[#101](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/101): create raw data table~~
- ~~[#277](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/277): Create a thread-safe query class.~~
- ~~[#279](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/279): Add queries to the class~~
- ~~[#293](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/293): Update gitignore with DB team specifics~~
- ~~[#303](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/303): Update ML tables format with ML team output format~~
- ~~[#342](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/342): Update README DB~~
- ~~[#392](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/392): Return all node id's~~
- ~~[#410](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/410): Test queries~~
- ~~[#474](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/474): Message Format~~
- ~~[#475](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/475): Channel Naming~~
- ~~[#507](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/507): Clean up DB directory~~
- ~~[#529](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/529): Fixed inference queries~~
- ~~[#547](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/547): Fix error with "_m_type" when attempting to query through REDIS~~
- ~~[#574](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/574): update message parsing for inference~~


---

## DE TEAM (81/30)

### Aldo Rios (21 individual, 7 shared)

- [#9](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/9): DE - Multiple Nodes Compatability
- ~~[#7](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/7): DE - Raw Data Distributor~~
- ~~[#10](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/10): DE - Labels for Mode and Anomalies~~
- ~~[#11](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/11): DE - Node Simulation~~
- ~~[#16](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/16): Idle~~
- ~~[#17](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/17): Maritime~~
- ~~[#19](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/19): Transportation Label~~
- ~~[#20](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/20): Anomaly Label~~
- ~~[#22](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/22): CLI Runner~~
- ~~[#25](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/25): Redis Channels~~
- ~~[#26](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/26): Redis~~
- ~~[#28](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/28): Hub~~
- ~~[#115](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/115): Read node config from .json~~
- ~~[#123](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/123): Find the physics of the idle transport method~~
- ~~[#125](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/125): generate message reading~~
- ~~[#126](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/126): argument for node config~~
- ~~[#127](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/127): argument for route config file~~
- ~~[#128](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/128): Physics formula~~
- ~~[#130](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/130): Generate data based on physics~~
- ~~[#220](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/220): Batching messages to channels~~
- ~~[#371](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/371): Modifications~~
- ~~[#384](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/384): Arg Parse For Training data vs Real Data~~
- ~~[#385](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/385): Arg Parse for redis output vs file output~~
- ~~[#386](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/386): arg parse redis to choose what channel to subscribe to and add maybe some config for that channel publishing~~
- ~~[#406](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/406): Update README~~
- ~~[#426](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/426): Update raw_data and update what data is passed in it~~
- ~~[#485](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/485): Pass anomaly type to raw_data~~
- ~~[#559](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/559): Visualize script to visualize raw_data.json~~

### Leo Liu (31 individual, 6 shared)

- [#9](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/9): DE - Multiple Nodes Compatability
- ~~[#7](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/7): DE - Raw Data Distributor~~
- ~~[#10](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/10): DE - Labels for Mode and Anomalies~~
- ~~[#11](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/11): DE - Node Simulation~~
- ~~[#18](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/18): Terrestrial~~
- ~~[#20](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/20): Anomaly Label~~
- ~~[#27](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/27): Route~~
- ~~[#122](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/122): Add Example Route Configuration File (JSON Format)~~
- ~~[#124](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/124): Add Hub Generation Method~~
- ~~[#129](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/129): Physic Simulation~~
- ~~[#131](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/131): Generate reading method~~
- ~~[#154](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/154): Create Section Class~~
- ~~[#176](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/176): Add Acceleration in y and z~~
- ~~[#222](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/222): Waypoint~~
- ~~[#223](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/223): Build Waypoint Abstract/Interface Class~~
- ~~[#224](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/224): Refine Route Definitions and Node class~~
- ~~[#225](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/225): Refractor Hub~~
- ~~[#227](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/227): Package stuck in Traffic~~
- ~~[#354](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/354): Refractor Generate Reading method method~~
- ~~[#371](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/371): Modifications~~
- ~~[#373](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/373): Create Waypoint class~~
- ~~[#375](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/375): Refractor Route to generate waypoints between hubs~~
- ~~[#377](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/377): Refractor Node class~~
- ~~[#400](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/400): Generate Waypoints in Route~~
- ~~[#403](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/403): Labeling and Hub Variable addition~~
- ~~[#413](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/413): time_at_hub needed for every Motion ?~~
- ~~[#417](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/417): Add segment progress to output~~
- ~~[#422](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/422): ADD Motion Type in Label ~~
- ~~[#423](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/423): Add is_Anamoly to Label~~
- ~~[#424](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/424): Add anomaly_type to Label~~
- ~~[#431](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/431): Node class modification ~~
- ~~[#442](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/442): Hub Idle time data generation~~
- ~~[#443](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/443): Satellites~~
- ~~[#496](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/496): Message Format~~
- ~~[#576](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/576): Terrestrial Z_acc fix and Maritime fix~~
- ~~[#580](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/580): Fix GPS calculation Issues~~
- ~~[#581](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/581): Update location in message outputs~~

### Sean Osman (22 individual, 7 shared)

- [#9](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/9): DE - Multiple Nodes Compatability
- ~~[#7](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/7): DE - Raw Data Distributor~~
- ~~[#8](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/8): DE - Anomalies~~
- ~~[#10](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/10): DE - Labels for Mode and Anomalies~~
- ~~[#11](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/11): DE - Node Simulation~~
- ~~[#14](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/14): Noise~~
- ~~[#15](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/15): Lift~~
- ~~[#20](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/20): Anomaly Label~~
- ~~[#112](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/112): Add physics~~
- ~~[#114](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/114): Keep Package in Hub~~
- ~~[#116](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/116): Generate sensor reading~~
- ~~[#117](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/117): Set bounds for Idle~~
- ~~[#118](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/118): Set bounds for Lift~~
- ~~[#119](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/119): Set bounds for Terrestrial~~
- ~~[#120](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/120): Set bounds for Maritime~~
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
- ~~[#371](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/371): Modifications~~
- ~~[#451](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/451): Have to label anomalies and pass that info to raw_data~~
- ~~[#485](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/485): Pass anomaly type to raw_data~~
- ~~[#565](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/565): fix single node anomaly issue~~


---

## UI TEAM (76/30)

### George Rumsey (19 individual, 9 shared)

- [#308](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/308): Ensure Live Data Support for Analytics Tab
- [#487](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/487): Ensure redis functionality for analytics_tab
- ~~[#29](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/29): User Story Network Tab~~
- ~~[#71](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/71): Create Layout for Analytics Tab~~
- ~~[#72](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/72): Live States Pie Chart~~
- ~~[#73](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/73): Anomaly Rate Line Chart~~
- ~~[#75](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/75): Anomaly Bar Chart~~
- ~~[#76](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/76): Numerical Data Display~~
- ~~[#251](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/251): Integrate Redis~~
- ~~[#263](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/263): Create OOP Structure for Analytics Tab~~
- ~~[#267](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/267): Create Base Class for AnalyticsComponent~~
- ~~[#272](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/272): Create Class for Pie Chart~~
- ~~[#275](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/275): Create Class for Line Chart~~
- ~~[#276](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/276): Create Class for Bar Chart~~
- ~~[#278](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/278): Create Class for Numerical Stats~~
- ~~[#287](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/287): Setup Main Dashboard~~
- ~~[#306](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/306): Adjust aesthetics in ui.utils to conform to client requirements~~
- ~~[#313](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/313): Implement File to Hold Parent classes~~
- ~~[#315](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/315): Increase Accessibility~~
- ~~[#344](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/344): Create ReadMe~~
- ~~[#479](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/479): Ensure functional redis integration~~
- ~~[#489](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/489): Use from Redis to populate Analytics Tab~~
- ~~[#490](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/490): Switch from reading fully existing JSON file to reading data from Redis~~
- ~~[#491](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/491): Update the Pie Chart parse method to read from redis~~
- ~~[#492](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/492): Fix Issue with Analytics Tab OOP implementation~~
- ~~[#531](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/531): 4/5/26 debugging day~~
- ~~[#535](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/535): Add image scaling to Network Tab~~
- ~~[#578](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/578): Update Redis parsing to match new message style~~

### Owen Conlon (22 individual, 14 shared)

- ~~[#29](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/29): User Story Network Tab~~
- ~~[#33](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/33): Issue: Create Network Tab with Node Visualization Canvas~~
- ~~[#34](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/34): Issue: Implement Node Click Interaction and Details Navigation~~
- ~~[#35](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/35): Issue: Add Anomaly Highlighting to Network Visualization~~
- ~~[#36](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/36): Issue: Integrate Network Tab with Database to Load Node Data~~
- ~~[#132](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/132): Open GUI Frame with labels~~
- ~~[#133](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/133): I want a legend~~
- ~~[#134](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/134): Draw Nodes~~
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
- ~~[#306](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/306): Adjust aesthetics in ui.utils to conform to client requirements~~
- ~~[#313](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/313): Implement File to Hold Parent classes~~
- ~~[#315](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/315): Increase Accessibility~~
- ~~[#344](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/344): Create ReadMe~~
- ~~[#345](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/345): Implement RedisReader class~~
- ~~[#479](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/479): Ensure functional redis integration~~
- ~~[#484](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/484): Ensure Redis in Network_tab.py~~
- ~~[#488](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/488): Implement anomaly toggle~~
- ~~[#504](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/504): Create Toggle for test_mode vs redis_mode~~
- ~~[#521](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/521): Fix Linux window size~~
- ~~[#531](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/531): 4/5/26 debugging day~~
- ~~[#589](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/589): fix anomaly toggle message~~
- ~~[#592](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/592): fix redis_reader inf lock~~
- ~~[#593](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/593): fix_redis_lock~~
- ~~[#600](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/600): refactor update-node to fit new message requirements~~
- ~~[#606](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/606): typecasting for pyreverse diagram~~

### Ty Esmond (19 individual, 15 shared)

- ~~[#29](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/29): User Story Network Tab~~
- ~~[#39](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/39): Implement Node Info foundation tab and link to home page~~
- ~~[#40](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/40): Implement the Anomalies tab foundation and link to home page~~
- ~~[#41](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/41): Create the UI Shell for the Anomalies Viewer~~
- ~~[#42](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/42): Implement data population in the Anomalies viewer~~
- ~~[#43](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/43): Implement UI Shell for Node Info Tab~~
- ~~[#44](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/44): Link Node Info Display Boxes to readable file (DB in the future)~~
- ~~[#213](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/213): Link node viewer to network and anomalies tab~~
- ~~[#246](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/246): Implement REDIS into Anomalies viewer tab~~
- ~~[#248](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/248): Transition node selection details to Node detials tab~~
- ~~[#249](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/249): Implement REDIS into Node_Viewer tab~~
- ~~[#250](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/250): Implement UI skeleton for REDIS message monitoring tab~~
- ~~[#251](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/251): Integrate Redis~~
- ~~[#253](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/253): Link REDIS subscription channel to REDIS monitor tab~~
- ~~[#294](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/294): Refactor Anomalies tab to integrate Node class etc.~~
- ~~[#295](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/295): Finalize Node Class in Node_viewer and refactor~~
- ~~[#306](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/306): Adjust aesthetics in ui.utils to conform to client requirements~~
- ~~[#313](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/313): Implement File to Hold Parent classes~~
- ~~[#315](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/315): Increase Accessibility~~
- ~~[#344](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/344): Create ReadMe~~
- ~~[#345](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/345): Implement RedisReader class~~
- ~~[#434](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/434): review pathways and resolve slight merge issues~~
- ~~[#479](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/479): Ensure functional redis integration~~
- ~~[#480](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/480): Ensure Redis_Reader functionality~~
- ~~[#483](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/483): ensure redis functionality for anomalies tab~~
- ~~[#486](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/486): ensure redis functionality for node_viewer~~
- ~~[#504](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/504): Create Toggle for test_mode vs redis_mode~~
- ~~[#531](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/531): 4/5/26 debugging day~~
- ~~[#571](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/571): fix merge issue~~
- ~~[#578](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/578): Update Redis parsing to match new message style~~
- ~~[#588](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/588): final debugging before system runthrough~~
- ~~[#592](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/592): fix redis_reader inf lock~~
- ~~[#593](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/593): fix_redis_lock~~
- ~~[#600](https://github.com/ComputerScienceUniversityofDenver/edge-anomly-mesh/issues/600): refactor update-node to fit new message requirements~~

