'''
Docstring for database.db_message_manager
m_Types: 'raw-data', 'inference-output', 'get-nodes', 'get-nodes-response','get-node-data-ids', 'get-node-data-ids-response', 'get-datum', 'get-datum-response', 'error'

TWO USAGE SCENARIOS:
1) sample usage, uses sample_message_data.json and sample_message_requests.json and writes results to sample_message_responses.json
2) send custom messages with python db_message_manager.py --infile <path_to_input_messages.json> --outfile <path_to_output_responses.json>
'''

import logging
import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List

from db_message_factory import MessageFactory
from db_table_manager import TableManager
from schema import create_schema

#logging for debugging purposes
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')

#default file paths for sample messages
SAMPLE_DATA_FILE = Path(__file__).parent / "example-data/sample_message_data.json"
SAMPLE_REQUEST_FILE  = Path(__file__).parent / "example-data/sample_message_requests.json"
SAMPLE_RESPONSE_FILE = Path(__file__).parent / "example-data/sample_message_responses.json"
NO_RESPONSE = ["raw-data", "inference-output"] #message types that do not generate responses 
class DBMessageManager:
    '''
    DB Message Manager class to handle incoming messages related to database operations. It registers handlers for different message types and processes them accordingly.
    '''


    def __init__(self):
        create_schema()  # Ensure database schema is created - caused issue so lets assume it is already created
        self.table_manager = TableManager()
        logging.info("DBMessageManager initialized and database schema created")


    def process_message(self, message:Dict[str, Any]):
        """Processes incoming message and creates message objects"""

     
        message_obj = MessageFactory.create_message(message)
        
        if message_obj is None:
            m_id   = message.get("m_id",   "unknown") if isinstance(message, dict) else "unknown"
            m_type = message.get("m_type", "unknown") if isinstance(message, dict) else "unknown"
            logging.error("Factory could not create message  m_id=%s  m_type=%s", m_id, m_type)
            return {
                "m_id":             f"error_{m_id}",
                "m_type":           "error",
                "responding_to":    m_id,
                "original_request": m_type,
                "error_code":       "INVALID_REQUEST",
                "error_message":    (
                    "Failed to create message object. "
                    "Invalid message format or unknown message type."
                ),
            }
        #GET RESULTS
        if message_obj.M_TYPE in NO_RESPONSE:
            message_obj.execute(self.table_manager)
            return None
        else:
            results = message_obj.execute()
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
            return responses
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
   
    manager = DBMessageManager()
    data_msg_responses = manager.read_file(SAMPLE_DATA_FILE, SAMPLE_RESPONSE_FILE)

    if data_msg_responses:
        #Errors
        print(f"{len(data_msg_responses)} messages from {SAMPLE_DATA_FILE} processed with responses written to {SAMPLE_RESPONSE_FILE}")

    request_msg_responses = manager.read_file(SAMPLE_REQUEST_FILE, SAMPLE_RESPONSE_FILE)

    if request_msg_responses:
        print(f"{len(request_msg_responses)} queries responses written to {SAMPLE_RESPONSE_FILE}")

    
    print(f"\n{'=' * 65}")
    print(f"\tDone")
    print(f"{'=' * 65}\n")


#CLI
def send_message(infile: str, outfile: str) -> None:
    """
    Process all messages in infile and write responses to outfile.

    Called by the argparse CLI when --infile and --outfile are both supplied.

    Example:
        python db_message_manager.py --infile my_messages.json --outfile my_responses.json, outfile will be overwritten if it already exists.
    """
    manager = DBMessageManager()
    responses = manager.read_file(infile, outfile)
 
    print(
        f"\n  Processed '{Path(infile).name}' "
        f"  {len(responses)} response(s) written to '{outfile}'"
        )
    


if __name__ == "__main__":
    #set up argparse for CLI usage
    parser = argparse.ArgumentParser(
        description="Process JSON message files through the DB message pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples--------
        # Built-in demo (no arguments required):
            python db_message_manager.py
        # Custom files via CLI (send_message mode):
            python db_message_manager.py --infile my_messages.json --outfile my_responses.json
        """,
    )

    parser.add_argument(
        "--infile",
        type=str,
        default=None,
        help="Path to input JSON file (single message dict or list of dicts).",
    )

    parser.add_argument(
        "--outfile",
        type=str,
        default=None,
        help="Path to output JSON file where responses will be written/appended.",
    )

    args = parser.parse_args()

    if args.infile and args.outfile:
        # CLI / send_message mode
        send_message(args.infile, args.outfile)
    elif args.infile or args.outfile:
        # Only one flag — that's an error
        parser.error("Both --infile and --outfile must be supplied together.")
    
        # No flags → built-in sample usage
        #run_sample_usage()






