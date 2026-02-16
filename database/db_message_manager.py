'''
Docstring for database.db_message_manager
m_Types: 'raw-data', 'inference-output', 'get-nodes', 'get-nodes-response','get-node-data-ids', 'get-node-data-ids-response', 'get-datum', 'get-datum-response', 'Error'
'''
from asyncio.log import logger
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

    def process_message(self,message:dict):
        m_type = message.get('m_type')
        recieved_m_id = message.get('m_id')
        handler = self.handlers.get(m_type)

        logging.info("Processing message with m_id: %s and m_type: %s", recieved_m_id, m_type)

        if handler:
            logging.info("Found handler for m_type: %s, processing message with m_id: %s", m_type, recieved_m_id)
            handler()
            #send to appropriate handler based on m_type and either it gets a dict to respond with or it just processes the message and updates the database accordingly
        
        else:
            logging.warning("No handler found for m_type: %s, message with m_id: %s cannot be processed", m_type, recieved_m_id)

    def validate_message(self, message: dict) -> bool:
        """Validates structure is a dictionary and contains required fields 'm_type' and 'm_id'"""

        if not isinstance(message, dict):
            logging.error("Message is not a dictionary")
            return False
            
        if 'm_type' not in message:
            logging.error("Message missing 'm_type' field")
            return False
        
        if 'm_id' not in message:
            logging.error("Message missing 'm_id' field")
            return False
        
        return True
    

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
    test_message = {
        "m_type": "get-nodes",
        "m_id": "ui_00001"
    }
    test_message_json = json.loads(test_message)
    
    logging.info("Testing message validation with invalid message")
    test_message = "message without proper structure"
    db_message_manager.validate_message(test_message)
    invalid_message = {"m_type": "raw-data"}
    db_message_manager.validate_message(invalid_message)
    invalid_message2 = {"m_id": "12345"}
    db_message_manager.validate_message(invalid_message2)
    valid_message = {"m_type": "raw-data", "m_id": "12345"}
    is_valid = db_message_manager.validate_message(valid_message)
    logging.info("Valid message validation result: %s", is_valid)
