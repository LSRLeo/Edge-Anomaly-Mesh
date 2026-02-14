'''
Docstring for database.db_message_manager
m_Types: 'raw-data', 'inference-output', 'get-nodes', 'get-nodes-response','get-node-data-ids', 'get-node-data-ids-response', 'get-datum', 'get-datum-response', 'Error'
'''
import logging
import json
import sys

#logging for debugging purposes
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

class DBMessageManager:
    '''
    DB Message Manager class to handle incoming messages related to database operations. It registers handlers for different message types and processes them accordingly.
    '''


    def __init__(self):
        self.handlers = {}
        self._register_handlers()
        logging.info("DBMessageManager initialized with handlers: %s", list(self.handlers.keys()))


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
        }


    def handle_raw_data(self):
        pass


    def handle_inference_output(self):
        pass


    def handle_get_nodes(self):
        pass


    def handle_get_nodes_response(self):
        pass


    def handle_get_node_data_ids(self):
        pass


    def handle_get_node_data_ids_response(self):
        pass


    def handle_get_datum(self):
        pass


    def handle_get_datum_response(self):
        pass


    def handle_error(self):
        pass


if __name__ == "__main__":
    db_message_manager = DBMessageManager()
    logging.info("DBMessageManager instance created: %s", db_message_manager)
