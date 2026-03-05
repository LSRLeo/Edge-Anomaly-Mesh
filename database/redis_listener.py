import redis
import json
from db_message_manager import DBMessageManager

REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Channels to subscribe to
# ================================================
# ADD MORE BASED ON UI TEAM AND OTHER SPECIFICATIONS
# ================================================
SUBSCRIBE_CHANNELS = [
    "sensor:raw:*",
    "inference:results:*",
    "ui:query"
]

def main():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.psubscribe(*SUBSCRIBE_CHANNELS)

    manager = DBMessageManager()

    print("Redis listener started. Waiting for messages...")
    for msg in pubsub.listen():
        if msg["type"] != "pmessage":
            continue
        try:
            data = json.loads(msg["data"])
            print(f"Received on {msg['channel']}: {data}")
            response = manager.process_message(data)
            # If this is a query request, publish response to UI channels
            if data.get("m_type", "").startswith("get-"):
                node_id = data.get("node_id", "all")
                channel = f"ui:responses"
                r.publish(channel, json.dumps(response))
                print(f"Published response to {channel}")
        except Exception as e:
            print(f"Error processing message: {e}")

if __name__ == "__main__":
    main()