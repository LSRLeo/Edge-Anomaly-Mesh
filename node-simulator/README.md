Team 1: Data Generation

Goal: Generate realistic, diverse accelerometer data that siimulates cargo desnors moving through a distirbution network.

To Build:
Motion Simulators - 4 separate classes, each generates realistic motion patterns
Idle Pattern - Cargo sitting still (only gravity: 9.81 m/s² on Z-axis)Terrestrial PatternTruck/train movement (periodic bumps, 2-5 Hz vibration, mostly X/Y)Maritime PatternShip in waves (chaotic 3D motion, unpredictable spikes)Lift PatternForklift raising/lowering (clear Z-axis trapezoid over 8-10 sec)
Anomaly Injection - Methods to inject impacts, sensor failures, calibration drift, noise
Node Simulator - Manages 10-100 concurrent nodes, transitions between states
REDIS Publisher - Publishes raw data to message queue at 50-100 Hz

REDIS channel sensor:raw:{node_id} receives messages like:
json{
  "node_id": "node_001",
  "timestamp": 1702656000.123456,
  "accel": {"x": 0.05, "y": -0.02, "z": 9.81},
  "gyro": {"x": 0.001, "y": 0.002, "z": 0.0},
  "location": "hub_A",
  "motion_state_ground_truth": "idle"
}

Key Constraint: Timestamps must increase monotonically; allow Team 2 to handle late arrivals

Shouldn't team1 create simulation data as well as pre-trained data?

Redis Channel
Channel: sensor:raw:{node_id}
Publisher: Node-simulator
Subscriber: ML & Databases



