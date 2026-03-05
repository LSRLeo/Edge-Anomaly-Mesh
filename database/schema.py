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
engine = create_engine(f'sqlite+pysqlite:///database/{DEFAULT_DB_PATH}', echo=False)


class RawSensorData(Base):
    """
    ORM mapping for raw_sensor_data table
    """
    __tablename__ = "raw_sensor_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String, nullable=False)
    timestamp = Column(Float, nullable=False)  # Unix timestamp
    seq = Column(Integer, nullable=False)  # Sequence number for ordering

    gps_lat_deg = Column(Float, nullable=False)
    gps_lon_deg = Column(Float, nullable=False)
    gps_altitude_m = Column(Float, nullable=False)

    accel_x_mss = Column(Float, nullable=False)
    accel_y_mss = Column(Float, nullable=False)
    accel_z_mss = Column(Float, nullable=False)

    gyro_x_rads = Column(Float, nullable=False)
    gyro_y_rads = Column(Float, nullable=False)
    gyro_z_rads = Column(Float, nullable=False)

    # TABLES FOR ML TEAM ONLY
    sim_mode = Column(String, CheckConstraint("sim_mode IN ('IDLE','TERRESTRIAL','MARITIME','LIFT','UNKNOWN')"), nullable=False, default='UNKNOWN')
    sim_anomaly = Column(Boolean, nullable=False)

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
    first_seen = Column(Float, nullable=False)
    last_seen = Column(Float, nullable=False)
    location_lat = Column(Float, nullable=False)
    location_lon = Column(Float, nullable=False)
    location_altitude_m = Column(Float, nullable=False)


# SQLAlchemy ORM model for the inference_results table
class InferenceResults(Base):
    """
    SQLAlchemy ORM model for the inference_results table.
    """
    __tablename__ = 'inference_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String, nullable=False)
    timestamp = Column(Float, nullable=False)
    classification = Column(String, CheckConstraint("classification IN ('IDLE', 'TERRESTRIAL', 'MARITIME', 'LIFT', 'UNKNOWN')"), nullable=False)
    confidences = Column(String, nullable=False)  # JSON string of confidence scores for each class
    is_anomaly = Column(Boolean, nullable=False)
    anomaly_score = Column(Float, nullable=False)

    processing_time_ms = Column(Integer, nullable=False)
    ingested_at = Column(Float, default=lambda: datetime.utcnow().timestamp(), nullable=False)
    __table_args__ = (UniqueConstraint('node_id', 'timestamp', name='uq_node_timestamp'),)  # Ensure no duplicate entries for the same node and time window

class AnomalyEvents(Base):
    """
    SQLAlchemy ORM model for the anomaly_events table
    """
    __tablename__ = 'anomaly_events'

    inference_id = Column(Integer, nullable=False)  # Foreign key to inference_results.id

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String, nullable=False)
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