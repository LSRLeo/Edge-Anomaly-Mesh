# DB Query Message Definitions

Message request/response pairs for DB query functions.

---

## Input Message Formats

### raw-data
**Singular:**
```json
{
  "m_type": "raw-data",
  "m_id": "node_001_12345",
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
  }
}
```

**Batch:**
```json
{
  "m_type": "raw-data",
  "m_id": "node_001_batch_001",
  "records": [
    {
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
      }
    },
    {
      "event_id": "node_001_2026-01-22T18:52:14.838400",
      "node_id": "node_001",
      "timestamp": "2026-01-22T18:52:14.838400",
      "seq": 12346,
      "gps": {
        "lat_deg": 40.713923,
        "lon_deg": -74.004764,
        "altitude_m": 50.1
      },
      "accel_mss": {
        "x": 0.04,
        "y": 0.03,
        "z": 9.82
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
      }
    }
  ]
}
```

**Notes:**
- Singular: data fields at top level alongside `m_type` and `m_id`
- Batch: data fields moved into `records` list; top level contains only `m_type`, `m_id`, and `records`

---

### inference-output

**Singular:**
```json
{
  "m_type": "inference-output",
  "m_id": "ml_00001",
  "event_id": "node_001_2026-01-22T18:52:14.818400",
  "node_id": "node_001",
  "timestamp": "2026-01-22T18:52:14.818400",
  "classification": "IDLE",
  "confidence": {
    "IDLE": 0.72,
    "TERRESTRIAL": 0.08,
    "MARITIME": 0.05,
    "LIFT": 0.03,
    "IDLE_ANOM": 0.06,
    "TERRESTRIAL_ANOM": 0.03,
    "MARITIME_ANOM": 0.02,
    "LIFT_ANOM": 0.01
  },
  "is_anomaly": false,
  "anomaly_score": 0.063
}
```

**Batch:**
```json
{
  "m_type": "inference-output",
  "m_id": "ml_batch_001",
  "records": [
    {
      "event_id": "node_001_2026-01-22T18:52:14.818400",
      "node_id": "node_001",
      "timestamp": "2026-01-22T18:52:14.818400",
      "classification": "IDLE",
      "confidence": {
        "IDLE": 0.72,
        "TERRESTRIAL": 0.08,
        "MARITIME": 0.05,
        "LIFT": 0.03,
        "IDLE_ANOM": 0.06,
        "TERRESTRIAL_ANOM": 0.03,
        "MARITIME_ANOM": 0.02,
        "LIFT_ANOM": 0.01
      },
      "is_anomaly": false,
      "anomaly_score": 0.063
    },
    {
      "event_id": "node_001_2026-01-22T18:52:14.838400",
      "node_id": "node_001",
      "timestamp": "2026-01-22T18:52:14.838400",
      "classification": "TERRESTRIAL",
      "confidence": {
        "IDLE": 0.05,
        "TERRESTRIAL": 0.81,
        "MARITIME": 0.03,
        "LIFT": 0.02,
        "IDLE_ANOM": 0.04,
        "TERRESTRIAL_ANOM": 0.03,
        "MARITIME_ANOM": 0.01,
        "LIFT_ANOM": 0.01
      },
      "is_anomaly": false,
      "anomaly_score": 0.041
    }
  ]
}
```

**Field notes:**
- `classification`: one of `IDLE`, `TERRESTRIAL`, `MARITIME`, `LIFT`, `UNKNOWN` (uppercase)
- `confidence`: per-class softmax probabilities summing to 1.0
- `anomaly_score`: range `[0.0, 1.0]`
- Singular: data fields at top level alongside `m_type` and `m_id`
- Batch: data fields moved into `records` list; top level contains only `m_type`, `m_id`, and `records`

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
  "event_ids": [
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
    "lat": 40.713923,
    "lon": -74.004764,
    "altitude_m": 50.1
  },
  "accel": {
    "x": 0.05,
    "y": 0.02,
    "z": 9.81
  },
  "gyro": {
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
    "lat": 40.712776,
    "lon": -74.005974,
    "altitude_m": 10.0
  },
  "dest": {
    "lat": 41.878113,
    "lon": -87.629799,
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
- `meta`, `origin`, and `dest` are excluded from this response
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
      "node_id": "node_001",
      "timestamp": "2026-01-22T18:52:14.818400",
      "classification": "IDLE",
      "confidence": {
        "IDLE": 0.72,
        "TERRESTRIAL": 0.08,
        "MARITIME": 0.05,
        "LIFT": 0.03,
        "IDLE_ANOM": 0.06,
        "TERRESTRIAL_ANOM": 0.03,
        "MARITIME_ANOM": 0.02,
        "LIFT_ANOM": 0.01
      },
      "is_anomaly": false,
      "anomaly_score": 0.063
    }
  ]
}
```

**Notes:**
- Each record mirrors the `inference-output` format
- Caller may optionally include a `limit` field in the request (default TBD)

---

## 6. get_active_nodes

**Request:**
```json
{
  "m_type": "get-active-nodes",
  "m_id": "ui_00001"
}
```

**Response:**
```json
{
  "m_type": "get-active-nodes-response",
  "m_id": "db_00006",
  "responding_to": "ui_00001",
  "nodes": [
    "node_001",
    "node_002"
  ]
}
```

---

## 7. get_node_info(node_id)

**Request:**
```json
{
  "m_type": "get-node-info",
  "m_id": "ui_00001",
  "node_id": "node_001"
}
```

**Response:**
```json
{
  "m_type": "get-node-info-response",
  "m_id": "db_00007",
  "responding_to": "ui_00001",
  "node_id": "node_001",
  "status": "active",
  "first_seen": "2026-01-22T18:52:14.818400",
  "last_seen": "2026-01-22T19:10:03.224100",
  "location": {
    "lat_deg": 40.713923,
    "lon_deg": -74.004764,
    "altitude_m": 50.1
  }
}
```
**Notes:**
- Gets `node` returns `status`, `first_seen`, and `last_seen` from the `Node` table
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
