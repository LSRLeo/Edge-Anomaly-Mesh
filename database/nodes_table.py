'''
WIP: nodes_table.py this module sets up node table and updates and inserts nodes from the raw data into the node table.

Columns: node_id (string, primary key), seq (integer), status (string, active/inactive), first_seen (datetime), last_seen (datetime), location_lat (float), location_lon (float), location_altitude_m (float)

will add get_node_status() and other functions for querying the node table later, for now just basic insert/update.
'''
# Standard library imports
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import ijson #use to load large json files iteratively instead of all at once, we can update/insert the node as we read it in, instead of loading the whole thing into memory

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
DATABASE_URL = 'sqlite:///database/nodes_test.db'
engine = sqlalchemy.create_engine(DATABASE_URL)
Base = declarative_base()


'''
Note: Order that parameters are passed.
(node_id, seq, timestamp, lat, lon, altitude_m)'''
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

#set up the database and create the nodes table if it doesn't exist, then create a session for managing node operations using SQLAlchemy ORM
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine) #
    
class NodeManager:
    '''
    NodeManager: Session for managing node operations using SQLAlchemy ORM
    '''
    def __init__(self):
        self.session = Session()


    def upsert_node(self, node_id, seq, timestamp, location_lat, location_lon, location_altitude_m):
        '''Insert a new node or update an existing node in the database'''
        node = self.get_node_by_id(node_id)

        if node:
            self.update_node(node_id, timestamp, location_lat, location_lon, location_altitude_m)

        else:
            self.insert_node(node_id, seq, timestamp, location_lat, location_lon, location_altitude_m)
    

    def insert_node(self, node_id,  seq, timestamp,location_lat, location_lon, location_altitude_m):
        '''Insert a new node into the database'''
        new_node = Node(node_id=node_id, seq=seq, first_seen=timestamp, last_seen=timestamp,
                        location_lat=location_lat, location_lon=location_lon, location_altitude_m=location_altitude_m)
        self.session.add(new_node)

        try:
            self.session.commit()
            debug_print(f"Inserted node {node_id}")

        except Exception as e:
            self.session.rollback() #undo the failed transaction
            debug_print(f"Error inserting node {node_id}: {e}")


    def update_node(self, node_id, timestamp, location_lat, location_lon, location_altitude_m):
        '''Update an existing node's last seen time and location'''

        node = self.get_node_by_id(node_id)
        #there could be a race condition and other issues if the node is being updated by multiple processes when threading
        if node:
            node.last_seen = timestamp
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


    '''Querying nodes - will add more complex queries later, for now just basic ones, order,group,filtering, etc.'''
    def get_all_nodes(self):
        '''Get all nodes from the database'''
        #refresh the session
        self.session.expire_all()
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



'''Loading and processing raw data'''
def load_json(file_path):
    '''update to getting line by line instead of loading the whole thing into memory, we can update/insert the node as we read it in.'''

    with open(file_path, 'rb') as f:
        data = ijson.items(f, 'item')
        node_data = []
        for i,node_dict in enumerate(data):
            if i>=5:
                #testing with 5 for now
                break
            node_data.append(node_dict)
        return node_data


def extract_node_data(node_dict):
    '''
    Docstring for extract_node_data
    
    :param node_dict: Description
    '''

    debug_print(f"Extracting data from node: {node_dict}")

    node_id = node_dict['node_id']
    seq = node_dict['seq']
    timestamp = datetime(node_dict['timestamp']) #convert to datetime object
    lat = node_dict['gps']['lat']
    lon = node_dict['gps']['lon']
    altitude_m = node_dict['gps']['altitude_m']

    return (node_id, seq, timestamp, lat, lon, altitude_m)


def process_nodes(node_manager, raw_data):
    '''
    Docstring for process_nodes
    
    :param node_manager: Description
    :param raw_data: Description
    '''

    for node_dict in raw_data:
        node_id, seq, timestamp, lat, lon, altitude_m = extract_node_data(node_dict)
        node_manager.upsert_node(node_id, seq, timestamp, lat, lon, altitude_m)


def debug_print_table(node_manager):
    '''
    Docstring for debug_print_table
    
    :param node_manager: Description
    '''
    print("Current state of nodes table:")
    nodes = node_manager.get_all_nodes()

    for node in nodes:
        print(f"Node ID: {node.node_id}, Seq: {node.seq}, Status: {node.status}, First Seen: {node.first_seen}, Last Seen: {node.last_seen}, location: ({node.location_lat}, {node.location_lon}, {node.location_altitude_m})")


def debug_print(message):
    '''Docstring for debug_print :param message: Description'''

    if DEBUG:
        print(message)


def main():
    '''Docstring for main'''
    node_manager = NodeManager()

    raw_data = load_json(file_path)
    process_nodes(node_manager, raw_data)
    debug_print_table(node_manager)
    print(("Inactive nodes in database after processing:",node_manager.get_inactive_nodes()))


main()
