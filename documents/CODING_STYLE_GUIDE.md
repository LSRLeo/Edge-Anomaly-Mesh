# Edge-Anomaly-Mesh Coding Style Guide

This document defines the coding standards and conventions for the edge-anomaly-mesh project, derived from existing code patterns and message definitions.

---

## Table of Contents

1. [General Principles](#general-principles)
2. [Python Code Style](#python-code-style)
3. [Naming Conventions](#naming-conventions)
4. [JSON Message Formats](#json-message-formats)
5. [Data Structures](#data-structures)
6. [Documentation](#documentation)
7. [Testing](#testing)

---

## General Principles

- **Consistency**: Follow existing patterns in the codebase
- **Clarity**: Code should be self-explanatory; prefer descriptive names over comments
- **Simplicity**: Avoid over-engineering; implement only what is needed

---

## Python Code Style

### Imports

Organize imports in the following order, separated by blank lines:

```python
# Standard library imports
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

# Third-party imports
import numpy as np
import pytest

# Local imports
from motion_generators import idle_generator
```

### Indentation and Spacing

- Use 4 spaces for indentation (no tabs)
- Use blank lines to separate logical sections within functions
- Two blank lines between top-level function definitions

```python
def generate_idle_data():
    """Generate IDLE motion data."""
    g = 9.81
    data = []

    for i in range(500):
        t = i * 0.02
        reading = {
            'timestamp': t,
            'accel_x': np.random.normal(0.0, 0.05),
        }
        data.append(reading)

    return data


def generate_terrestrial_data():
    """Generate TERRESTRIAL motion data."""
    # Implementation
    pass
```

### Comments

- Use `#` with a space after for inline comments
- Place comments on their own line above the code they describe
- Avoid obvious comments; code should be self-documenting

```python
# Generate small samples (10 seconds each at 50Hz = 500 samples)
motions = {
    'idle': generate_idle_data(),
    'terrestrial': generate_terrestrial_data(),
}

# Inject 2 shocks
for _ in range(2):
    idx = np.random.randint(0, len(data))
```

### String Formatting

- Use f-strings for string interpolation
- Use single quotes for dictionary keys and short strings
- Use double quotes for user-facing messages and docstrings

```python
print(f"Location: {data_dir}")
json_file = motion_dir / f'{motion_type}_starter.json'
```

---

## Naming Conventions

### Variables and Functions

- Use `snake_case` for variables, functions, and method names
- Use descriptive names that indicate purpose

```python
sample_rate_hz = 50
motion_class = "IDLE"
anomaly_score = 0.12

def generate_starter_data():
    pass

def save_json(data, filepath, motion_type):
    pass
```

### Constants

- Use `UPPER_SNAKE_CASE` for constants
- Define at module level

```python
MOTION_CLASSES = ['IDLE', 'TERRESTRIAL', 'MARITIME', 'LIFT', 'UNKNOWN']
ERROR_CODES = ['NOT_FOUND', 'INVALID_REQUEST', 'INTERNAL_ERROR']
SIM_MODES = ['IDLE', 'TERRESTRIAL', 'MARITIME', 'LIFT']
```

### Classes

- Use `PascalCase` for class names

```python
class NodeSimulator:
    pass

class HubManager:
    pass
```

### Files and Directories

- Use `snake_case` for Python files: `generate_init_data.py`, `hub_manager.py`
- Use `kebab-case` for directories: `node-simulator/`, `test-machine-learning/`
- Use descriptive names that indicate module purpose

---

## JSON Message Formats

### Field Naming

- Use `snake_case` for all JSON field names
- Include unit suffixes where applicable to indicate measurement units

| Suffix | Unit | Example |
|--------|------|---------|
| `_m` | meters | `altitude_m`, `distance_m` |
| `_mss` | meters per second squared (m/s^2) | `accel_mss` |
| `_rads` | radians per second (rad/s) | `gyro_rads` |
| `_hz` | hertz | `sample_rate_hz`, `dominant_freq_hz` |
| `_deg` | degrees | `lat_deg`, `lon_deg` |
| `_pct` | percentage (0-100) | `battery_pct` |
| `_ms` | milliseconds | `processing_time_ms` |

```json
{
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
  "sample_rate_hz": 50,
  "battery_pct": 95
}
```

### Message Type Convention

- All messages include `m_type` to identify the message type
- All messages include `m_id` for tracking with format `{sender_id}_{seq}`
- Response messages include `responding_to` field referencing the original request's `m_id`

**Valid m_types:**
- `raw-data`
- `inference-output`
- `get-nodes`
- `get-nodes-response`
- `get-node-data-ids`
- `get-node-data-ids-response`
- `get-datum`
- `get-datum-response`
- `error`

```json
{
  "m_type": "raw-data",
  "m_id": "node_001_12345",
  "node_id": "node_001",
  "timestamp": "2026-01-22T18:52:14.818400"
}
```

### Timestamps

- Use ISO 8601 format: `YYYY-MM-DDTHH:MM:SS.ffffff`
- Include microseconds for precision
- All timestamps should be in UTC

```json
{
  "timestamp": "2026-01-22T18:52:14.818400"
}
```

### ID Formats

| ID Type | Format | Example |
|---------|--------|---------|
| `node_id` | `node_{number}` | `node_001`, `node_002` |
| `hub_id` | `hub_{city}_{number}` | `hub_nyc_01`, `hub_la_01` |
| `event_id` | `{node_id}_{timestamp}` | `node_001_2026-01-22T18:52:14.818400` |
| `m_id` | `{sender_id}_{seq}` | `node_001_12345`, `ui_00001` |

### Nested Objects

Group related fields into nested objects:

```json
{
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
  "anomaly": {
    "detected": false,
    "score": 0.063,
    "type": null
  }
}
```

---

## Data Structures

### Sensor Readings

```python
reading = {
    'timestamp': t,
    'accel_x': 0.05,
    'accel_y': 0.02,
    'accel_z': 9.81,
    'gyro_x': 0.01,
    'gyro_y': 0.01,
    'gyro_z': 0.01,
}
```

### Inference Results

```python
result = {
    'node_id': 'node_001',
    'timestamp': '2026-01-22T18:52:14.818400',
    'motion_class': 'IDLE',
    'confidence': 0.95,
    'anomaly': {
        'detected': False,
        'score': 0.12,
        'type': None
    }
}
```

### Configuration Objects

```python
hub = {
    'hub_id': 'hub_nyc_01',
    'name': 'NYC Distribution Center',
    'lat': 40.7128,
    'lon': -74.006,
    'altitude_m': 10.0,
    'radius_m': 500,
    'type': 'distribution_center'
}
```

---

## Documentation

### Module Docstrings

Place at the top of files:

```python
"""
Pytest fixtures shared across all test modules.
"""
```

### Function Docstrings

Use triple double quotes, describe what the function does:

```python
def generate_idle_data():
    """Generate IDLE motion data."""
    pass

def save_json(data, filepath, motion_type):
    """Save data as JSON in REDIS format."""
    pass
```

### Script Headers

Include usage instructions in script comments:

```python
# To run this script: python3 scripts/generate_init_data.py --duration 30

# Download/generate starter simulation data for anomaly-mesh
```

---

## Testing

### Test File Organization

- Place tests in `tests/` directory
- Use subdirectories for module-specific tests: `test-machine-learning/`, `test-databases/`
- Use `conftest.py` for shared fixtures

### Test Fixtures

Define reusable test data as pytest fixtures:

```python
@pytest.fixture
def sample_sensor_reading():
    """Sample sensor reading for testing."""
    return {
        "node_id": "node_001",
        "timestamp": "2024-01-15T10:30:00",
        "accel_x": 0.05,
        "accel_y": -0.02,
        "accel_z": 9.81,
        "gyro_x": 0.01,
        "gyro_y": 0.01,
        "gyro_z": 0.00,
    }


@pytest.fixture
def sample_inference_result():
    """Sample inference result for testing."""
    return {
        "node_id": "node_001",
        "timestamp": 1702656000.123456,
        "motion_class": "IDLE",
        "motion_confidence": 0.95,
        "anomaly_flag": False,
        "anomaly_score": 0.12,
    }
```

### Test Naming

- Use descriptive test names that indicate what is being tested
- Prefix test functions with `test_`

```python
def test_idle_motion_classification():
    pass

def test_anomaly_detection_threshold():
    pass
```

---

## Domain-Specific Conventions

### Motion Classes

Always use uppercase for motion class values:
- `IDLE`
- `TERRESTRIAL`
- `MARITIME`
- `LIFT`
- `UNKNOWN`

### Anomaly Scores

- Range: `0.0` to `1.0`
- Values closer to `1.0` indicate higher anomaly likelihood

### Confidence Scores

- Range: `0.0` to `1.0`
- Values closer to `1.0` indicate higher confidence

### Physical Constants

```python
g = 9.81  # gravitational acceleration in m/s^2
```

### Sample Rates

Standard sample rate is 50Hz:

```python
sample_rate_hz = 50
sample_interval = 0.02  # 1/50 seconds
```

---

## Error Handling

### Error Response Format

```json
{
  "m_type": "error",
  "m_id": "ui_00002",
  "original_request": "get-datum",
  "error_code": "NOT_FOUND",
  "error_message": "Event ID not found"
}
```

### Valid Error Codes

- `NOT_FOUND` - Requested resource does not exist
- `INVALID_REQUEST` - Request format is incorrect
- `INTERNAL_ERROR` - Server-side error occurred

---

## File Organization

```
edge-anomaly-mesh/
├── data/
│   ├── config/           # Configuration files (JSON)
│   ├── examples/         # Example data files
│   └── generated_data/   # Output from scripts
├── database/             # Database module
├── documents/            # Project documentation
├── ml/                   # Machine learning module
├── node-simulator/       # Sensor simulation module
├── scripts/              # Utility scripts
├── tests/                # Test suites
│   ├── conftest.py
│   ├── test-databases/
│   ├── test-data-engineering/
│   └── test-machine-learning/
└── ui/                   # User interface module
```

---

## Quick Reference

| Category | Convention | Example |
|----------|------------|---------|
| Python variables | `snake_case` | `sample_rate_hz` |
| Python functions | `snake_case` | `generate_idle_data()` |
| Python classes | `PascalCase` | `NodeSimulator` |
| Constants | `UPPER_SNAKE_CASE` | `MOTION_CLASSES` |
| JSON fields | `snake_case` | `node_id`, `motion_class` |
| Unit suffixes | `_unit` | `altitude_m`, `accel_mss` |
| Message types | `kebab-case` | `raw-data`, `get-nodes` |
| Node IDs | `node_{number}` | `node_001` |
| Hub IDs | `hub_{city}_{number}` | `hub_nyc_01` |
| Timestamps | ISO 8601 | `2026-01-22T18:52:14.818400` |
