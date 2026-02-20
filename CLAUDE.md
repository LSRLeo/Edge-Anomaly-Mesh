# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**edge-anomaly-mesh** is a distributed anomaly detection system that simulates cargo monitoring in supply chains. It classifies IoT sensor motion data (accelerometer/gyroscope at 50-100 Hz) into 4 motion types (IDLE, TERRESTRIAL, MARITIME, LIFT) and detects anomalies in real-time.

## Architecture

```
node-simulator → ml → database → ui
   (Team 1)    (Team 2) (Team 3)  (Team 4)
```

**Inter-module communication:** Redis pub/sub
- Raw sensor data: `sensor:raw:{node_id}` channel
- Inference results: `inference:results:{node_id}` channel

**Technology Stack:** Python 3, PyTorch, Redis, SQLite, Tkinter, NumPy, SciPy

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis via Docker (required for inter-module communication)
docker run --name redis-server -p 6379:6379 -d redis:latest

# Stop/start Redis
docker stop redis-server
docker start redis-server
```

## Common Commands

```bash
# Run sensor simulator
python node-simulator/run_simulator.py
python node-simulator/run_simulator.py --nodes 10 --duration 60

# Generate training data
python node-simulator/training_data_generator.py --samples 1000 --output data/training
python scripts/generate_init_data.py --duration 30

# Train ML model
python ml/train_classifier.py
python ml/train_classifier.py --epochs 200 --batch-size 64 --learning-rate 0.0005

# Run all tests
pytest tests/

# Run specific test modules
pytest tests/test-data-engineering/
pytest tests/test-machine-learning/
pytest tests/test-databases/

# Run a single test file
pytest tests/test-machine-learning/test_feature_extraction.py

# Run a single test
pytest tests/test-machine-learning/test_feature_extraction.py::test_function_name
```

## Module Structure

- **node-simulator/** - Sensor simulation and data generation
  - `run_simulator.py` - Main entry point
  - `node_simulator.py` - `SensorNode`, `NodeManager` classes
  - `hub_manager.py` - Network topology management
  - `redis_publisher.py` - Redis data publication
  - `motion_generators/` - Factory pattern: `get_generator(motion_type)` returns generator for IDLE, TERRESTRIAL, MARITIME, or LIFT

- **ml/** - Classification and anomaly detection
  - `train_classifier.py` - PyTorch MLP training (20 features → 64 → 32 → 4 classes)
  - `feature_extraction.py` - Windowed feature engineering (RMS, peaks, variance, FFT)

- **database/** - SQLite persistence (tables: `inference_results`, `nodes`, `anomaly_events`)

- **ui/** - Tkinter dashboard (Network, Anomalies, Analytics, Node Details tabs)

- **scripts/** - Utility scripts including Redis pub/sub tools (`redis_pub.py`, `redis_sub.py`)

- **tests/** - Pytest suite with shared fixtures in `conftest.py`

## Coding Style

### Naming Conventions
- Variables/functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- JSON fields: `snake_case` with unit suffixes (`_m`, `_mss`, `_rads`, `_hz`, `_deg`, `_pct`, `_ms`)
- Directories: `kebab-case` (e.g., `node-simulator/`, `test-machine-learning/`)
- Python files: `snake_case` (e.g., `hub_manager.py`)

### Message Type Convention
All messages include:
- `m_type`: Message type (`raw-data`, `inference-output`, `get-nodes`, `get-datum`, `error`, etc.)
- `m_id`: Tracking ID with format `{sender_id}_{seq}` (e.g., `node_001_12345`)

### ID Formats
- `node_id`: `node_{number}` (e.g., `node_001`)
- `hub_id`: `hub_{city}_{number}` (e.g., `hub_nyc_01`)
- `event_id`: `{node_id}_{timestamp}` (e.g., `node_001_2026-01-22T18:52:14.818400`)
- Timestamps: ISO 8601 with microseconds (`YYYY-MM-DDTHH:MM:SS.ffffff`)

## Data Formats

**Raw Sensor Data (node-simulator → ml):**
```json
{
  "m_type": "raw-data",
  "m_id": "node_001_12345",
  "event_id": "node_001_2026-01-22T18:52:14.818400",
  "node_id": "node_001",
  "timestamp": "2026-01-22T18:52:14.818400",
  "accel_mss": {"x": 0.05, "y": 0.02, "z": 9.81},
  "gyro_rads": {"x": 0.01, "y": 0.01, "z": 0.01},
  "meta": {"sample_rate_hz": 50, "battery_pct": 95, "sim_mode": "IDLE", "sim_anomaly": false}
}
```

**Inference Output (ml → database):**
```json
{
  "m_type": "inference-output",
  "m_id": "ml_00001",
  "event_id": "node_001_2026-01-22T18:52:14.818400",
  "node_id": "node_001",
  "timestamp": "2026-01-22T18:52:14.818400",
  "classification": "IDLE",
  "confidence": 0.95,
  "is_anomaly": false,
  "anomaly_score": 0.12
}
```

## Key Constraints

- Motion classes: `IDLE`, `TERRESTRIAL`, `MARITIME`, `LIFT`, `UNKNOWN` (always uppercase)
- `anomaly_score` and `confidence`: range [0.0, 1.0]
- Sample rate: 50-100 Hz (default 50)
- Timestamps must increase monotonically
- Database queries must respond in < 500ms
- Handle out-of-order/duplicate messages gracefully

## Redis Pub/Sub Testing

```bash
# Monitor all Redis activity (useful for debugging)
docker exec -it redis-server redis-cli monitor

# List active pub/sub channels
docker exec -it redis-server redis-cli pubsub channels

# Manual publish/subscribe for testing
cd scripts
python redis_sub.py sensor:raw:node_001    # Terminal 1: subscribe
python redis_pub.py sensor:raw:node_001    # Terminal 2: publish (type messages, CTRL-d to exit)
```

## Current Status

This is a skeleton codebase with extensive TODO comments. Most modules have scaffolding but incomplete implementations. Training data samples exist in `data/generated_data/`.
