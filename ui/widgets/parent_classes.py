from inspect import isabstract
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

class DashboardParents:
    def __init__(self, redis_reader, parent: ttk.Notebook, dashboard: 'DashboardApp'):

        self.redis_reader = redis_reader
        self. dashboard = dashboard
    
    @abstractmethod
    def refresh(self):
        pass

    @abstractmethod
    def parse_node(self):
        pass


class Node:
    motion_states = ["IDLE", "TERRESTRIAL", "MARITIME", "LIFT", "IDLE_ANOMALY", "TERRESTRIAL_ANOMALY", "MARITIME_ANOMALY", "LIFT_ANOMALY"] #key for motion class index to string
    def __init__(self, node_id: str, lat: float, lon: float, timestamp: datetime, motion_class: int, anomaly: bool, confidence: float):
        self.node_id = node_id
        self.lat = lat
        self.lon = lon
        self.timestamp = timestamp
        self.motion_class = motion_class
        self.anomaly = anomaly
        self.confidence = confidence
        self.anomaly = anomaly
        self.motion_states = ["IDLE", "TERRESTRIAL", "MARITIME", "LIFT", "IDLE_ANOMALY", "TERRESTRIAL_ANOMALY", "MARITIME_ANOMALY", "LIFT_ANOMALY"] #key for motion class index to string
    def updateTimestamp(self):
        self.timestamp = datetime.now()
    def updateMotion(self, motion_class, confidence: float):
        if isinstance(motion_class, int):
            self.motion_class = motion_class
        if isinstance(motion_class, str):
            if motion_class in self.motion_states:
                self.motion_class = self.motion_states.index(motion_class)
            else:                raise ValueError(f"Invalid motion class string: {motion_class}")
        self.confidence = confidence
    def __str__(self):
        return f"Node({self.node_id}, {self.lat}, {self.lon}, {self.timestamp}, {self.motion_class}, {self.confidence})"
    def getNodeID(self):
        return self.node_id
    def getCoords(self):
        return (self.lat, self.lon)
    def getTimestamp(self):
        return self.timestamp
    def getMotion(self):
        return (self.motion_class, self.confidence)
    def toDict(self): #returns a dictionary representation of the node for easy access
        return {
            'node_id': self.node_id,
            'lat': self.lat,
            'lon': self.lon,
            'timestamp': self.timestamp,
            'motion_class': self.motion_class,
            'anomaly': self.anomaly,
            'confidence': self.confidence
        }
    def motionString(self): #returns the motion class as a string for the user
        return self.motion_states[self.motion_class]  

