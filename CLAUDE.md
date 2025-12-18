# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Edge-anomly-mesh is a hybrid mesh network simulation system for detecting anomalies in cargo sensor data. It simulates IoT devices attached to packages moving between distribution hubs, generating accelerometer/gyroscope data that is classified into 4 motion types (IDLE, TERRESTRIAL, MARITIME, LIFT) with anomaly detection.

**Tech Stack:** Python, Redis (message queue), PyTorch (ML), SQLite (persistence), Tkinter (visualization)

## Architecture

The project is organized into 4 team modules that form a data pipeline:

```
data-engineering → machine-learning → databases → frontend-engineering
   (Team 1)           (Team 2)         (Team 3)       (Team 4)
```

### Team 1: Data Engineering (`data-engineering/`)
- Generates simulated sensor data at 50-100 Hz
- Motion generators in `motion_generators/` create realistic patterns for each motion type
- `node_simulator.py` - Manages sensor nodes attached to cargo
- `hub_manager.py` - Network topology of distribution hubs and routes
- `redis_publisher.py` - Publishes to Redis channel `sensor:raw:{node_id}`
- `training_data_generator.py` - Creates labeled datasets for ML training
- `run_simulator.py` - Main entry point

### Team 2: Machine Learning (`machine-learning/`)
- Subscribes to `sensor:raw:*` channels
- Buffers 2-5 second windows, extracts features (RMS, peaks, variance, FFT)
- Classifies motion using PyTorch model
- Detects anomalies via K-means clustering
- Publishes results to `inference:results:{node_id}`

### Team 3: Databases (`databases/`)
- SQLite with 3 tables: `inference_results`, `nodes`, `anomaly_events`
- Subscribes to `inference:results:*`
- Provides query functions for Team 4

### Team 4: Frontend Engineering (`frontend-engineering/`)
- Tkinter dashboard with tabs: Network map, Anomalies feed, Analytics charts, Node details

## Motion Classification

| Class | Description | Characteristics |
|-------|-------------|-----------------|
| IDLE | Stationary cargo | Only gravity (~9.81 m/s² on Z), minimal noise |
| TERRESTRIAL | Truck/train | Periodic vibration 2-5 Hz, mostly X/Y movement |
| MARITIME | Ship at sea | Chaotic 3D motion, random wave impacts |
| LIFT | Forklift | 8-10 sec vertical cycle (up→hold→down→rest) |

## Redis Message Formats

**Sensor data** (`sensor:raw:{node_id}`):
```json
{"node_id": "node_001", "timestamp": 1702656000.123, "accel": {"x": 0.05, "y": -0.02, "z": 9.81}, "gyro": {"x": 0.001, "y": 0.002, "z": 0.0}, "location": "hub_A", "motion_state_ground_truth": "idle"}
```

**Inference results** (`inference:results:{node_id}`):
```json
{"node_id": "node_001", "timestamp": 1702656000.123, "motion_class": "IDLE", "motion_confidence": 0.95, "anomaly_flag": false, "anomaly_score": 0.12}
```

## Commands

```bash
# Run simulator
python data-engineering/run_simulator.py
python data-engineering/run_simulator.py --nodes 10 --duration 60

# Generate training data
python data-engineering/training_data_generator.py --samples 1000 --output data/training

# Run tests
pytest tests/

# Run specific test module
pytest tests/test-data-engineering/
pytest tests/test-machine-learning/
pytest tests/test-databases/
```

## Key Constraints

- Timestamps must increase monotonically
- `motion_class` must be: IDLE, TERRESTRIAL, MARITIME, LIFT, or UNKNOWN
- `anomaly_score` must be in range [0, 1]
- Database queries should respond in < 500ms
- Handle duplicate/out-of-order messages gracefully
