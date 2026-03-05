import json
from datetime import datetime

from pathlib import Path
from sqlalchemy.orm import Session
from schema import engine, RawSensorData, Node, InferenceResults, AnomalyEvents



class TableManager:
    """
    Class to manage the inference results database.
    """

    def __init__(self):
        self.session = Session(engine)

    def insert_raw_data(self, messages: list[dict]) -> bool:
        for msg in messages:
            record = RawSensorData(
                node_id=msg["node_id"],
                timestamp=self.iso_to_unix_timestamp(msg["timestamp"]),
                seq=msg["seq"],
                accel_x=msg["accel_mss"]["x"],
                accel_y=msg["accel_mss"]["y"],
                accel_z=msg["accel_mss"]["z"],
                gyro_x=msg["gyro_rads"]["x"],
                gyro_y=msg["gyro_rads"]["y"],
                gyro_z=msg["gyro_rads"]["z"],
                gps_lat=msg["gps"]["lat_deg"],
                gps_lon=msg["gps"]["lon_deg"],
                gps_altitude_m=msg["gps"]["altitude_m"]
            )
            self.session.add(record)
            self.insert_node(msg)
        try:
            self.session.commit()
            self.session.close()
            return True
        except Exception as e:
            self.session.rollback()
            self.session.close()
            print(f"Error inserting raw data: {e}")
            return False


    def insert_node(self, msg):
        if not self.session.query(Node).filter_by(node_id=msg["node_id"]).first():
            record = Node(
                node_id=msg["node_id"],
                status='active',
                first_seen=self.iso_to_unix_timestamp(msg["timestamp"]),
                last_seen=self.iso_to_unix_timestamp(msg["timestamp"]),
                location_lat=msg["gps"]["lat_deg"],
                location_lon=msg["gps"]["lon_deg"],
                location_altitude_m=msg["gps"]["altitude_m"]
            )
            self.session.add(record)

        else:
            node = self.session.query(Node).filter_by(node_id=msg["node_id"]).first()
            node.last_seen = self.iso_to_unix_timestamp(msg["timestamp"])
            node.location_lat = msg["gps"]["lat_deg"]
            node.location_lon = msg["gps"]["lon_deg"]
            node.location_altitude_m = msg["gps"]["altitude_m"]
            self.session.add(node)
        return

            
    def insert_inference_results(self, messages: list[dict]) -> bool:
        for msg in messages:
            record = InferenceResults(
                node_id=msg["node_id"],
                timestamp=self.iso_to_unix_timestamp(msg["timestamp"]),
                window_start=self.iso_to_unix_timestamp(msg["window"]["start"]),
                window_end=self.iso_to_unix_timestamp(msg["window"]["end"]),
                window_samples=msg["window"]["samples"],
                location_state=msg["location_state"],
                motion_class=msg["motion_class"],
                confidence=msg["confidence"],
                anomaly_detected=msg["anomaly"]["detected"],
                anomaly_score=msg["anomaly"]["score"],
                anomaly_type=msg["anomaly"]["type"],
                nearest_hub_id=msg["nearest_hub"]["hub_id"],
                nearest_hub_distance=msg["nearest_hub"]["distance_m"],
                feature_vector=json.dumps(msg["features"]),
                processing_time_ms=msg["processing_time_ms"]
            )
            self.session.add(record)
            self.session.flush()  # Flush to get the record ID for anomaly event insertion
            if msg["anomaly"]["detected"]:
                self.insert_anomaly_event(record)
        try:
            self.session.commit()
            self.session.close()
            return True
        except Exception as e:
            self.session.rollback()
            self.session.close()
            print(f"Error inserting inference results: {e}")
            return False


    def insert_anomaly_event(self, inference_record: InferenceResults) -> bool:
        anomaly_record = AnomalyEvents(
            inference_id=inference_record.id,
            node_id=inference_record.node_id,
            start_timestamp=inference_record.window_start,
            end_timestamp=inference_record.window_end,
            severity='CRITICAL' if inference_record.anomaly_score >= 0.75 else 'HIGH' if inference_record.anomaly_score >= 0.5 else 'MEDIUM' if inference_record.anomaly_score >= 0.25 else 'LOW',
            description=f"Anomaly detected with score {inference_record.anomaly_score} and type {inference_record.anomaly_type}",
        )
        self.session.add(anomaly_record)
        return
    

    def iso_to_unix_timestamp(self, iso_str: str) -> int:
        dt = datetime.fromisoformat(iso_str)
        return int(dt.timestamp())
    

    def clear_tables(self):
        self.session.query(RawSensorData).delete()
        self.session.query(Node).delete()
        self.session.query(InferenceResults).delete()
        self.session.query(AnomalyEvents).delete()
        self.session.commit()

def load_json(file_path: Path):
    """
    Load raw JSON file.
    Supports:
    - single JSON object
    - list of JSON objects
    """
    with open(file_path, "r") as f:
        data = json.load(f)

    if isinstance(data, dict):
        print("Loaded single JSON object")
        return [data]
    
    return data
    
def main():
    # Example usage, uncomment chunk "if isinstance(raw_data)...", change raw_data filepath
    manager = TableManager()
    raw_data = load_json(Path("test_data/raw-data-001.json"))
    inference_data = load_json(Path("data/examples/inference_results/example_inference_results.json"))
    
    TableManager().clear_tables()
    # if isinstance(raw_data, list):
    #     success = manager.insert_raw_data(raw_data)
    #     print(f"Inserted {len(raw_data)} records: {success}")
    # else:
    #     print("Invalid JSON format. Expected a list of records.")
    
    # if isinstance(inference_data, list):
    #     success = manager.insert_inference_results(inference_data)
    #     print(f"Inserted {len(inference_data)} inference records: {success}")
    # else:
    #     print("Invalid JSON format. Expected a list of records.")

if __name__ == "__main__":
    main()