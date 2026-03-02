## Team 3: Databases

## Goal:Store data from DE and ML teams as well as provide functional queries for ML and UI teams

## To Build: 
REDIS Listener - Subscribe to inference:results:*, write to database
Query Functions - 6 Python functions for Team 4 to call
Aggregations - Compute motion distributions, anomaly rates, statistics
Error Handling - Batch inserts, transaction management, graceful failures

## How to run

# Instantiate empty database
-In edge-anomaly-mesh directory, run
```bash
python database/schema.py
```
-This instantiates the empty mesh.db file

## Database Schema:

raw_sensor_data: id, node_id, timestamp, seq, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, gps_lat, gps_lon, gps_altitude_m, ingested_at

nodes: node_id, status, first_seen, last_seen, location_lat, location_lon, location_altitude_m

inference_results: id, node_id, timestamp, window_start, window_end, window_samples, location_state, motion_class, confidence, anomaly_detected, anomaly_score, anomaly_type, nearest_hub_id, nearest_hub_distance, feature_vector, processing_time_ms, ingested_at

anomaly_events: inference_id, id, node_id, start_timestamp, end_timestamp, severity, description, acknowledged, acknowledged_by, acknowledged_at

## Sprint 1

-implemented db using pysqlite and sqlalchemy
-Created tables and table managers
-created db file for each table
-began work on managing REDIS messages

## Key Constraints:

Queries respond in < 500ms
Handle duplicate messages idempotently
Proper indexing for common queries
Thread-safe access (Team 4 calls from UI thread)

Redis Channel
Channel: inference:results*
Publisher: ML
Subscriber: Database

Channel: dashboard:updates:{node_id}
Publisher: Database
Channel: dashboard:anomalies:{node_id}
Publisher: Database