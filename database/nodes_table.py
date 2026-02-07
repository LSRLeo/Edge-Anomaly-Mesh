# Standard library imports
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

# Third-party imports
import numpy as np
import pytest
import pysqlite3
import sqlalchemy 
from sqlalchemy import Column, Integer, String, Float, DateTime, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# Local imports


# Constants
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'sample_raw_data.json')
DEBUG = True

#SQL Alchemy setup
DATABASE_URL = 'sqlite:///database/nodes.db'
engine = sqlalchemy.create_engine(DATABASE_URL)
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine) #


class Node(Base):
    __tablename__ = 'nodes'
    node_id = Column(String, primary_key=True)
    seq = Column(Integer)
    status = Column(String, CheckConstraint("status IN ('active', 'inactive')", name='status_check'), default='active')
    first_seen = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, nullable=False)
    location_lat = Column(Float)
    location_lon = Column(Float)
    location_altitude_m = Column(Float)

    
class NodeManager:
    '''
    NodeManager: Session for managing node operations using SQLAlchemy ORM
    '''
    def __init__(self):
        self.session = Session()

    def insert_node(self, node_id, seq, first_seen, last_seen, location_lat, location_lon, location_altitude_m):
        '''Insert a new node into the database'''

        new_node = Node(node_id=node_id, seq=seq, first_seen=first_seen, last_seen=last_seen,
                        location_lat=location_lat, location_lon=location_lon, location_altitude_m=location_altitude_m)
        self.session.add(new_node)
        try:
            self.session.commit()
            debug_print(f"Inserted node {node_id}")
        except Exception as e:
            self.session.rollback() #undo the failed transaction
            debug_print(f"Error inserting node {node_id}: {e}")


    def update_node(self, node_id, last_seen, location_lat, location_lon, location_altitude_m):
        '''Update an existing node's last seen time and location'''

        node = self.get_node_by_id(node_id)
        #there could be a race condition and other issues if the node is being updated by multiple processes when threading
        if node:
            #if exists, update the node, otherwise, insert a new node or throw an error
            node.last_seen = last_seen
            node.location_lat = location_lat
            node.location_lon = location_lon
            node.location_altitude_m = location_altitude_m
            self.session.commit()

            debug_print(f"Updated node {node_id}")
        else:
            debug_print(f"Node {node_id} not found for update")

    def toggle_node_status(self, node_id, status):
        '''Toggle a node's status between active and inactive'''

        node = self.get_node_by_id(node_id)
        if node:
            node.status = status
            self.session.commit()
            debug_print(f"Updated status for node {node_id} to {status}")
        else:
            debug_print(f"Node {node_id} not found for status update")

    #QUERIES
    def get_all_nodes(self):
        '''Get all nodes from the database'''
        return self.session.query(Node).all()
    
    def get_active_nodes(self):
        '''Get all active nodes from the database'''
        return self.session.query(Node).filter_by(status='active').all()
    
    def get_inactive_nodes(self):
        '''Get all inactive nodes from the database'''
        return self.session.query(Node).filter_by(status='inactive').all()
    
    def get_node_by_id(self, node_id):
        '''Get a node by its ID'''
        return self.session.query(Node).filter_by(node_id=node_id).first()
    
    def delete_node(self, node_id):
        '''Delete a node from the database'''
        node = self.get_node_by_id(node_id)
        if node:
            self.session.delete(node)
            self.session.commit()
            debug_print(f"Deleted node {node_id}")
        else:
            debug_print(f"Node {node_id} not found for deletion")

'''DB setup'''
def set_up_db():
    '''
    Docstring for set_up_db
    '''
    conn = pysqlite3.connect('database/nodes.db')
    c = conn.cursor()
    
    if not table_exists(c, 'nodes'):
        c.execute('''CREATE TABLE IF NOT EXISTS nodes
                (node_id TEXT PRIMARY KEY,
                seq INTEGER,
                status TEXT default 'active' CHECK(status IN ('active', 'inactive')),
                first_seen REAL NOT NULL,
                last_seen REAL NOT NULL,
                location_lat REAL,
                location_lon REAL,
                location_altitude_m REAL
                )''')
        conn.commit()

    return conn, c


def table_exists(c, table_name) -> bool:
    '''
    Docstring for table_exists
    
    :param c: Description
    :param table_name: Description
    :return: Description
    :rtype: bool
    '''
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))

    return c.fetchone() is not None


def node_exists(c, node_id) -> bool:
    '''
    Docstring for node_exists
    
    :param c: Description
    :param node_id: Description
    :return: Description
    :rtype: bool
    '''
    c.execute("SELECT * FROM nodes WHERE node_id=?", (node_id,))

    return c.fetchone() is not None


def insert_node(c, *args):
    '''
    Docstring for insert_node
    
    :param c: Description
    :param args: Description
    '''
    node_id, first_seen, seq, lat, lon, altitude_m = args
    last_seen = first_seen

    c.execute('''INSERT INTO nodes (node_id, seq, first_seen, last_seen, location_lat, location_lon, location_altitude_m)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', (node_id, seq, first_seen, last_seen, lat, lon, altitude_m))
    
    debug_print(f"Inserted node {node_id}")
    debug_print_table(c)


'''Node Table Operations'''
def update_node(c, *args):
    '''
    Docstring for update_node
    
    :param c: Description
    :param args: Description
    '''
    node_id, last_seen, lat, lon, altitude_m = args

    c.execute('''UPDATE nodes
                 SET last_seen=?, location_lat=?, location_lon=?, location_altitude_m=?
                 WHERE node_id=?''', (last_seen, lat, lon, altitude_m, node_id))
    
    debug_print(f"Updated node {node_id}")
    debug_print_table(c)


def update_node_status(c, node_id, status):
    '''
    Docstring for update_node_status
    
    :param c: Description
    :param node_id: Description
    :param status: Description
    '''
    c.execute('''UPDATE nodes
                 SET status=?
                 WHERE node_id=?''', (status, node_id))
    
    debug_print(f"Updated status for node {node_id} to {status}")
    debug_print_table(c)


def get_active_nodes(c):
    '''
    Docstring for get_active_nodes
    
    :param c: Description
    :return: Description
    :rtype: list
    '''
    c.execute("SELECT * FROM nodes WHERE status='active'")
    return c.fetchall()


def get_inactive_nodes(c):
    '''
    Docstring for get_inactive_nodes
    
    :param c: Description
    :return: Description
    :rtype: list
    '''
    c.execute("SELECT * FROM nodes WHERE status='inactive'")
    return c.fetchall()


def get_node_by_id(c, node_id):
    '''
    Docstring for get_node_by_id
    
    :param c: Description
    :param node_id: Description
    :return: Description
    :rtype: tuple
    '''
    c.execute("SELECT * FROM nodes WHERE node_id=?", (node_id,))
    return c.fetchone()


'''Loading and processing raw data'''
def load_json(file_path):
    ''''''
    with open(file_path, 'r') as f:
        data = json.load(f)
        return data


def extract_node_data(node_dict):
    '''
    Docstring for extract_node_data
    
    :param node_dict: Description
    '''

    debug_print(f"Extracting data from node: {node_dict}")

    node_id = node_dict['node_id']
    timestamp = node_dict['timestamp']
    seq = node_dict['seq']
    lat = node_dict['gps']['lat']
    lon = node_dict['gps']['lon']
    altitude_m = node_dict['gps']['altitude_m']

    return (node_id, timestamp, seq, lat, lon, altitude_m)


def process_nodes(c, raw_data):
    '''
    Docstring for process_nodes
    
    :param c: Description
    :param raw_data: Description
    '''
    for node_dict in raw_data[:3]:
        node_id, timestamp, seq, lat, lon, altitude_m = extract_node_data(node_dict)

        if node_exists(c, node_id):
            update_node(c, node_id, timestamp, lat, lon, altitude_m)
        else:
            insert_node(c, node_id, timestamp, seq, lat, lon, altitude_m)


def debug_print_table(c):
    '''
    Docstring for debug_print_table
    
    :param c: Description
    '''
    print("Current state of nodes table:")
    c.execute("SELECT * FROM nodes")
    rows = c.fetchall()
    for node_id,seq,status,first_seen,last_seen,location_lat,location_lon,location_altitude_m in rows:
        print(f"Node ID: {node_id}, Seq: {seq}, Status: {status}, First Seen: {first_seen}, Last Seen: {last_seen}, location: ({location_lat}, {location_lon}, {location_altitude_m})")


def debug_print(message):
    '''Docstring for debug_print :param message: Description'''
    if DEBUG:
        print(message)


def main():
    '''Docstring for main'''

    conn, c = set_up_db()
    raw_data = load_json(file_path)
    process_nodes(c, raw_data)
    conn.commit()
    conn.close()


main()
