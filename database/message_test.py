

"""
Tests to verify message execution with actual database insertion.
Tests both RawDataMessage and InferenceOutputMessage execute() methods.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent))

from db_message_factory import MessageFactory
from db_table_manager import TableManager
from schema import engine, RawSensorData, Node, InferenceResults, AnomalyEvents, create_schema
from sqlalchemy.orm import Session


def print_test_header(test_name):
    """Print a formatted test header"""
    print("\n" + "="*70)
    print(f"TEST: {test_name}")
    print("="*70)


def setup_test_database():
    """Create fresh database schema for testing"""
    print("Setting up test database...")
    create_schema()
    manager = TableManager()
    manager.clear_tables()
    print("Database schema created and cleared")
    return manager


def verify_raw_data_in_db(session, expected_node_id, expected_seq):
    """Verify raw data was inserted into database"""
    # Check RawSensorData table
    raw_data = session.query(RawSensorData).filter_by(
        node_id=expected_node_id,
        seq=expected_seq
    ).first()
    
    if raw_data is None:
        return False, "Raw sensor data not found in database"
    
    # Check Node table
    node = session.query(Node).filter_by(node_id=expected_node_id).first()
    
    if node is None:
        return False, "Node not found in database"
    
    return True, {
        "raw_data": {
            "node_id": raw_data.node_id,
            "seq": raw_data.seq,
            "accel_x": raw_data.accel_x,
            "gps_lat": raw_data.gps_lat
        },
        "node": {
            "node_id": node.node_id,
            "status": node.status,
            "location_lat": node.location_lat
        }
    }


def test_raw_data_message_fields():
    """Test RawDataMessage class fields match what's expected"""
    print_test_header("RawDataMessage Class Fields Test")
    
    # Create raw-data message
    raw_data_dict = {
        "m_type": "raw-data",
        "m_id": "node_001_test_fields",
        "event_id": "node_001_2026-02-25T13:28:18.935751",
        "node_id": "node_001",
        "timestamp": "2026-02-25T13:28:18.935751",
        "seq": 888,
        "gps": {
            "lat_deg": 39.7392,
            "lon_deg": -104.9903,
            "altitude_m": 1609.3
        },
        "accel_mss": {
            "x": 0.019661708765145478,
            "y": 0.035165038521073784,
            "z": 9.870986259634625
        },
        "gyro_rads": {
            "x": 0.065473642565412,
            "y": -0.02240765207602273,
            "z": -0.018875053228777607
        },
        "meta": {
            "sample_rate_hz": 1,
            "battery_pct": 95,
            "sim_mode": "IDLE",
            "sim_anomaly": False
        },
        "origin": {
            "lat_deg": 39.7392,
            "lon_deg": -104.9903,
            "altitude_m": 1609.3
        },
        "dest": {
            "lat_deg": 39.542,
            "lon_deg": -103.5915,
            "altitude_m": 1612.8
        }
    }
    
    print(f"Creating message from dict with m_id: {raw_data_dict['m_id']}")
    
    # Create message using factory
    message = MessageFactory.create_message(raw_data_dict)
    
    if message is None:
        print("FAILED: Factory returned None")
        return False
    
    print(f"Message created: {message.__class__.__name__}")
    
    # Test Message base class fields
    print("\nTesting Message base class fields:")
    print(f"  message.m_id = {message.m_id}")
    assert hasattr(message, 'm_id'), "Message missing m_id attribute"
    assert message.m_id == "node_001_test_fields"
    
    print(f"  message.m_type = {message.m_type}")
    assert hasattr(message, 'm_type'), "Message missing m_type attribute"
    assert message.m_type == "raw-data"
    
    print(f"  message.M_TYPE = {message.M_TYPE}")
    assert hasattr(message, 'M_TYPE'), "Message missing M_TYPE class attribute"
    assert message.M_TYPE == "raw-data"
    
    print(f"  message.m_content exists: {hasattr(message, 'm_content')}")
    assert hasattr(message, 'm_content'), "Message missing m_content attribute"
    
    # Test RawDataMessage specific fields
    print("\nTesting RawDataMessage specific fields:")
    print(f"  message.data exists: {hasattr(message, 'data')}")
    assert hasattr(message, 'data'), "RawDataMessage missing data attribute"
    
    print(f"  message.event_id = {message.event_id}")
    assert hasattr(message, 'event_id'), "RawDataMessage missing event_id attribute"
    assert message.event_id == "node_001_2026-02-25T13:28:18.935751"
    
    print(f"  message.node_id = {message.node_id}")
    assert hasattr(message, 'node_id'), "RawDataMessage missing node_id attribute"
    assert message.node_id == "node_001"
    
    # Test that data contains all the fields
    print("\nTesting message.data contents:")
    assert "event_id" in message.data
    assert "node_id" in message.data
    assert "timestamp" in message.data
    assert "seq" in message.data
    assert "gps" in message.data
    assert "accel_mss" in message.data
    assert "gyro_rads" in message.data
    assert "meta" in message.data
    print(f"  message.data['seq'] = {message.data['seq']}")
    print(f"  message.data['gps'] = {message.data['gps']}")
    
    # Test to_dict() method
    print("\nTesting to_dict() method:")
    message_dict = message.to_dict()
    print(f"  to_dict() returns dict: {isinstance(message_dict, dict)}")
    assert isinstance(message_dict, dict)
    assert "m_id" in message_dict
    assert "m_type" in message_dict
    print(f"  to_dict()['m_id'] = {message_dict['m_id']}")
    print(f"  to_dict()['m_type'] = {message_dict['m_type']}")
    
    print("\nAll field tests passed")
    return True


def test_raw_data_message_execute():
    """Test that RawDataMessage.execute() inserts data into database"""
    print_test_header("RawDataMessage Execute - Database Insertion")
    
    # Setup
    db_manager = setup_test_database()
    session = Session(engine)
    
    # Create raw-data message
    raw_data_dict = {
        "m_type": "raw-data",
        "m_id": "node_001_test_0",
        "event_id": "node_001_2026-02-25T13:28:18.935751",
        "node_id": "node_001",
        "timestamp": "2026-02-25T13:28:18.935751",
        "seq": 999,
        "gps": {
            "lat_deg": 39.7392,
            "lon_deg": -104.9903,
            "altitude_m": 1609.3
        },
        "accel_mss": {
            "x": 0.019661708765145478,
            "y": 0.035165038521073784,
            "z": 9.870986259634625
        },
        "gyro_rads": {
            "x": 0.065473642565412,
            "y": -0.02240765207602273,
            "z": -0.018875053228777607
        },
        "meta": {
            "sample_rate_hz": 1,
            "battery_pct": 95,
            "sim_mode": "IDLE",
            "sim_anomaly": False
        },
        "origin": {
            "lat_deg": 39.7392,
            "lon_deg": -104.9903,
            "altitude_m": 1609.3
        },
        "dest": {
            "lat_deg": 39.542,
            "lon_deg": -103.5915,
            "altitude_m": 1612.8
        }
    }
    
    print(f"Creating message: {raw_data_dict['m_id']}")
    
    # Create message using factory
    message = MessageFactory.create_message(raw_data_dict)
    
    if message is None:
        print("FAILED: Factory returned None")
        session.close()
        return False
    
    print(f"Message created: {message.__class__.__name__}")
    print(f"   message.event_id: {message.event_id}")
    print(f"   message.node_id: {message.node_id}")
    print(f"   message.data['seq']: {message.data.get('seq')}")
    
    # Execute message (should insert into database)
    print("\nExecuting message.execute(db_manager)...")
    result = message.execute(db_manager)
    
    if result is not None:
        print(f"FAILED: Execute returned error: {result.error_message}")
        session.close()
        return False
    
    print("Execute returned None (success)")
    
    # Verify data was inserted into database
    print("\nVerifying database insertion...")
    is_found, db_result = verify_raw_data_in_db(session, "node_001", 999)
    
    if not is_found:
        print(f"FAILED: {db_result}")
        session.close()
        return False
    
    print("Data verified in database:")
    print(f"   Raw Data: node_id={db_result['raw_data']['node_id']}, "
          f"seq={db_result['raw_data']['seq']}, "
          f"accel_x={db_result['raw_data']['accel_x']:.6f}")
    print(f"   Node: node_id={db_result['node']['node_id']}, "
          f"status={db_result['node']['status']}, "
          f"lat={db_result['node']['location_lat']}")
    
    # Verify specific field values
    assert db_result['raw_data']['node_id'] == "node_001"
    assert db_result['raw_data']['seq'] == 999
    assert abs(db_result['raw_data']['accel_x'] - 0.019661708765145478) < 1e-10
    assert abs(db_result['raw_data']['gps_lat'] - 39.7392) < 1e-6
    
    session.close()
    print("\nTEST PASSED: RawDataMessage successfully inserted data into database")
    return True


def test_inference_message_fields():
    """Test InferenceOutputMessage class fields"""
    print_test_header("InferenceOutputMessage Class Fields Test")
    
    # Create inference-output message
    inference_dict = {
        "m_type": "inference-output",
        "m_id": "ml_00001",
        "event_id": "node_001_2026-02-25T13:28:18.935751",
        "node_id": "node_001",
        "timestamp": "2026-02-25T13:28:18.935751",
        "classification": "IDLE",
        "confidence": 0.95,
        "is_anomaly": False,
        "anomaly_score": 0.12
    }
    
    print(f"Creating message from dict with m_id: {inference_dict['m_id']}")
    
    # Create message using factory
    message = MessageFactory.create_message(inference_dict)
    
    if message is None:
        print("FAILED: Factory returned None")
        return False
    
    print(f"Message created: {message.__class__.__name__}")
    
    # Test Message base class fields
    print("\nTesting Message base class fields:")
    print(f"  message.m_id = {message.m_id}")
    assert hasattr(message, 'm_id')
    assert message.m_id == "ml_00001"
    
    print(f"  message.m_type = {message.m_type}")
    assert hasattr(message, 'm_type')
    assert message.m_type == "inference-output"
    
    print(f"  message.M_TYPE = {message.M_TYPE}")
    assert hasattr(message, 'M_TYPE')
    assert message.M_TYPE == "inference-output"
    
    # Test InferenceOutputMessage specific fields
    print("\nTesting InferenceOutputMessage specific fields:")
    print(f"  message.event_id = {message.event_id}")
    assert hasattr(message, 'event_id')
    assert message.event_id == "node_001_2026-02-25T13:28:18.935751"
    
    print(f"  message.node_id = {message.node_id}")
    assert hasattr(message, 'node_id')
    assert message.node_id == "node_001"
    
    print(f"  message.classification = {message.classification}")
    assert hasattr(message, 'classification')
    assert message.classification == "IDLE"
    
    # Test m_content contains inference fields
    print("\nTesting message.m_content contents:")
    assert hasattr(message, 'm_content')
    print(f"  'event_id' in m_content: {'event_id' in message.m_content}")
    print(f"  'classification' in m_content: {'classification' in message.m_content}")
    print(f"  'confidence' in m_content: {'confidence' in message.m_content}")
    print(f"  message.m_content['confidence'] = {message.m_content.get('confidence')}")
    
    print("\nAll field tests passed")
    return True


def test_raw_data_batch_execute():
    """Test executing multiple raw-data messages"""
    print_test_header("RawDataMessage Batch Execute - Multiple Insertions")
    
    # Setup
    db_manager = setup_test_database()
    session = Session(engine)
    
    # Create multiple messages
    messages_data = []
    for i in range(5):
        msg_dict = {
            "m_type": "raw-data",
            "m_id": f"node_001_batch_{i}",
            "event_id": f"node_001_2026-02-25T13:28:1{i}.000000",
            "node_id": "node_001",
            "timestamp": f"2026-02-25T13:28:1{i}.000000",
            "seq": 1000 + i,
            "gps": {"lat_deg": 39.7392 + i*0.001, "lon_deg": -104.9903, "altitude_m": 1609.3},
            "accel_mss": {"x": 0.01 + i*0.01, "y": 0.02, "z": 9.81},
            "gyro_rads": {"x": 0.01, "y": 0.01, "z": 0.01},
            "meta": {"sample_rate_hz": 1, "battery_pct": 95, "sim_mode": "IDLE", "sim_anomaly": False},
            "origin": {"lat_deg": 39.7392, "lon_deg": -104.9903, "altitude_m": 1609.3},
            "dest": {"lat_deg": 39.542, "lon_deg": -103.5915, "altitude_m": 1612.8}
        }
        messages_data.append(msg_dict)
    
    print(f"Creating and executing {len(messages_data)} messages...")
    
    success_count = 0
    for msg_dict in messages_data:
        message = MessageFactory.create_message(msg_dict)
        if message:
            # Verify message has expected fields
            assert hasattr(message, 'm_id')
            assert hasattr(message, 'm_type')
            assert hasattr(message, 'event_id')
            assert hasattr(message, 'node_id')
            
            result = message.execute(db_manager)
            if result is None:
                success_count += 1
            else:
                print(f"  Message {msg_dict['m_id']} failed: {result.error_message}")
    
    print(f"\nSuccessfully executed {success_count}/{len(messages_data)} messages")
    
    # Verify all records in database
    total_records = session.query(RawSensorData).filter_by(node_id="node_001").count()
    print(f"Database contains {total_records} raw data records for node_001")
    
    # Verify specific records
    for i in range(5):
        is_found, _ = verify_raw_data_in_db(session, "node_001", 1000 + i)
        assert is_found, f"Record with seq={1000+i} not found"
    
    print(f"All {len(messages_data)} records verified in database")
    
    session.close()
    print("\nTEST PASSED: Batch insertion successful")
    return True


def test_message_with_missing_fields():
    """Test that execute() handles missing required fields"""
    print_test_header("RawDataMessage Execute - Missing Fields Handling")
    
    # Setup
    db_manager = setup_test_database()
    
    # Create message with missing event_id
    invalid_data = {
        "m_type": "raw-data",
        "m_id": "node_001_invalid",
        # "event_id": "missing!",  # Intentionally missing
        "node_id": "node_001",
        "timestamp": "2026-02-25T13:28:18.935751",
        "seq": 9999,
        "gps": {"lat_deg": 39.7392, "lon_deg": -104.9903, "altitude_m": 1609.3},
        "accel_mss": {"x": 0.01, "y": 0.02, "z": 9.81},
        "gyro_rads": {"x": 0.01, "y": 0.01, "z": 0.01},
        "meta": {"sample_rate_hz": 1, "battery_pct": 95, "sim_mode": "IDLE", "sim_anomaly": False},
        "origin": {"lat_deg": 39.7392, "lon_deg": -104.9903, "altitude_m": 1609.3},
        "dest": {"lat_deg": 39.542, "lon_deg": -103.5915, "altitude_m": 1612.8}
    }
    
    print("Creating message with missing event_id...")
    message = MessageFactory.create_message(invalid_data)
    
    if message is None:
        print("FAILED: Factory returned None (should create message)")
        return False
    
    print("Message created (factory doesn't validate event_id)")
    
    # Verify message fields
    print(f"  message.m_id = {message.m_id}")
    print(f"  message.m_type = {message.m_type}")
    print(f"  message.event_id = {message.event_id}")
    
    # Execute should return ErrorResponse
    print("\nExecuting message (should fail)...")
    result = message.execute(db_manager)
    
    if result is None:
        print("FAILED: Execute should have returned ErrorResponse")
        return False
    
    print(f"Execute returned ErrorResponse as expected")
    
    # Verify ErrorResponse fields
    print(f"  result.m_id = {result.m_id}")
    print(f"  result.m_type = {result.m_type}")
    print(f"  result.error_code = {result.error_code}")
    print(f"  result.error_message = {result.error_message}")
    
    # Verify it's an ErrorResponse
    from db_message import ErrorResponse
    assert isinstance(result, ErrorResponse)
    assert hasattr(result, 'error_code')
    assert hasattr(result, 'error_message')
    assert result.error_code == "INVALID_REQUEST"
    assert "event_id" in result.error_message or "node_id" in result.error_message
    
    print("\nTEST PASSED: Missing fields properly handled")
    return True


def test_node_update():
    """Test that node record is updated when new data arrives"""
    print_test_header("Node Update - Last Seen and Location")
    
    # Setup
    db_manager = setup_test_database()
    session = Session(engine)
    
    # Insert first message
    msg1_dict = {
        "m_type": "raw-data",
        "m_id": "node_002_0",
        "event_id": "node_002_2026-02-25T10:00:00.000000",
        "node_id": "node_002",
        "timestamp": "2026-02-25T10:00:00.000000",
        "seq": 0,
        "gps": {"lat_deg": 40.0, "lon_deg": -105.0, "altitude_m": 1600.0},
        "accel_mss": {"x": 0.01, "y": 0.02, "z": 9.81},
        "gyro_rads": {"x": 0.01, "y": 0.01, "z": 0.01},
        "meta": {"sample_rate_hz": 1, "battery_pct": 95, "sim_mode": "IDLE", "sim_anomaly": False},
        "origin": {"lat_deg": 40.0, "lon_deg": -105.0, "altitude_m": 1600.0},
        "dest": {"lat_deg": 39.542, "lon_deg": -103.5915, "altitude_m": 1612.8}
    }
    
    msg1 = MessageFactory.create_message(msg1_dict)
    
    # Verify message1 fields
    print(f"Message 1 fields:")
    print(f"  m_id: {msg1.m_id}")
    print(f"  node_id: {msg1.node_id}")
    print(f"  event_id: {msg1.event_id}")
    
    msg1.execute(db_manager)
    
    # Check initial node state
    node = session.query(Node).filter_by(node_id="node_002").first()
    initial_lat = node.location_lat
    initial_last_seen = node.last_seen
    
    print(f"\nInitial node state:")
    print(f"  Location: lat={initial_lat}, lon={node.location_lon}")
    print(f"  Last seen: {initial_last_seen}")
    
    # Insert second message with different location and time
    msg2_dict = {
        "m_type": "raw-data",
        "m_id": "node_002_1",
        "event_id": "node_002_2026-02-25T11:00:00.000000",
        "node_id": "node_002",
        "timestamp": "2026-02-25T11:00:00.000000",
        "seq": 1,
        "gps": {"lat_deg": 40.1, "lon_deg": -105.1, "altitude_m": 1650.0},
        "accel_mss": {"x": 0.01, "y": 0.02, "z": 9.81},
        "gyro_rads": {"x": 0.01, "y": 0.01, "z": 0.01},
        "meta": {"sample_rate_hz": 1, "battery_pct": 90, "sim_mode": "TERRESTRIAL", "sim_anomaly": False},
        "origin": {"lat_deg": 40.0, "lon_deg": -105.0, "altitude_m": 1600.0},
        "dest": {"lat_deg": 39.542, "lon_deg": -103.5915, "altitude_m": 1612.8}
    }
    
    msg2 = MessageFactory.create_message(msg2_dict)
    
    # Verify message2 fields
    print(f"\nMessage 2 fields:")
    print(f"  m_id: {msg2.m_id}")
    print(f"  node_id: {msg2.node_id}")
    print(f"  event_id: {msg2.event_id}")
    
    msg2.execute(db_manager)
    
    # Check updated node state
    session.expire_all()
    node = session.query(Node).filter_by(node_id="node_002").first()
    updated_lat = node.location_lat
    updated_last_seen = node.last_seen
    
    print(f"\nUpdated node state:")
    print(f"  Location: lat={updated_lat}, lon={node.location_lon}")
    print(f"  Last seen: {updated_last_seen}")
    
    # Verify updates
    assert updated_lat != initial_lat, "Location should have updated"
    assert updated_last_seen != initial_last_seen, "Last seen should have updated"
    assert abs(updated_lat - 40.1) < 1e-6
    assert abs(node.location_lon - (-105.1)) < 1e-6
    
    print("\nNode record properly updated")
    
    session.close()
    print("\nTEST PASSED: Node updates working correctly")
    return True


def test_database_stats():
    """Test database statistics after insertions"""
    print_test_header("Database Statistics")
    
    # Setup and insert test data
    db_manager = setup_test_database()
    session = Session(engine)
    
    # Insert data for multiple nodes
    nodes = ["node_001", "node_002", "node_003"]
    total_messages = 0
    
    for node_id in nodes:
        for i in range(3):
            msg_dict = {
                "m_type": "raw-data",
                "m_id": f"{node_id}_{i}",
                "event_id": f"{node_id}_2026-02-25T10:0{i}:00.000000",
                "node_id": node_id,
                "timestamp": f"2026-02-25T10:0{i}:00.000000",
                "seq": i,
                "gps": {"lat_deg": 39.7 + float(i), "lon_deg": -104.9, "altitude_m": 1600.0},
                "accel_mss": {"x": 0.01, "y": 0.02, "z": 9.81},
                "gyro_rads": {"x": 0.01, "y": 0.01, "z": 0.01},
                "meta": {"sample_rate_hz": 1, "battery_pct": 95, "sim_mode": "IDLE", "sim_anomaly": False},
                "origin": {"lat_deg": 39.7, "lon_deg": -104.9, "altitude_m": 1600.0},
                "dest": {"lat_deg": 39.5, "lon_deg": -103.5, "altitude_m": 1612.8}
            }
            message = MessageFactory.create_message(msg_dict)
            if message:
                result = message.execute(db_manager)
                if result is None:
                    total_messages += 1
    
    # Get statistics
    total_raw_data = session.query(RawSensorData).count()
    total_nodes = session.query(Node).count()
    
    print(f"Database Statistics:")
    print(f"  Messages processed: {total_messages}")
    print(f"  Raw data records: {total_raw_data}")
    print(f"  Unique nodes: {total_nodes}")
    
    assert total_messages == 9
    assert total_raw_data == 9
    assert total_nodes == 3
    
    print("\nAll statistics match expected values")
    
    session.close()
    print("\nTEST PASSED: Database statistics correct")
    return True


def run_all_tests():
    """Run all database insertion tests"""
    print("\n" + "="*70)
    print("RUNNING ALL MESSAGE EXECUTE DATABASE TESTS")
    print("="*70)
    
    tests = [
        ("Raw Data Message Fields", test_raw_data_message_fields),
        ("Inference Message Fields", test_inference_message_fields),
        ("Raw Data Message Execute", test_raw_data_message_execute),
        ("Raw Data Batch Execute", test_raw_data_batch_execute),
        ("Missing Fields Handling", test_message_with_missing_fields),
        ("Node Update", test_node_update),
        ("Database Statistics", test_database_stats)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\nEXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nALL TESTS PASSED")
        print("RawDataMessage.execute() successfully inserts data into database")
        return True
    else:
        print(f"\n{total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)