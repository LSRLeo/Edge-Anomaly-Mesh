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
    "ui:query"
]
RESPONSE_CHANNELS_MAP = {
    "ui:query": "ui:responses",
} #CAN ADD MORE CHANNELS LATER
#TODO map m-types to channels as needed or based on responding_to field in message
#TODO validate response messages before sending to UI channels

def publish_response(channel:str, message: Dict[str, Any]) -> None:
    #used to send response to UI channels, can expand to other channels as needed
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.publish(channel, json.dumps(message))
    except Exception as e:
        logging.error(f"Error sending message to {channel}: {e}")

def process_data(manager: DBMessageManager, channel:str, data: Dict[str, Any]):
    try:
        response = manager.process_message(data)
        
        if response:
            #send response to correct channel
            logging.info(f"Processed message, response: {response}")
                
            if channel:
                publish_response(channel, response)
                logging.info(f"Published response to {channel}")

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        return None

def main():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.psubscribe(SUBSCRIBE_CHANNELS)
    manager = DBMessageManager()

    logging.info("Redis listener started. Waiting for messages...")
    for msg in pubsub.listen():
        if msg["type"] != "pmessage":
            continue
        try:
            incoming_channel = msg["channel"]
            channel = RESPONSE_CHANNELS_MAP.get(incoming_channel)
            data = json.loads(msg["data"])
            logging.info(f"Received message on channel {incoming_channel}")

            if isinstance(data, list):
                logging.info(f"Received list of messages, processing each one...")
                for item in data:
                    process_data(manager, channel, item)

            else:
                process_data(manager, channel, data)
                    
            # If this is a query request, publish response to UI channels
        except Exception as e:
            logging.error(f"Error processing message: {e}")

if __name__ == "__main__":
    main()