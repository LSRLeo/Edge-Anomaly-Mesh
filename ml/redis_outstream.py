"""
redis_outstream.py

Redis publisher for inference-output messages.

Publishes standardized classification results to inference:results:{node_id} channel.

Usage:
    python redis_outstream.py
"""

import redis
import json
import argparse
from datetime import datetime

# ============================================================================
# CONSTANTS
# ============================================================================
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
CHANNEL_PREFIX = "inference:results:"

"""
Inference Output Schema (ml → database → ui):

{
    "m_type": "inference-output",           # string, required
    "m_id": "ml_{seq}",                     # string, required, unique per message
    "event_id": "{node_id}_{timestamp}",    # string, required
    "node_id": "node_{number}",             # string, required
    "timestamp": "YYYY-MM-DDTHH:MM:SS.ffffff", # ISO 8601, required
    "classification": "IDLE|TERRESTRIAL|MARITIME|LIFT|UNKNOWN", # string, required, uppercase
    "confidence": float,                    # required, range [0.0, 1.0]
    "is_anomaly": bool,                     # required
    "anomaly_score": float                  # required, range [0.0, 1.0]
}
"""

# ============================================================================
# STANDARDIZED OUTPUT FORMAT (CLAUDE.md)
# ============================================================================
def build_inference_output(
    m_id: str,
    event_id: str,
    node_id: str,
    timestamp: str,
    classification: str,
    confidence: float,
    is_anomaly: bool,
    anomaly_score: float
) -> dict:
    return {
        "m_type": "inference-output",
        "m_id": m_id,
        "event_id": event_id,
        "node_id": node_id,
        "timestamp": timestamp,
        "classification": classification,
        "confidence": confidence,
        "is_anomaly": is_anomaly,
        "anomaly_score": anomaly_score
    }

# ============================================================================
# REDIS PUBLISHER
# ============================================================================
class InferenceRedisPublisher:
    """
    Publishes standardized inference-output messages to Redis.
    Channel: inference:results:{node_id}
    """
    def __init__(self, host="localhost", port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def publish(self, node_id: str, inference_msg: dict):
        """
        Publishes the inference-output message to the correct Redis channel.
        Args:
            node_id: Node identifier (e.g., 'node_001')
            inference_msg: Dict matching the inference-output schema
        Returns:
            channel: The Redis channel used
        """
        channel = f"inference:results:{node_id}"
        self.redis_client.publish(channel, json.dumps(inference_msg))
        return channel

# ============================================================================
# MAIN (for CLI testing)
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description="Publish inference-output to Redis.")
    parser.add_argument("--node_id", required=True)
    parser.add_argument("--classification", required=True, choices=["IDLE", "TERRESTRIAL", "MARITIME", "LIFT", "UNKNOWN"])
    parser.add_argument("--confidence", type=float, required=True)
    parser.add_argument("--is_anomaly", action="store_true")
    parser.add_argument("--anomaly_score", type=float, default=0.0)
    args = parser.parse_args()

    timestamp = datetime.utcnow().isoformat(timespec="microseconds")
    event_id = f"{args.node_id}_{timestamp}"
    m_id = f"ml_{event_id}"

    msg = build_inference_output(
        m_id=m_id,
        event_id=event_id,
        node_id=args.node_id,
        timestamp=timestamp,
        classification=args.classification,
        confidence=args.confidence,
        is_anomaly=args.is_anomaly,
        anomaly_score=args.anomaly_score
    )

    publisher = InferenceRedisPublisher()
    channel = publisher.publish(args.node_id, msg)
    print(f"Published to {channel}: {msg}")

def publish_inference_result(node_id: str, inference_data: dict):
    """
    Validates, formats, and publishes inference-output in real-time.
    Should be called immediately after inference.
    """
    # Validate schema
    validate_inference_output(inference_data)
    # Publish to Redis
    publisher = InferenceRedisPublisher()
    publisher.publish(node_id, inference_data)

# ============================================================================
# SCHEMA VALIDATION
# ============================================================================
def validate_inference_output(data: dict):
    required_fields = [
        "m_type", "m_id", "event_id", "node_id", "timestamp",
        "classification", "confidence", "is_anomaly", "anomaly_score"
    ]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    if data["m_type"] != "inference-output":
        raise ValueError("m_type must be 'inference-output'")
    if not isinstance(data["confidence"], float):
        raise ValueError("confidence must be a float")
    if not (0.0 <= data["confidence"] <= 1.0):
        raise ValueError("confidence must be in [0.0, 1.0]")
    if not isinstance(data["anomaly_score"], float):
        raise ValueError("anomaly_score must be a float")
    if not (0.0 <= data["anomaly_score"] <= 1.0):
        raise ValueError("anomaly_score must be in [0.0, 1.0]")
    if not isinstance(data["is_anomaly"], bool):
        raise ValueError("is_anomaly must be a bool")
    allowed_classes = {"IDLE", "TERRESTRIAL", "MARITIME", "LIFT", "UNKNOWN"}
    if data["classification"] not in allowed_classes:
        raise ValueError(f"classification must be one of {allowed_classes}")

if __name__ == "__main__":
    main()