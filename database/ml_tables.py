"""
inference_results_table.py

Creates the inference_results table using SQLAlchemy ORM.

Responsibilities:
- Define the schema for the inference_results table, including all necessary fields and constraints.
- Ensure that the table can store all relevant information about inference results, such as node ID,
timestamps, location state, motion class, confidence scores, anomaly detection results, nearest hub information, feature vectors, processing time, and ingestion time.
- Implement constraints to maintain data integrity, such as ensuring confidence scores are between 0 and 1, and that motion classes are limited to predefined categories.
"""
# Standard library imports
import json
from pathlib import Path
from datetime import datetime

#third party imports
import pysqlite3
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import (
    ForeignKeyConstraint,
    create_engine, 
    Column, 
    Integer, 
    String, 
    Float, 
    CheckConstraint, 
    Boolean, 
    UniqueConstraint
)

# setup
Base = declarative_base()
INFERENCE_DB_PATH = 'inference_results.db'
ANOMALY_DB_PATH = 'anomaly_events.db'

# SQLAlchemy ORM model for the inference_results table
class inference_results(Base):
    """
    SQLAlchemy ORM model for the inference_results table.
    """
    __tablename__ = 'inference_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String, nullable=False)
    timestamp = Column(Float, nullable=False)
    window_start = Column(Float, nullable=False)
    window_end = Column(Float, nullable=False)
    window_samples = Column(Integer, nullable=False)

    location_state = Column(String, nullable=False)
    motion_class = Column(String, CheckConstraint("motion_class IN ('IDLE','TERRESTRIAL','MARITIME','LIFT','UNKNOWN')"), nullable=False)
    confidence = Column(Float, CheckConstraint("confidence >= 0.0 AND confidence <= 1.0"), nullable=False)
    anomaly_detected = Column(Boolean, nullable=False)
    anomaly_score = Column(Float, CheckConstraint("anomaly_score >= 0.0 AND anomaly_score <= 1.0"), nullable=False)
    anomaly_type = Column(String, nullable=True)  # Optional field for anomaly type

    nearest_hub_id = Column(String, nullable=False)
    nearest_hub_distance = Column(Float, nullable=False)
    feature_vector = Column(String, nullable=False)  # Store as JSON string

    processing_time_ms = Column(Integer, nullable=False)
    ingested_at = Column(Float, default=lambda: datetime.utcnow().timestamp(), nullable=False)
    __table_args__ = (UniqueConstraint('node_id', 'window_start', 'window_end', name='uq_node_window'),)  # Ensure no duplicate entries for the same node and time window

class anomaly_events(Base):
    """
    SQLAlchemy ORM model for the anomaly_events table
    """
    __tablename__ = 'anomaly_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String, nullable=False)
    start_timestamp = Column(Float, nullable=False)
    end_timestamp = Column(Float)
    severity = Column(String, CheckConstraint("severity IN ('LOW','MEDIUM','HIGH', 'CRITICAL')"))
    description = Column(String)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String)
    acknowledged_at = Column(Float)

    #modify when we can link this table to the nodes table via a foreign key constraint on node_id
    #__table_args__ = (ForeignKeyConstraint(['node_id'], ['nodes.node_id'], name='fk_anomaly_node'),)

class InferenceResultsManager:
    """
    Class to manage the inference results database.
    """

    def __init__(self, db_path=INFERENCE_DB_PATH):
        abs_db_path = Path(db_path).resolve()
        print(f"[InferenceResultsManager] Using database at: {abs_db_path}")
        self.engine = create_engine(f'sqlite+pysqlite:///{abs_db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def insert_inference_result(self, record: inference_results) -> bool:
        """
        Inserts a new inference result into the database.
        record: An instance of the inference_results ORM model.
        return True if insertion was successful, False otherwise.
        """
        session = self.Session()
        try:
            session.add(record)
            session.commit()
            if record.anomaly_detected:
                ingest_anomaly_event(record)
            return True
        except Exception as e:
            session.rollback()
            print(f"Error inserting record: {e}")
            return False
        finally:   
            session.close()

    def get_latest_inference_result(self, node_id: str) -> dict:
        """
        Retrieves the latest inference result for a given node_id.
        node_id: The ID of the node to query.
        return The latest inference result record for the specified node_id, or None if not found.
        """
        session = self.Session()
        try:
            result = session.query(inference_results).filter_by(node_id=node_id).order_by(inference_results.timestamp.desc()).first()
            return result.__dict__ if result else None
        except Exception as e:
            print(f"Error retrieving record: {e}")
            return None
        finally:
            session.close()
        
    def get_inferences_by_timerange(self, start_time: float, end_time: float, node_id=None) -> list[dict]:
        """
        Retrieves inference results for a given node_id within a specified time range.
        start_time: The start of the time range (inclusive).
        end_time: The end of the time range (inclusive).
        node_id: The ID of the node to query (optional, if None retrieves for all nodes).
        return A list of inference result records that match the criteria.
        """
        session = self.Session()
        try:
            query = session.query(inference_results).filter(inference_results.timestamp >= start_time, inference_results.timestamp <= end_time)
            if node_id:
                query = query.filter_by(node_id=node_id)
            results = query.order_by(inference_results.timestamp.desc()).all()
            return [result.__dict__ for result in results]
        except Exception as e:
            print(f"Error retrieving records: {e}")
            return []
        finally:
            session.close()
    
class AnomalyEventsManager:
    """
    Class to manage the anomaly events database.
    """

    def __init__(self, db_path=ANOMALY_DB_PATH):
        abs_db_path = Path(db_path).resolve()
        print(f"[AnomalyEventsManager] Using database at: {abs_db_path}")
        self.engine = create_engine(f'sqlite+pysqlite:///{abs_db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def insert_anomaly_event(self, record: anomaly_events) -> bool:
        """
        Inserts a new anomaly event into the database.
        record: An instance of the anomaly_events ORM model.
        return True if insertion was successful, False otherwise.
        """
        session = self.Session()
        try:
            session.add(record)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error inserting anomaly event: {e}")
            return False
        finally:   
            session.close()
    
    def get_anomaly_events(self, node_id=None, acknowledged=None) -> list[dict]:
        """
        Retrieves anomaly events based on specified criteria.
        node_id: The ID of the node to query (optional, if None retrieves for all nodes).
        acknowledged: Filter by acknowledgment status (optional, if None retrieves all).
        return A list of anomaly event records that match the criteria.
        """
        session = self.Session()
        try:
            query = session.query(anomaly_events)
            if node_id:
                query = query.filter_by(node_id=node_id)
            if acknowledged is not None:
                query = query.filter_by(acknowledged=acknowledged)
            results = query.order_by(anomaly_events.start_timestamp.desc()).all()
            return [result.__dict__ for result in results]
        except Exception as e:
            print(f"Error retrieving anomaly events: {e}")
            return []
        finally:
            session.close()
    
    def acknowledge_anomaly(self, event_id: int, acknowledged_by: str) -> bool:
        """
        Acknowledges an anomaly event by updating its status and acknowledgment details.
        event_id: The ID of the anomaly event to acknowledge.
        acknowledged_by: The name of the person acknowledging the event.
        return True if the acknowledgment was successful, False otherwise.
        """
        session = self.Session()
        try:
            event = session.query(anomaly_events).filter_by(id=event_id).first()
            if not event:
                print(f"Anomaly event with ID {event_id} not found.")
                return False
            event.acknowledged = True
            event.acknowledged_by = acknowledged_by
            event.acknowledged_at = datetime.utcnow().timestamp()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error acknowledging anomaly event: {e}")
            return False
        finally:
            session.close()

def iso_to_unix_timestamp(iso_str: str) -> float:
    """
    Converts an ISO 8601 formatted string to a UNIX timestamp.
    iso_str: The ISO 8601 formatted string to convert.
    return The corresponding UNIX timestamp as a float, or None if conversion fails.
    """
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.timestamp()
    except ValueError as e:
        print(f"Error converting ISO string to timestamp: {e}")
        return None

def parse_inference_message(msg: dict) -> inference_results:
    """
    Parses an incoming inference message and converts it into an inference_results ORM object.
    msg: The incoming message as a dictionary.
    return An instance of the inference_results ORM model populated with data from the message, or None if parsing fails.
    """

    return inference_results(
        node_id=msg['node_id'],
        timestamp=iso_to_unix_timestamp(msg['timestamp']),
        window_start=iso_to_unix_timestamp(msg['window']['start']),
        window_end=iso_to_unix_timestamp(msg['window']['end']),
        window_samples=msg['window']['samples'],
        location_state=msg['location_state'],
        motion_class=msg['motion_class'],
        confidence=msg['confidence'],
        anomaly_detected=msg['anomaly']['detected'],
        anomaly_score=msg['anomaly']['score'],
        anomaly_type=msg['anomaly'].get('type'),  # Optional field
        nearest_hub_id=msg['nearest_hub']['hub_id'],
        nearest_hub_distance=msg['nearest_hub']['distance_m'],
        feature_vector=json.dumps(msg['features']),  # Convert list to JSON string
        processing_time_ms=msg['processing_time_ms']
    )

def load_json(file_path: Path):
    """
    Loads a JSON file and returns its contents as a dictionary.
    file_path: The path to the JSON file to load.
    return The contents of the JSON file as a dictionary, or None if loading fails.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
   
        if isinstance(data, dict):
            return [data]
    
        return data
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None
    
def ingest_inference_results(manager: InferenceResultsManager, messages: list[dict]):
    """
    Ingests a list of inference messages into the database using the provided manager.
    manager: An instance of InferenceResultsManager to handle database operations.
    messages: A list of inference messages as dictionaries to ingest.
    """
    for msg in messages:
        record = parse_inference_message(msg)
        if record:       
            success = manager.insert_inference_result(record)
            if not success:
                print(f"Failed to insert record for node_id: {record.node_id} at timestamp: {record.timestamp}")

def ingest_anomaly_event(inference_record: inference_results):
    """
    Ingests an anomaly event into the database based on the provided inference record.
    inference_record: An instance of inference_results that contains anomaly information to be ingested as an event.
    """
    anomaly_manager = AnomalyEventsManager()
    event = anomaly_events(
        node_id=inference_record.node_id,
        start_timestamp=inference_record.window_start,
        end_timestamp=inference_record.window_end,
        severity='CRITICAL' if inference_record.anomaly_score >= 0.75 else 'HIGH' if inference_record.anomaly_score >= 0.5 else 'MEDIUM' if inference_record.anomaly_score >= 0.25 else 'LOW',
        description=f"Anomaly detected with score {inference_record.anomaly_score} and type {inference_record.anomaly_type}"
    )
    success = anomaly_manager.insert_anomaly_event(event)
    if not success:
        print(f"Failed to insert anomaly event for node_id: {event.node_id} at timestamp: {event.start_timestamp}")

def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python inference_results_table.py <example_inference_results.json>")
        return
    
    json_file = Path(sys.argv[1])
    ir_manager = InferenceResultsManager()
    ae_manager = AnomalyEventsManager()

    messages = load_json(json_file)
    ingest_inference_results(ir_manager, messages)

if __name__ == "__main__":
    main()
        
    
