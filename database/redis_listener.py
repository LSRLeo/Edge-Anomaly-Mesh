import redis
import json
from db_message_manager import DBMessageManager
from db_message import Message
import logging
from typing import Dict, Any, Optional, List
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Channels to subscribe to
# ================================================
# ADD MORE BASED ON UI TEAM AND OTHER SPECIFICATIONS
# ================================================
SUBSCRIBE_CHANNELS = [
    "sensor:raw:*",
    "inference:results:*",
    "ui:query:*" # placeholder
]

def send_message(message: dict) -> None:
    # Implement the logic to send a message
    pass

def validate_response(response: Dict[str, Any]) -> bool:
    # Implement the logic to validate a response
    return True

def main():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.psubscribe(*SUBSCRIBE_CHANNELS)

    manager = DBMessageManager()

    logging.info("Redis listener started. Waiting for messages...")
    for msg in pubsub.listen():
        if msg["type"] != "pmessage":
            continue
        try:
            data = json.loads(msg["data"])
            logging.info(f"Received on {msg['channel']}: {data}")
            if isinstance(data, list):
                logging.info(f"Received list of messages, processing each one...")
                for item in data:
                    item_response = manager.process_message(item)
                    logging.info(f"Processed message: {item_response}")
            else:
                response = manager.process_message(data)
                logging.info(f"Processed message: {response}")
            # If this is a query request, publish response to UI channels
            if data.get("m_type", "").startswith("get-"):
                node_id = data.get("node_id", "all")
                # Choose the correct channel based on query type
                if "anomaly" in data.get("m_type", ""):
                    channel = f"dashboard:anomalies:{node_id}"
                else:
                    channel = f"dashboard:updates:{node_id}"
                r.publish(channel, json.dumps(response))
                logging.info(f"Published response to {channel}")
        except Exception as e:
            print(f"Error processing message: {e}")

if __name__ == "__main__":
    main()