import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

pubsub = r.pubsub()
pubsub.subscribe("sensor:raw:node_001")

print("Listening on sensor:raw:node_001")

for msg in pubsub.listen():
    if msg["type"] != "message":
        continue

    # First decode: unwrap outer JSON string
    inner_json_str = json.loads(msg["data"])

    # Second decode: actual message object
    # message = json.loads(inner_json_str)

    print("Received message:", inner_json_str)