#!/usr/bin/env python3
"""
redis_insteam.py

Redis subscriber for live sensor data ingestion.
"""

import logging

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