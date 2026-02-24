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
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB):
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def publish(self, node_id: str, inference_msg: dict):
        channel = f"{CHANNEL_PREFIX}{node_id}"
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

if __name__ == "__main__":
    main()