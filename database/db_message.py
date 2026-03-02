"""
Message Class
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging
from db_table_manager import TableManager
from queries import get_nodes,get_nodes,get_node_data_ids,get_datum, get_recent_inference, get_recent_raw_data,get_recent_raw_data
import json
from datetime import datetime

ERROR_CODES = ["NOT_FOUND", "INVALID_REQUEST", "INTERNAL_ERROR"]
M_ID_DB = "db_message_id" #temp id for DB messages, to be replaced by actual message ID generation logic


def _serialize_inference_full(inf) -> Optional[Dict[str, Any]]:
    """
    Serialize an InferenceResults ORM row to the full get-recent-inference record format.
    """
    if inf is None:
        return None

    feature_vector = {}
    if inf.feature_vector:
        try:
            feature_vector = json.loads(inf.feature_vector)
        except (json.JSONDecodeError, TypeError):
            feature_vector = {}

    return {
        "event_id": f"{inf.node_id}_{inf.timestamp}",
        "timestamp": f"{inf.timestamp}",
        "window_start": inf.window_start,
        "window_end": inf.window_end,
        "window_samples": inf.window_samples,
        "location_state": inf.location_state,
        "motion_class": inf.motion_class,
        "confidence": inf.confidence,
        "anomaly_detected": inf.anomaly_detected,
        "anomaly_score": inf.anomaly_score,
        "anomaly_type": inf.anomaly_type,
        "nearest_hub_id": inf.nearest_hub_id,
        "nearest_hub_distance": inf.nearest_hub_distance,
        "feature_vector": feature_vector,
    }


def _serialize_raw(raw) -> Dict[str, Any]:
    """
    Serialize a RawSensorData ORM row to the message_outputs format.
    Returns None if raw is None.
    """
    if raw is None:
        return None
    return {
        "event_id": f"{raw.node_id}_{raw.timestamp}",
        "timestamp": f"{raw.timestamp}",
        "seq": raw.seq,
        "accel_mss": {"x": raw.accel_x, "y": raw.accel_y, "z": raw.accel_z},
        "gyro_rads": {"x": raw.gyro_x, "y": raw.gyro_y, "z": raw.gyro_z},
        "gps": {
            "lat_deg": raw.gps_lat,
            "lon_deg": raw.gps_lon,
            "altitude_m": raw.gps_altitude_m,
        },
    }


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


    def __init__(self, m_id: str, m_type: str, responding_to: str,results: Dict[str, Any]):
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

        results = {
            "original_request": original_request,
            "error_code": error_code,
            "error_message": error_message
        }
        
        super().__init__(m_id, responding_to, self.M_TYPE, results)
        # self.original_request = original_request
        # self.error_code = error_code
        # self.error_message = error_message
    # def to_dict(self) -> Dict[str, Any]:
    #     """Convert error response to dictionary for publishing"""
    #     return {
    #         "m_id": self.m_id,
    #         "m_type": self.m_type,
    #         "responding_to": self.responding_to,
    #         "original_request": self.original_request,
    #         "error_code": self.error_code,
    #         "error_message": self.error_message
    #     }

class MessageRequest(Message):
    '''
    Abstract class for message requests.
    '''   
    @abstractmethod
    def execute(self, db_manager: TableManager) -> MessageResponse:
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
    def execute(self, db_manager: TableManager) -> Optional[ErrorResponse]:
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

    def execute(self, db_manager: TableManager) -> Optional[ErrorResponse]:
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
            
            db_manager.insert_raw_data([self.data]) 
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
        self.classification = inference_output.get("classification", None)

    def execute(self, db_manager: TableManager) -> Optional[ErrorResponse]:
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
            db_manager.insert_inference_results([self.m_content])
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
        
        logging.info("Executing get-nodes request")

        try: 
            #TODO: Implement the actual logic to retrieve nodes from the database using db_manager
            node_ids = get_nodes()  # Example function call to get nodes from the database
            logging.info(f"Retrieved nodes: {node_ids}")
            logging.info("Executing get-nodes request")
            return MessageResponse(
                m_id=M_ID_DB,
                m_type="get-nodes-response",
                responding_to=self.m_id,
                results={"nodes": node_ids})
        
        except Exception as e:
            return ErrorResponse(
                m_id=M_ID_DB,
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INTERNAL_ERROR"
            )


class GetNodeDataIdsRequest(MessageRequest):
    M_TYPE = "get-node-data-ids"

    def __init__(self, m_id: str, m_content: Dict[str,Any]):
        super().__init__(m_id,m_content)
        self.node_id = m_content.get("node_id", None)

    def execute(self, db_manager):
        
            
        logging.info(f"Executing get-node-data-ids for node: {self.node_id}")

        try:
            if not self.node_id:
                raise ValueError("Missing required field: node_id")

            data_ids = get_node_data_ids(self.node_id)

            if data_ids is None:
                return ErrorResponse(
                    m_id=M_ID_DB,
                    responding_to=self.m_id,
                    original_request=self.m_type,
                    error_message=f"Node not found: {self.node_id}",
                    error_code="NOT_FOUND",
                )

            return MessageResponse(
                m_id=M_ID_DB,
                m_type="get-node-data-ids-response",
                responding_to=self.m_id,
                results={"node_id": self.node_id, "data_ids": data_ids},
            )

        except ValueError as e:
            return ErrorResponse(
                m_id=M_ID_DB,
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INVALID_REQUEST",
            )
        except Exception as e:
            logging.error(f"get-node-data-ids failed: {e}")
            return ErrorResponse(
                m_id=M_ID_DB,
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INTERNAL_ERROR",
            )

class GetDatumRequest(MessageRequest):
    M_TYPE = "get-datum"

    def __init__(self, m_id: str, m_content: Dict[str,Any]):
        super().__init__(m_id,m_content)
        self.event_id = self.m_content.get("event_id")

    def execute(self, db_manager):
        logging.info(f"Executing get-datum for event: {self.event_id}")

        try:
            if not self.event_id:
                raise ValueError("Missing required field: event_id")

            result = get_datum(self.event_id)

            if result is None:
                return ErrorResponse(
                    m_id=M_ID_DB,
                    responding_to=self.m_id,
                    original_request=self.m_type,
                    error_message=f"Event ID not found: {self.event_id}",
                    error_code="NOT_FOUND",
                )


            return MessageResponse(
                m_id=M_ID_DB,
                m_type="get-datum-response",
                responding_to=self.m_id,
                results=result
            )

        except ValueError as e:
            return ErrorResponse(
                m_id=M_ID_DB,
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INVALID_REQUEST",
            )
        except Exception as e:
            logging.error(f"get-datum failed: {e}")
            return ErrorResponse(
                m_id=M_ID_DB,
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INTERNAL_ERROR",
            )


#TODO: Implement GetRecentRawDataRequest and GetRecentInferenceRequest classes
class GetRecentRawDataRequest(MessageRequest):

    M_TYPE = "get-recent-raw-data"

    def __init__(self, m_id: str, m_content: Dict[str, Any]):
        super().__init__(m_id, m_content)
        self.node_id = m_content.get("node_id", None)

    def execute(self, db_manager: TableManager) -> MessageResponse:
        logging.info(f"Executing get-recent-raw-data for node: {self.node_id}")

        try:
            if not self.node_id:
                raise ValueError("Missing required field: node_id")

            row = get_recent_raw_data(self.node_id)

            if row is None:
                return ErrorResponse(
                    m_id=M_ID_DB,
                    responding_to=self.m_id,
                    original_request=self.m_type,
                    error_message=f"No raw data found for node: {self.node_id}",
                    error_code="NOT_FOUND",
                )

            records = [_serialize_raw(row)]

            return MessageResponse(
                m_id=M_ID_DB,
                m_type="get-recent-raw-data-response",
                responding_to=self.m_id,
                results={"node_id": self.node_id, "records": records},
            )
        except ValueError as e:
            return ErrorResponse(
                m_id=M_ID_DB,
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INVALID_REQUEST",
            )
        except Exception as e:
            logging.error(f"get-recent-raw-data failed: {e}")
            return ErrorResponse(
                m_id=M_ID_DB,
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INTERNAL_ERROR",
            )


class GetRecentInferenceRequest(MessageRequest):

    M_TYPE = "get-recent-inference"

    def __init__(self, m_id: str, m_content: Dict[str, Any]):
        super().__init__(m_id, m_content)
        self.node_id = m_content.get("node_id", None)

    def execute(self, db_manager: TableManager) -> MessageResponse:
        logging.info(f"Executing get-recent-inference for node: {self.node_id}")

        try:
            if not self.node_id:
                raise ValueError("Missing required field: node_id")

            row = get_recent_inference(self.node_id)

            if row is None:
                return ErrorResponse(
                    m_id=M_ID_DB,
                    responding_to=self.m_id,
                    original_request=self.m_type,
                    error_message=f"No inference data found for node: {self.node_id}",
                    error_code="NOT_FOUND",
                )
            #if multiple rows, can do list comprehension to serialize each row and return list
            records = [_serialize_inference_full(row)]

            return MessageResponse(
                m_id=M_ID_DB,
                m_type="get-recent-inference-response",
                responding_to=self.m_id,
                results={"node_id": self.node_id, "records": records},
            )

        except ValueError as e:
            return ErrorResponse(
                m_id=M_ID_DB,
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INVALID_REQUEST",
            )
        except Exception as e:
            logging.error(f"get-recent-inference failed: {e}")
            return ErrorResponse(
                m_id=M_ID_DB,
                responding_to=self.m_id,
                original_request=self.m_type,
                error_message=str(e),
                error_code="INTERNAL_ERROR",
            )

#TODO: Method for generating unique message IDs instead of using M_ID_DB for all messages