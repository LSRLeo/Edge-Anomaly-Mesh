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

# Sprint 2
# DB Message System

Handles all database reads and writes through a unified JSON message interface. Send a message in, get a response out — the same pattern whether you're inserting sensor data, storing inference results, or querying the database.

---

## How It Works

Three files work together:

```
db_message_manager.py   ← entry point: receives messages, returns responses
db_message_factory.py   ← validates and constructs the right message object
db_message.py           ← message classes that know how to execute themselves
```

**Flow for every message:**

```
dict (JSON message)
    │
    ▼
DBMessageManager.process_message()
    │
    ▼
MessageFactory.create_message()     ← validates m_id + m_type, picks the class
    │
    ▼
message_obj.execute(table_manager)  ← runs the DB operation
    │
    ▼
response dict  or  None
```

---

## Message Structure

Every message is a JSON object with two required fields plus any type-specific fields:

```json
{
  "m_type": "get-nodes",
  "m_id":   "ui_001"
}
```

| Field    | Required | Description                          |
|----------|----------|--------------------------------------|
| `m_type` | yes      | Determines which class handles it    |
| `m_id`   | yes      | Unique ID for this message; echoed back in the response as `responding_to` |

---

## Supported Message Types

| `m_type` | Response? | Description |
|----------|-----------|-------------|
| `raw-data` | Only on failure | Insert a raw sensor record into the database |
| `inference-output` | Only on failure | Insert an ML inference result into the database |
| `get-nodes` | Always | Return all known node IDs |
| `get-node-data-ids` | Always | Return all event IDs for a given node |
| `get-datum` | Always | Return a single raw + inference record by event ID |
| `get-recent-raw-data` | Always | Return the most recent raw record for a node |
| `get-recent-inference` | Always | Return the most recent inference result for a node |

> **Note on `event_id`:** The `event_id` links a raw record to its inference result. It is formed from `node_id` + the Unix integer timestamp that the database stores — not the ISO string. Use `get-node-data-ids` to retrieve valid event IDs after inserting data.

---

## Usage

### Option 1 — Sample demo (no arguments)

Runs a built-in end-to-end demo using the bundled sample files:

```bash
python db_message_manager.py
```

What it does:
1. Reads `sample_message_data.json` — inserts raw-data and inference-output records into the DB. Successful inserts produce no output; any errors are written to the response file.
2. Reads `sample_message_requests.json` — runs get-nodes, get-node-data-ids, and get-datum queries against the data just inserted.
3. Writes all responses to `sample_message_responses.json`.

This is the fastest way to verify the whole pipeline end-to-end.

---

### Option 2 — CLI with your own files

```bash
python db_message_manager.py --infile <input.json> --outfile <output.json>
```

Both flags are required together. The input file can be a single message object or an array of messages.

> **⚠ The outfile is overwritten on every run.** Anything previously in the file will be lost. If you need to keep prior responses, copy or rename the file before running again.

**Insert data:**
```bash
python db_message_manager.py --infile sample_message_data.json --outfile responses.json
```
`responses.json` will be `[]` if all inserts succeeded, or contain error dicts for any that failed.

**Query the database:**
```bash
python db_message_manager.py --infile sample_message_requests.json --outfile responses.json
```
`responses.json` will contain one response object per query message.

**Typical workflow — insert first, then query:**
```bash
# 1. Insert data
python db_message_manager.py --infile sample_message_data.json --outfile responses.json

# 2. Find valid event IDs for a node
python db_message_manager.py --infile node_id_requests.json --outfile event_ids.json

# 3. Use those event IDs in get-datum requests
python db_message_manager.py --infile my_queries.json --outfile results.json
```

---

## Sample Files

| File | Contents |
|------|----------|
| `sample_message_data.json`     | 6 raw-data + 6 inference-output messages for node_001 (5 records) and node_002 (1 record) |
| `sample_message_requests.json` | get-nodes, get-node-data-ids for both nodes, get-datum for 3 event IDs |
| `sample_message_responses.json`| Written by the manager — populated after running the sample demo or CLI |

---

## Component Reference

### `DBMessageManager`

The public interface. Instantiate once; reuse across multiple `process_message` calls.

| Method | Description |
|--------|-------------|
| `process_message(dict)` | Process a single message dict. Returns a response dict or `None`. |
| `read_file(infile, outfile)` | Read a JSON file, process all messages, write responses. Returns the response list. |

### `MessageFactory`

Never instantiated — all methods are `@classmethod`. Called internally by `DBMessageManager`.

| Method | Description |
|--------|-------------|
| `create_message(dict)` | Validate `m_id`/`m_type`, strip envelope fields, return a typed message object or `None`. |
| `validate_message_dict(dict)` | Returns `(bool, error_string)`. |
| `get_supported_types()` | Returns the list of registered `m_type` strings. |

### `db_message.py` — Message classes

| Class | Type | `execute()` returns |
|-------|------|---------------------|
| `RawDataMessage` | Data | `None` on success, error dict on failure |
| `InferenceOutputMessage` | Data | `None` on success, error dict on failure |
| `GetNodesRequest` | Query | Response dict always |
| `GetNodeDataIdsRequest` | Query | Response dict always |
| `GetDatumRequest` | Query | Response dict always |
| `GetRecentRawDataRequest` | Query | Response dict always |
| `GetRecentInferenceRequest` | Query | Response dict always |

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