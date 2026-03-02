Team 2: Motion Classification & Anomaly Detection

Goal: Process raw sensor data in real-time, classify motion types, and detect anomalies using machine learning.

To Build:

Data Listener - Subscribe to all sensor:raw:* channels, handle multiple nodes
Windowing - Buffer 2-5 second windows of raw data
Feature Extraction - Compute RMS, peaks, variance, FFT features (15-20 dimensions)
Motion Classifier - Use TensorFlow Lite model to classify into 4 motion typesAnomaly DetectorK-means clustering to identify unusual patternsREDIS PublisherPublish classification + anomaly results

REDIS channel inference:results:{node_id} receives messages like:
json{
  "node_id": "node_001",
  "timestamp": 1702656000.123456,
  "window_start": 1702655998.123456,
  "window_end": 1702656000.123456,
  "motion_class": "IDLE",
  "motion_confidence": 0.95,
  "anomaly_flag": false,
  "anomaly_score": 0.12,
  "feature_vector": [0.05, 0.02, 9.81, ...],
  "processing_time_ms": 45
}

Key Constraints:
motion_class must be one of: IDLE, TERRESTRIAL, MARITIME, LIFT, UNKNOWN
anomaly_score must be in [0, 1]
Handle out-of-order messages gracefully

Redis Channel
Channel: sensor:raw:*
Publisher: Node-simulator
Subscriber: ML

Channel: inference:results:{node_id}
Puglisher: ML
