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

from data_pipeline import stream_window_to_features
from train_classifier import MotionClassifier

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

    INACTIVITY_THRESHOLD = 600 # An inactive buffer for 10 minutes is inactive and should be emptied

    def __init__(self, channel="sensor:raw:*", window_size=100, stride=0, classifier=None):
        """
        Initialize the Redis subscriber.

        Args:
            channel (str): Redis channel pattern.
        """
        self.channel = channel
        self.window_size = window_size
        self.stride = stride
        self.classifier = classifier
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
        }
        logger.info(
            f"Inference for node {node_id}: predicted={predicted.item()}, confidence={confidence.item()}, "
            f"latency={latency:.3f}s, window_metadata={window_metadata}"
        )
        # Pass window_metadata to outstream for decoding terrain/anomaly as needed
        return result

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    args = parse_args()
    classifier = MotionClassifier(input_dim=38)  # Adjust input_dim as needed
    classifier.load_state_dict(torch.load(args.model_path))
    classifier.eval()

    subscriber = RedisSubscriber(
        channel="sensor:raw:*",
        window_size=args.window_size,
        stride=args.stride,
        classifier=classifier
    )
    subscriber.listen()
