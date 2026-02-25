"""
test_insert.py
simple insert test for the database schema
"""

# third party imports
from sqlalchemy.orm import Session
# local imports
from schema import engine, RawSensorData

def test_insert_raw_sensor_data():

    new_data = RawSensorData(
            node_id="node_1",
            timestamp=1625247600.0,
            seq=1,
            accel_x=0.1,
            accel_y=0.2,
            accel_z=0.3,
            gyro_x=0.01,
            gyro_y=0.02,
            gyro_z=0.03,
            gps_lat=37.7749,
            gps_lon=-122.4194,
            gps_altitude_m=10.0
        )
        # Add the instance to the session and commit
    with Session(engine) as session:
        session.add(new_data)
        session.commit()

        # Query the database to verify the insert
        result = session.query(RawSensorData).filter_by(node_id="node_1").first()
    
    assert result is not None
    assert result.node_id == "node_1"
    assert result.timestamp == 1625247600.0
    assert result.seq == 1
    assert result.accel_x == 0.1
    assert result.accel_y == 0.2
    assert result.accel_z == 0.3
    assert result.gyro_x == 0.01
    assert result.gyro_y == 0.02
    assert result.gyro_z == 0.03
    assert result.gps_lat == 37.7749
    assert result.gps_lon == -122.4194
    assert result.gps_altitude_m == 10.0

    # Clean up the session
    session.close()

def test_delete_raw_sensor_data():
    with Session(engine) as session:
        # Query the database to find the record to delete
        result = session.query(RawSensorData).filter_by(node_id="node_1").first()
        
        if result:
            session.delete(result)
            session.commit()

        # Verify the record has been deleted
        deleted_result = session.query(RawSensorData).filter_by(node_id="node_1").first()
    
    assert deleted_result is None


if __name__ == "__main__":
    #test one then the other, testing insert twice will cause a unique constraint violation
    test_insert_raw_sensor_data()
    #test_delete_raw_sensor_data()