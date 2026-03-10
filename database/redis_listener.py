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
RESPONSE_CHANNELS_MAP = {
    "ui:query": "ui:responses",
} #CAN ADD MORE CHANNELS LATER



def send_message(channel:str, message: Dict[str, Any]) -> None:
    # Implement the logic to send a message, use responding_to field to determine the channel to publish to
    #TODO: used to send response to UI channels, can expand to other channels as needed
    responding_to = message.get("responding_to")
    if responding_to:
        
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.publish(channel, json.dumps(message))


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
            incoming_channel = msg["channel"]
            channel = RESPONSE_CHANNELS_MAP.get(incoming_channel)
            data = json.loads(msg["data"])
            
            if isinstance(data, list):
                logging.info(f"Received list of messages, processing each one...")
                for item in data:
                    item_response = manager.process_message(item)
                    if item_response:
                        logging.info(f"Processed message, response: {item_response}")
                        #send response to correct channel
                        if channel:
                            r.publish(channel, json.dumps(item_response))
                            logging.info(f"Published response to {channel}")


            else:
                logging.info(f"Received on {msg['channel']}: {data}")
                response = manager.process_message(data)
                if response:
                    #send response to correct channel
                    logging.info(f"Processed message, response: {response}")
                    channel = RESPONSE_CHANNELS_MAP.get(incoming_channel)
                    if channel:
                        r.publish(channel, json.dumps(response))
                        logging.info(f"Published response to {channel}")
                
                    
            # If this is a query request, publish response to UI channels
        except Exception as e:
            logging.error(f"Error processing message: {e}")

if __name__ == "__main__":
    main()