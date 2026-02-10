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
        """Register all message type handlers"""
        self.handlers = {
            'raw-data': self.handle_raw_data,
            'inference-output': self.handle_inference_output,
            'get-nodes': self.handle_get_nodes,
            'get-nodes-response': self.handle_get_nodes_response,
            'get-node-data-ids': self.handle_get_node_data_ids,
            'get-node-data-ids-response': self.handle_get_node_data_ids_response,
            'get-datum': self.handle_get_datum,
            'get-datum-response': self.handle_get_datum_response,
            'error': self.handle_error
        } #would it be better to call the methods by their message type or have handle before?


    def process_message(self,message):
        pass


    def validate_message(self,message):
        pass
    
    def handle_raw_data(self,message):
        pass


    def handle_inference_output(self,message):
        pass


    def handle_get_nodes(self,message):
        pass


    def handle_get_nodes_response(self,message):
        pass


    def handle_get_node_data_ids(self,message):
        pass


    def handle_get_node_data_ids_response(self,message):
        pass


    def handle_get_datum(self,message):
        pass


    def handle_get_datum_response(self,message):
        pass


    def handle_error(self,message):
        pass


#read .json file and process it
