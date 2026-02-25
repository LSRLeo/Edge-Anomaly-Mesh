"""
schema.py

Creates the database schema using SQLAlchemy ORM.

Responsibilities:
- Define the database schema using SQLAlchemy ORM models.
- Ensure the schema is optimized for efficient storage and retrieval of inference results and anomaly events.
"""
# Standard library imports
from datetime import datetime

#third party imports
from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    DateTime,
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
DEFAULT_DB_PATH = 'mesh.db'
engine = create_engine(f'sqlite+pysqlite:///database/{DEFAULT_DB_PATH}', echo=True)

class RawSensorData(Base):
    """
    ORM mapping for raw_sensor_data table
    """
    __tablename__ = "raw_sensor_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String, nullable=False)
    timestamp = Column(Float, nullable=False)  # Unix timestamp
    seq = Column(Integer, nullable=False)  # Sequence number for ordering

    accel_x = Column(Float, nullable=False)
    accel_y = Column(Float, nullable=False)
    accel_z = Column(Float, nullable=False)

    gyro_x = Column(Float, nullable=False)
    gyro_y = Column(Float, nullable=False)
    gyro_z = Column(Float, nullable=False)

    gps_lat = Column(Float, nullable=False)
    gps_lon = Column(Float, nullable=False)
    gps_altitude_m = Column(Float, nullable=False)

    ingested_at = Column(
        Float,
        default=lambda: datetime.utcnow().timestamp()
    )

    __table_args__ = (
        UniqueConstraint("node_id", "timestamp", name="uq_node_timestamp"),
    )

class Node(Base):
    __tablename__ = 'nodes'
    node_id = Column(String, primary_key=True, nullable=False)
    status = Column(String, CheckConstraint("status IN ('active', 'inactive')", name='status_check'), default='active', nullable=False)
    first_seen = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, nullable=False)
    location_lat = Column(Float, nullable=False)
    location_lon = Column(Float, nullable=False)
    location_altitude_m = Column(Float, nullable=False)


    def __repr__(self):
        return f"<Node(node_id='{self.node_id}', seq={self.seq}, status='{self.status}', first_seen='{self.first_seen}', last_seen='{self.last_seen}', location=({self.location_lat}, {self.location_lon}, {self.location_altitude_m}))>"

# SQLAlchemy ORM model for the inference_results table
class InferenceResults(Base):
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

class AnomalyEvents(Base):
    """
    SQLAlchemy ORM model for the anomaly_events table
    """
    __tablename__ = 'anomaly_events'

    inference_id = Column(Integer, nullable=False)  # Foreign key to inference_results.id

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String, nullable=False)
    start_timestamp = Column(Float, nullable=False)
    end_timestamp = Column(Float)
    severity = Column(String, CheckConstraint("severity IN ('LOW','MEDIUM','HIGH', 'CRITICAL')"), nullable=False)
    description = Column(String)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String)
    acknowledged_at = Column(Float)

    __table_args__ = (ForeignKeyConstraint(['node_id'], ['nodes.node_id'], name='fk_anomaly_node'),
                      ForeignKeyConstraint(['inference_id'], ['inference_results.id'], name='fk_anomaly_inference'),)
    
def create_schema():
    """
    Creates the database schema by creating all tables defined in the ORM models.
    """
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    create_schema()