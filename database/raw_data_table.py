"""
raw_data_table.py

This module defines and manages the raw_sensor_data table.
Responsibilities:
- Create raw data table
- Parse raw sensor JSON messages
- Insert raw sensor data
- Select/query raw sensor data

Uses SQLAlchemy ORM.
"""

# Standard library
import json
from pathlib import Path
from datetime import datetime

# Third-party
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    Text,
    UniqueConstraint
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError

# ======================
# SQLAlchemy setup
# ======================
Base = declarative_base()
DEFAULT_DB_PATH = "sensor_data.db"


# ======================
# ORM Model
# ======================
class RawSensorData(Base):
    """
    ORM mapping for raw_sensor_data table
    """
    __tablename__ = "raw_sensor_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(Text, nullable=False)
    timestamp = Column(Float, nullable=False)  # Unix timestamp

    accel_x = Column(Float, nullable=False)
    accel_y = Column(Float, nullable=False)
    accel_z = Column(Float, nullable=False)

    gyro_x = Column(Float, nullable=False)
    gyro_y = Column(Float, nullable=False)
    gyro_z = Column(Float, nullable=False)

    ingested_at = Column(
        Float,
        default=lambda: datetime.utcnow().timestamp()
    )

    __table_args__ = (
        UniqueConstraint("node_id", "timestamp", name="uq_node_timestamp"),
    )


# ======================
# Table manager
# ======================
class RawDataManager:
    """
    Handles DB lifecycle and CRUD operations for raw_sensor_data
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    # ------------------
    # Insert
    # ------------------
    def insert_raw_data(self, record: RawSensorData) -> bool:
        """
        Insert a single RawSensorData record.
        Returns True if inserted, False if skipped due to idempotency.
        """
        session = self.Session()
        try:
            session.add(record)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False
        finally:
            session.close()

    # ------------------
    # Select
    # ------------------
    def get_all(self):
        session = self.Session()
        try:
            return session.query(RawSensorData).all()
        finally:
            session.close()


# ======================
# Parsing helpers
# ======================
def iso_to_unix(ts: str) -> float:
    """
    Convert ISO-8601 timestamp to Unix timestamp (seconds)
    """
    return datetime.fromisoformat(ts).timestamp()


def parse_raw_message(msg: dict) -> RawSensorData:
    """
    Convert a raw JSON message into a RawSensorData ORM object
    """
    return RawSensorData(
        node_id=msg["node_id"],
        timestamp=iso_to_unix(msg["timestamp"]),

        accel_x=msg["accel"]["x"],
        accel_y=msg["accel"]["y"],
        accel_z=msg["accel"]["z"],

        gyro_x=msg["gyro"]["x"],
        gyro_y=msg["gyro"]["y"],
        gyro_z=msg["gyro"]["z"],
    )


# ======================
# JSON ingestion
# ======================
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
        return [data]

    return data


def ingest_raw_data(manager: RawDataManager, messages: list[dict]):
    """
    Parse and insert raw messages into the database
    """
    for msg in messages:
        if msg.get("m_type") != "raw-data":
            continue

        record = parse_raw_message(msg)
        inserted = manager.insert_raw_data(record)

        if not inserted:
            print(
                f"Skipped duplicate: node_id={record.node_id}, "
                f"timestamp={record.timestamp}"
            )


# ======================
# Debug / CLI entrypoint
# ======================
def debug_print_table(manager: RawDataManager):
    """
    Print all rows in raw_sensor_data table
    """
    rows = manager.get_all()
    for row in rows:
        print(
            row.id,
            row.node_id,
            row.timestamp,
            row.accel_x,
            row.accel_y,
            row.accel_z,
            row.gyro_x,
            row.gyro_y,
            row.gyro_z,
            row.ingested_at,
        )


def main():
    """
    Example usage:
    python raw_data_table.py sample_raw_data.json
    """
    import sys

    if len(sys.argv) < 2:
        print("Usage: python raw_data_table.py <sample_raw_data.json>")
        return

    file_path = Path(sys.argv[1])
    manager = RawDataManager()

    raw_messages = load_json(file_path)
    ingest_raw_data(manager, raw_messages)
    debug_print_table(manager)


if __name__ == "__main__":
    main()
