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
    print("RawSensorData (full):", raw)

def print_inference(inf):
    if not inf:
        print("No inference result found.")
        return
    print("InferenceResults (full):", inf)

def main():
    print("--- Testing get_nodes() ---")
    print(get_nodes())

    print("\n--- Testing get_node_data_ids() ---")
    print(get_node_data_ids(TEST_NODE_ID))

    print("\n--- Testing get_datum() ---")
    datum = get_datum(TEST_EVENT_ID)
    print("Datum (full):", datum)

    print("\n--- Testing get_recent_raw_data() ---")
    raw = get_recent_raw_data(TEST_NODE_ID)
    print("Recent Raw Data (full):", raw)

    print("\n--- Testing get_recent_inference() ---")
    inf = get_recent_inference(TEST_NODE_ID)
    print("Recent Inference (full):", inf)

if __name__ == "__main__":
    main()
