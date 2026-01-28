# Edge-Anomaly-Mesh Message Schemas

# Message Definitions

M_Types: 'raw-data', 'inference-output', 'Error'


## 1. raw-data

**Owner:** Node-Sim

```json
{
  "M_type": "raw-data",
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
  }
}
```

**Notes:**
- `sim_mode` values: `IDLE`, `TERRESTRIAL`, `MARITIME`, `LIFT`
- `event_id` format: `{node_id}_{timestamp}`

---

## 2. inference-output

**Owner:** ML Team

```json
{
  "M_type": "inference-output",
  "event_id": "node_001_2026-01-22T18:52:14.818400",
  "node_id": "node_001",
  "timestamp": "2026-01-22T18:52:14.818400",
  "classification": "IDLE",
  "confidence": 0.95,
  "is_anomaly": false,
  "anomaly_score": 0.12
}
```

**Notes:**
- `classification` values: `IDLE`, `TERRESTRIAL`, `MARITIME`, `LIFT`, `UNKNOWN`
- `confidence` and `anomaly_score` range: 0.0 to 1.0

---

## 3. get-nodes / get-nodes-response

**Owner:** UI → DB

**Request:**
```json
{
  "M_type": "get-nodes"
}
```

**Response:**
```json
{
  "M_type": "get-nodes-response",
  "nodes": [
    "node_001",
    "node_002",
    "node_003"
  ]
}
```

---

## 4. get-node-data-ids / get-node-data-ids-response

**Owner:** UI → DB

**Request:**
```json
{
  "M_type": "get-node-data-ids",
  "node_id": "node_001"
}
```

**Response:**
```json
{
  "M_type": "get-node-data-ids-response",
  "node_id": "node_001",
  "data_ids": [
    "node_001_2026-01-22T18:52:14.818400",
    "node_001_2026-01-22T18:52:14.838400",
    "node_001_2026-01-22T18:52:14.858400"
  ]
}
```

---

## 5. get-datum / get-datum-response

**Owner:** UI → DB

**Request:**
```json
{
  "M_type": "get-datum",
  "event_id": "node_001_2026-01-22T18:52:14.818400"
}
```

**Response:**
```json
{
  "M_type": "get-datum-response",
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
- `inference` may be `null` if ML has not yet processed this packet

---

## Error Response

```json
{
  "M_type": "error",
  "original_request": "get-datum",
  "error_code": "NOT_FOUND",
  "error_message": "Event ID not found"
}
```

Error codes: `NOT_FOUND`, `INVALID_REQUEST`, `INTERNAL_ERROR`