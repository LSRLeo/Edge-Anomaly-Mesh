# edge-anomaly-mesh

## Project Overview

Edge-anomly-mesh is a hybrid mesh network simulation system for detecting anomalies in cargo sensor data. It simulates IoT devices attached to packages moving between distribution hubs, generating accelerometer/gyroscope data that is classified into 4 motion types (IDLE, TERRESTRIAL, MARITIME, LIFT) with anomaly detection.

This is a simulation-based project.

---
## Running the program

Start up docker and redis

Start up your virtual environment

Make sure you are in the root directory just edge-anomaly-mesh/

Install all requirements, copy paste this in your activated environment make sure you start in the entire root directory .

```
cd node-simulator/
pip3 install -r requirements.txt
cd ../ui/
pip3 install -r requirements.txt
cd ../ml/
pip3 install -r requirements.txt
cd ../database/
pip3 install -r requirements.txt
```

Now we have to run these in a few seperate terminals. Make sure you activate the SAME virtual environment for all of your terminals 

### Terminal 1

Start Database schema, from root directory:

```
python3 database/schema.py
```

Start Database listener, from root directory:

```
python3 database/redis_listener.py
```

### Terminal 2

Start ML model, from root directory:

```
python3 ml/redis_insteam.py --window-size 100 --stride 100 --model-path ml/models/motion_classifier.pt
```

### Terminal 3

Start UI Dashboard, from root directory:
```
cd ui/
python3 -m widgets.dashboard_main
```

### Terminal 4

Once you are ready to start sending messages:

Create a simulation file, from root directory:
```
python3 node-simulator/simulation.py sim -t -n node-simulator/nodeConfig.json -r node-simulator/routes/compactAllModes.json --no-a
```

Send messages, from root directory:
```
python3 node-simulator/simulation.py redis sensor:raw:
```

## Background & Motivation

### The Real-World Problem

Global supply chains move billions of packages annually through complex networks of warehouses, trucks, ships, and aircraft. During transit, cargo faces numerous risks:

- **Physical damage** from drops, impacts, or rough handling
- **Environmental exposure** to extreme temperatures, humidity, or vibration
- **Theft or tampering** during extended transit periods
- **Delays and misrouting** causing spoilage of time-sensitive goods
- **Equipment failures** in refrigeration units or handling machinery

Traditional monitoring relies on periodic checkpoints and manual inspections, which means problems are often discovered only after damage has occurred. By the time a damaged shipment reaches its destination, the cost has already been incurred—and determining where the damage happened becomes nearly impossible.

Real-time sensor-based monitoring with edge computing and anomaly detection offers a solution: continuous visibility into cargo conditions with immediate alerts when something goes wrong.

### Use Cases for Cargo/Package Monitoring Systems

**Pharmaceutical & Healthcare Logistics**
- Temperature-sensitive vaccines and medications require strict cold chain compliance
- Anomaly detection can identify refrigeration failures before product spoilage
- Regulatory requirements (FDA, WHO) mandate documented handling conditions

**High-Value Electronics & Manufacturing**
- Sensitive components (semiconductors, displays) are vulnerable to shock and vibration
- Early detection of rough handling enables rerouting or inspection before delivery
- Reduces costly returns and warranty claims

**Food & Perishables**
- Fresh produce, seafood, and frozen goods have narrow temperature tolerances
- Motion patterns can indicate improper storage (e.g., a pallet that should be stationary is moving)
- Contamination risks from handling anomalies

**E-Commerce & Last-Mile Delivery**
- High package volumes make manual inspection impractical
- Automated anomaly detection scales to millions of shipments
- Customer satisfaction depends on arrival condition

**Industrial & Heavy Equipment**
- Oversized cargo requires specialized handling
- Tilt, shock, and orientation monitoring prevents damage to machinery
- Insurance claims require documented handling evidence

### Why Anomaly Detection Matters in Logistics

**Proactive vs. Reactive**
Traditional logistics discovers problems at delivery. Anomaly detection shifts to real-time awareness, enabling intervention while cargo is still in transit.

**Cost Reduction**
- Damaged goods cost the logistics industry over $50 billion annually
- Early detection reduces claim disputes and speeds resolution
- Predictive maintenance of handling equipment prevents breakdowns

**Accountability & Transparency**
- Sensor data creates an immutable record of handling conditions
- Identifies exactly when and where anomalies occurred
- Enables data-driven carrier performance evaluation

**Scalability**
- Machine learning models can process millions of sensor readings per second
- Edge computing reduces bandwidth by filtering normal data locally
- Only anomalies and summaries need to reach central systems

**Regulatory Compliance**
- Industries like pharmaceuticals require chain-of-custody documentation
- Automated anomaly logging satisfies audit requirements
- Reduces manual paperwork and human error

### Target Audience & Intended Users

**Supply Chain & Logistics Professionals**
- Operations managers seeking visibility into cargo handling
- Quality assurance teams monitoring compliance
- Route planners optimizing for cargo safety

**Developers & Engineers**
- IoT/embedded systems developers building sensor networks
- ML engineers working on time-series anomaly detection
- Platform engineers designing distributed monitoring systems

**Researchers & Students**
- Those studying edge computing and mesh networks
- Machine learning practitioners exploring real-world classification problems
- Supply chain researchers modeling logistics networks

**Technology Evaluators**
- Companies assessing cargo monitoring solutions
- Consultants advising on logistics technology investments
- Startups exploring the smart logistics space

---

## What We Are Building

A distributed anomaly detection system that simulates cargo monitoring networks.

## Tech Stack

- [Redis](https://redis.io/) - In-memory message broker for real-time sensor data streaming between nodes
- [PyTorch](https://pytorch.org/) - Deep learning framework for motion classification and anomaly detection models
- [SQLite](https://www.sqlite.org/) - Lightweight database for storing inference results and anomaly events
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - Python GUI library for the real-time visualization dashboard


## Architecture

The project is organized into 4 modules with the database at the center:

```
                    ┌──────────────────┐
                    │  node-simulator  │
                    │     (Team 1)     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
    ┌───────────────│    database      │───────────────┐
    │               │     (Team 3)     │               │
    │               └──────────────────┘               │
    │                        │                         │
    ▼                        ▼                         ▼
┌───┴───┐                                          ┌───┴───┐
│  ml   │◄────────────────────────────────────────►│  ui   │
│(Team 2)                                          │(Team 4)
└───────┘                                          └───────┘
```

### Team 1: Node Simulator (`node-simulator/`)
- Generates simulated sensor data at 50-100 Hz
- Motion generators in `motion_generators/` create realistic patterns for each motion type
- `node_simulator.py` - Manages sensor nodes attached to cargo
- `hub_manager.py` - Network topology of distribution hubs and routes
- `redis_publisher.py` - Publishes to Redis channel `sensor:raw:{node_id}`
- `training_data_generator.py` - Creates labeled datasets for ML training
- `run_simulator.py` - Main entry point

### Team 2: Machine Learning (`ml/`)
- Subscribes to `sensor:raw:*` channels
- Buffers 2-5 second windows, extracts features (RMS, peaks, variance, FFT)
- Classifies motion using PyTorch model
- Detects anomalies via K-means clustering
- Publishes results to `inference:results:{node_id}`

### Team 3: Database (`database/`)
- SQLite with 3 tables: `inference_results`, `nodes`, `anomaly_events`
- Subscribes to `inference:results:*`
- Provides query functions for Team 2 and Team 4

### Team 4: UI (`ui/`)
- Tkinter dashboard with tabs: Network map, Anomalies feed, Analytics charts, Node details

| Directory | Description |
|-----------|-------------|
| [node-simulator](node-simulator/) | Sensor simulation, motion generators, and training data generation |
| [ml](ml/) | Motion classification and anomaly detection models |
| [database](database/) | SQLite storage and query functions for inference results |
| [ui](ui/) | Tkinter dashboard for real-time visualization |
| tests/ | Test suites for all modules |
| data/ | Generated training and simulation data |

---

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
   - Example: Varied movement, jagged to flat, random peaks across all axes (most peaks in X and Y)

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

---

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
python node-simulator/run_simulator.py
python node-simulator/run_simulator.py --nodes 10 --duration 60

# Generate training data
python node-simulator/training_data_generator.py --samples 1000 --output data/training

# Run tests
pytest tests/

# Run specific test module
pytest tests/test-node-simulator/
pytest tests/test-ml/
pytest tests/test-database/
```

## Key Constraints

- Timestamps must increase monotonically
- `motion_class` must be: IDLE, TERRESTRIAL, MARITIME, LIFT, or UNKNOWN
- `anomaly_score` must be in range [0, 1]
- Database queries should respond in < 500ms
- Handle duplicate/out-of-order messages gracefully


