import json
import time
from datetime import datetime


def getMessages(filename = "raw_data.json"):
    with open(filename, "r") as f:
        return json.load(f)


def _group_by_second(messages):
    if not messages:
        return []

    messages = sorted(messages, key=lambda m: m.get("timestamp", ""))

    groups = []
    current_group = []
    current_second = None

    for msg in messages:
        ts_str = msg.get("timestamp")
        try:
            ts = datetime.fromisoformat(ts_str) if ts_str else None
        except (TypeError, ValueError):
            ts = None

        second_key = ts.replace(microsecond=0) if ts else None

        if current_second is None:
            current_second = second_key
            current_group.append(msg)
            continue

        if second_key == current_second:
            current_group.append(msg)
        else:
            groups.append(current_group)
            current_group = [msg]
            current_second = second_key

    if current_group:
        groups.append(current_group)

    return groups


def publish(rdis, channel_name, sleep_sec=1.0, filename="raw_data.json"):
    messages = getMessages(filename)

    # --- Batching (kept, commented out): publish one batch per second (list of messages per second)
    # groups = _group_by_second(messages)
    # for idx, group in enumerate(groups):
    #     payload = json.dumps(group)
    #     rdis.publish(channel_name, payload)
    #     print(f"Published to channel {channel_name}: message {idx + 1} of {len(groups)}")
    #     if idx != len(groups) - 1:
    #         time.sleep(sleep_sec)
    # ---

    # Current: one message per second (single dict per publish)
    for idx, msg in enumerate(messages):
        payload = json.dumps(msg)
        rdis.publish(channel_name, payload)
        print(f"Published to channel {channel_name}: message {idx + 1} of {len(messages)}")
        if idx != len(messages) - 1:
            time.sleep(sleep_sec)
