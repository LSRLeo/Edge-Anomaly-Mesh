"""
Message Class
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging


from db_table_manager import TableManager
from queries import get_nodes,get_nodes,get_node_data_ids,get_datum, get_recent_inference, get_recent_raw_data,get_recent_raw_data

ERROR_CODES = ["NOT_FOUND", "INVALID_REQUEST", "INTERNAL_ERROR"]

"""
MESSAGE FORMAT:
{
"m_type": 
"m_id":
"responding_to":
...
}
"""


class MIDGenerator:
    """Generates MID for db responses"""
    counter = 0 #this is the class var (static)
    M_ID_PREFIX = "db_"

    @classmethod
    def generate_m_id(cls):
        cls.counter +=1
        return f"{cls.M_ID_PREFIX}{cls.counter:05d}" #zero pad to 5 digits
    

class Message(ABC):
    """
    Message Base Class
    
    Args: message_id (str): The unique identifier for the message.
        message_id (str): The unique identifier for the message.
        msg (Dict[str, Any], optional): The original message dictionary. Defaults to None.
        M_TYPE (str): m_type of message, class constant, to be defined in subclasses. Handle Error if not defined in constructor.
        m_type (str): m_type of message, instance variable, initialized to M_TYPE in constructor.
    """
    M_TYPE: str = None 


    def __init__(self, m_id: str, msg: Dict[str, Any] = None):

        if self.M_TYPE is None:
            raise NotImplementedError("M_TYPE must be defined in subclasses")
        
        self.m_type = self.M_TYPE
        self.m_id = m_id 
        self.msg = msg #original message 


    # m_type is now a direct attribute
    

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary.
        Returns:
            A dictionary representation of the message.
        """
        return {
            **self.msg
        }
    

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(m_id='{self.m_id}', m_type='{self.m_type}')"
    

class MessageResponse(Message):
    """
        Initialize response message.
        
        Args:
            m_id: Response message ID
            m_type: Response message type (e.g., 'get-nodes-response')
            responding_to: Original request message ID
            result: Dictionary containing query results
        
    Message Response does not have a fixed M_TYPE, (it can be either get-nodes-response or get-datum-response or others)
    """

    def __init__(self, m_type: str, m_id: str, responding_to: str, result: Dict[str, Any]):
        self.M_TYPE = m_type  # override M_TYPE in constructor
        super().__init__(m_id)
        self.msg = {
            "m_type": self.m_type,
            "m_id": m_id,
            "responding_to": responding_to,
            **result
        }
        
        #super().__init__(m_id, self.msg)
        
    def get_responding_to(self) -> str:
        """Get the ID of the original message that this is responding to."""
        return self.responding_to
    

class ErrorResponse(Message):
    M_TYPE = "error"  # Fixed type for all errors
    """
    {
    "m_type": "error",
    "m_id": "db_00099",
    "responding_to": "ui_00001",
    "original_request": "get-datum",
    "error_code": "NOT_FOUND",
    "error_message": "Event ID not found"
    }
    """

    def __init__(self, m_id: str, responding_to: str, original_request: str, error_message: str, error_code: str = "INTERNAL_ERROR"):
        """
        Initialize error response.
        m_type is automatically set to "error" and cannot be changed.
        
        Args:
            m_id: Error message ID
            responding_to: Original message ID that caused error
            original_request: The original m-type that caused the error
            error_code: Error code (NOT_FOUND, INVALID_REQUEST, INTERNAL_ERROR)
            error_message: Human-readable error description
        """

        if error_code not in ERROR_CODES:
            logging.warning(f"Invalid error code '{error_code}' provided. Defaulting to 'INTERNAL_ERROR'.")
            error_code = "INTERNAL_ERROR"

        self.msg = {
            "m_type": self.M_TYPE,
            "m_id": m_id,
            "responding_to": responding_to,
            "original_request": original_request,
            "error_code": error_code,
            "error_message": error_message
        }
        
        super().__init__(m_id, self.msg)


class MessageRequest(Message):
    '''
    Abstract class for message requests.
    '''   
    @abstractmethod
    def execute(self) -> MessageResponse | ErrorResponse:
        """
        Execute the message and return the result. Returns: Dict of query reults for message requests"""
        pass


class MessageData(Message):
    '''
    Abstract class for message data. Messages that do not return any response. 
    '''   
    @abstractmethod
    def execute(self, db_manager: TableManager) -> None:
        """Inserts Data into the DB"""
        pass


class RawDataMessage(MessageData):
    M_TYPE = "raw-data"

    def __init__(self, m_id: str, msg: Dict[str, Any]):
        #confirm if there is multiple raw data records. For now, just pass the whole messge dict
        super().__init__(m_id, msg)
        
        try:
            self.records = msg.get("records", None)  # Expecting a list of raw data records under "records" key
            if self.records is None:
                #just no records field wrap msg in a list and treat as single record
                #logging.warning(f"No 'records' field found in raw data message. Treating entire message as a single record.")
                self.records = [msg]

            elif not isinstance(self.records, list):
                #logging.warning(f"'records' field is not a list. Wrapping it in a list.")
                self.records = [self.records]

        except Exception as e:
            logging.error(f"Error processing raw data message content: {e}")
            self.records = [msg]  # Default to treating entire message as a single record
                
    def execute(self, db_manager: TableManager) -> Optional[ErrorResponse]:
        """
        Process the raw data and store it in the database.
        """
        try:
            db_manager.insert_raw_data(self.records) 
            logging.info(f"Successfully stored raw data")

            return None  # Indicate successful execution
        
        except Exception as e:
            logging.error(f"Error storing raw data: {e}")


class InferenceOutputMessage(MessageData):
    M_TYPE = "inference-output"

    def __init__(self, m_id: str, msg: Dict[str, Any]):
        super().__init__(m_id, msg)
        self.log = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        try:
            self.records = msg.get("records", None)  # Expecting a list of raw data records under "records" key
            if self.records is None:
                #just no records field wrap msg in a list and treat as single record
                #self.log.info(f"No 'records' field found in inference output message. Treating entire message as a single record.")
                self.records = [msg]

            elif not isinstance(self.records, list):
                #self.log.info(f"'records' field is not a list. Wrapping it in a list.")
                self.records = [self.records]

        except Exception as e:
            self.log.error(f"Error processing inference output message content: {e}")
            self.records = [msg]  # Default to treating entire message as a single record
                
    def execute(self, db_manager: TableManager) -> None:
        """
        Process the inference output data and store it in the database.
        """
        try:
            #store_inference_result(self.records)
            db_manager.insert_inference_results(self.records)
            self.log.info(f"Successfully stored inference output for {self.msg.get('node_id')} at timestamp {self.msg.get('timestamp')}")
            return None  # Indicate successful execution
        
        except Exception as e:
            self.log.error(f"Error storing inference output: {e}")

class GetNodesRequest(MessageRequest):
    M_TYPE = "get-nodes"
    
    def execute(self) -> MessageResponse | ErrorResponse:
        """
        Execute the get-nodes query and return the result. Returns: MessageResponse containing the list of nodes or an ErrorResponse if execution fails.
        """
        
        logging.info("Executing get-nodes request")

        try: 
            node_ids = get_nodes()  
            logging.info(f"Retrieved nodes: {node_ids}")

            return MessageResponse(
                m_type="get-nodes-response",
                m_id=MIDGenerator.generate_m_id(), 
                responding_to=self.m_id,
                result={"nodes": node_ids})
        
        except Exception as e:
            logging.error(f"get-nodes request failed: {e}")
            return ErrorResponse(
                m_id=MIDGenerator.generate_m_id(),
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INTERNAL_ERROR"
            )


class GetNodeDataIdsRequest(MessageRequest):
    M_TYPE = "get-node-data-ids"

    def execute(self) -> MessageResponse | ErrorResponse:

        try:
            self.node_id = self.msg.get("node_id", None)
            logging.info(f"Executing get-node-data-ids for node: {self.node_id}")

            if self.node_id is None:
                raise ValueError("Missing required field: node_id")

            data_ids = get_node_data_ids(self.node_id)

            if data_ids is None:

                return ErrorResponse(
                    m_id=MIDGenerator.generate_m_id(),
                    responding_to=self.m_id,
                    original_request=self.m_type,
                    error_message=f"Node not found: {self.node_id}",
                    error_code="NOT_FOUND",
                )

            return MessageResponse(
                m_type="get-node-data-ids-response",
                m_id=MIDGenerator.generate_m_id(),
                responding_to=self.m_id,
                result={"node_id": self.node_id, "data_ids": data_ids},
            )

        except ValueError as e:

            return ErrorResponse(
                m_id=MIDGenerator.generate_m_id(),
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INVALID_REQUEST",
            )
        
        except Exception as e:
            logging.error(f"get-node-data-ids failed: {e}")

            return ErrorResponse(
                m_id=MIDGenerator.generate_m_id(),
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INTERNAL_ERROR",
            )

class GetDatumRequest(MessageRequest):
    M_TYPE = "get-datum"

    def execute(self) -> MessageResponse | ErrorResponse:
        
        try:
            self.event_id = self.msg.get("event_id", None)

            if self.event_id is None:
                raise ValueError("Missing required field: event_id")
            
            logging.info(f"Executing get-datum for event: {self.event_id}")
            result = get_datum(self.event_id)

            if result is None:
                return ErrorResponse(
                    m_id=MIDGenerator.generate_m_id(),
                    responding_to=self.m_id,
                    original_request=self.m_type,
                    error_message=f"Event ID not found: {self.event_id}",
                    error_code="NOT_FOUND",
                )

            return MessageResponse(
                m_type="get-datum-response",
                m_id=MIDGenerator.generate_m_id(),
                responding_to=self.m_id,
                result=result
            )

        except ValueError as e:

            return ErrorResponse(
                m_id=MIDGenerator.generate_m_id(),
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INVALID_REQUEST",
            )
        
        except Exception as e:
            logging.error(f"get-datum failed: {e}")

            return ErrorResponse(
                m_id=MIDGenerator.generate_m_id(),
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INTERNAL_ERROR",
            )



class GetRecentRawDataRequest(MessageRequest):
    M_TYPE = "get-recent-raw-data"

    def execute(self) -> MessageResponse | ErrorResponse:
        

        try:
            self.node_id = self.msg.get("node_id", None)

            if not self.node_id:
                raise ValueError("Missing required field: node_id")
            
            logging.info(f"Executing get-recent-raw-data for node: {self.node_id}")
            row = get_recent_raw_data(self.node_id)

            if row is None:

                return ErrorResponse(
                    m_id=MIDGenerator.generate_m_id(),
                    responding_to=self.m_id,
                    original_request=self.m_type,
                    error_message=f"No raw data found for node: {self.node_id}",
                    error_code="NOT_FOUND",
                )
            
            if not isinstance(row, list):
                result = {"node_id": self.node_id, **row}

            else:
                result = {"node_id": self.node_id, "records": row}

            return MessageResponse(
                m_type="get-recent-raw-data-response",
                m_id=MIDGenerator.generate_m_id(),
                responding_to=self.m_id,
                result=result,
            )
        
        except ValueError as e:

            return ErrorResponse(
                m_id=MIDGenerator.generate_m_id(),
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INVALID_REQUEST",
            )
        
        except Exception as e:
            logging.error(f"get-recent-raw-data failed: {e}")

            return ErrorResponse(
                m_id=MIDGenerator.generate_m_id(),
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INTERNAL_ERROR",
            )


class GetRecentInferenceRequest(MessageRequest):

    M_TYPE = "get-recent-inference"

    def execute(self) -> MessageResponse | ErrorResponse:
       
        try:
            self.node_id = self.msg.get("node_id", None)
            
            if not self.node_id:
                raise ValueError("Missing required field: node_id")
            
            logging.info(f"Executing get-recent-inference for node: {self.node_id}")
            row = get_recent_inference(self.node_id)

            if row is None:
                return ErrorResponse(
                    m_id=MIDGenerator.generate_m_id(),
                    responding_to=self.m_id,
                    original_request=self.m_type,
                    error_message=f"No inference data found for node: {self.node_id}",
                    error_code="NOT_FOUND",
                )
            #if multiple rows, can do list comprehension to serialize each row and return list
            if not isinstance(row, list):
                result = {"node_id": self.node_id, **row}

            else:
                result = {"node_id": self.node_id, "records": row}
            
            return MessageResponse(
                m_type="get-recent-inference-response",
                m_id=MIDGenerator.generate_m_id(),
                responding_to=self.m_id,
                result=result,
            )

        except ValueError as e:
            return ErrorResponse(
                m_id=MIDGenerator.generate_m_id(),
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INVALID_REQUEST",
            )
        
        except Exception as e:
            logging.error(f"get-recent-inference failed: {e}")
            return ErrorResponse(
                m_id=MIDGenerator.generate_m_id(),
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INTERNAL_ERROR",
            )


