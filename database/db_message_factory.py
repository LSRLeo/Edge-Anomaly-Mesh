# message_factory.py
from typing import Dict, Any, Optional, Tuple
from .db_message import Message, GetNodesRequest, GetNodeDataIdsRequest, GetDatumRequest, RawDataMessage, InferenceOutputMessage, ErrorResponse
import logging

class MessageFactory:
    """Factory for creating message objects - Memory optimized."""
    
    MESSAGE_TYPES = {
        "get-nodes": GetNodesRequest,
        "get-node-data-ids": GetNodeDataIdsRequest,
        "get-datum": GetDatumRequest,
        "raw-data": RawDataMessage,
        "inference-output": InferenceOutputMessage,
        "error": ErrorResponse
    }

    @classmethod
    def validate_message_dict(cls, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate that the dictionary has required fields for message creation."""
        required_fields = {"m_id", "m_type"}
        if not isinstance(data, dict):
            return False, "Input data is not a dictionary"
        if not all(field in data for field in required_fields):
            missing_fields = required_fields - data.keys()
            logging.error(f"Message dictionary missing required fields: {missing_fields}")
            return False, f"Missing fields: {missing_fields}"

        m_type = data.get("m_type")
        if not isinstance(m_type, str) or not m_type.strip():
            logging.error("Invalid 'm_type' field: must be a non-empty string")
            return False, "Invalid 'm_type' field: must be a non-empty string"
        if m_type not in cls.MESSAGE_TYPES:
            logging.error(f"Unknown message type: {m_type}")
            return False, f"Unknown message type: {m_type}. Valid types are: {cls.get_supported_types()}"
        #confirm m_id is a non-empty string
        m_id = data.get("m_id")
        if not isinstance(m_id, str) or not m_id.strip():
            logging.error("Invalid 'm_id' field: must be a non-empty string")
            return False, "Invalid 'm_id' field: must be a non-empty string"
        
        return True, ""
    
    @classmethod
    def create_message(cls, data: Dict[str, Any]) -> Optional[Message]:
        """
        Validate Message, Extract Validated Fields, Extract m_contents, and Instantiate Message Object.
        Create a message object from a dictionary.
        Passes original dict to avoid copying.
        
        Args:
            data: Dictionary containing complete message
        
        Returns:
            Message object of appropriate type, or None if creation fails
        """
        
        #Validate m_id and m_type
        is_valid, error_message = cls.validate_message_dict(data)
        if not is_valid:
            logging.error(f"Message validation failed: {error_message}")
            return None
        
        m_id = data.get("m_id")
        m_type = data.get("m_type")
        m_contents = {k: v for k, v in data.items() if k not in ["m_id", "m_type"]}
        try:
            message_class = cls.MESSAGE_TYPES[m_type]
            message = message_class(m_id, m_contents)
            
            logging.debug(f"Created {m_type} message: {m_id}")
            return message
            
        except Exception as e:
            logging.error(f"Failed to create {m_type} message: {e}")
            return None
        
    @classmethod
    def get_supported_types(cls) -> list:
        """Return list of supported message types"""
        return list(cls.MESSAGE_TYPES.keys())