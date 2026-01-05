# edge-anomaly-mesh

## Project Overview

Edge-anomaly-mesh is a hybrid mesh network simulation system that detects anomalies in motion data from nodes traveling between network hubs.

In the real world, packages/cargo move between distribution centers (hubs) while sensors on them collect accelerometer data. This project simulates that scenario using machine learning to:

- Classify motion types (idle, terrestrial, maritime, lift)
- Detect anomalies (unexpected patterns that indicate problems)
- Aggregate and visualize the data across the entire network

This is a simulation-based project.

---

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

## Anomaly Detection

Anything that breaks the expected pattern:

- Sudden impacts/drops
- Sensor failures (loss of gravity signal)
- Unexpected high-frequency vibration
- Calibration drift over time
