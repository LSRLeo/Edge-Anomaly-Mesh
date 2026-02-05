# Standard library imports
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

# Third-party imports
import numpy as np
import pytest
import pysqlite3
# Local imports


# Constants
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'sample_raw_data.json')
DEBUG = True


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
                status TEXT default 'active',
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
