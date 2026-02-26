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

    def insert_node(self, msg) -> bool:
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

            
    def insert_inference_results(self, record: InferenceResults) -> bool:
        pass

    def insert_anomaly_event(self, record: AnomalyEvents) -> bool:
        pass

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
    # Example usage
    manager = TableManager()
    data = load_json(Path("simulator/raw_data.json"))
    
    TableManager().clear_tables()
    # if isinstance(data, list):
    #     success = manager.insert_raw_data(data)
    #     print(f"Inserted {len(data)} records: {success}")
    # else:
    #     print("Invalid JSON format. Expected a list of records.")

if __name__ == "__main__":
    main()