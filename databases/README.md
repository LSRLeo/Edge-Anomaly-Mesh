Team 3: Databases

Goal:Store all inferences durably and provide query access for Team 4.

To Build: 
SQLite Schema - 3 tables: inference_results, nodes, anomaly_events
REDIS Listener - Subscribe to inference:results:*, write to database
Query Functions - 6 Python functions for Team 4 to call
Aggregations - Compute motion distributions, anomaly rates, statistics
Error Handling - Batch inserts, transaction management, graceful failures

Database Schema Example:

inference_results: node_id, timestamp, motion_class, confidence, anomaly_flag, anomaly_score
nodes: node_id, location, status, first_seen, last_seen
anomaly_events: node_id, start/end timestamp, severity, description, acknowledged

Key Constraints:

Queries respond in < 500ms
Handle duplicate messages idempotently
Proper indexing for common queries
Thread-safe access (Team 4 calls from UI thread)

