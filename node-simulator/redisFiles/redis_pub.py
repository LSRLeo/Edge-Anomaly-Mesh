import json

def getMessages(filename="raw_data.json"):
    with open(filename, "r") as f:
        return json.load(f)

def publish(rdis, channel_name):
    messages = getMessages()
    rdis.publish(channel_name, messages)