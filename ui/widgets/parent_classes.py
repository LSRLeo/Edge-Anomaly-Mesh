from inspect import isabstract
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import Optional

from redis_reader import RedisReader

class DashboardParents():
    def __init__(self, redis_reader: Optional[RedisReader], parent: ttk.Notebook, dashboard: 'DashboardApp', test_mode=False):
        if redis_reader is None:
            redis_reader = None
        self.redis_reader = redis_reader
        self. dashboard = dashboard
        self.test_mode = test_mode
    
    @abstractmethod
    def refresh(self):
        pass

    @abstractmethod
    def parse_node(self):
        pass


class Node:
    motion_states = ["IDLE", "TERRESTRIAL", "MARITIME", "LIFT", "IDLE_ANOMALY", "TERRESTRIAL_ANOMALY", "MARITIME_ANOMALY", "LIFT_ANOMALY"] #key for motion class index to string
    def __init__(self, node_id: str, timestamp:str, seq, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, lat: float, lon: float, motion_class: int, anomaly: bool, confidence: float):
        self.node_id = node_id
        self.timestamp = timestamp
        self.seq = seq
        self.accel_x = accel_x
        self.accel_y = accel_y
        self.accel_z = accel_z
        self.gyro_x = gyro_x
        self.gyro_y = gyro_y
        self.gyro_z = gyro_z
        self.lat = lat
        self.lon = lon
        self.motion_class = motion_class
        self.anomaly = anomaly
        self.confidence = confidence
        self.motion_states = ["IDLE", "TERRESTRIAL", "MARITIME", "LIFT", "IDLE_ANOMALY", "TERRESTRIAL_ANOMALY", "MARITIME_ANOMALY", "LIFT_ANOMALY"] #key for motion class index to string
    def updateMotion(self, motion_class, confidence: float):
        if isinstance(motion_class, int):
            self.motion_class = motion_class
        if isinstance(motion_class, str):
            if motion_class in self.motion_states:
                self.motion_class = self.motion_states.index(motion_class)
            else:                raise ValueError(f"Invalid motion class string: {motion_class}")
        self.confidence = confidence
    def __str__(self):
        return f"Node {self.node_id}: ({self.lat}, {self.lon}) - Motion: {self.getMotionString()} (Confidence: {self.confidence:.2f})"
    def getNodeID(self):
        return self.node_id
    def getCoords(self):
        return (self.lat, self.lon)
    def getTimestamp(self)->str:
        return self.timestamp
    def getMotion(self):
        return (self.motion_class, self.confidence)
    def toDict(self): #returns a dictionary representation of the node for easy access
        return {
            'node_id': self.node_id,
            'timestamp': self.timestamp,
            'seq': self.seq,
            'accel_x': self.accel_x,
            'accel_y': self.accel_y,
            'accel_z': self.accel_z,
            'gyro_x': self.gyro_x,
            'gyro_y': self.gyro_y,
            'gyro_z': self.gyro_z,
            'lat': self.lat,
            'lon': self.lon,
            'motion_class': self.motion_class,
            'anomaly': self.anomaly,
            'confidence': self.confidence
        }
    def getMotionString(self): #returns the motion class as a string for the user
        return self.motion_states[self.motion_class]  

