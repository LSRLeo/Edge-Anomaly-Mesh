"""
Docstring for database.db_message_manager
m_Types: 'raw-data', 'inference-output', 'get-nodes', 'get-nodes-response','get-node-data-ids', 'get-node-data-ids-response', 'get-datum', 'get-datum-response', 'Error'
"""
import json
import os
import ijson 

class DBMessageManager:
    '''
    Docstring for DBMessageManager
    '''

    def __init__(self):
        self.handlers = {}
        self._register_handlers()

    
    def _register_handlers(self):
        pass


    def process_message(self,message):
        pass


    def validate_message(self,message):
        pass
    #handler functions for each message type

#read .json file and process it
