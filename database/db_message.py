"""
Message Class
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging


ERROR_CODES = ["NOT_FOUND", "INVALID_REQUEST", "INTERNAL_ERROR"]
M_ID_DB = "db_message_id" #temp id for DB messages, to be replaced by actual message ID generation logic

class Message(ABC):
    """
    Message Base Class
    
    Args: message_id (str): The unique identifier for the message.
        message_id (str): The unique identifier for the message.
        content (Dict[str, Any], optional): The content of the message. Defaults to None.
        M_TYPE (str): m_type of message, class constant, to be defined in subclasses. Handle Error if not defined in constructor.
        _m_type (str): m_type of message, private instance variable, initialized to M_TYPE in constructor.
    """
    M_TYPE: str = None 


    def __init__(self, m_id: str, m_content: Dict[str, Any] = None):

        if self.M_TYPE is None:
            raise NotImplementedError("M_TYPE must be defined in subclasses")
        
        self._m_type = self.M_TYPE #private
        self.m_id = m_id 
        self.m_content = m_content #


    @property
    def m_type(self) -> str:
        """Get the m_type of the message.""" 
        return self._m_type
    

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary.
        
        Returns:
            A dictionary representation of the message.
        """
        return {
            "m_id": self.m_id,
            "m_type": self.m_type,
            **self.m_content
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
            results: Dictionary containing query results
        
    Message Response does not have a fixed M_TYPE, (it can be either get-nodes-response or get-datum-response or others)
    """


    def __init__(self, m_id: str, responding_to: str, m_type: str, results: Dict[str, Any]):
        self.responding_to = responding_to 
        self.results = results
        self.M_TYPE = m_type #override M_TYPE in constructor
        
        super().__init__(m_id, self.results)

    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for publishing"""
        return {
            "m_id": self.m_id,
            "m_type": self.m_type,
            "responding_to": self.responding_to,
            **self.results
        }


class ErrorResponse(MessageResponse):
    M_TYPE = "Error"  # Fixed type for all errors


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

        results = {
            "original_request": responding_to,
            "error_code": error_code,
            "error_message": error_message
        }
        
        super().__init__(m_id, self.M_TYPE, responding_to, results)
        self.original_request = original_request
        self.error_code = error_code
        self.error_message = error_message


class MessageRequest(Message):
    '''
    Abstract class for message requests.
    '''   
    @abstractmethod
    def execute(self, db_manager) -> MessageResponse:
        """
        Execute the message and return the result.
        
        Returns:
            Dict for message requests and None for message responses. 
        """
        pass


class MessageData(Message):
    '''
    Abstract class for message data.
    '''   
    @abstractmethod
    def execute(self, db_manager):
        """
        Execute the message and return the result.
        
        Returns:
            ErrorResponse if execution fails, otherwise None. 
        """
        pass


class RawDataMessage(MessageData):
    M_TYPE = "raw-data"

    def __init__(self, m_id: str, raw_data: Dict[str, Any]):
        self.data = raw_data
        super().__init__(m_id, self.data)
        #Try to get event_id and node_id
        self.event_id = raw_data.get("event_id", None)
        self.node_id = raw_data.get("node_id", None)

    def execute(self, db_manager):
        """
        Process the raw data and store it in the database.
        
        Args:
            db_manager: The database manager instance to interact with the database.
        """
        logging.info(f"Executing raw-data storage for event: {self.event_id}")
        logging.info(f"Executing node storage for node: {self.node_id}")

        try:
            if not self.event_id or not self.node_id:
                logging.error("Missing event_id or node_id in raw data")
                raise ValueError("Missing event_id or node_id in raw data")
            # Store the processed data in the database
            #call correct methods to store in Node Table and RawData Table
            #TODO: Implement the actual storage logic in the db_manager
            logging.info(f"Successfully stored raw data for event: {self.event_id} and node: {self.node_id}")
            return None  # Indicate successful execution
        
        except Exception as e:
            return ErrorResponse(
                m_id=M_ID_DB,
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INVALID_REQUEST"
            )


class InferenceOutputMessage(MessageData):
    M_TYPE = "inference-output"

    def __init__(self, m_id: str, inference_output: Dict[str, Any]):
        
        super().__init__(m_id, inference_output)
        #Try to get event_id and node_id
        self.event_id = inference_output.get("event_id", None)
        self.node_id = inference_output.get("node_id", None)

    def execute(self, db_manager):
        """
        Process the inference output data and store it in the database.
        
        Args:
            db_manager: The database manager instance to interact with the database.
        """
        logging.info(f"Executing inference-output storage for event: {self.event_id}")
        logging.info(f"Executing node storage for node: {self.node_id}")

        try:
            if not self.event_id or not self.node_id:
                logging.error("Missing event_id or node_id in inference output data")
                raise ValueError("Missing event_id or node_id in inference output data")
            # Store the processed data in the database
            #call correct methods to store in Anomaly Table and InferenceOutput Table
            #TODO: Implement the actual storage logic in the db_manager
            logging.info(f"Successfully stored inference output for event: {self.event_id} and node: {self.node_id}")
            return None  # Indicate successful execution
        
        except Exception as e:
            return ErrorResponse(
                m_id=M_ID_DB,
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INVALID_REQUEST"
            )
        
class GetNodesRequest(MessageRequest):
    M_TYPE = "get-nodes"
    
    def execute(self, db_manager) -> MessageResponse:
        """
        Execute the get-nodes request and return the result.
        
        Args:
            db_manager: The database manager instance to interact with the database.
        
        Returns:
            MessageResponse containing the list of nodes or an ErrorResponse if execution fails.
        """
        #TODO: Implement the actual logic to retrieve nodes from the database using db_manager
        logging.info("Executing get-nodes request")

        try: 
            #TODO: Implement the actual logic to retrieve nodes from the database using db_manager
            logging.info("Executing get-nodes request")
            return MessageResponse(
                m_id=M_ID_DB,
                responding_to=self.m_id,
                m_type="get-nodes-response",
                results={"nodes": []}  # Placeholder for actual nodes data
                )
        
        except Exception as e:
            return ErrorResponse(
                m_id=M_ID_DB,
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INTERNAL_ERROR"
            )

"""
{
  "m_type": "get-node-data-ids-response",
  "m_id": "ui_00002",
  "node_id": "node_001",
  "data_ids": [
    "node_001_2026-01-22T18:52:14.818400",
    "node_001_2026-01-22T18:52:14.838400",
    "node_001_2026-01-22T18:52:14.858400"
  ]
}
"""
class GetNodeDataIdsRequest(MessageRequest):
    M_TYPE = "get-node-data-ids"

    def __init__(self, m_id: str, m_content: Dict[str,Any]):
        super().__init__(m_id,m_content)
        self.node_id = m_content.get("node_id", None)

    def execute(self, db_manager):
        #TODO: 
        pass

class GetDatumRequest(MessageRequest):
    M_TYPE = "get-datum"

    def __init__(self, m_id: str, m_content: Dict[str,Any]):
        super().__init__(m_id,m_content)
        self.event_id = self.m_content.get("event_id")

    def execute(self, db_manager):
        #TODO: execute datum query, handle errors, respond
        pass


