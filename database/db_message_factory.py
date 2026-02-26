# message_factory.py
from typing import Dict, Any, Optional
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
    def validate_message_dict(cls, data: Dict[str, Any]) -> bool:
        """Validate that the dictionary has required fields for message creation."""
        required_fields = {"m_id", "m_type"}
        
        m_type = data.get("m_type")
        if m_type not in cls.MESSAGE_TYPES:
            logging.error(f"Unknown message type: {m_type}")
            return False
        
        return True
    
    @classmethod
    def create_message(cls, data: Dict[str, Any]) -> Optional[Message]:
        """
        Create a message object from a dictionary.
        Passes original dict to avoid copying.
        
        Args:
            data: Dictionary containing complete message
        
        Returns:
            Message object of appropriate type, or None if creation fails
        """
        m_id = data.get("m_id")
        m_type = data.get("m_type")
        #Validate m_id and m_type
        
        try:
            message_class = cls.MESSAGE_TYPES[m_type]
            
            
            message = message_class(m_id, data)
            
            logging.debug(f"Created {m_type} message: {m_id}")
            return message
            
        except Exception as e:
            logging.error(f"Failed to create {m_type} message: {e}")
            return None
        