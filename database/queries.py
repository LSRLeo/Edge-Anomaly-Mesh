
# queries.py
# SQLAlchemy query functions for database operations
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from schema import engine, Node, RawSensorData, InferenceResults


Session = sessionmaker(bind=engine)

# Helper to convert SQLAlchemy ORM object to dict
def orm_to_dict(obj) -> Optional[Dict[str, Any]]:
	if obj is None:
		return None
	# Try to use __table__.columns if available
	if hasattr(obj, '__table__'):
		return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
	# Fallback: use __dict__ and filter out private attributes
	return {k: v for k, v in vars(obj).items() if not k.startswith('_')}

def get_nodes() -> List[str]::
	"""Return all node_ids in the nodes table."""
	session = Session()
	try:
		nodes = session.query(Node.node_id).all()
		return [n[0] for n in nodes]
	finally:
		session.close()

def get_node_data_ids(node_id: str) -> List[str]:
	"""Return all event_ids (node_id + timestamp) for a node from raw_sensor_data, ordered by timestamp."""
	session = Session()
	try:
		rows = session.query(RawSensorData.node_id, RawSensorData.timestamp).filter(RawSensorData.node_id == node_id).order_by(RawSensorData.timestamp).all()
		# event_id format: {node_id}_{timestamp}
		return [f"{row.node_id}_{row.timestamp}" for row in rows]
	finally:
		session.close()

def get_datum(event_id: str) -> Optional[Dict[str, Any]]:
	"""Return a single datum (raw + inference) for a given event_id (node_id_timestamp)."""
	try:
		node_id, timestamp = event_id.rsplit('_', 1)
		timestamp = float(timestamp)
	except Exception:
		return None
	session = Session()
	try:
		raw = session.query(RawSensorData).filter(RawSensorData.node_id == node_id, RawSensorData.timestamp == timestamp).first()
		if not raw:
			return None
		# Try to get inference for this node/timestamp (window containing timestamp)
		inference = session.query(InferenceResults).filter(
			InferenceResults.node_id == node_id,
			InferenceResults.window_start <= timestamp,
			InferenceResults.window_end >= timestamp
		).order_by(desc(InferenceResults.window_end)).first()
		return {
			'raw': orm_to_dict(raw),
			'inference': orm_to_dict(inference)
		}
	finally:
		session.close()

def get_recent_raw_data(node_id: str) -> Optional[Dict[str, Any]]:
	"""Return the most recent raw_sensor_data row for a node."""
	session = Session()
	try:
		row = session.query(RawSensorData).filter(RawSensorData.node_id == node_id).order_by(desc(RawSensorData.timestamp)).first()
		return orm_to_dict(row)
	finally:
		session.close()
		
def get_recent_inference(node_id: str) -> Optional[Dict[str, Any]]:
	"""Return the most recent inference_results row for a node."""
	session = Session()
	try:
		row = session.query(InferenceResults).filter(InferenceResults.node_id == node_id).order_by(desc(InferenceResults.window_end)).first()
		return orm_to_dict(row)
	finally:
		session.close()
