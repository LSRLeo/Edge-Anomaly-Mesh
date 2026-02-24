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
from collections import deque
import torch

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
            if not node_id:
                logger.warning("Missing node_id in message")
                return

            # Initialize buffer for new node_id
            if node_id not in self.node_states:
                self.node_states[node_id] = {
                    'buffer': deque(),
                    'stride_count': 0,
                    'last_seq': -1
                }

            # Append new sample to node's buffer
            node_state = self.node_states[node_id]
            node_state['buffer'].append(data)
            node_state['stride_count'] += 1

            logger.info(f"Received message for node {node_id}: {data}")

            # Trigger inference when window and stride conditions are met
            if len(node_state['buffer']) >= self.window_size and node_state['stride_count'] >= self.stride:
                self.trigger_inference(node_id)
                for _ in range(self.stride):
                    node_state['buffer'].popleft()
                node_state['stride_count'] = 0

        except json.JSONDecodeError:
            logger.warning(f"Received invalid JSON: {message}")

    def trigger_inference(self, node_id):
        """
        Extract features from the buffer and run classifier inference.
        """
        buffer = list(self.node_states[node_id]['buffer'])
        features = stream_window_to_features(buffer, self.window_size, sample_rate=50)
        features_tensor = torch.FloatTensor(features)
        predicted, confidence = self.classifier.predict(features_tensor)
        logger.info(f"Inference for node {node_id}: predicted={predicted.item()}, confidence={confidence.item()}")

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
