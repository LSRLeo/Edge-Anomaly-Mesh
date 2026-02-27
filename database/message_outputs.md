# DB Query Message Definitions

Message request/response pairs for DB query functions.

---

## 1. get_nodes

**Request:**
```json
{
  "m_type": "get-nodes",
  "m_id": "ui_00001"
}
```

**Response:**
```json
{
  "m_type": "get-nodes-response",
  "m_id": "db_00001",
  "responding_to": "ui_00001",
  "nodes": [
    "node_001",
    "node_002",
    "node_003"
  ]
}
```

---

## 2. get_node_data_ids(node_id)

**Request:**
```json
{
  "m_type": "get-node-data-ids",
  "m_id": "ui_00001",
  "node_id": "node_001"
}
```

**Response:**
```json
{
  "m_type": "get-node-data-ids-response",
  "m_id": "db_00002",
  "responding_to": "ui_00001",
  "node_id": "node_001",
  "data_ids": [
    "node_001_2026-01-22T18:52:14.818400",
    "node_001_2026-01-22T18:52:14.838400",
    "node_001_2026-01-22T18:52:14.858400"
  ]
}
```

---

## 3. get_datum(event_id)

**Request:**
```json
{
  "m_type": "get-datum",
  "m_id": "ui_00001",
  "event_id": "node_001_2026-01-22T18:52:14.818400"
}
```

**Response:**
```json
{
  "m_type": "get-datum-response",
  "m_id": "db_00003",
  "responding_to": "ui_00001",
  "event_id": "node_001_2026-01-22T18:52:14.818400",
  "node_id": "node_001",
  "timestamp": "2026-01-22T18:52:14.818400",
  "seq": 12345,
  "gps": {
    "lat_deg": 40.713923,
    "lon_deg": -74.004764,
    "altitude_m": 50.1
  },
  "accel_mss": {
    "x": 0.05,
    "y": 0.02,
    "z": 9.81
  },
  "gyro_rads": {
    "x": 0.01,
    "y": 0.01,
    "z": 0.01
  },
  "meta": {
    "sample_rate_hz": 50,
    "battery_pct": 95,
    "sim_mode": "IDLE",
    "sim_anomaly": false
  },
  "origin": {
    "lat_deg": 40.712776,
    "lon_deg": -74.005974,
    "altitude_m": 10.0
  },
  "dest": {
    "lat_deg": 41.878113,
    "lon_deg": -87.629799,
    "altitude_m": 180.0
  },
  "inference": {
    "classification": "IDLE",
    "confidence": 0.913,
    "is_anomaly": false,
    "anomaly_score": 0.063
  }
}
```

**Notes:**
- `inference` may be `null` if ML has not yet processed this event

---

## 4. get_recent_raw_data(node_id)

**Request:**
```json
{
  "m_type": "get-recent-raw-data",
  "m_id": "ui_00001",
  "node_id": "node_001"
}
```

**Response:**
```json
{
  "m_type": "get-recent-raw-data-response",
  "m_id": "db_00004",
  "responding_to": "ui_00001",
  "node_id": "node_001",
  "records": [
    {
      "event_id": "node_001_2026-01-22T18:52:14.818400",
      "timestamp": "2026-01-22T18:52:14.818400",
      "seq": 12345,
      "accel_mss": {
        "x": 0.05,
        "y": 0.02,
        "z": 9.81
      },
      "gyro_rads": {
        "x": 0.01,
        "y": 0.01,
        "z": 0.01
      },
      "gps": {
        "lat_deg": 40.713923,
        "lon_deg": -74.004764,
        "altitude_m": 50.1
      }
    }
  ]
}
```

**Notes:**
- `records` is ordered newest-first
- Caller may optionally include a `limit` field in the request (default TBD)

---

## 5. get_recent_inference(node_id)

**Request:**
```json
{
  "m_type": "get-recent-inference",
  "m_id": "ui_00001",
  "node_id": "node_001"
}
```

**Response:**
```json
{
  "m_type": "get-recent-inference-response",
  "m_id": "db_00005",
  "responding_to": "ui_00001",
  "node_id": "node_001",
  "records": [
    {
      "event_id": "node_001_2026-01-22T18:52:14.818400",
      "timestamp": "2026-01-22T18:52:14.818400",
      "window_start": 1769133132,
      "window_end": 1769133134,
      "window_samples": 20,
      "location_state": HOME,
      "motion_class": IDLE,
      "confidence": 0.95,
      "anomaly_detected": false,
      "anomaly_score": 0.12,
      "anomaly_type": IMPACT,
      "nearest_hub_id": hub_nyc_01,
      "nearest_hub_distance": 39.7,
      "feature_vector": {
            "rms_accel": 0.05,
            "peak_accel": 0.12,
            "dominant_freq_hz": 0.0,
            "variance_x": 0.002,
            "variance_y": 0.002,
            "variance_z": 0.003
      }
    }
  ]
}
```

**Notes:**
- `records` is ordered newest-first
- Caller may optionally include a `limit` field in the request (default TBD)

---

## Error Response (all requests)

```json
{
  "m_type": "error",
  "m_id": "db_00099",
  "responding_to": "ui_00001",
  "original_request": "get-datum",
  "error_code": "NOT_FOUND",
  "error_message": "Event ID not found"
}
```

**Error codes:** `NOT_FOUND`, `INVALID_REQUEST`, `INTERNAL_ERROR`
