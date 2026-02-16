'''
Docstring for database.db_message_manager
m_Types: 'raw-data', 'inference-output', 'get-nodes', 'get-nodes-response','get-node-data-ids', 'get-node-data-ids-response', 'get-datum', 'get-datum-response', 'Error'
'''
from asyncio.log import logger
from email import message
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
            'get-node-data-ids': self.handle_get_node_data_ids,
            'get-datum': self.handle_get_datum,  
        }

    def process_message(self, message:dict):
        """Processes incoming message and routes it to the appropriate handler after calling validation"""

        if self.validate_message(message):
            m_type = message.get('m_type')
            recieved_m_id = message.get('m_id')
            handler = self.handlers.get(m_type)

            if handler:
                logging.info("Found handler for m_type: %s, processing message with m_id: %s", m_type, recieved_m_id)
                #call handler function
                handler(message)

            else:
                logging.error("No handler found for m_type: %s, message with m_id: %s cannot be processed", m_type, recieved_m_id)
                return

        else:
            #Handle error and send error response
            logging.error("Message failed validation and will not be processed")
            return
        
        

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
    

    def handle_raw_data(self, message: dict):
        logger.info(f"Handling raw-data message: {message['m_id']} inserts raw data into the databases")


    def handle_inference_output(self, message: dict):
        logger.info(f"Handling inference-output message: {message['m_id']} inserts inference output into the databases")


    def handle_get_nodes(self, message: dict):
        logger.info(f"Handling get-nodes request: {message['m_id']} returns message of type get-nodes-response") 
        


    def handle_get_node_data_ids(self, message: dict):
        logger.info(f"Handling get-node-data-ids request: {message['m_id']} returns message of type get-node-data-ids-response")

    def handle_get_datum(self, message: dict):
        logger.info(f"Handling get-datum request: {message['m_id']} returns message of type get-datum-response")



    def handle_error(self):
        logger.error(f"sends error response to sender")


if __name__ == "__main__":
    db_message_manager = DBMessageManager()
    # logging.info("DBMessageManager instance created: %s", db_message_manager)
    test_message = '''{
        "m_type": "inference-output",
        "m_id": "ui_00001"
    }'''
    test_message_json = json.loads(test_message)
    testing_result = db_message_manager.process_message(test_message_json)

