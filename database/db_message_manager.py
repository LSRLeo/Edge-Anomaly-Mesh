'''
Docstring for database.db_message_manager
m_Types: 'raw-data', 'inference-output', 'get-nodes', 'get-nodes-response','get-node-data-ids', 'get-node-data-ids-response', 'get-datum', 'get-datum-response', 'error'

TWO USAGE SCENARIOS:
1) sample usage, uses sample_message_data.json and sample_message_requests.json and writes results to sample_message_responses.json
2) send own messages with python db_message_manager.py --infile <path_to_input_messages.json> --outfile <path_to_output_responses.json>
'''
from asyncio.log import logger
from email import message
import logging
import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

from db_message_factory import MessageFactory
from db_table_manager import TableManager
from schema import create_schema

#logging for debugging purposes
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

#default file paths for sample messages
SAMPLE_DATA_FILE     = Path("sample_message_data.json")
SAMPLE_REQUEST_FILE  = Path("sample_message_requests.json")
SAMPLE_RESPONSE_FILE = Path("sample_message_responses.json")

class DBMessageManager:
    '''
    DB Message Manager class to handle incoming messages related to database operations. It registers handlers for different message types and processes them accordingly.
    '''


    def __init__(self):
        #create_schema()  # Ensure database schema is created - caused issue so lets assume it is already created
        self.table_manager = TableManager()
        logging.info("DBMessageManager initialized and database schema created")


    def process_message(self, message:Dict[str, Any]):
        """Processes incoming message and creates message objects"""

        #Could validate message here too and then remove m_id and m_type before passing to message factory, but message factory already does validation and we want to avoid copying the dict if possible, so we'll just pass the original dict to the message factory and let it handle validation and object creation.
        message_obj = MessageFactory.create_message(message)
        if message_obj is None:
            return MessageFactory.create_message({
                "m_id": "error_" + message.get("m_id", "unknown"),
                "m_type": "error",
                "error": "Failed to create message object. Invalid message format or unknown message type."
            })
        #GET RESULTS
        results = message_obj.execute(self.table_manager)
        return results.to_dict() if results else None

    def read_file(self, infile: str | Path, outfile: str | Path):
        """Processes messages from an input file and writes responses to an output file."""
        infile  = Path(infile)
        outfile = Path(outfile)

        try:
            with open(infile, "r") as f:
                data = json.load(f)
                messages = data if isinstance(data, list) else [data]

            responses = []
            for message in messages:
                response = self.process_message(message)

                if response:
                    responses.append(response)

            self._write_responses(responses, outfile)

        except FileNotFoundError:
            logging.error("Input file not found: %s", infile)
            return []
        
        except json.JSONDecodeError as e:
            logging.error("JSON parse error in %s : %s", infile, e)
            return []

    def _write_responses(self, responses: list[Dict[str, Any]], outfile: str | Path):
        """Writes responses to an output file."""
        outfile = Path(outfile)
        try:
            with open(outfile, "w") as f:
                json.dump(responses, f, indent=2)
        except FileNotFoundError:
            logging.error("Output file not found: %s", outfile)
            return []
        except json.JSONDecodeError as e:
            logging.error("JSON parse error in %s : %s", outfile, e)
            return []

    #VALIDATE is done in message factory
    def validate_message(self, message: Dict[str, Any]) -> bool:
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
    
def run_sample_usage():
    """demonstrates usage with sample files. Reads sample_message_data.json and populates database,
    then eads sample_message_requests.json, Runs: get-nodes, get-node-data-ids, get-datum queries against the DB.
    Every query response is appended to sample_message_responses.json"""
    #EMPTY response file before writing new responses
    print("\n\n\n\n  DB MESSAGE MANAGER — SAMPLE USAGE")
    print("=" * 65)
    #EMPTY response file before writing new responses
   
    db_message_manager = DBMessageManager()
    data_msg_responses = db_message_manager.read_file(SAMPLE_DATA_FILE, SAMPLE_RESPONSE_FILE)

    if data_msg_responses:
        #Errors
        print(f"{len(data_msg_responses)} messages from {SAMPLE_DATA_FILE} processed with responses written to {SAMPLE_RESPONSE_FILE}")

    request_msg_responses = db_message_manager.read_file(SAMPLE_REQUEST_FILE, SAMPLE_RESPONSE_FILE)

    if request_msg_responses:
        print(f"{len(request_msg_responses)} queries responses written to {SAMPLE_RESPONSE_FILE}")

    
    print(f"\n{'=' * 65}")
    print(f"\tDone")
    print(f"{'=' * 65}\n")

if __name__ == "__main__":
    db_message_manager = DBMessageManager()
    # logging.info("DBMessageManager instance created: %s", db_message_manager)
    run_sample_usage()
    