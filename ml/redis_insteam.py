#!/usr/bin/env python3
"""
redis_insteam.py

Redis subscriber for live sensor data ingestion.
"""

import redis
import logging
import json

# ============================================================================
# CONSTANTS
# ============================================================================

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_TIMEOUT = 5
CHANNEL_INTERNAL = "internal_msgs"

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

    def __init__(self, channel="sensor:raw:*"):
        """
        Initialize the Redis subscriber.

        Args:
            channel (str): Redis channel pattern.
        """
        self.channel = channel
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=REDIS_TIMEOUT,
            socket_timeout=REDIS_TIMEOUT
        )
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