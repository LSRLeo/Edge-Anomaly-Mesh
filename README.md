# edge-anomly-mesh

## Project Overview

Edge-anomly-mesh is a hybrid mesh network simulation system that detects anomalies in motion data from nodes traveling between network hubs.

In the real world, packages/cargo move between distribution centers (hubs) while sensors on them collect accelerometer data. This project simulates that scenario using machine learning to:

- Classify motion types (idle, terrestrial, maritime, lift)
- Detect anomalies (unexpected patterns that indicate problems)
- Aggregate and visualize the data across the entire network

This is a simulation-based project.

## What We Are Building

A distributed anomaly detection system that simulates cargo monitoring networks.

## Tech Stack

- [Redis](https://redis.io/) - In-memory message broker for real-time sensor data streaming between nodes
- [PyTorch](https://pytorch.org/) - Deep learning framework for motion classification and anomaly detection models
- [SQLite](https://www.sqlite.org/) - Lightweight database for storing inference results and anomaly events
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - Python GUI library for the real-time visualization dashboard

## Project Organization

The project is organized into 4 team modules that form a data pipeline:

```
data-engineering → machine-learning → databases → frontend-engineering
```

| Directory | Description |
|-----------|-------------|
| [data-engineering](data-engineering/) | Sensor simulation, motion generators, and training data generation |
| [machine-learning](machine-learning/) | Motion classification and anomaly detection models |
| [databases](databases/) | SQLite storage and query functions for inference results |
| [frontend-engineering](frontend-engineering/) | Tkinter dashboard for real-time visualization |
| tests/ | Test suites for all modules |
| data/ | Generated training and simulation data |

## The 4 Motion Classes

The system learns to classify movement into 4 categories:

1. **IDLE** - Cargo sitting stationary in a warehouse.
   - Device is completely still
   - Only gravity acts (9.81 m/s² downward)
   - Minimal noise/vibration
   - Example: Flat line with Z-axis near 9.81

2. **TERRESTRIAL** - Cargo in a truck/train moving on roads/rails.
   - Horizontal shaking from road bumps
   - Regular, periodic vibration pattern (2-5 Hz)
   - Less vertical movement than horizontal
   - Example: Varied movement, jagged to flat, random peaks across all axes (most peaks will be x and y, going up and down)

3. **MARITIME** - Cargo on a ship in rough seas.
   - Chaotic 3D motion (all axes equally affected)
   - Random wave impacts (sudden spikes)
   - Non-periodic, unpredictable pattern
   - Example: Sine wave pattern, peaks in X and Y axes (if the ocean was a perfect sine wave)

4. **LIFT** - Cargo being lifted by a forklift or freight elevator
   - Vertical acceleration/deceleration
   - Clear 8-10 second cycle: up → hold → down → rest
   - Minimal horizontal movement
   - Example: Z-axis shows distinctive trapezoid shape

## Anomaly Detection

Anything that breaks the expected pattern:

- Sudden impacts/drops
- Sensor failures (loss of gravity signal)
- Unexpected high-frequency vibration
- Calibration drift over time

