# edge-anomly-mesh
Project Overview
Edge-anomly-mesh is a hybrid mesh network simulation system that detects anomalies in motion data from nodes traveling between network hubs.

In the real world, packages/cargo move between distribution centers (hubs) while sensors on them collect accelerometer data. This project simulates that scenario using machine learning to:

Classify motion types (idle, terrestrial, maritime, lift)
Detect anomalies (unexpected patterns that indicate problems)
Aggregate and visualize the data across the entire network

This is a simulation-based project. 

What We Are Building: 
A distributed anomaly detection system that simulates cargo monitoring networks

Tech Stack
REDIS
TensorFlow Lite
Scikit-learn
SQLite
Flask(Maybe?)
Tkinger
Pytest

The 4 Motion Classes
The system learns to classify movement into 4 categories:
1. IDLE
Cargo sitting stationary in a warehouse

Device is completely still
Only gravity acts (9.81 m/s² downward)
Minimal noise/vibration
Example: Flat line with Z-axis near 9.81

2. TERRESTRIAL
Cargo in a truck/train moving on roads/rails

Horizontal shaking from road bumps
Regular, periodic vibration pattern (2-5 Hz)
Less vertical movement than horizontal
Example: varied movmenet, jagged to flat, random peaks across all axes (most peaks will be x and y, going up and down), 


3. MARITIME
Cargo on a ship in rough seas

Chaotic 3D motion (all axes equally affected)
Random wave impacts (sudden spikes)
Non-periodic, unpredictable pattern
xample: Sine wave pattern, peaks in X and Y axes (If the ocean was a perfect sine wave)

4. LIFT
Cargo being lifted by a forklift

Vertical acceleration/deceleration
Clear 8-10 second cycle: up → hold → down → rest
Minimal horizontal movement
Example: Z-axis shows distinctive trapezoid shape

ANOMALY
Anything that breaks the expected pattern:

Sudden impacts/drops
Sensor failures (loss of gravity signal)
Unexpected high-frequency vibration
Calibration drift over time

Team Roles & Responsibilities
Team 1: Data Generation (Simulation)
Your Job: Create realistic simulated accelerometer data.
What You'll Build:

A sensor simulator that generates MPU6050 accelerometer/gyroscope data
Realistic motion patterns for all 4 motion types
The ability to inject anomalies (simulate problems)
Publishing system to send data to REDIS

Example:REDIS channel: sensor:raw:{node_id}
{
  "node_id": "node_001",
  "timestamp": 1702656000.123,
  "accel": {"x": 0.05, "y": -0.02, "z": 9.81},
  "gyro": {"x": 0.01, "y": 0.02, "z": 0.0}
}

Team 2: Brain (Data Processing & ML)
Your Job: Process sensor data and classify motion using machine learning.
What You'll Build:

A data processing pipeline that listens to REDIS
Integration with a pre-trained TensorFlow Lite model
Anomaly detection using K-means clustering
Publishing system to send results back to REDIS

Example:REDIS channel: inference:results:{node_id}
{
  "node_id": "node_001",
  "timestamp": 1702656000.123,
  "motion_class": "IDLE",
  "motion_confidence": 0.95,
  "anomaly_flag": false,
  "anomaly_score": 0.12
}

Team 3: Database (Persistence & API)
Your Job: Store results and provide an API for querying data.
What You'll Build:

SQLite database schema for storing inferences
Background listener to REDIS for incoming results
Flask REST API with GET endpoints
Query system for filtering/searching data



Team 4: UI (Visualization)
Your Job: Build a GUI that displays everything happening in the system.
What You'll Build:

Tkinter GUI application
Real-time dashboard showing node status
Visualization of motion classifications
Anomaly alerts and statistics

Example:
Tkinter GUI with four tabs (Network, Anomalies, Analytics, Node Detials). Network woulld display a visual map of active modes (could be color-coded by motion state). Anomalies, live feed of alerts with a severity level. Analytics, which includes motion class distribution, anomaly trends. Node Detials, motion histroy, anomoly score trend, feature heatmap

Team Interfaces:
Team 1 -> Team 2 
Timestamps should be monotonically increasing per node, team 2 should be able to handle gaps.
Team 2 -> Team 3 
Message format should include annomly_flag(boolean) as well as anomaly_score(float)
Team 3 -> Tema 4 

