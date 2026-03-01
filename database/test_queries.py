"""
test_queries.py

Test script for queries.py functions using the example database.
"""
from queries import (
    get_nodes,
    get_node_data_ids,
    get_datum,
    get_recent_inference,
    get_recent_raw_data
)

# Example node_id and event_id for testing (adjust as needed)
TEST_NODE_ID = "node_001"
TEST_EVENT_ID = "node_001_1234567890.0"  # Replace with a real event_id in your DB

def print_raw_sensor_data(raw):
    if not raw:
        print("No raw sensor data found.")
        return
    print(f"RawSensorData: node_id={raw.node_id}, timestamp={raw.timestamp}, seq={raw.seq}")

def print_inference(inf):
    if not inf:
        print("No inference result found.")
        return
    print(f"InferenceResults: node_id={inf.node_id}, window=({inf.window_start}, {inf.window_end}), class={inf.motion_class}, confidence={inf.confidence}")

def main():
    print("--- Testing get_nodes() ---")
    print(get_nodes())

    print("\n--- Testing get_node_data_ids() ---")
    print(get_node_data_ids(TEST_NODE_ID))

    print("\n--- Testing get_datum() ---")
    datum = get_datum(TEST_EVENT_ID)
    if datum:
        print_raw_sensor_data(datum['raw'])
        print_inference(datum['inference'])
    else:
        print("Datum not found for event_id:", TEST_EVENT_ID)

    print("\n--- Testing get_most_recent_raw_data() ---")
    raw = get_recent_raw_data(TEST_NODE_ID)
    print_raw_sensor_data(raw)

    print("\n--- Testing get_most_recent_inference() ---")
    inf = get_recent_inference(TEST_NODE_ID)
    print_inference(inf)

if __name__ == "__main__":
    main()
