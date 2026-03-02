#!/usr/bin/env python3
"""
redis_insteam.py

Redis subscriber for live sensor data ingestion.

Listens to the sensor:raw:* channel and logs incoming messages.

Usage:
    python redis_insteam.py
"""

import redis
import logging
import json
import argparse
import torch
import time
from datetime import datetime

from data_pipeline import stream_window_to_features
from feature_extraction import normalize_features
from train_classifier import MotionClassifier
from redis_outstream import build_inference_output, InferenceRedisPublisher

# ============================================================================
# CONSTANTS
# ============================================================================

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_TIMEOUT = 5
CHANNEL_INTERNAL = "internal_msgs"

# ============================================================================
# ARGPARSE
# ============================================================================

def parse_args():
    parser = argparse.ArgumentParser(description="Redis subscriber for live sensor data ingestion")
    parser.add_argument('--window-size', type=int, default=100, help='Sliding window size')
    parser.add_argument('--stride', type=int, default=0, help='Stride for overlapping windows')
    parser.add_argument('--model-path', type=str, default='models/motion_classifier.pt', help='Path to trained model')
    return parser.parse_args()

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================================
# REDIS SUBSCRIBER CLASS
# ============================================================================

class RedisSubscriber:
    """
    Redis subscriber for live data ingestion.

    Listens to a Redis channel pattern and processes incoming messages.

    Args:
        channel (str): Redis channel pattern to subscribe to.

    Attributes:
        channel (str): Channel pattern.
        redis_client (redis.Redis): Redis client instance.
    """

    def __init__(self, channel="sensor:raw:*", window_size=100, stride=0, classifier=None, scaler=None):
        """
        Initialize the Redis subscriber.

        Args:
            channel (str): Redis channel pattern.
            scaler: (mean, std) tuple from training normalization, used to
                    normalize features before inference.
        """
        self.channel = channel
        self.window_size = window_size
        self.stride = stride
        self.classifier = classifier
        self.scaler = scaler
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=REDIS_TIMEOUT,
            socket_timeout=REDIS_TIMEOUT
        )
        self.node_states = {}  # Maps node_id to buffer and state
        self.seen_seqs = {}    # Maps node_id to set of seen seq numbers
        self.publisher = InferenceRedisPublisher(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        try:
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        except redis.ConnectionError:
            logger.error("Failed to connect to Redis")
            raise

    def listen(self):
        """
        Start listening to the Redis channel.

        Processes messages as they arrive.
        """
        pubsub = self.redis_client.pubsub()
        pubsub.psubscribe(self.channel)
        logger.info(f"Subscribed to channel pattern: {self.channel}")

        for message in pubsub.listen():
            if message['type'] == 'pmessage':
                self.process_data(message['data'])

    def insert_event_in_order(self, buffer, event):
        seq = event.get("seq")
        if seq is None:
            buffer.append(event)
            return
        # Skip duplicates (already handled by seen_seqs, but double check)
        if any(e.get("seq") == seq for e in buffer):
            return
        # Insert in order
        for i, existing in enumerate(buffer):
            if existing.get("seq", -1) > seq:
                buffer.insert(i, event)
                return
        buffer.append(event)

    def process_data(self, message):
        """
        Process incoming messages, handle bytes or str.

        Args:
            message (str or bytes): The message payload.
        """
        try:
            # Decode bytes if needed
            if isinstance(message, bytes):
                message = message.decode('utf-8')

            data = json.loads(message)

            node_id = data.get('node_id')
            seq = data.get('seq')
            if not node_id:
                logger.warning("Missing node_id in message")
                return

            # Duplicate filtering
            if node_id not in self.seen_seqs:
                self.seen_seqs[node_id] = set()
            if seq in self.seen_seqs[node_id]:
                logger.info(f"Duplicate packet detected for node {node_id} seq {seq}, skipping.")
                return
            self.seen_seqs[node_id].add(seq)

            # Add receipt time for latency monitoring
            receipt_time = time.time()
            data['receipt_time'] = receipt_time

            # Initialize buffer for new node_id
            now = time.time()
            if node_id not in self.node_states:
                self.node_states[node_id] = {
                    'buffer': [],  # Use a list
                    'stride_count': 0,
                    'last_seq': -1,
                    'last_active': now
                }
            
            # Update last activity time for node
            self.node_states[node_id]['last_active'] = now

            # Append new sample to node's buffer
            node_state = self.node_states[node_id]
            self.insert_event_in_order(node_state['buffer'], data)
            node_state['stride_count'] += 1

            logger.info(f"Received message for node {node_id}: {data}")

            # Trigger inference when window and stride conditions are met
            if len(node_state['buffer']) >= self.window_size and node_state['stride_count'] >= self.stride:
                window = node_state['buffer'][:self.window_size]
                # Extract metadata for the window and reconstruct ground truth
                terrain_map = {"IDLE": 0, "TERRESTRIAL": 1, "TRANSIT": 1, "MARITIME": 2, "LIFT": 3}
                window_metadata = []
                for event in window:
                    meta = event.get("meta", {})
                    terrain_str = meta.get("sim_mode") or meta.get("mode") or event.get("mode")
                    anomaly = meta.get("anomaly", False) or meta.get("has_anomaly", False) or event.get("anomaly", False)
                    terrain_idx = terrain_map.get(terrain_str.upper()) if terrain_str else None
                    ground_truth = terrain_idx + (4 if anomaly else 0) if terrain_idx is not None else None
                    window_metadata.append({
                        "node_id": event.get("node_id"),
                        "seq": event.get("seq"),
                        "timestamp": event.get("timestamp"),
                        "terrain_type": terrain_str,
                        "is_anomaly": anomaly,
                        "ground_truth": ground_truth
                    })
                self.trigger_inference(node_id, window, window_metadata)
                node_state['buffer'] = node_state['buffer'][self.stride:]
                node_state['stride_count'] = 0
            
            # Inactivity cleanup
            self.cleanup_inactive_nodes()


        except json.JSONDecodeError:
            logger.warning(f"Received invalid JSON: {message}")

    def cleanup_inactive_nodes(self):
        """
        Remove nodes from node_states and seen_seqs if inactive for threshold.
        """

        now = time.time()
        inactive = [
            node_id for node_id, state in self.node_states.items()
            if now - state.get('last_active', now) > self.INACTIVITY_THRESHOLD
        ]
        for node_id in inactive:
            logger.info(f"Cleaning up inactive node: {node_id}")
            self.node_states.pop(node_id, None)
            self.seen_seqs.pop(node_id, None)

    def trigger_inference(self, node_id, window, window_metadata):
        """
        Extract features from the buffer and run classifier inference.
        Also calculates latency between message receipt and inference trigger.
        """
        # Latency monitoring: calculate time difference from earliest receipt_time
        receipt_times = [event.get('receipt_time', None) for event in window]
        earliest_receipt_time = min([t for t in receipt_times if t is not None], default=None)
        latency = None
        if earliest_receipt_time is not None:
            latency = time.time() - earliest_receipt_time

        features = stream_window_to_features(window, self.window_size, sample_rate=50)
        features_tensor = torch.FloatTensor(features)
        predicted, confidence = self.classifier.predict(features_tensor)
        result = {
            "node_id": node_id,
            "predicted": predicted.item(),
            "confidence": confidence.item(),
            "window_metadata": window_metadata,
            "latency": latency
        Extract features from the window and run classifier inference.

        Computes:
          - terrain_confidence: P(terrain) + P(terrain_anomaly), i.e. the total
            probability mass the model assigns to the predicted terrain type
            regardless of anomaly status.
          - anomaly_score: sum of all anomaly-class probabilities (classes 4-7),
            used as the continuous anomaly score.

        Publishes a standardized inference-output message to Redis.
        """
        TERRAIN_NAMES = ['IDLE', 'TERRESTRIAL', 'MARITIME', 'LIFT']

        # Use the window events passed in (not the internal buffer)
        features = stream_window_to_features(window, self.window_size, sample_rate=50)
        if self.scaler is not None:
            features, _ = normalize_features(features, scaler=self.scaler)
        features_tensor = torch.FloatTensor(features)  # shape: (1, n_features)

        # predict() returns (predicted_class_0-7, max_softmax_prob, full_prob_tensor)
        predicted, _, probabilities = self.classifier.predict(features_tensor)

        pred_class = predicted.item()
        terrain_idx = pred_class % 4
        is_anomaly = bool(pred_class >= 4)
        terrain_name = TERRAIN_NAMES[terrain_idx]

        # Per-class confidence: softmax probability for each of the 8 classes (sums to 1.0)
        CLASS_NAMES = ['IDLE', 'TERRESTRIAL', 'MARITIME', 'LIFT',
                       'IDLE_ANOM', 'TERRESTRIAL_ANOM', 'MARITIME_ANOM', 'LIFT_ANOM']
        confidence = {
            name: round(float(probabilities[0, i].item()), 6)
            for i, name in enumerate(CLASS_NAMES)
        }

        # Anomaly score: total probability assigned to any anomaly class (4-7)
        anomaly_score = round(float(probabilities[0, 4:].sum().item()), 6)

        # Build standardized inference-output message
        last_meta = window_metadata[-1] if window_metadata else {}
        timestamp = last_meta.get("timestamp") or datetime.utcnow().isoformat(timespec="microseconds")
        event_id = f"{node_id}_{timestamp}"
        m_id = f"ml_{event_id}"

        result = build_inference_output(
            m_id=m_id,
            event_id=event_id,
            node_id=node_id,
            timestamp=timestamp,
            classification=terrain_name,
            confidence=confidence,
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
        )

        logger.info(
            f"Inference for node {node_id}: predicted={predicted.item()}, confidence={confidence.item()}, "
            f"latency={latency:.3f}s, window_metadata={window_metadata}"
        )

        self.publisher.publish(node_id, result)
        return result

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    args = parse_args()
    checkpoint = torch.load(args.model_path, weights_only=False)
    config = checkpoint['model_config']
    classifier = MotionClassifier(
        input_dim=config['input_dim'],
        hidden_dims=tuple(config['hidden_dims']),
        dropout=config['dropout'],
        num_classes=config['num_classes'],
    )
    classifier.load_state_dict(checkpoint['model_state_dict'])
    classifier.eval()

    subscriber = RedisSubscriber(
        channel="sensor:raw:*",
        window_size=args.window_size,
        stride=args.stride,
        classifier=classifier,
        scaler=checkpoint['scaler'],
    )
    subscriber.listen()
